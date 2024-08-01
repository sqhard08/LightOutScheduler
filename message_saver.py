import logging
import re
import subprocess
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from dotenv import load_dotenv
import os

# Загрузка переменных из .env файла
load_dotenv()

# Параметры учетной записи Telegram
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone_number = os.getenv('PHONE_NUMBER')

# ID чатов
source_chat_id = os.getenv('SOURCE_CHAT_ID')
destination_chat_id = os.getenv('DESTINATION_CHAT_ID')

# Токен бота
bot_token = os.getenv('BOT_TOKEN')

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='/root/telegram_message_saver/message_saver.log'
)
logger = logging.getLogger(__name__)

# Инициализация клиента Telegram
client = TelegramClient('session_name', api_id, api_hash)

@client.on(events.NewMessage(chats=source_chat_id))
async def handler(event):
    message = event.raw_text

    # Сохранение всех сообщений в файл
    with open('/root/telegram_message_saver/messages.txt', 'a') as f:
        f.write(f"{datetime.now()} - {message}\n")

    # Проверка сообщения на наличие информации о "Черга 4"
    if re.search(r'Черга\s*4|4\s*черга|Черги\s*4', message, re.IGNORECASE):
        # Отправка сообщения через curl
        try:
            curl_command = [
                'curl', '--socks5-basic',
                '-X', 'POST',
                f'https://api.telegram.org/bot{bot_token}/sendMessage',
                '-d', f'chat_id={destination_chat_id}',
                '-d', f'text={message}',
                '-d', 'disable_notification=false'
            ]
            subprocess.run(curl_command, check=True)
            logger.info("Сообщение отправлено через curl")
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка при отправке сообщения через curl: {str(e)}")

        shutdown_time_str = None

        # Первая проверка
        match1 = re.search(r'(\d{2}:\d{2})\s*–\s*\d{2}:\d{2}\s+вимикатиметься\s+4\s+черга', message, re.IGNORECASE)
        if match1:
            shutdown_time_str = match1.group(1)

        # Вторая проверка
        if not shutdown_time_str:
            match2 = re.search(r'(Черга\s*4|4\s*черга|Черги\s*4).*?(\d{2}:\d{2})', message, re.IGNORECASE)
            if match2:
                shutdown_time_str = match2.group(2)

        # Третья проверка
        if not shutdown_time_str:
            match3 = re.search(r'🟢\s*(\d{2}:\d{2})\s*-\s*\d{2}:\d{2}\s*вимикатиметься\s*4\s*черга', message, re.IGNORECASE)
            if match3:
                shutdown_time_str = match3.group(1)

        if shutdown_time_str:
            logger.info(f"Получено время отключения для Черга 4: {shutdown_time_str}")
            # Преобразование времени в datetime объект и вычитание 5 минут
            shutdown_time = datetime.strptime(shutdown_time_str, '%H:%M')
            shutdown_time = shutdown_time - timedelta(minutes=5)
            logger.info(f"Обновленное время для crontab: {shutdown_time.strftime('%H:%M')}")
            update_crontab(shutdown_time)

def update_crontab(shutdown_time):
    hour = shutdown_time.hour
    minute = shutdown_time.minute
    new_cron_job = f"{minute} {hour} * * * /root/telegram_message_saver/shutdown_script.sh\n"

    with open("/tmp/crontab.tmp", "w") as f:
        f.write(new_cron_job)

    # Установка нового crontab
    import os
    os.system("crontab /tmp/crontab.tmp")
    logger.info("Crontab обновлен")

async def main():
    await client.start(phone_number)
    print("Client created")
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
