import telebot
import re
import random
import threading
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
API_TOKEN = 'токен'
bot = telebot.TeleBot(API_TOKEN)
games = {}
r_waiting_delay = 10
cleaning_delay = 20
r_start_delay = 40


def change_roulette(msg_id):
    try:
        games[msg_id][1].cancel()
        del games[msg_id]
        bot.edit_message_text(inline_message_id=msg_id, text='Сессия завершена, слишком много ждунов...', reply_markup=None)
    except Exception as e:
        print('*****')
        print("Warning!", e.__class__, "occurred.", 'Function: del_roulette')
        print('Details: ' + str(e))


def username_fix(username):
    usr_name = re.sub(r'[<>_{}&]', '-', username)
    usr_name = usr_name.encode(
        'utf-8')[:11].decode('utf-8', 'ignore') if len(usr_name.encode('utf-8')) > 20 else usr_name
    return usr_name


def renew_keyboard(frst_plr, scnd_plr, frstp_name, scndp_name, agreed=False):
    view_keyboard = InlineKeyboardMarkup().row(
    InlineKeyboardButton(' ', callback_data='rlt_wrong_0_0_-_-'),
    InlineKeyboardButton('🔵', callback_data='rlt_1_' + frst_plr + '_' + scnd_plr + '_' + frstp_name + '_' + scndp_name),
    InlineKeyboardButton('🔵', callback_data='rlt_2_' + frst_plr + '_' + scnd_plr + '_' + frstp_name + '_' + scndp_name),
    InlineKeyboardButton(' ', callback_data='rlt_wrong_0_0_-_-')).row(
    InlineKeyboardButton('🔵', callback_data='rlt_3_' + frst_plr + '_' + scnd_plr + '_' + frstp_name + '_' + scndp_name),
    InlineKeyboardButton(' ', callback_data='rlt_wrong_0_0_-_-'),
    InlineKeyboardButton('🔵', callback_data='rlt_4_' + frst_plr + '_' + scnd_plr + '_' + frstp_name + '_' + scndp_name)).row(
    InlineKeyboardButton(' ', callback_data='rlt_wrong_0_0_-_-'),
    InlineKeyboardButton('🔵', callback_data='rlt_5_' + frst_plr + '_' + scnd_plr + '_' + frstp_name + '_' + scndp_name),
    InlineKeyboardButton('🔵', callback_data='rlt_6_' + frst_plr + '_' + scnd_plr + '_' + frstp_name + '_' + scndp_name),
    InlineKeyboardButton(' ', callback_data='rlt_wrong_0_0_-_-'))

    if agreed:
        view_keyboard.row(InlineKeyboardButton('Выйти', callback_data='rlt_leave_' + frst_plr + '_' + scnd_plr + '_' + frstp_name + '_' + scndp_name))

    return view_keyboard


@bot.inline_handler(lambda query: True)
def query_text(inline_query):
    try:
        invite = InlineKeyboardMarkup().row(InlineKeyboardButton("Play",
            callback_data=f"rlt_join_0_0_-_-"))

        msg_text = f'*Русская рулетка*\nИгра готова\n⌛Ожидаем игроков...'

        rlt = InlineQueryResultArticle('roulette', 'Roulette', InputTextMessageContent(msg_text, parse_mode='Markdown'), reply_markup=invite,
            description='Russian roulette, kind of...',
            thumb_url='https://www.meme-arsenal.com/memes/c933f3402e63483f6eee37762d09349f.jpg')

        bot.answer_inline_query(inline_query.id, [rlt], is_personal=True, cache_time=10)
    except Exception as e:
        print('*****')
        print("Warning!", e.__class__, "occurred.", 'Function: roulette')
        print('Details: ' + str(e))


@bot.callback_query_handler(func=lambda call: call.data.startswith("rlt_"))
def roulette_setup(call):
    try:
        shoot_num = 0
        players_inf = call.data.split('_')
        if players_inf[2] != '0' and players_inf[4] != '-':
            if players_inf[3] != '0' and players_inf[5] != '-':
                initiator = "[" + players_inf[4] + \
                    "](tg://user?id=" + players_inf[2] + ")"
                opponent = "[" + players_inf[5] + \
                    "](tg://user?id=" + players_inf[3] + ")"
            else:
                usr_name = username_fix(str(call.from_user.first_name))
                initiator = "[" + players_inf[4] + \
                    "](tg://user?id=" + players_inf[2] + ")"
                opponent = "[" + usr_name + \
                    "](tg://user?id=" + str(call.from_user.id) + ")"

        if call.inline_message_id in games:
            shoot_num = games[call.inline_message_id][0]

        if 'join' in call.data[4:]:
            if players_inf[2] != '0' and players_inf[4] != '-':
                if players_inf[2] != str(call.from_user.id):
                    usr_name = username_fix(str(call.from_user.first_name))
                    msg_text = f'*Русская рулетка*\n{initiator} vs {opponent}\n\n➡️ {initiator} начинает...\n🙄 {opponent} ждет...'
                    bot.edit_message_text(inline_message_id=call.inline_message_id, text=msg_text,
                        parse_mode='Markdown', reply_markup=renew_keyboard(players_inf[2], str(call.from_user.id), players_inf[4], usr_name, True))
                    bot.answer_callback_query(call.id, 'Добро пожаловать в игру!')
                    random.seed()
                    if call.inline_message_id in games:
                        games[call.inline_message_id][1].cancel()
                    games[call.inline_message_id] = [random.randint(1, 7), threading.Timer(r_start_delay, change_roulette, args=(call.inline_message_id,))]
                    games[call.inline_message_id][1].start()
                else:
                    bot.answer_callback_query(call.id, 'Нельзя играть самому с собой!')
            else:
                    usr_name = username_fix(str(call.from_user.first_name))
                    initiator = "[" + usr_name + "](tg://user?id=" + str(call.from_user.id) + ")"
                    invite = InlineKeyboardMarkup().row(InlineKeyboardButton("Play", callback_data=f"rlt_join_{str(call.from_user.id)}_0_{usr_name}_-"))
                    msg_text = f'*Русская рулетка*\n➡️ {initiator} ожидает оппонента...'
                    bot.edit_message_text(inline_message_id=call.inline_message_id, text=msg_text,
                        parse_mode='Markdown', reply_markup=invite)
                    bot.answer_callback_query(call.id, 'Добро пожаловать в игру!')
                    if call.inline_message_id in games:
                        games[call.inline_message_id][1].cancel()
                    games[call.inline_message_id] = [0, threading.Timer(r_waiting_delay, change_roulette, args=(call.inline_message_id,))]
                    games[call.inline_message_id][1].start()

        elif 'wrong' in call.data[4:]:
            bot.answer_callback_query(call.id, 'Систему не обманешь!')

        elif 'leave' in call.data[4:] and players_inf[5] != '-':
            if (str(call.from_user.id) == players_inf[2]) or (str(call.from_user.id) == players_inf[3]):
                join_button = ''
                if str(call.from_user.id) == players_inf[3]:
                    msg_text = f'*Русская рулетка*\nИгра перезапущена\n⌛️{initiator} ожидает нового оппонента\n{opponent} ливнул...'
                    join_button = InlineKeyboardMarkup().row(InlineKeyboardButton("Play",
                        callback_data=f"rlt_join_{players_inf[2]}_0_{players_inf[4]}_-"))
                    games[call.inline_message_id][1].cancel()
                    games[call.inline_message_id][1] = threading.Timer(r_waiting_delay,
                            change_roulette, args=(call.inline_message_id,))
                    games[call.inline_message_id][1].start()

                else:
                    msg_text = f'*Русская рулетка*\nИгра перезапущена\n⌛️{opponent} ожидает нового оппонента\n{initiator} ливнул...'
                    join_button = InlineKeyboardMarkup().row(InlineKeyboardButton("Play",
                        callback_data=f"rlt_join_{players_inf[3]}_0_{players_inf[5]}_-"))
                    games[call.inline_message_id][1].cancel()
                    games[call.inline_message_id][1] = threading.Timer(r_waiting_delay,
                            change_roulette, args=(call.inline_message_id,))
                    games[call.inline_message_id][1].start()
                
                bot.edit_message_text(inline_message_id=call.inline_message_id, text=msg_text, parse_mode='Markdown', reply_markup=join_button)
                bot.answer_callback_query(call.id, 'Быбы, ссыкло...')
            else:
                bot.answer_callback_query(call.id, 'Это не твоя игра, свали...')

        elif players_inf[5] != '-':
            if players_inf[2] == str(call.from_user.id):
                if players_inf[1] == str(shoot_num):
                    msg_text = f'*Русская рулетка*\n{initiator} vs {opponent}\n'
                    if str(call.from_user.id) == players_inf[2]:
                        msg_text += f'\n💀 {initiator} застрелился...'
                        msg_text += f'\n🏆 {opponent} выжил...'
                        bot.edit_message_text(inline_message_id=call.inline_message_id, text=msg_text + '',
                            parse_mode='Markdown', reply_markup=None)
                        games[call.inline_message_id][1].cancel()
                    else:
                        msg_text += f'\n💀 {opponent} застрелился...'
                        msg_text += f'\n🏆 {initiator} выжил...'
                        bot.edit_message_text(inline_message_id=call.inline_message_id, text=msg_text + '',
                            parse_mode='Markdown', reply_markup=None)
                        games[call.inline_message_id][1].cancel()
                    bot.answer_callback_query(call.id, 'Выстрел!')

                elif players_inf[1] != str(shoot_num):
                    msg_text = f'*Русская рулетка*\n{initiator} против {opponent}\n'
                    if str(call.from_user.id) == players_inf[2]:
                        msg_text += f'\n➡️ {opponent} ты следующий...'
                        msg_text += f'\n😎 {initiator} повезло...'
                        bot.edit_message_text(inline_message_id=call.inline_message_id, text=msg_text + '',
                            parse_mode='Markdown', reply_markup=renew_keyboard(players_inf[3], players_inf[2], players_inf[5], players_inf[4]))
                        games[call.inline_message_id][1].cancel()
                        games[call.inline_message_id][1] = threading.Timer(r_waiting_delay,
                            change_roulette, args=(call.inline_message_id,))
                        games[call.inline_message_id][1].start()
                    else:
                        msg_text += f'\n➡️ {initiator} ты следующий...'
                        msg_text += f'\n😎 {opponent} повезло...'
                        bot.edit_message_text(inline_message_id=call.inline_message_id, text=msg_text + '',
                            parse_mode='Markdown', reply_markup=renew_keyboard(players_inf[2], players_inf[3], players_inf[4], players_inf[5]))
                        games[call.inline_message_id][1].cancel()
                        games[call.inline_message_id][1] = threading.Timer(r_waiting_delay,
                            change_roulette, args=(call.inline_message_id,))
                        games[call.inline_message_id][1].start()
                    bot.answer_callback_query(call.id, 'Повезло!')
                    random.seed()
                    games[call.inline_message_id][0] = random.randint(1, 7)
            else:
                bot.answer_callback_query(call.id, 'Жди совей очереди!')
        else:
            bot.answer_callback_query(call.id, 'Ждем оппонента!')
    except Exception as e:
        print('*****')
        print("Warning!", e.__class__, "occurred.", 'Function: roulette_setup')
        print('Details: ' + str(e))

bot.infinity_polling()
