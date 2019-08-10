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
        markup = telebot.types.ReplyKeyboardMarkup()
        markup.add(telebot.types.KeyboardButton("/getCurrentTarget"))
        markup.add(telebot.types.KeyboardButton("/getPhotoOf"))
        markup.add(telebot.types.KeyboardButton("/getCurrentTarget"))
        bot.send_message(messages.chat.id, text="Howdy, how are you doing?", reply_markup=markup)


@bot.message_handler(regexp="/photo [a-zA-Z]+")
def readyGetPhoto(messages):
    if isinstance(messages, telebot.types.Message):
        DataSet.prepareForInput()
        bot.reply_to(messages, "add photo please")
        DataSet.addTarget(messages.text[6:])


@bot.message_handler(commands=["getPhotoOf"])
def getNameList(messages):
    if isinstance(messages, telebot.types.Message):
        bot.reply_to(messages, "Please input Name")
        msg = bot.reply_to(messages, "a")
        telebot.apihelper.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
            text="msg edited",
            token=token)

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


@bot.message_handler(content_types=['photo'])
def getPhoto(messages):
    if isinstance(messages, telebot.types.Message):
        if DataSet.inputing:
            fileInfo = bot.get_file(messages.photo[0].file_id)
            file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(token, fileInfo.file_path))
            DataSet.addPhoto(file.content, DataSet.getName())
            # print(file.content)
            bot.reply_to(messages, 'photo added')
        else:
            bot.reply_to(messages, 'photo not added')

@bot.message_handler(content_types=['location'])
def getLocation(messages):
    if isinstance(messages, telebot.types.Message):
        bot.send_location(messages.chat.id,
        latitude=messages.location.latitude,
        longitude=messages.location.longitude)

@bot.message_handler(commands=['help'])
def getHelpInfo(messages):
    if isinstance(messages, telebot.types.Message):
        bot.reply_to(messages, "/photo target name\n /getCurrentTarget \n /getPhotoOf name")

bot.polling(none_stop=False, interval=0, timeout=20)
