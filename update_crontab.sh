#!/bin/bash

# Загрузка переменных из .env файла
export $(grep -v '^#' /root/telegram_message_saver/.env | xargs)

/usr/bin/python3 /root/telegram_message_saver/message_saver.py
