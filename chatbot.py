from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

import os
import configparser #需要修改
import logging
import redis  #需要修改
import http.client

global redis1

def main():
    # Load your token and create an Updater for your Bot
    
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher

    global redis1
    redis1 = redis.Redis(host=(config['REDIS']['HOST']), password=(config['REDIS']['PASSWORD']), port=(config['REDIS']['REDISPORT']))

    # You can set this logging module, so you will know when and why things do not work as expected
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    
    # register a dispatcher to handle message: here we register an echo dispatcher
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    # on different commands - answer in Telegram
    
    dispatcher.add_handler(CommandHandler("help", help_command))
    # dispatcher.add_handler(CommandHandler("meat", meat_command))
    # dispatcher.add_handler(CommandHandler("vegetables", vegetables_command))
    # dispatcher.add_handler(CommandHandler("fruites", fruites_command))
    # dispatcher.add_handler(CommandHandler("carbohybrates", carbohybrates_command))
    # dispatcher.add_handler(CommandHandler("show", show_command))
    # dispatcher.add_handler(CommandHandler("end", end_command))

    # To start the bot:
    updater.start_polling()
    updater.idle()


def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    conn = http.client.HTTPSConnection("spoonacular-recipe-food-nutrition-v1.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': "5080feaeaamshfc732c2331bf80bp17201ajsn44131be48caa",
        'x-rapidapi-host': "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
        }
    problem = "/recipes/quickAnswer?q=" + update.message.text.replace(" ","%20") +"%3F"
    

    conn.request("GET", problem, headers=headers)

    res = conn.getresponse()
    data = res.read()

    #print(data.decode("utf-8"))
    print(update.message.text)
    print(update.message.text.replace(" ","%20"))

    print(problem)
    reply_message=data.decode("utf-8")
    context.bot.send_message(chat_id=update.effective_chat.id, text= reply_message)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('This chatbot will help you to calculate how many calories you eat each meal./meat XXX(grams), /vegetebles XXX(grams), /fruites XXX(grams), /carbohydrates XXX(grams), /show will show how many calories you eat, /reset will reset your records')

def kevin_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /hello Kevin is issued."""
    update.message.reply_text('Good day, Kevin!')


def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try: 
        global redis1
        logging.info(context.args[0])
        msg = context.args[0]   # /add keyword <-- this should store the keyword
        redis1.incr(msg)
        update.message.reply_text('You have said ' + msg +  ' for ' + redis1.get(msg).decode('UTF-8') + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')



if __name__ == '__main__':
    main()