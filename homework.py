import logging
import os
import time
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(
    'my_logs.log', maxBytes=50000000, backupCount=2)
logger_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(name)s - %(message)s')
handler.setFormatter(logger_formatter)
logger.addHandler(handler)

PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
PRAKTIKUM_URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework_name is not None:
        if homework.get('status') == 'rejected':
            verdict = 'К сожалению в работе нашлись ошибки.'
        else:
            verdict = ('Ревьюеру всё понравилось, можно приступать к '
                       'следующему уроку.')
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    if current_timestamp is None:
        current_timestamp = int(time.time())
    # current_timestamp = current_timestamp - 300000
    params = {
        'from_date': current_timestamp
    }
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    try:
        homework_statuses = requests.get(
            url=PRAKTIKUM_URL, headers=headers, params=params)
        return homework_statuses.json()
    except Exception as e:
        message = f'Бот сломался в методе get_homework_statuses: {e}'
        # logger.error(
        #     f'I broke down in get_homework_status!!! my error ====>>>{e}')


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    # проинициализировать бота здесь
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())  # начальное значение timestamp
    # logger.debug('I stared to work')
    send_message('I started to work', bot_client)
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            send_message('Bot try to check homework status', bot_client)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]), bot_client)
                # logger.info('I sent you a message')
            current_timestamp = new_homework.get(
                'current_date', current_timestamp)  # обновить timestamp
            time.sleep(1200)

        except Exception as e:
            message = f'Бот столкнулся с ошибкой: {e}'
            # logger.error(f'I broke down!!! my error ====>>>{e}')
            send_message(message, bot_client)
            time.sleep(5)


if __name__ == '__main__':
    main()
