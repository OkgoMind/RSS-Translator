import logging
import os
from pathlib import Path

import feedparser
from django.conf import settings
from django.utils import timezone
from huey.contrib.djhuey import HUEY as huey
from huey.contrib.djhuey import on_startup, db_task, on_shutdown, task
from translator.tasks import translate_feed

from .models import O_Feed, T_Feed
from .utils.feed_action import fetch_feed, generate_atom_feed

# from huey_monitor.models import TaskModel

log = logging.getLogger('huey')


# @periodic_task(crontab( minute='*/1'))
@on_startup()
def schedule_update():
    feeds = O_Feed.objects.all()
    for feed in feeds:
        update_original_feed.schedule(args=(feed.sid,), delay=feed.update_frequency * 60)


@on_shutdown()
def flush_all():
    huey.storage.flush_queue()
    huey.storage.flush_schedule()
    huey.storage.flush_results()
    # clean TaskModel all data
    # TaskModel.objects.all().delete()


@task(retries=3)
def update_original_feed(sid: str):
    try:
        obj = O_Feed.objects.get(sid=sid)
    except O_Feed.DoesNotExist:
        return False

    log.debug("Call task update_original_feed: %s", obj.feed_url)
    feed_dir_path = Path(settings.DATA_FOLDER) / "feeds"

    if not os.path.exists(feed_dir_path):
        os.makedirs(feed_dir_path)

    original_feed_file_path = feed_dir_path / f"{obj.sid}.xml"
    try:
        fetch_feed_results = fetch_feed(obj.feed_url, obj.modified, obj.etag)

        if fetch_feed_results['error']:
            raise Exception(f"Fetch Original Feed Failed: ({obj.sid}){obj.feed_url}")
        elif not fetch_feed_results.get("update"):
            log.debug("Original Feed is up to date, Skip fetch:(%s)%s", obj.sid, obj.feed_url)
        else:
            with open(original_feed_file_path, "w", encoding="utf-8") as f:
                f.write(fetch_feed_results.get("xml"))
            feed = fetch_feed_results.get("feed")
            obj.name = feed.feed.title
            obj.size = os.path.getsize(original_feed_file_path)
            obj.modified = feed.get(
                "modified",
                timezone.now().strftime("%Y-%m-%d %H:%M:%S %Z")
            )
            obj.etag = feed.get("etag", '')

        obj.valid = True
    except Exception as e:
        obj.valid = False
        log.error("task update_original_feed error: %s", str(e))
    finally:
        obj.save()
        update_original_feed.schedule(args=(obj.sid,), delay=obj.update_frequency * 60)

    # Update T_Feeds
    t_feeds = obj.t_feed_set.all()
    for t_feed in t_feeds:
        update_translated_feed.schedule(args=(t_feed.sid,), delay=1)


@task(retries=3)
def update_translated_feed(sid: str):
    try:
        obj = T_Feed.objects.get(sid=sid)
    except T_Feed.DoesNotExist:
        return False
    log.debug("Call task update_translated_feed: (%s)(%s)", obj.language, obj.o_feed.feed_url)

    if obj.o_feed.pk is None:
        log.error("Unable translate feed, because Original Feed is None: (%s)%s", obj.language, obj.o_feed.feed_url)
        return False
    if obj.modified == obj.o_feed.modified:
        log.debug("Translated Feed is up to date, Skip translation: (%s)%s", obj.language, obj.o_feed.feed_url)
        return False

    feed_dir_path = f"{settings.DATA_FOLDER}/feeds"
    if not os.path.exists(feed_dir_path):
        os.makedirs(feed_dir_path)

    original_feed_file_path = f"{feed_dir_path}/{obj.o_feed.sid}.xml"
    if not os.path.exists(original_feed_file_path):
        obj.o_feed.update()

    translated_feed_file_path = f"{feed_dir_path}/{obj.sid}.xml"

    original_feed = feedparser.parse(original_feed_file_path)

    try:
        if original_feed:
            engine = obj.o_feed.translator
            # log.debug("Start translate feed: [%s]%s" , obj.language, obj.o_feed.feed_url)
            results = translate_feed.call_local(
                feed=original_feed,
                target_language=obj.language,
                engine=engine,
                translate_title=obj.translate_title,
                translate_content=obj.translate_content,
            )

            if not results:
                return False
            else:
                feed = results.get("feed")
                total_tokens = results.get("tokens")
                translated_characters = results.get("characters")
            xml_str = generate_atom_feed(feed)  # ???feed is feedparser object

            # There can only be one billing method at a time, either token or character count.
            if total_tokens > 0:
                obj.total_tokens += total_tokens
            else:
                obj.total_characters += translated_characters

            obj.modified = obj.o_feed.modified
            with open(translated_feed_file_path, "w", encoding="utf-8") as f:
                f.write(xml_str)
            obj.size = os.path.getsize(translated_feed_file_path)
            obj.status = True
    except Exception as e:
        log.error("task update_translated_feed error: %s", str(e))
        obj.status = False
    finally:
        obj.save()
