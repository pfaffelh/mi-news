#!/bin/bash

CURRENTDATE=`date +"%Y-%m-%d-%H-%M"`

echo Current Date and Time is: ${CURRENTDATE}

# Server-Hostname
SERVER="www2"

# Benutzername für die SSH-Verbindung
USERNAME="flask-reader"

# Führe den Befehl "deploy" auf dem Remote-Server aus
ssh $USERNAME@$SERVER 'cd mi-news/backup; CURRENTDATE=`date +"%Y-%m-%d-%H-%M"`; mongodump --db news --archive=news_backup_${CURRENTDATE}'
scp $USERNAME@$SERVER:~/mi-news/backup/news_backup_${CURRENTDATE} backup
mongorestore --drop --archive=backup/news_backup_${CURRENTDATE}

