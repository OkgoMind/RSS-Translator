<div align="center">
<em><img src="https://github.com/rss-translator/RSS-Translator/assets/2398708/8f10db75-d5b4-4cdd-9fd6-7d319d20079f" height="90px"></em>
<h1>RSS翻译器<br/><sub>开源、简洁、可自部署</sub></h1>
</div>
<br/>

[English](README_EN.md)

可查看 [Demo](https://demo.rsstranslator.com) 预览效果\
Telegram交流群: https://t.me/rsstranslator \
开发进度：https://github.com/orgs/rss-translator/projects/2/views/1

开发的主要原因是解决个人需求，关注了很多国外的博主，但英文标题不利于快速筛选，因此做了RSS翻译器。
### 目录
- [功能](#功能)
- [技术栈](#技术栈)
- [安装要求](#安装要求)
- [安装方法](#安装方法)
  - [自动安装](#自动安装推荐)
  - [使用Docker安装](#使用docker安装)
  - [手动安装](#手动安装)
- [升级](#升级)
- [卸载](#卸载)
- [开启SSL](#开启ssl)
- [IPv6](#IPv6)
- [使用说明](#使用说明)
- [赞助](#赞助)
- [贡献](#贡献)


### 功能：
1. 可添加并翻译RSS源的标题(内容翻译正在开发中)
2. 可订阅翻译后的RSS，也可仅代理原来的RSS
3. 可添加多种翻译引擎，每个源都可以指定一个翻译引擎
4. 可控制每个源的更新频率和查看翻译状态
5. 缓存所有翻译内容，尽可能减少翻译费用
6. 可查看每个源所花费的Token/字符数
   
目前支持的翻译引擎：
- DeepL API
- OpenAI API
- Azure OpenAI API
- Microsoft Translate API 

陆续增加中

### 技术栈
Django 5

### 安装要求
Ubuntu 22.04 LTS / Debian 12 (内存建议512M以上)\
Python >= 3.10

### 安装方法
#### 自动安装（推荐）
下载安装脚本[install_update.sh](https://github.com/rss-translator/RSS-Translator/blob/main/deploy/install_update.sh)\
`wget "https://raw.githubusercontent.com/rss-translator/RSS-Translator/main/deploy/install_update.sh"`

使用root赋予运行权限后执行, 此脚本可多次运行，并可用于升级更新
```
sudo chmod +x rsstranslator_install_update.sh
sudo ./rsstranslator_install_update.sh
```
安装成功后，访问[http://127.0.0.1:8000](http://127.0.0.1:8000)\
默认账户：admin\
默认密码：rsstranslator\
请登录后立即修改你的密码\
如需开启SSL(https)，请参考[这里](#开启SSL)

---

#### 使用Docker安装

创建数据文件夹，以存放数据\
`mkdir -p ~/rsstranslator/`\
进入rsstranslator文件夹\
`cd ~/rsstranslator`\
下载[docker-compose.yml](deploy/docker-compose.yml)文件\
`wget "https://raw.githubusercontent.com/rss-translator/RSS-Translator/main/deploy/docker-compose.yml"`\
启动容器\
`docker-compose up -d`\
完成\
如果您遇到CSRF的报错问题，则您需要设置环境变量`CSRF_TRUSTED_ORIGINS`，以允许您的域名访问，例如：\
`CSRF_TRUSTED_ORIGINS=https://*.example.com`\
设置完成后请重启服务

---
#### 手动安装
安装必要软件\
`sudo apt install python3-venv git zip -y`\
下载项目\
`git clone https://github.com/rss-translator/RSS-Translator.git`\
创建执行用户
```
sudo useradd -r -s /sbin/nologin rsstranslator
sudo usermod -a -G rsstranslator your_user_name
```
移动文件夹并修正权限
```
mv -f RSS-Translator /home/rsstranslator
mkdir /home/rsstranslator/data
sudo chown -R rsstranslator:rsstranslator /home/rsstranslator
sudo chmod -R 775 /home/rsstranslator
sudo chmod a+x /home/rsstranslator/deploy/*.sh
```
创建虚拟环境
```
sudo -u rsstranslator /bin/bash -c "python3 -m venv /home/rsstranslator/.venv"
```
安装依赖\
`sudo -u rsstranslator /bin/bash -c "/home/rsstranslator/.venv/bin/pip install -q -r /home/rsstranslator/requirements/prod.txt"`\
创建服务\
`sudo nano /etc/systemd/system/rsstranslator.service`\
粘贴并修改下面的内容
```
[Unit]
Description=RSS Translator Application Service
After=network.target

[Service]
Type=simple
User=rsstranslator
Group=rsstranslator
WorkingDirectory=/home/rsstranslator/
ExecStart=/home/rsstranslator/deploy/start.sh
Restart=always
RestartSec=2

[Install]
WantedBy=multi-user.target
```
重启daemon并开机自启动
```
sudo systemctl daemon-reload
sudo systemctl enable rsstranslator.service
```
初始化运行环境
```
sudo -u rsstranslator /bin/bash -c "/home/rsstranslator/.venv/bin/python /home/rsstranslator/manage.py makemigrations"
sudo -u rsstranslator /bin/bash -c "/home/rsstranslator/.venv/bin/python /home/rsstranslator/manage.py migrate"
sudo -u rsstranslator /bin/bash -c "/home/rsstranslator/.venv/bin/python /home/rsstranslator/manage.py collectstatic --noinput"
sudo -u rsstranslator /bin/bash -c "/home/rsstranslator/.venv/bin/python /home/rsstranslator/manage.py create_default_superuser"
```
启动服务\
`systemctl start rsstranslator.service`\
查看服务状态\
`systemctl status rsstranslator.service`\
安装完成，访问 http://127.0.0.1:8000
### 升级
`sudo ./home/rsstranslator/deploy/install_update.sh`
### 卸载
`sudo ./home/rsstranslator/deploy/uninstall.sh`
注意：该卸载脚本并不会删除/tmp目录下的数据备份文件，以防万一

---
### 开启SSL
建议使用caddy并配合cloudflare的dns代理使用\
安装Caddy: https://caddyserver.com/docs/install#debian-ubuntu-raspbian 

创建caddy配置文件\
可参考[/home/rsstranslator/deploy/Caddyfile](deploy/Caddyfile)进行修改，正常只要修改第一行的域名即可\
docker用户请参考[/home/rsstranslator/deploy/Caddyfile_for_docker](deploy/Caddyfile_for_docker)\
`sudo nano /home/rsstranslator/deploy/Caddyfile`\
内容如下:
```
example.com {
        encode zstd gzip
        #tls internal
        handle_path /static/* {
                root * /home/rsstranslator/static/
                file_server
        }

        handle_path /media/* {
                root * /home/rsstranslator/media/
                file_server
        }

        reverse_proxy 127.0.0.1:8000
}
```
修改完成后，复制配置文件，并重启即可
```
sudo mv /etc/caddy/Caddyfile /etc/caddy/Caddyfile.back
sudo cp /home/rsstranslator/deploy/Caddyfile /etc/caddy/
sudo systemctl reload caddy
```
如果cloudflare开启了dns代理，则需要在cloudflare的SSL/TLS页面，加密模式选择Full
### IPv6
目前无法同时支持IPv4和IPv6；\
如需改为监听IPv6地址，仅需修改deploy/start.sh文件，将`0.0.0.0`改为`::`, 然后重启服务即可

### 使用说明
首次登录后，建议点击右上方的修改密码修改默认密码\
建议先添加翻译引擎后再添加Feed，除非只是想代理源\
首次添加源后，需要一些时间进行翻译和生成，可能会耗时1分钟左右\
状态说明：\
![loading](https://github.com/rss-translator/RSS-Translator/assets/2398708/c796ed1d-b088-4e34-9419-c65fe4cf47c4)：正在处理中\
![yes](https://github.com/rss-translator/RSS-Translator/assets/2398708/3e974467-948f-486a-9923-91978d47e7ea)：处理完成\
![no](https://github.com/rss-translator/RSS-Translator/assets/2398708/6a6a5fdc-ac8b-4e7a-b3ae-5093adcf9021)：处理失败\
目前状态不会自动更新，请刷新页面以获取最新状态
### 赞助
感谢您的赞助\
[爱发电](https://afdian.net/a/versun)
### 贡献
[请查看Wiki](https://github.com/rss-translator/RSS-Translator/wiki)
