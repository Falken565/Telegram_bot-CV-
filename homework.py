import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
    filename='homework.log',
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s'
)

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telegram.Bot(token=TELEGRAM_TOKEN)

VER_DICT = {
    'rejected': 'К сожалению, в работе нашлись ошибки.',
    'reviewing': 'Работа проверяется, наберитесь терпения',
    'approved': 'Ревьюеру всё понравилось, работа зачтена!'
}

url = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    if homework_name is None or status is None:
        return 'Пришли пустые данные'
    if status in VER_DICT:
        verdict = VER_DICT[status]
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    return 'Неизвестный статус работы )))'


def get_homeworks(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp or int(time.time())}
    try:
        homework_statuses = requests.get(
            url, headers=headers, params=payload
        )
    except requests.exceptions.RequestException as error:
        logging.error(error, exc_info=True)
        raise requests.exceptions.RequestException(error)
    try:
        return homework_statuses.json()
    except ValueError as e:
        logging.error(e, exc_info=True)
        raise ValueError(e)
    except TypeError as e:
        logging.error(e, exc_info=True)
        raise TypeError(e)


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())
    while True:
        try:
            if get_homeworks(current_timestamp).get('homeworks'):
                homeworks = get_homeworks(current_timestamp).get('homeworks')
                homework = homeworks[0]
                message = parse_homework_status(homework)
                current_timestamp = get_homeworks(
                    current_timestamp).get('current_date')
                send_message(message)
                time.sleep(20 * 60)
            time.sleep(20 * 60)
        except Exception as e:
            logging.error(e, exc_info=True)
            message = f'Бот упал с ошибкой: {e}'
            send_message(message)
            time.sleep(5)


if __name__ == '__main__':
    main()
