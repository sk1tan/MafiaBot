from telebot import TeleBot
from random import *
import dbp
from time import *

print('Bot ready!')
game = False
players = []
TOKEN = '6507522083:AAHGxeJOrUIyK8BS5Ax4JX0uYXNtbAcJnus'
bot = TeleBot(TOKEN)
night = True

def get_killed(night):
    if not night:
        username_killed = dbp.citizen_kill()
        return f'Гаражане выгнали: {username_killed}'
    else:
        username_killed = dbp.mafia_kill()
        return f'Мафии убили: {username_killed}'

def game_loop(message):
    global night, game
    bot.send_message(message.chat.id, 'Добро пожаловать в игру! Вам даётся 2 минуты, чтобы познакомиться!')
    sleep(120)
    while True:
        get_killed(night)
        if night:
            bot.send_message(message.chat.id, 'Город засыпает, просыпается мафия')
        else:
            bot.send_message(message.chat.id, 'Город просыпается')
        winner = dbp.get_winner()
        if winner == 'Citizen' or winner == 'Mafia':
            bot.send_message(message.chat.id, f'Игра окончена, победили: {winner}')
            game = False
        #dbp.clear(dead=False) Потом сделаю функцию
        night = not night
        alive_people = dbp.get_all_alive()
        alive_people = '/n'.join(alive_people)
        bot.send_message(message.chat.id, f'Живые игроки: {alive_people}')
        sleep(120)

@bot.message_handler(commands=['start'])
def game(message):
    if game == False:
        bot.send_message(message.chat.id, 'Если хотите играть - напишите "готов" в лс')

@bot.message_handler(func=lambda m: m.text.lower() == 'готов' and m.chat.type == 'private')
def sent_text(message):
    bot.send_message(message.chat.id, f'Пользователь {message.from_user.first_name} готов к игре')
    dbp.insert_player(message.from_user.id, message.from_user.first_name)

@bot.message_handler(commands=['game'])
def game_start(message):
    global game
    players = dbp.player_amount()
    if players >= 5 and not game:
        game = True
        dbp.set_role(players)
        players_roles = dbp.get_players_role()
        mafia_usernames = dbp.get_mafia_usernames()
        for player_id, role in players_roles:
            bot.send_message(player_id, role)
            if role == 'mafia':
                bot.send_message(player_id, f'Мафии: {mafia_usernames}')
        bot.send_message(message.chat.id, 'Игра началась')
        return
    bot.send_message(message.chat.id, 'Мало людей')

@bot.message_handler(commands=["kick"])
def kick(message):
    username = ' '.join(message.text.split(' ')[1:])
    usernames = dbp.get_all_alive()
    if not night:
        if not username in usernames:
            bot.send_message(message.chat.id, 'Такого имени нет')
            return
        voted = dbp.vote("citizen_vote", username, message.from_user.id)
        if voted:
            bot.send_message(message.chat.id, 'Ваш голос учтён')
            return
        bot.send_message(message.chat.id, 'У вас нет права голосовать!')
        return
    bot.send_message(message.chat.id, 'Сейчас ночь, вы не можете никого выгнать')

@bot.message_handler(commands=["kill"])
def kill(message):
    username = ' '.join(message.text.split(' ')[1:])
    usernames = dbp.get_all_alive()
    mafias = dbp.get_mafia_usernames()
    if message.from_user.first_name in mafias:
        if night:
            if not username in usernames:
                bot.send_message(message.chat.id, 'Такого имени нет')
                return
            voted = dbp.vote("mafia_vote", username, message.from_user.id)
            if voted:
                bot.send_message(message.chat.id, 'Ваш голос учтён')
                return
            bot.send_message(message.chat.id, 'У вас нет права голосовать!')
            return
        bot.send_message(message.chat.id, 'Сейчас не ночь, вы не можете никого убить')
        return
    bot.send_message(message.chat.id, 'Вы не мафия!')
        
if __name__ == '__main__':
    bot.infinity_polling(none_stop = True)