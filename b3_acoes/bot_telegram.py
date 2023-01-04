# Bibliotecas / Libraries:
import telebot

# Configurando o BOT Telegram:
from config import chave_bot_telegram                                                                                           # Importando a chave API para criacao do BOT

# Configurando o BOT Telegram:
bot = telebot.TeleBot(chave_bot_telegram)                                                                                       # Criando o BOT Telegram
user_register_dict = {}

# Emoji List:
robot_face = "\U0001F916"
brazilian_flag = "\U0001f1e7\U0001f1f7"
unites_states_flag = "\U0001f1fA\U0001f1f8"
spanish_flag = "\U0001f1eA\U0001f1f8"

# Funcao verificadora de mensagem:
def msg_true(msg):
        return True

# Function 1 (contact details - English Language option):
@bot.message_handler(commands=["option1"])
def option1(msg):
    text = """
Please, find below the Leonardo's Delboni contact details:

Mobile:            
    https://api.whatsapp.com/send?phone=5511994421880
Personal E-mail:   
    leonardodelboni@gmail.com
GitHub:            
    https://github.com/leonardo-travagini-delboni
Current Address:   
    Vila Olimpia, South Area, Sao Paulo, SP, Brazil
    """
    bot.send_message(msg.chat.id, text)

# Function 2 (Brazilian Stock Market Company Data through e-mail - English option):
@bot.message_handler(commands=["option2"])
def option2(msg):
    text = """
Please, enter the 5-digit Brazilian Stock market company you want to get the information.
    """
    sent_message = bot.send_message(msg.chat.id, text)
    sent_message_id = sent_message.message_id
    replied_message = msg.reply_to_message.message_id
    print('sent_message: ', sent_message)
    print('sent_message_id: ', sent_message_id)
    print('replied_message: ', replied_message)

# Function 3 (Critics and Suggestions - English option):
@bot.message_handler(commands=["option3"])
def option3(msg):
    bot.reply_to('Thank you very much for your message! We will really consider this!')

# English Language Chosen:
@bot.message_handler(commands=["ENG"])
def english_opening(msg):    
    full_name = str(msg.from_user.first_name) + ' ' + str(msg.from_user.last_name)                                             # Finding the new contact fullname
    bot.send_message(msg.chat.id, f'Welcome Mr(s) {full_name}! Nice to meet you!')                                             # Sending standard welcome message
    bot.send_message(msg.chat.id, f'I am the Leo Delboni Telegram BOT! {robot_face}.')                                         # Presenting ourselves to the user
    text = """
We kindly ask you to choose one of the following options:

/option1 Get in touch with me (Leonardo Travagini Delboni)!
/option2 Get a Brazilian stock company data in your e-mail!
/option3 Critics and Suggestions!
    """
    bot.reply_to(msg, text)                                                                                                    # Sending the option menu to the user

# Funcao de boas-vindas ao usuario
@bot.message_handler(func = msg_true)                                                                                          # Decorator da funcao de boas-vindas
def telegram_boas_vindas(msg):                                                                                                 # Funcao de resposta automatica de boas vindas
    text = f"""
Click in /ENG to speak in English!  {unites_states_flag}
Clique em /PT para falar em Português! {brazilian_flag}
Pulse /ESP para hablar en español! {spanish_flag}
    """
    bot.reply_to(msg, text)                                                                                                    # Sending the option menu to the user
 
# Permanent BOT execution command:
print('ANTES DO POLLING!')
bot.polling()                                                                                                                  # Setting Telegram BOT in permanent execution
print('DEPOIS DO POLLING!')
