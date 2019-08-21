from pathlib import Path
import telebot
import logging
import requests
import numpy as np

# logger = telebot.logger
# telebot.logger.setLevel(logging.DEBUG)

token = Path('active_token.txt').read_text().replace('\n', '')
bot = telebot.AsyncTeleBot(token)

def np_getDistance(A , B ):# 先緯度後經度
    ra = 6378140  # radius of equator: meter
    rb = 6356755  # radius of polar: meter
    flatten = 0.003353 # Partial rate of the earth
    # change angle to radians
    print(A)
    print(B)
    radLatA = np.radians(A[:,0])
    radLonA = np.radians(A[:,1])
    radLatB = np.radians(B[:,0])
    radLonB = np.radians(B[:,1])

    pA = np.arctan(rb / ra * np.tan(radLatA))
    pB = np.arctan(rb / ra * np.tan(radLatB))

    x = np.arccos( np.multiply(np.sin(pA),np.sin(pB)) + np.multiply(np.multiply(np.cos(pA),np.cos(pB)),np.cos(radLonA - radLonB)))
    c1 = np.multiply((np.sin(x) - x) , np.power((np.sin(pA) + np.sin(pB)),2)) / np.power(np.cos(x / 2),2)
    c2 = np.multiply((np.sin(x) + x) , np.power((np.sin(pA) - np.sin(pB)),2)) / np.power(np.sin(x / 2),2)
    dr = flatten / 8 * (c1 - c2)
    distance = 0.001 * ra * (x + dr)
    return distance

class Data:
    def __init__(self):
        self.photoDS = {}
        self.nameList = []
        self.inputing = False
        self.PoPoPositionDS = {}
        self.positionList = []
        self.clientList = {}

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
            self.clientList[chatId] = (False,True)

    def inputFinished(self, chatId):
        if self.inputing:
            self.clientList[chatId] = (False,False)

    def getName(self):
        if len(self.nameList) == 0:
            return "No current Target"
        else:
            return self.nameList[-1]

    def reportPopo(self, chatId):
        x = {str(chatId) : {'status': (True,False), 'position': ""}}
        self.clientList[str(chatId)] = {'status': (True,False), 'position': ""}
        print("clientList: ",self.clientList)

    def addPoPoposition(self, chatId, position):
        if str(chatId) in self.clientList:
            if self.clientList[str(chatId)]['status']:
                print("clientList: ",self.clientList)
                self.positionList.append(position)
                self.clientList[str(chatId)]['position'] = str(position[0])+" , "+str(position[1])
        else:
            print("not in clientList")
            self.reportPopo(chatId)

    def addPoPoNumber(self, chatId, number):
        print("clientList at eact: ", self.clientList)
        self.PoPoPositionDS[self.clientList[str(chatId)]['position']] = number

DataSet = Data()


@bot.message_handler(commands=['start'])
def sendWelcome(messages):
    if isinstance(messages, telebot.types.Message):
        markup = telebot.types.ReplyKeyboardMarkup()
        markup.add(telebot.types.KeyboardButton("/getCurrentTarget"))
        markup.add(telebot.types.KeyboardButton("/getPhotoOf"))
        markup.add(telebot.types.KeyboardButton("/getCurrentTarget"))
        markup.add(telebot.types.KeyboardButton("/reportPoPoPosition"))
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
        telebot.apihelper.edit_message_text(chat_id=messages.chat.id, message_id=messages.message_id,
            text="msg edited",
            token=token)

@bot.message_handler(commands=['getCurrentTarget'])
def getName(messages):
    if isinstance(messages, telebot.types.Message):
        bot.reply_to(messages, DataSet.getName())

@bot.message_handler(commands=['reportPoPoPosition'])
def reportPopoPosition(messages):
    if isinstance(messages, telebot.types.Message):
        DataSet.reportPopo(messages.chat.id)
        bot.send_message(messages.chat.id, "Position?")

@bot.message_handler(commands=['getPoPoPosition'])
def getPoPoPosition(messages):
    if isinstance(messages, telebot.types.Message):
        for key in DataSet.PoPoPositionDS:
            bot.send_message(messages.chat.id, "At Position "+key+" , there is "+DataSet.PoPoPositionDS[key]+" Popos")
        print(DataSet.PoPoPositionDS)


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
def addLocation(messages):
    if isinstance(messages, telebot.types.Message):
        Find_loc = np.matrix([[float(messages.location.latitude),float(messages.location.longitude)]])
        if len(DataSet.positionList) == 0:
            locationList = np.matrix([[0.,0.]])
        else:
            locationList = np.matrix(DataSet.positionList)
        distanceList = np_getDistance(locationList, Find_loc)
        print('distanceList: ', distanceList)
        print('DataSet.positionList: ',DataSet.positionList)
        if np.min(distanceList) <=0.3:
            DataSet.addPoPoposition(messages.chat.id,DataSet.positionList[distanceList.argmin(axis=0)[0,0]])
        else:
            DataSet.addPoPoposition(messages.chat.id,(messages.location.latitude,messages.location.longitude))
        print('DataSet.clientList: ',DataSet.clientList)
        @bot.message_handler(regexp="[0-9]+")
        def getPoPoNumber(messages):
            if isinstance(messages, telebot.types.Message):
                DataSet.addPoPoNumber(messages.chat.id, messages.text)
                bot.send_message(messages.chat.id, "PoPo number updated")
        bot.send_message(messages.chat.id, distanceList.argmin(axis=0)[0,0])
        bot.send_message(messages.chat.id, 'added')

@bot.message_handler(commands=['done'])
def getHelpInfo(messages):
    if isinstance(messages, telebot.types.Message):
        DataSet.inputFinished(messages.chat.id)
        bot.send_message(messages.chat.id,"done")

@bot.message_handler(commands=['help'])
def getHelpInfo(messages):
    if isinstance(messages, telebot.types.Message):
        bot.reply_to(messages, "/photo target name\n /getCurrentTarget \n /getPhotoOf name")

bot.polling(none_stop=False, interval=0, timeout=20)
