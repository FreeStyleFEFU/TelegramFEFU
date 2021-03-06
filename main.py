import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import telebot
from multiprocessing import Process
import time
import schedule


general_data = []

TOKEN = '1465745696:AAFiPZRJFZjhOwXv8y18yFjN6A9WPh4IA2Y'
cluster = MongoClient('mongodb+srv://FreeStyle:Kp10SSss17WWbZ1u@cluster0.7ed7r.mongodb.net/ProrectorsFEFU?retryWrites=true&w=majority')
db = cluster['ProrectorsFEFU']
collection = db['CollectionFEFU']

HOST = 'https://www.dvfu.ru'
URLS = ['https://www.dvfu.ru/about/rectorate/4915/', 'https://www.dvfu.ru/about/rectorate/22008/', 'https://www.dvfu.ru/about/rectorate/288/', 'https://www.dvfu.ru/about/rectorate/4925/', 'https://www.dvfu.ru/about/rectorate/4917/', 'https://www.dvfu.ru/about/rectorate/32416/', 'https://www.dvfu.ru/about/rectorate/4921/', 'https://www.dvfu.ru/about/rectorate/37260/', 'https://www.dvfu.ru/about/rectorate/4923/', 'https://www.dvfu.ru/about/rectorate/33014/', 'https://www.dvfu.ru/about/rectorate/4913/']
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 YaBrowser/20.12.2.105 Yowser/2.5 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
}
CLASSES = ['author-name', 'author-dolj', 'block-address', 'block-phone', 'block-email']
KEYS = ["ФИО", "Должность", "Адрес", "Телефон", "Почта"]

def get_html(url):
    response = requests.get(url, headers=HEADERS).text
    return response


def get_data_json():
    htmls = []
    data = []
    for url in URLS:
        htmls.append(get_html(url))

    for i in range(len(htmls)):
        data.append([])
        soup = BeautifulSoup(htmls[i], 'html.parser')
        for c in range(len(CLASSES)):
            try:
                data[i].append(
                    {
                        KEYS[c] : soup.find('div', class_=CLASSES[c]).text
                    }
                )
            except:
                data[i].append(
                    {
                        KEYS[c] : 'Пусто Пусто Пусто'
                    }
                )
            data[i][0].update(data[i][c])

    split_fio = []
    for d in data:
        fio = d[0]['ФИО'].split(' ')

        split_fio.append(
            {
                'Фамилия': fio[0],
                'Имя': fio[1],
                'Отчество': fio[2],
            }
        )

    to_data_base = []
    for d in range(len(data)):
        split_fio[d].update(data[d][0])
        to_data_base.append(split_fio[d])

    global general_data
    general_data = to_data_base

    setToDataBase()


def setToDataBase():
    global general_data
    collection.delete_many({})
    for d in general_data:
        collection.insert_one(d)


def bot():
    bot = telebot.TeleBot(TOKEN)

    @bot.message_handler(commands=['list'])
    def message(message):
        print(collection.find())
        for obj in collection.find():
            bot.send_message(message.chat.id, obj['Должность'])


    @bot.message_handler(commands=['worker'])
    def message(message):
        text_list = message.text.split(' ')
        text_list.pop(0)
        text = ' '.join(text_list)
        found = 0
        for obj in collection.find():
            if obj['Должность'].lower() == text.lower():
                bot.send_message(message.chat.id, obj['Фамилия'])
                bot.send_message(message.chat.id, obj['Имя'])
                bot.send_message(message.chat.id, obj['Отчество'])
                bot.send_message(message.chat.id, obj['Должность'])
                bot.send_message(message.chat.id, obj['Адрес'])
                bot.send_message(message.chat.id, obj['Телефон'])
                bot.send_message(message.chat.id, obj['Почта'])
                found = 1
        if found == 0:
            bot.send_message(message.chat.id, 'Нет такого')

    bot.polling()

def parser():
    schedule.every().day.at("23:07").do(get_data_json)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    start_parser = Process(target=parser)
    start_bot = Process(target=bot)

    start_parser.start()
    start_bot.start()

    start_parser.join()
    start_bot.join()





