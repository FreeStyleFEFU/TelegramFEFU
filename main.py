import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import telebot

TOKEN = '1465745696:AAFiPZRJFZjhOwXv8y18yFjN6A9WPh4IA2Y'
cluster = MongoClient('mongodb+srv://FreeStyle:hQXlKHByR4QWZNau@cluster0.7ed7r.mongodb.net/ProrectorsFEFU?retryWrites=true&w=majority')
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

    return to_data_base

def setToDataBase(data):
    collection.delete_many({})
    for d in data:
        collection.insert_one(d)


def bot():
    bot = telebot.TeleBot(TOKEN)

    @bot.message_handler(commands=['worker'])
    def message(message):
        text_list = message.text.split(' ')
        text_list.pop(0)
        text = ' '.join(text_list)
        print(text)
        find = collection.find_one({ 'Должность': text })
        print(find)
        if find == None:
            bot.send_message(message.chat.id, 'Нет такого')
        else:
            bot.send_message(message.chat.id, find['Фамилия'])
            bot.send_message(message.chat.id, find['Имя'])
            bot.send_message(message.chat.id, find['Отчество'])
            bot.send_message(message.chat.id, find['Должность'])
            bot.send_message(message.chat.id, find['Адрес'])
            bot.send_message(message.chat.id, find['Телефон'])
            bot.send_message(message.chat.id, find['Почта'])

    bot.polling()

if __name__ == "__main__":
    # setToDataBase(get_data_json())
    bot()

