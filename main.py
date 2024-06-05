from bs4 import BeautifulSoup
import requests
import telebot
import datetime
import schedule
import time
from pytz import timezone
import threading
from dotenv import load_dotenv
import os

# Ініціалізація Telegram-бота
bot = telebot.TeleBot(os.getenv('TOKEN'))

# Ідентифікатор каналу, куди будуть надсилатися повідомлення
channel_name = (os.getenv('CHANNEL_NAME'))


def extract_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    news_summary = soup.find('div', {'id': 'newsSummary'})
    stats_list = news_summary.find('ul')

    stats = {}
    for item in stats_list.find_all('li'):
        stat_key, stat_value = item.get_text().split(' – ')
        stats[stat_key] = stat_value

    return stats


def send_stats(chat_id):
    # Запит до веб-сайту та отримання HTML-контенту
    response = requests.get('https://zaxid.net/vtrati_rosiyan_u_viyni_proti_ukrayini_n1537635')
    html_content = response.content

    data = extract_data(html_content)
    current_date = get_current_date()

    response = f"Втрати росіян від початку вторгнення в Україну, станом на {current_date}:\n\n"
    response += "🐖Особовий склад: " + data.get('особового складу', '') + "\n"
    response += "☑️Танки: " + data.get('танків', '') + "\n"
    response += "☑️Бойові броньовані машини (ББМ): " + data.get('бойових броньованих машин (ББМ)', '') + "\n"
    response += "☑️Артилерійські системи: " + data.get('артилерійських систем', '') + "\n"
    response += "☑️Реактивні системи залпового вогню (РСЗВ): " + data.get('реактивних систем залпового вогню (РСЗВ)',
                                                                          '') + "\n"
    response += "☑️Засоби протиповітряної оборони: " + data.get('засобів протиповітряної оборони', '') + "\n"
    response += "☑️Літаки: " + data.get('літаків', '') + "\n"
    response += "☑️Гелікоптери: " + data.get('гелікоптерів', '') + "\n"
    response += "☑️Безпілотники оперативно-тактичного рівня: " + data.get('безпілотників оперативно-тактичного рівня',
                                                                          '') + "\n"
    response += "☑️Крилаті ракети: " + data.get('крилатих ракет', '') + "\n"
    response += "☑️Катери/кораблі: " + data.get('катерів/кораблів', '') + "\n"
    response += "☑️Автомобільна техніка і цистерни з паливом: " + data.get('автомобільної техніки і цистерн з паливом',
                                                                           '') + "\n"
    response += "☑️Спеціальна техніка: " + data.get('спеціальної техніки',
                                                    '') + "\n\n"
    response += "#дохларусня"

    bot.send_message(chat_id, response)


def get_current_date():
    kiev_timezone = timezone('Europe/Kiev')
    now = datetime.datetime.now(kiev_timezone)
    current_date = now.strftime("%d %B")
    months_dict = {
        'January': 'січня',
        'February': 'лютого',
        'March': 'березня',
        'April': 'квітня',
        'May': 'травня',
        'June': 'червня',
        'July': 'липня',
        'August': 'серпня',
        'September': 'вересня',
        'October': 'жовтня',
        'November': 'листопада',
        'December': 'грудня'
    }

    for month_en, month_ua in months_dict.items():
        current_date = current_date.replace(month_en, month_ua)

    return current_date


def send_daily_stats():
    send_stats(channel_name)


schedule.every().day.at("08:00").do(send_daily_stats)


def schedule_daily_stats():
    while True:
        schedule.run_pending()
        time.sleep(1)


# Обробка команди "/start"
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Вітаю! Я бот, який показує втрати росіян 🐖\nНапиши /get_stats, щоб отримати статистику")


# Обробка команди "/get_stats"
@bot.message_handler(commands=['get_stats'])
def send_stats_message(message):
    chat_id = message.chat.id
    send_stats(chat_id)



# Запуск бота в окремому потоці
def run_bot():
    bot.polling()


# Запуск бота та планувальника в окремих потоках
bot_thread = threading.Thread(target=run_bot)
schedule_thread = threading.Thread(target=schedule_daily_stats)

bot_thread.start()
schedule_thread.start()
