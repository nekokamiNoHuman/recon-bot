from flask import Flask, request
from pathlib import Path
import telebot
import logging
from Data import Data
import googlemaps
#for taking heroku variable
from boto.s3.connection import S3Connection
herokuVariable = S3Connection(os.environ['telegram_bot'], os.environ['google_api_token'], os.environ['GOOGLE_APPLICATION_CREDENTIALS'], os.environ['GOOGLE_CREDENTIALS'])

token = herokuVariable["telegram_bot"]
DataSet = Data()
googleAPIToken = herokuVariable["google_api_token"]

bot = telebot.AsyncTeleBot(token)
gmaps = googlemaps.Client(key=googleAPIToken)

@bot.message_handler(commands=['start'])
def sendWelcome(messages):
    if isinstance(messages, telebot.types.Message):
        markup = telebot.types.ReplyKeyboardMarkup()
        markup.add(telebot.types.KeyboardButton("/getCurrentTarget"))
        markup.add(telebot.types.KeyboardButton("/getPhotoOf"))
        markup.add(telebot.types.KeyboardButton("/getCurrentTarget"))
        markup.add(telebot.types.KeyboardButton("/reportPoPoPosition"))
        markup.add(telebot.types.KeyboardButton("/getPoPoPosition"))
        markup.add(telebot.types.KeyboardButton("/done"))
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

@bot.message_handler(commands=['reportPoPoPosition'])
def reportPopoPosition(messages):
    if isinstance(messages, telebot.types.Message):
        DataSet.reportPopo(messages.chat.id)
        bot.send_message(messages.chat.id, "Position?")

@bot.message_handler(commands=['getPoPoPosition'])
def getPoPoPosition(messages):
    if isinstance(messages, telebot.types.Message):
        for key in DataSet.PoPoPositionDS:
            geocode_result = gmaps.geocode(key)[0]["geometry"]["location"]
            # print(geocode_result["lat"]," , ",geocode_result["lng"])
            bot.send_location(messages.chat.id, geocode_result["lat"],geocode_result["lng"])
            bot.send_message(messages.chat.id, "There is "+DataSet.PoPoPositionDS[key]+" Popos at "+key)
        # print(DataSet.PoPoPositionDS)

@bot.message_handler(content_types=['location'])
def addLocation(messages):
    if isinstance(messages, telebot.types.Message):
        if str(messages.chat.id) in DataSet.clientList:
            if DataSet.clientList[str(messages.chat.id)]["status"][0]:
                # Find_loc = np.matrix([[float(messages.location.latitude),float(messages.location.longitude)]])
                if len(DataSet.positionList) == 0:
                    reverse_geocode_result = gmaps.reverse_geocode((messages.location.latitude,messages.location.longitude))
                    # print(reverse_geocode_result[0]["formatted_address"])
                    status = DataSet.addPoPoposition(messages.chat.id,reverse_geocode_result[0]["formatted_address"])
                    # print('DataSet.clientList: ',DataSet.clientList)
                else:
                    locationList = np.matrix(DataSet.positionList)
                    # print('DataSet.positionList: ',DataSet.positionList)
                    reverse_geocode_result = gmaps.reverse_geocode((messages.location.latitude,messages.location.longitude))
                    # print(reverse_geocode_result[0]["formatted_address"])
                    status = DataSet.addPoPoposition(messages.chat.id,reverse_geocode_result[0]["formatted_address"])
                    # print('DataSet.clientList: ',DataSet.clientList)
                if not status:
                    bot.send_message(messages.chat.id, "You should update the PoPo number for last position first")
                    bot.send_message(messages.chat.id, "Or type /deleteLastPosition to delete it")
                else:
                    bot.send_message(messages.chat.id, 'Position added')
                @bot.message_handler(regexp="[0-9]+")
                def getPoPoNumber(messages):
                    if isinstance(messages, telebot.types.Message):
                        DataSet.addPoPoNumber(messages.chat.id, messages.text)
                        bot.send_message(messages.chat.id, "PoPo number updated")
            else:
                bot.send_message(messages.chat.id, ' Please call /reportPoPoPosition command first.')
        else:
            bot.send_message(messages.chat.id, ' Please call /reportPoPoPosition command first.')

@bot.message_handler(commands=['done'])
def done(messages):
    if isinstance(messages, telebot.types.Message):
        DataSet.inputFinished(messages.chat.id)
        bot.send_message(messages.chat.id,"done")

@bot.message_handler(commands=['help'])
def getHelpInfo(messages):
    if isinstance(messages, telebot.types.Message):
        bot.reply_to(messages, "/photo target name\n /getCurrentTarget \n /getPhotoOf name")


logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

app= Flask(__name__)

@app.route('/', method=["POST"])
def respond():
    if flask.request.headers.get("content-type") == "application/json":
        json_string = flask.request.get_data().decode("utf-8")
        logger.info(json_string)
        update = teleBot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK"
    else:
        flask.abort(403)

@app.route("/set_hook")
def set_hook():
    bot.set_webhook("https://deadcommunist-bot.herokuapp.com/"+token)
    return "OK"
# bot.polling(none_stop=False, interval=0, timeout=20)
