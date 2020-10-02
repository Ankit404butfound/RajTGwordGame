from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram.utils.helpers import mention_markdown
import threading
#import enchant
import time
import requests
import os
#from telegram.ext.dispatcher import run_async
TOKEN = os.environ.get("TOKEN")
PORT = int(os.environ.get('PORT', 5000))

updater = Updater(TOKEN)


group_lst = []
GROUP = ""
username_lst = []
chatid_lst = []
name_lst = []
whose_chance = 0
used_word_lst = []
user_num = 0
round_com = 1
user_lst = []
game_started = False
start_time = 0
end_time = 0
user_point_dic = {}

def end(bot,update):
    global group_lst,GROUP,username_lst,chatid_lst,name_lst,whose_chance,used_word_lst,user_num,round_com,user_lst,game_started,start_time,end_time,user_point_dic

    final_score = "Final score is as followed"
    bot.sendMessage(GROUP,"Game ENDED!!!")
    for i in range(len(chatid_lst)):
        user = name_lst[i]
        score = user_point_dic[chatid_lst[i]]
        final_score = f"{final_score}\n{mention_markdown(chatid_lst[i],user)} : {score}"
    bot.sendMessage(GROUP,final_score,parse_mode="Markdown")
    GROUP = ""
    username_lst = []
    chatid_lst = []
    name_lst = []
    whose_chance = 0
    used_word_lst = []
    user_num = 0
    round_com = 1
    user_lst = []
    game_started = False
    start_time = 0
    end_time = 0
    user_point_dic = {}
    group_lst = []


def join(bot,update):
    username = update.message.from_user.username
    name = update.message.from_user.first_name
    chat_id = update.message.from_user.id
    if chat_id not in chatid_lst:
        user_lst.append(f"{name}:{username}:{chat_id}")
        username_lst.append(username)
        chatid_lst.append(chat_id)
        name_lst.append(name)
        user_point_dic[chat_id] = 0
        bot.sendMessage(GROUP,text=f"{mention_markdown(chat_id,name)} joined the game, there are currently {len(user_lst)} players.",parse_mode="Markdown")

    else:
        update.message.reply_text("You have already joined the game")


def start_game(bot,update):
    global game_started
    total_players = len(user_lst)

    if not game_started:
    
        if total_players > 1:
            bot.sendMessage(GROUP,f"Starting a game with {total_players} players")
            game_started = True
            incriment(bot=bot,update=update)

        else:
             update.message.reply_text("Game must have atleast 2 players.")

    else:
        update.message.reply_text("Game has already started")


def word(bot,update):
    global group_lst,GROUP,username_lst,chatid_lst,name_lst,whose_chance,used_word_lst,user_num,round_com,user_lst,game_started,start_time,end_time,user_point_dic
    chat_id = update.message.from_user.id
    name = update.message.from_user.first_name
    if whose_chance == chat_id:
        end_time = time.time()
        total_time = end_time - start_time
        message = update.message.text
        message = message.replace("/w ","")
        message = message.lower()
        total_time = round(total_time)
        points = 20 - total_time
        print(points)
        if message == "_pass":
            bot.sendMessage(GROUP,text=f"{mention_markdown(chat_id,name)} loses 5 points.",parse_mode="Markdown")
            score = user_point_dic[chat_id]
            user_point_dic[chat_id] = score - 5
            end_time = 0
            start_time = 0

        elif points < 0:
            bot.sendMessage(GROUP,text=f"{mention_markdown(chat_id,name)} loses 5 points as 20 seconds have passed.",parse_mode="Markdown")
            score = user_point_dic[chat_id]
            user_point_dic[chat_id] = score - 5
            end_time = 0
            start_time = 0
            
        else:
            total_words = len(used_word_lst)
            prev_word = used_word_lst[total_words-1]
            prev_let = prev_word[len(prev_word)-1]
            print(message[0])
            word_check = requests.get("http://rajma.pythonanywhere.com/check?word="+message).text
            print(f"{word_check} {message[0]} {prev_let} {used_word_lst}")
            if word_check == "True" and message[0] == prev_let and message.lower() not in used_word_lst:
                bot.sendMessage(GROUP,text=f"{mention_markdown(chat_id,name)} chose '{message.upper()}' which is a valid English word\nThey earned {points} points.",parse_mode="Markdown")
                score = user_point_dic[chat_id]
                user_point_dic[chat_id] = points + score
                print(user_point_dic)
                end_time = 0
                start_time = 0
                used_word_lst.append(message.lower())

            elif message.lower() in used_word_lst:
                bot.sendMessage(GROUP,text=f"{mention_markdown(chat_id,name)} chose '{message.upper()}' which has been used before\nThey loses 5 points.",parse_mode="Markdown")
                score = user_point_dic[chat_id]
                user_point_dic[chat_id] = score - 5
                end_time = 0
                start_time = 0

            elif message[0] != prev_let :
                bot.sendMessage(GROUP,text=f"{mention_markdown(chat_id,name)} chose '{message.upper()}' which does *not* start with '{prev_let.upper()}'\nThey loses {points} points.",parse_mode="Markdown")
                score = user_point_dic[chat_id]
                user_point_dic[chat_id] = score - points
                end_time = 0
                start_time = 0

            else:
                bot.sendMessage(GROUP,text=f"{mention_markdown(chat_id,name)} chose '{message.upper()}' which is *not* a valid English word\nThey loses {points} points.",parse_mode="Markdown")
                score = user_point_dic[chat_id]
                user_point_dic[chat_id] = score - points
                end_time = 0
                start_time = 0

        whose_chance = 0
        final_score = ""
        for i in range(len(chatid_lst)):
            user = name_lst[i]
            score = user_point_dic[chatid_lst[i]]
            final_score = f"{final_score}\n{mention_markdown(chatid_lst[i],user)} : {score}"
        bot.sendMessage(GROUP,final_score,parse_mode="Markdown")
        incriment(bot,update)

def incriment(bot,update):
    global whose_chance, start_time, user_num, round_com
    name = name_lst[user_num]
    chat_id = chatid_lst[user_num]
    #bot.sendMessage(GROUP,f"""*Round {round}*\n{mention_markdown(chat_id,name+"'s")} chance.""",parse_mode="Markdown")
    total_words = len(used_word_lst)
    whose_chance = chat_id
    if total_words < 1:
        bot.sendMessage(GROUP,f"""*Round {round_com}*\n{mention_markdown(chat_id,name+"'s")} chance.

Starting word is 'PYTHON', {mention_markdown(chat_id,name)} you have to say a word starting with 'N'

*Message like this* - /w THE WORD HERE.

You will have 20 seconds to reply, the points you earn will be determined by how fast you replied.

If you replied within first 'n' seconds you earn 20 - n points, *if you fail to reply, type '/w pass', you will lose 5 points*.""",parse_mode="Markdown")
        used_word_lst.append("python")

    else:
        prev_word = used_word_lst[total_words-1]
        time.sleep(3)
        bot.sendMessage(GROUP,f"""*Round {round_com}*\n{mention_markdown(chat_id,name+"'s")} chance.\nPrevious word was *'{prev_word.upper()}'*
You have to say a word starting with {(prev_word[len(prev_word)-1]).upper()}
*Message like this* - /w THE WORD HERE.""",parse_mode="Markdown")

    start_time = time.time()
    user_num = user_num+1
    round_com = round_com+1
    if len(chatid_lst)-1 < user_num:
        user_num = 0

def new_word_game(bot,update):
    global GROUP
    group_id = update.message.chat_id
    if group_id not in group_lst:
        GROUP = group_id
        group_lst.append(group_id)
        updater.dispatcher.add_handler(CommandHandler("join_word_game",join))
        updater.dispatcher.add_handler(CommandHandler("start_word_game",start_game))
        updater.dispatcher.add_handler(CommandHandler("w",word))
        updater.dispatcher.add_handler(CommandHandler("end_game",end))
        update.message.reply_text("Starting new game\nType /join_word_game to join.")
    else:
        update.message.reply_text("A game is already running")

updater.dispatcher.add_handler(CommandHandler('new_word_game', new_word_game))

#updater.start_polling()
updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)

updater.bot.setWebhook('https://rajwordgamebot.herokuapp.com/' + TOKEN)

updater.idle()


