<div align="center">
<em><img src="https://github.com/rss-translator/RSS-Translator/assets/2398708/8f10db75-d5b4-4cdd-9fd6-7d319d20079f" height="90px"></em>
<h1>RSS Translator<br/><sub>Open Source, Lightweight, Self-hosted</sub></h1>
</div>
<br/>

Check [Demo](https://demo.rsstranslator.com) for preview\
Telegram Group: https://t.me/rsstranslator \
Development Progress: https://github.com/orgs/rss-translator/projects/2/views/1

The main reason for development was to solve personal needs. I followed many foreign bloggers, but the English titles were not conducive to quick filtering, so I made an RSS translator.
### Table of Contents
- [Functions](#functions)
- [Technology Stack](#technology-stack)
- [Installation Requirements](#installation-requirements)
- [Installation Method](#installation-method)
 - [Automatic Installation](#automatic-installation-recommended)
- [Install with Docker](#install-with-docker)
 - [Manual Installation](#manual-installation)
- [Upgrade](#upgrade)
- [Uninstall](#uninstall)
- [Enable SSL](#enable-ssl)
- [IPv6](#IPv6)
- [Usage Guide](#usage-guide)
- [Sponsorship](#sponsorship)
- [Contribution](#contribution)

### Functions:
1. Ability to add and translate the titles of RSS sources (content translation is under development).
2. Ability to subscribe to translated RSS or simply proxy the original RSS.
3. Support for multiple translation engines, with each source being able to specify a translation engine.
4. Control over the update frequency for each source and the ability to view translation status.
5. Caching of all translation content to minimize translation costs.
6. Ability to view the number of tokens/characters used by each source.
   
Currently supported translation engines: 
- DeepL API
- OpenAI API
- Azure OpenAI API
- Microsoft Translate API

We will add more translation engines soon.

### Technology Stack
Django 5

### Installation Requirements
Ubuntu 22.04 LTS / Debian 12 (Memory recommendation of 512M above)\
Python >= 3.10

### Installation Method
#### Automatic Installation (Recommended)
Download the installation script [install_update.sh](https://github.com/rss-translator/RSS-Translator/blob/main/deploy/install_update.sh)\
`wget "https://raw.githubusercontent.com/rss-translator/RSS-Translator/main/deploy/install_update.sh"`

Use root to grant execution permissions, and this script can be run multiple times and can be used for updates
```
sudo chmod +x rsstranslator_install_update.sh
sudo ./rsstranslator_install_update.sh
```

After successful installation, access [http://127.0.0.1:8000]\
Default account: admin\
Default password: rsstranslator\
Please change your password after logging in\
If you need to enable SSL (https), please refer to [here](#enable-ssl)

---

#### Install with Docker

Create a data folder to store the data\
`mkdir -p ~/rsstranslator/`\
Enter the rsstranslator folder\
`cd ~/rsstranslator`\
Download the [docker-compose.yml](deploy/docker-compose.yml) file\
`wget "https://raw.githubusercontent.com/rss-translator/RSS-Translator/main/deploy/docker-compose.yml"`\
Start the container\
`docker-compose up -d`\
Done\
If you encounter a CSRF error, you need to set the environment variable `
CSRF_TRUSTED_ORIGINS` to allow your domain to access, for example:\
`CSRF_TRUSTED_ORIGINS=https://*.example.com`\
After setting, please restart the service

---
#### Manual Installation
Install necessary software\
`sudo apt install python3-venv git zip -y`\
Download the project\
`git clone https://github.com/rss-translator/RSS-Translator.git`\
Create executing user
```
sudo useradd -r -s /sbin/nologin rsstranslator
sudo usermod -a -G rsstranslator your_user_name
```
Move folders and correct permissions
```
mv -f RSS-Translator /home/rsstranslator
mkdir /home/rsstranslator/data
sudo chown -R rsstranslator:rsstranslator /home/rsstranslator
sudo chmod -R 775 /home/rsstranslator
sudo chmod a+x /home/rsstranslator/deploy/*.sh
```
Create virtual environment\
`sudo -u rsstranslator /bin/bash -c "python3 -m venv /home/rsstranslator/.venv"`\

Install dependencies\
`sudo -u rsstranslator /bin/bash -c "/home/rsstranslator/.venv/bin/pip install -q -r /home/rsstranslator/requirements/prod.txt"`\
Create service\
`sudo nano /etc/systemd/system/rsstranslator.service`\
Paste and modify the following content
```
[Unit] Description=RSS Translator Application Service After=network.target

[Service] Type=simple
User=rsstranslator
Group=rsstranslator
WorkingDirectory=/home/rsstranslator/
ExecStart=/home/rsstranslator/deploy/start.sh
Restart=always RestartSec=2

[Install] WantedBy=multi-user.target
```
Restart daemon and enable startup at boot
```
sudo systemctl daemon-reload
sudo systemctl enable rsstranslator.service
```
Initialize runtime environment
```
sudo -u rsstranslator /bin/bash -c "/home/rsstranslator/.venv/bin/python /home/rsstranslator/manage.py makemigrations"
sudo -u rsstranslator /bin/bash -c "/home/rsstranslator/.venv/bin/python /home/rsstranslator/manage.py migrate"
sudo -u rsstranslator /bin/bash -c "/home/rsstranslator/.venv/bin/python /home/rsstranslator/manage.py collectstatic --noinput"
sudo -u rsstranslator /bin/bash -c "/home/rsstranslator/.venv/bin/python /home/rsstranslator/manage.py create_default_superuser"
```
Start the service\
`systemctl start rsstranslator.service`
Check the service status\
`systemctl status rsstranslator.service`
Installation complete, visit [http://127.0.0.1:8000](http://127.0.0.1:8000)
### Upgrade
`sudo . /home/rsstranslator/deploy/install_update.sh`
### Uninstall
`sudo . /home/rsstranslator/deploy/uninstall.sh`
Note: This uninstall script does not delete the data backup files in the /tmp directory, just in case!

---
### Enable SSL
It is recommended to use caddy with cloudflare's dns proxy.
Install Caddy: https://caddyserver.com/docs/install#debian-ubuntu-raspbian 

Create caddy configuration file\
You can refer to [/home/rsstranslator/deploy/Caddyfile](deploy/Caddyfile) for modification, normally you just need to
modify the domain name in the first line.\
If you use docker to install, please refer
to [/home/rsstranslator/deploy/Caddyfile_for_docker](deploy/Caddyfile_for_docker)\
`sudo nano /home/rsstranslator/deploy/Caddyfile`\
The content is as follows.

```Caddyfile
example.com {
        encode zstd gzip
        #tls internal
        handle_path /static/* {
                root * /home/rsstranslator/static/
                file_server
        }

        handle_path /media/* {
                root * /home/rsstranslator/media/ file_server } handle_path /media/* { root * /home/rsstranslator/static/
                file_server
        }

        reverse_proxy 127.0.0.1:8000
}
```
Once you've made the changes, copy the configuration file and restart it
```
sudo mv /etc/caddy/Caddyfile /etc/caddy/Caddyfile.back
sudo cp /home/rsstranslator/deploy/Caddyfile /etc/caddy/
sudo systemctl reload caddy
``
If dns proxy is enabled in cloudflare, you need to select Full for encryption mode on the SSL/TLS page in cloudflare.
### IPv6
IPv4 and IPv6 cannot be supported at the same time;\
If you want set the server to listen on IPv6 address, just edit the deploy/start.sh file, change `0.0.0.0` to `::`, then restart the service.
### Usage Guide
After login for the first time, it is recommended to change the default password by clicking Change Password on the top right.
It is recommended to add the translation engine first before adding the feed, unless you just want to proxy the source.
After adding the feed for the first time, it will take some time to translate and generate it, it may take about 1 minute \
Status Note: \
! [loading](https://github.com/rss-translator/RSS-Translator/assets/2398708/c796ed1d-b088-4e34-9419-c65fe4cf47c4): being processed \
! [yes](https://github.com/rss-translator/RSS-Translator/assets/2398708/3e974467-948f-486a-9923-91978d47e7ea): Processing completed \
! [no](https://github.com/rss-translator/RSS-Translator/assets/2398708/6a6a5fdc-ac8b-4e7a-b3ae-5093adcf9021): Processing failed \
The current status will not be updated automatically, please refresh the page to get the latest status.
### Sponsorship
Thank you for your sponsorship\
[AFDIAN](https://afdian.net/a/versun)
### Contribution
[Please check the Wiki](https://github.com/rss-translator/RSS-Translator/wiki)
