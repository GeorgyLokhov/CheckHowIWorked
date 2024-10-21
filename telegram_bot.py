import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import schedule
import time
import threading
import requests
from datetime import datetime
import os

# Конфигурации
TELEGRAM_TOKEN = '7505210934:AAFkCSqtKGEyjUzICCQg-ehaA6HJ3xP0WVk'
USER_ID = 386701740
YANDEX_DISK_TOKEN = 'y0_AgAAAABz8Y7CAAyjpQAAAAEVOEgUAAAPxWPCBlJI0LWIDxKEEghg1vNZzg'
FILE_PATH = '/Мой сейф/Входящие/Отчёты с бота.md'

bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Флаг, отслеживающий ожидание ответа
waiting_for_answer = False
last_question_time = None

def send_question():
    global waiting_for_answer, last_question_time
    if not waiting_for_answer:
        bot.send_message(chat_id=USER_ID, text="Что было сделано за это время?")
        waiting_for_answer = True
        last_question_time = datetime.now()

def handle_response(update, context):
    global waiting_for_answer
    user_id = update.message.from_user.id
    if user_id == USER_ID:
        if waiting_for_answer:
            response = update.message.text
            save_to_yandex_disk(response)
            bot.send_message(chat_id=USER_ID, text="Информация перенесена в базу данных.")
            waiting_for_answer = False
        else:
            bot.send_message(chat_id=USER_ID, text="Вы не успели в 30-минутный интервал для отчёта. Ждите следующего интервала.")

def save_to_yandex_disk(text):
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = f"\n## Отчёт от {current_time}\n{text}\n"
        
        # Получение ссылки на загрузку файла
        upload_url = f"https://cloud-api.yandex.net/v1/disk/resources/upload?path={FILE_PATH}&overwrite=true"
        headers = {"Authorization": f"OAuth {YANDEX_DISK_TOKEN}"}
        response = requests.get(upload_url, headers=headers)
        upload_link = response.json().get('href')
        
        # Запись данных в файл на Яндекс.Диске
        requests.put(upload_link, files={"file": data.encode('utf-8')})
    except Exception as e:
        bot.send_message(chat_id=USER_ID, text=f"Ошибка при сохранении на Яндекс.Диск: {str(e)}")

def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_response))

    updater.start_polling()

    # Расписание отправки вопросов
    schedule.every().day.at("10:30").do(send_question)
    schedule.every().day.at("12:30").do(send_question)
    schedule.every().day.at("16:30").do(send_question)
    schedule.every().day.at("18:10").do(send_question)  # Новое время запуска
    schedule.every().day.at("18:30").do(send_question)
    schedule.every().day.at("21:00").do(send_question)
    schedule.every().day.at("23:00").do(send_question)

    # Запуск проверки расписания в отдельном потоке
    threading.Thread(target=schedule_checker).start()

    updater.idle()

if __name__ == '__main__':
    main()
