from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram.utils.helpers import mention_markdown
import threading
#import enchant
import time
import os
import requests
#from telegram.ext.dispatcher import run_async

TOKEN = os.environ.get("TOKEN")
PORT = int(os.environ.get('PORT', 5000))
updater = Updater(TOKEN)
group_lst = []
#word = enchant.Dict("en_US")
class WordGame:
    def __init__(self,GROUP):
        self.GROUP = GROUP
        self.username_lst = []
        self.chatid_lst = []
        self.name_lst = []
        self.whose_chance = 0
        self.used_word_lst = []
        self.user_num = 0
        self.round = 1
        self.user_lst = []
        self.game_started = False
        self.start_time = 0
        self.end_time = 0
        self.user_point_dic = {}

    def end(self,bot,update):
        final_score = ""
        bot.sendMessage(self.GROUP,"Game ENDED!!!")
        for i in range(len(self.chatid_lst)):
            user = self.name_lst[i]
            score = self.user_point_dic[self.chatid_lst[i]]
            final_score = f"{final_score}\n{mention_markdown(self.chatid_lst[i],user)} : {score}"
        bot.sendMessage(self.GROUP,final_score,parse_mode="Markdown")
        self.GROUP = GROUP
        self.username_lst = []
        self.chatid_lst = []
        self.name_lst = []
        self.whose_chance = 0
        self.used_word_lst = []
        self.user_num = 0
        self.round = 1
        self.user_lst = []
        self.game_started = False
        self.start_time = 0
        self.end_time = 0
        self.user_point_dic = {}
        

    def join(self,bot,update):
        username = update.message.from_user.username
        name = update.message.from_user.first_name
        chat_id = update.message.from_user.id
        if chat_id not in self.chatid_lst:
            self.user_lst.append(f"{name}:{username}:{chat_id}")
            self.username_lst.append(username)
            self.chatid_lst.append(chat_id)
            self.name_lst.append(name)
            self.user_point_dic[chat_id] = 0
            bot.sendMessage(self.GROUP,text=f"{mention_markdown(chat_id,name)} joined the game, there are currently {len(self.user_lst)} players.",parse_mode="Markdown")

        else:
            update.message.reply_text("You have already joined the game")
       

    def start_game(self,bot,update):
        total_players = len(self.user_lst)

        if not self.game_started:
        
            if total_players > 1:
                bot.sendMessage(self.GROUP,f"Starting a game with {total_players} players")
                self.game_started = True
                self.incriment(bot=bot,update=update)

            else:
                 update.message.reply_text("Game must have atleast 2 players.")

        else:
            update.message.reply_text("Game has already started")

    def word(self,bot,update):
        chat_id = update.message.from_user.id
        name = update.message.from_user.first_name
        if self.whose_chance == chat_id:
            self.end_time = time.time()
            total_time = self.end_time - self.start_time
            message = update.message.text
            message = message.replace("/w ","")
            message = message.lower()
            total_time = round(total_time)
            points = 20 - total_time
            print(points)
            if message == "_pass":
                bot.sendMessage(self.GROUP,text=f"{mention_markdown(chat_id,name)} loses 5 points.",parse_mode="Markdown")
                score = self.user_point_dic[chat_id]
                self.user_point_dic[chat_id] = score - 5
                self.end_time = 0
                self.start_time = 0

            elif points < 0:
                bot.sendMessage(self.GROUP,text=f"{mention_markdown(chat_id,name)} loses 5 points as 20 seconds have passed.",parse_mode="Markdown")
                score = self.user_point_dic[chat_id]
                self.user_point_dic[chat_id] = score - 5
                self.end_time = 0
                self.start_time = 0
                
            else:
                total_words = len(self.used_word_lst)
                prev_word = self.used_word_lst[total_words-1]
                prev_let = prev_word[len(prev_word)-1]
                print(message[0])
                word_check = requests.get("http://rajma.pythonanywhere.com/check?word="+message).text
                
                if word_check == "True" and message[0] == prev_let and message.lower() not in self.used_word_lst:
                    bot.sendMessage(self.GROUP,text=f"{mention_markdown(chat_id,name)} chose '{message.upper()}' which is a valid English word\nThey earned {points} points.",parse_mode="Markdown")
                    score = self.user_point_dic[chat_id]
                    self.user_point_dic[chat_id] = points + score
                    print(self.user_point_dic)
                    self.end_time = 0
                    self.start_time = 0
                    self.used_word_lst.append(message.lower())

                elif message.lower() in self.used_word_lst:
                    bot.sendMessage(self.GROUP,text=f"{mention_markdown(chat_id,name)} chose '{message.upper()}' which has been used before\nThey loses 5 points.",parse_mode="Markdown")
                    score = self.user_point_dic[chat_id]
                    self.user_point_dic[chat_id] = score - 5
                    self.end_time = 0
                    self.start_time = 0

                elif message[len(message)-1] != prev_let :
                    bot.sendMessage(self.GROUP,text=f"{mention_markdown(chat_id,name)} chose '{message.upper()}' which does *not* start with '{prev_let.upper()}'\nThey loses {points} points.",parse_mode="Markdown")
                    score = self.user_point_dic[chat_id]
                    self.user_point_dic[chat_id] = score - points
                    self.end_time = 0
                    self.start_time = 0

                else:
                    bot.sendMessage(self.GROUP,text=f"{mention_markdown(chat_id,name)} chose '{message.upper()}' which is *not* a valid English word\nThey loses {points} points.",parse_mode="Markdown")
                    score = self.user_point_dic[chat_id]
                    self.user_point_dic[chat_id] = score - points
                    self.end_time = 0
                    self.start_time = 0

            self.whose_chance = 0
            final_score = ""
            for i in range(len(self.chatid_lst)):
                user = self.name_lst[i]
                score = self.user_point_dic[self.chatid_lst[i]]
                final_score = f"{final_score}\n{mention_markdown(self.chatid_lst[i],user)} : {score}"
            bot.sendMessage(self.GROUP,final_score,parse_mode="Markdown")
            self.incriment(bot,update)
            
                


    def incriment(self,bot,update):
        name = self.name_lst[self.user_num]
        chat_id = self.chatid_lst[self.user_num]
        #bot.sendMessage(self.GROUP,f"""*Round {self.round}*\n{mention_markdown(chat_id,name+"'s")} chance.""",parse_mode="Markdown")
        total_words = len(self.used_word_lst)
        self.whose_chance = chat_id
        if total_words < 1:
            bot.sendMessage(self.GROUP,f"""*Round {self.round}*\n{mention_markdown(chat_id,name+"'s")} chance.

Starting word is 'PYTHON', {mention_markdown(chat_id,name)} you have to say a word starting with 'N'

*Message like this* - /w THE WORD HERE.

You will have 20 seconds to reply, the points you earn will be determined by how fast you replied.

If you replied within first 'n' seconds you earn 20 - n points, *if you fail to reply, type '/w pass', you will lose 5 points*.""",parse_mode="Markdown")
            self.used_word_lst.append("python")

        else:
            prev_word = self.used_word_lst[total_words-1]
            time.sleep(3)
            bot.sendMessage(self.GROUP,f"""*Round {self.round}*\n{mention_markdown(chat_id,name+"'s")} chance.\nPrevious word was *'{prev_word.upper()}'*
You have to say a word starting with {(prev_word[len(prev_word)-1]).upper()}
*Message like this* - /w THE WORD HERE.""",parse_mode="Markdown")

        self.start_time = time.time()
        self.user_num = self.user_num+1
        self.round = self.round+1
        if len(self.chatid_lst)-1 < self.user_num:
            self.user_num = 0

             

#@run_async
def new_word_game(bot,update):
    group_id = update.message.chat_id
    if group_id not in group_lst:
        new_game = WordGame(group_id)
        group_lst.append(group_id)
        updater.dispatcher.add_handler(CommandHandler("join_word_game",new_game.join))
        updater.dispatcher.add_handler(CommandHandler("start_word_game",new_game.start_game))
        updater.dispatcher.add_handler(CommandHandler("w",new_game.word))
        updater.dispatcher.add_handler(CommandHandler("end_game",new_game.end))
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


