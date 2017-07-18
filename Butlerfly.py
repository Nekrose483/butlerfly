import json
import requests
import time
import urllib
import random
import threading

from os import listdir
from os.path import isfile, join

global aveCount
aveCount = 0

from dbhelper import DBHelper

db = DBHelper()

TOKEN = "395680838:AAH2OLuxvN69YakY8RzHsU3qx6uBj8Wibac"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def removeAt(text):
    atLess = text.split('@ButlerflyBot')[0]+text.split('@ButlerflyBot')[1]
    print(atLess)
    return atLess


def handle_updates(updates):
    for update in updates["result"]:
        if "message" in update:
            handle_update(update)


def handle_update(update):
    global aveCount
    aveCount = aveCount - 1
    print(update)
    if 'text' in update["message"]:
        if ('@ButlerflyBot' in update["message"]['text']):
            text = removeAt(update["message"]['text'])
        else:
            text = update["message"]['text']
    else:
        text = "invalid"
    chat = update["message"]["chat"]["id"]
    if text.split()[0] == "/roll" or text.split()[0] == "/r":
        if len(text.split()) > 1:
            dice = text.split()[1].split('d')
            if '+' in dice[1]:
                sides = int(dice[1].split('+')[0])
                bonus = int(dice[1].split('+')[1])
            else:
                sides = int(dice[1])
                bonus = 0
            send_message(diceroll(int(dice[0]), sides, bonus), chat)
        else:
            send_message("Missing Arguments", chat)
    if text.split()[0] == "/ScriptRead":
        scriptRead(chat,open('Scripts/'+text.split()[1],'r'))
    elif text.split()[0] == "/addDrone":
        if len(text.split()) > 2:
            db.add_item(text.split()[1],text.split()[2])
        else:
            send_message("Missing Arguments", chat)
    elif text.split()[0] == "/removeDrone":
        if len(text.split()) > 1:
            db.delete_item(text.split()[1])
        else:
            send_message("Missing Arguments", chat)
    elif text.split()[0] == "/getDrone":
        if len(text.split()) > 1:
            db.get_id(text.split()[1])
        else:
            send_message("Missing Arguments", chat)
    elif text == "/script":
        script(update)
    elif text == "/avecommuni":
        send_message("Ave Communi!", chat)
    elif text == "/start":
        send_message("Hello! I'm the Butlerfly! I have a few commands that you should know! \n/roll or /r will "
                     "allow you to roll dice in the standard format (number)d(sides) format"
                     "\n/script (only available in private chat) will read you hypnosis scripts\n "
                     "/avecommuni will motivate the hive!", chat)
    elif "ave communi" in text.lower() and aveCount <= 0:
        send_message("Ave Communi!", chat)
        aveCount = 10



def script(update):
    if update['message']['chat']['type'] == 'private':
        scriptSelector(update['message']['chat']['id'])
    else:
        send_message('Invalid channel, this command is only available in private chat', update['message']['from']['id'])


def scriptRead(chat,script):
    line = script.readline()
    while line != '':
        send_message(line, chat)
        time.sleep(1)
        line = script.readline()
    script.close()

def scriptSelector(chat):
    mypath = 'Scripts'
    scripts = ["/ScriptRead "+ f for f in listdir(mypath) if isfile(join(mypath, f))]
    send_message("Pick a Script", chat, build_keyboard(scripts))

    return

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard": keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)


def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)


def diceroll(number, size, bonus=0):
    text = "Rolling Dice:\n" + str(number) + "d" + str(size) + "= "
    totalvalue = 0
    for x in range(0, number):
        value = random.randint(1, size)
        totalvalue += value
        text = text + str(value) + ' + '
    text = text + str(bonus) + '=' + str(totalvalue + bonus)
    return text


def main():
    db.setup()
    last_update_id = None
    global aveCount
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            updates = threading.Thread(target=handle_updates(updates))
            updates.daemon = True
            updates.start()
        time.sleep(0.5)


if __name__ == '__main__':
    mainTask =threading.Thread(target=main())
    maintask.start()
