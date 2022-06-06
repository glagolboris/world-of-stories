import telebot
import speech
import buttons
from telebot import types
import api
import random

# https://telegra.ph/Soglashenie-05-17

class Bot:
    def __init__(self, tok):
        self.bot = telebot.TeleBot(token=tok)
        self.handler()
        self.user_story = {}
        self.group_id = api.group_token()
        self.public_id = api.public_token()
        self.data = {}


    def story_example(self, id):
        example = f"{self.user_story[id]['title']} {speech.smiles()}  ({self.user_story[id]['author']})\n" \
                  f" \n" \
                  f"{self.user_story[id]['story']}\n" \
                  f" \n" \
                  f"#{self.user_story[id]['genre'].split()[0]}  #{self.user_story[id]['author'].split()[-1]}  #{'_'.join(self.user_story[id]['title'].split()[0:2])}\n" \
                  f"{'@' + self.user_story[id]['user_nickname'] if self.user_story[id]['user_nickname'] is not None else '@анон'}"

        self.bot.send_message(id, example)
        markup = types.InlineKeyboardMarkup()
        button_yes = types.InlineKeyboardButton(buttons.yes(), callback_data=buttons.yes())
        markup.add(button_yes)
        button_no = types.InlineKeyboardButton(buttons.no(), callback_data=buttons.no())
        markup.add(button_no)
        self.user_story[id]['result'] = example
        self.user_story[id]['params']['result'] = True
        self.bot.send_message(id, speech.that_true(), reply_markup=markup)

    def handler(self):
        @self.bot.message_handler(commands=['start'])
        def start(message):
            try:
                if message.chat.id in self.user_story:
                    del self.user_story[message.chat.id]
                self.user_story[message.chat.id] = {'title': None, 'story': None, 'genre': None, 'author': None,
                                                    'user_nickname': None, 'result': None,
                                                    'params': {'title': False, 'story': False, 'genre': False,
                                                               'author': False, 'user_nickname': False,
                                                               'result': False}}
                markup = types.InlineKeyboardMarkup()
                button = types.InlineKeyboardButton(buttons.start_bttn(), callback_data=buttons.start_bttn())
                markup.add(button)
                self.bot.send_message(message.chat.id, speech.command_start(user_name=message.chat.first_name),
                                      reply_markup=markup)
            except Exception: pass

        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_query(call):
            try:
                print(call.message.chat.id, self.group_id)
                if call.message.chat.id != self.group_id and call.message.chat.id in self.user_story:
                    if call.data == buttons.start_bttn():
                        self.bot.delete_message(call.message.chat.id, message_id=call.message.id)
                        markup = types.InlineKeyboardMarkup()
                        button = types.InlineKeyboardButton(buttons.doc(), callback_data=buttons.doc())
                        markup.add(button)
                        self.bot.send_message(call.message.chat.id, speech.doc_without_link() + speech.doc(),
                                              reply_markup=markup, parse_mode='MarkdownV2')

                    elif call.data == buttons.doc():
                        self.bot.delete_message(call.message.chat.id, message_id=call.message.id)
                        markup = types.InlineKeyboardMarkup()
                        button = types.InlineKeyboardButton(buttons.start_anket(), callback_data=buttons.start_anket())
                        markup.add(button)
                        self.bot.send_message(call.message.chat.id, speech.start_anket(), reply_markup=markup)

                    elif call.data == buttons.start_anket():
                        self.bot.delete_message(call.message.chat.id, message_id=call.message.id)
                        markup = types.InlineKeyboardMarkup()
                        for genre in buttons.all_genres():
                            markup.add(types.InlineKeyboardButton(genre, callback_data=genre[0:-2]))
                        self.bot.send_message(call.message.chat.id, speech.genre(), reply_markup=markup)
                        self.user_story[call.message.chat.id]['params']['genre'] = True

                    elif self.user_story[call.message.chat.id]['params']['genre']:
                        self.bot.delete_message(call.message.chat.id, message_id=call.message.id)
                        self.user_story[call.message.chat.id]['genre'] = call.data
                        self.user_story[call.message.chat.id]['params']['genre'] = False
                        self.bot.send_message(call.message.chat.id, speech.title_story())
                        self.user_story[call.message.chat.id]['params']['title'] = True

                    elif call.data == buttons.yes()[0:-2]:
                        self.bot.delete_message(call.message.chat.id, message_id=call.message.id)
                        self.user_story[call.message.chat.id]['user_nickname'] = call.message.chat.username
                        self.story_example(id=call.message.chat.id)

                    elif call.data == buttons.no()[0:-2]:
                        self.bot.delete_message(call.message.chat.id, message_id=call.message.id)
                        self.story_example(id=call.message.chat.id)


                    elif call.data == buttons.yes():
                        self.bot.delete_message(call.message.chat.id, message_id=call.message.id)
                        story_id = self.get_storyId()
                        markup = types.InlineKeyboardMarkup()
                        admin_true = types.InlineKeyboardButton(buttons.check_true(),
                                                                callback_data=f"{story_id}=_=True")
                        markup.add(admin_true)
                        admin_false = types.InlineKeyboardButton(buttons.check_false(),
                                                                 callback_data=f"{story_id}=_=False")
                        self.data[story_id] = [self.user_story[call.message.chat.id]['result'], call.message.chat.id]
                        markup.add(admin_false)
                        self.bot.send_message(self.group_id, self.user_story[call.message.chat.id]['result'],
                                              reply_markup=markup)
                        self.bot.send_message(call.message.chat.id, speech.has_sended())


                    elif call.data == buttons.no():
                        self.bot.delete_message(call.message.chat.id, message_id=call.message.id)
                        del self.user_story[call.message.chat.id]
                        self.bot.send_message(call.message.chat.id, speech.restart())

                else:
                    callback = call.data.split('=_=')
                    print(callback)
                    if callback[1] == 'True':
                        self.bot.delete_message(self.group_id, call.message.id)
                        self.bot.send_message(self.public_id, self.data[callback[0]][0])
                        self.bot.send_message(self.data[callback[0]][1], speech.published())
                        self.bot.send_message(self.data[callback[0]][1], self.data[callback[0]][0].split('\n')[0] + '...')
                        del self.data[callback[0]]
                    else:
                        self.bot.delete_message(self.group_id, call.message.id)
                        self.bot.send_message(self.data[callback[0]][1], speech.rejected())
                        self.bot.send_message(self.data[callback[0]][1], self.data[callback[0]][0].split('\n')[0] + '...')
                        del self.data[callback[0]]
            except Exception as e: print(e)

        @self.bot.message_handler(content_types=['text'])
        def text_handler(message):
            try:
                if message.chat.id in self.user_story:
                    if self.user_story[message.chat.id]['params']['title']:
                        self.user_story[message.chat.id]['title'] = message.text
                        self.user_story[message.chat.id]['params']['title'] = False
                        self.user_story[message.chat.id]['params']['story'] = True
                        self.bot.send_message(message.chat.id, speech.story())

                    elif self.user_story[message.chat.id]['params']['genre']:
                        self.bot.send_message(message.chat.id, speech.change_genre())

                    elif self.user_story[message.chat.id]['params']['story']:
                        self.user_story[message.chat.id]['story'] = message.text
                        self.user_story[message.chat.id]['params']['story'] = False
                        self.user_story[message.chat.id]['params']['author'] = True
                        self.bot.send_message(message.chat.id, speech.author_story())

                    elif self.user_story[message.chat.id]["params"]["author"]:
                        self.user_story[message.chat.id]['author'] = message.text.title().strip()
                        self.user_story[message.chat.id]['params']['author'] = False
                        self.user_story[message.chat.id]["params"]["user_nickname"] = True
                        markup = types.InlineKeyboardMarkup()
                        button_yes = types.InlineKeyboardButton(buttons.yes(), callback_data=buttons.yes()[0:-2])
                        markup.add(button_yes)
                        button_no = types.InlineKeyboardButton(buttons.no(), callback_data=buttons.no()[0:-2])
                        markup.add(button_no)
                        self.bot.send_message(message.chat.id, speech.anon(), reply_markup=markup)

                    else:
                        markup = types.InlineKeyboardMarkup()
                        button = types.InlineKeyboardButton(buttons.start_anket(), callback_data=buttons.start_bttn())
                        markup.add(button)
                        self.bot.send_message(message.chat.id, speech.no_handler(user_name=message.chat.first_name),
                                              reply_markup=markup)
            except Exception as e: print(e)

    def get_storyId(self):
        while True:
            material = list('12345678901234567890qwertyuiopQWERTYUIOPasdfghjklASDFGHJKLzxcvbnmZXCVBNM:')
            random.shuffle(material)
            result = str(random.choice(material)).join(material)[0:15]

            if result not in self.data:
                return result


b = Bot(tok=api.token())
b.bot.polling(interval=0, none_stop=True)

