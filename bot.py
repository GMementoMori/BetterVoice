import config
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ContentType, File, Message
import os
import speech_recognition as sr
from gtts import gTTS
import pyowm
from datetime import datetime
import re
# from parser import Parser

pathVoice = "voice/voice"
pathAudio = "voice/audio"
logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)
owm = pyowm.OWM(config.API_TOKEN_OWM)
AUDIO_PATH = os.path.expanduser(pathAudio + ".mp3")
now = datetime.now()
current_time = now.strftime("%H:%M")
# sg = Parser()

def recognize_message():
    os.system("ffmpeg -i " + pathVoice + ".ogg " + pathVoice + ".wav -y")
    r = sr.Recognizer()
    file = sr.AudioFile(pathVoice + ".wav")
    with file as source:
        audio = r.record(source)
    try:
        return r.recognize_google(audio, language="ru-RU")
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}" . format(e))


def save_answer(text: str):
    s = gTTS(text, lang="ru")
    s.save(pathAudio + ".mp3")


def weather_status(place: str):
    if place:
        mgr = owm.weather_manager()
        observation = mgr.weather_at_place(place)
        weather = observation.weather
        temp = weather.temperature("celsius")
        cells = ''
        cells_feels = ''
        if int(temp["temp"]) == 1 or int(temp["temp"]) == -1:
            cells = "градус"
        if (int(temp["temp"]) != 1 and int(temp["temp"]) != -1) and (-5 < int(temp["temp"]) < 5):
            cells = "градуса"
        if (int(temp["temp"]) != 1 and int(temp["temp"]) != -1) \
                and (int(temp["temp"]) <= -5 or int(temp["temp"]) >= 5
                     or int(temp["temp"]) == 0):
            cells = "градусов"
        if int(temp["feels_like"]) == 1 or int(temp["feels_like"]) == -1:
            cells_feels = "градус"
        if (int(temp["feels_like"]) != 1 and int(temp["feels_like"]) != -1) and (-5 < int(temp["feels_like"]) < 5):
            cells_feels = "градуса"
        if (int(temp["feels_like"]) != 1 and int(temp["feels_like"]) != -1) \
                and (int(temp["feels_like"]) <= -5 or int(temp["feels_like"]) >= 5
                     or int(temp["feels_like"]) == 0):
            cells_feels = "градусов"

        text = "Температура в городе - " + place + " : " + str(int(temp["temp"])) + " " + cells + "  по цельсию! " + \
               "Ощущаеться как: " + str(int(temp["feels_like"])) + " " + cells_feels + " по цельсию! "
        return text


@dp.message_handler(commands=['start', 'help'])
async def process_start_command(message: types.Message):
    await message.reply("Привет!\n Отправь мне аудиосообщение с названием города что бы узнать погоду.")


@dp.message_handler(content_types=[ContentType.VOICE])
async def voice_message_handler(message: Message):
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, pathVoice + ".ogg")
    phrase = recognize_message()
    phrase = phrase.lower()
    print(phrase)

    if 'погода' in phrase :
        x = re.findall("погода\s*([^>]*)", phrase)
        text = weather_status(x[0])
        if text:
            save_answer(text)
            audio = types.InputFile(AUDIO_PATH)
            await message.reply_voice(audio)
    

@dp.message_handler()
async def echo_message(msg: types.Message):
    print(str(msg.from_user.id) + " - " + str(msg.from_user.username) + " = " + msg.text)
    # await bot.send_message(msg.from_user.id, msg.text)

if __name__ == '__main__':
    executor.start_polling(dp)
    print("Current Time =", current_time)