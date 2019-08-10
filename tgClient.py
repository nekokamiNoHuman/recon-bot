from pathlib import Path
import telebot
import logging
import requests

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

token = Path('active_token.txt').read_text().replace('\n', '')
bot = telebot.TeleBot(token)

class Data:
    def __init__(self):
        self.photoDS = {}
        self.nameList = []
        self.inputing = False

    def addPhoto(self, photo, name):
        if str(name) in self.photoDS:
            print(name in self.photoDS)
            self.photoDS[name].append(photo)
        else:
            self.photoDS[name].append(photo)

    def addTarget(self, name):
        if not (name in self.nameList):
            self.nameList.append(name)
            self.photoDS[name] = []

    def prepareForInput(self):
        if not self.inputing:
            self.inputing = True

    def inputFinished(self):
        if self.inputing:
            self.inputing = False

    def getName(self):
        if len(self.nameList) == 0:
            return "No current Target"
        else:
            return self.nameList[-1]


DataSet = Data()


@bot.message_handler(commands=['start'])
def sendWelcome(messages):
    if isinstance(messages, telebot.types.Message):
        bot.reply_to(messages, "Howdy, how are you doing?")
    elif isinstance(messages, list):
        for message in messages:
            print(message)


@bot.message_handler(regexp="/photo [a-zA-Z]+")
def readyGetPhoto(messages):
    if isinstance(messages, telebot.types.Message):
        DataSet.prepareForInput()
        bot.reply_to(messages, "add photo please")
        DataSet.addTarget(messages.text[6:])


@bot.message_handler(commands=['getCurrentTarget'])
def getName(messages):
    if isinstance(messages, telebot.types.Message):

        bot.reply_to(messages, DataSet.getName())


@bot.message_handler(regexp="/getPhotoOf [a-zA-Z]+")
def getPhotoListOfSomeone(messages):
    if isinstance(messages, telebot.types.Message):
        name = messages.text[11:]
        if name in DataSet.nameList:
            for photo in DataSet.photoDS[name]:
                bot.send_photo(messages.chat.id, photo)
        else:
            bot.reply_to(messages, 'no such a target')


@bot.message_handler(commands=['help'])
def getHelpInfo(messages):
    if isinstance(messages, telebot.types.Message):
        bot.reply_to(messages, "/photo target name\n /getCurrentTarget \n /getPhotoOf name")


bot.polling(none_stop=False, interval=0, timeout=20)
