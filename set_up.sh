#!/bin/bash
#
# Short little script to make setting up my development environment easier.
# Will have to make sure this script is executable before it can be run.
# May have to be changed since I haven't used it yet
#
sudo apt update
sudo snap install atom --classic
sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools

sudo apt install python3-venv

sudo apt-get install -y default-libmysqlclient-dev

sudo apt install mysql-server

sudo apt install wkhtmltopdf

python3 -m venv venv

source venv/bin/activate

pip install wheel

pip install -r requirements.txt

sudo mysql_secure_installation
