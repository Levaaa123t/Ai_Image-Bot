import telebot
from config import *
from ai_code import Text2ImageAPI
import base64
import random
#Импорт библиотек

bot = telebot.TeleBot(TOKEN)
#Объект бот из класса

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который генерирует картинки. Напиши /photo_promt чтобы начать")

@bot.message_handler(commands=['photo_promt'])
def photo_promt(message):
    promt_question = bot.send_message(message.chat.id, 'Напиши свой промт:')
    bot.register_next_step_handler(promt_question, get_promt)  

def get_promt(message): 
    promt = message.text
    style_question = bot.send_message(message.chat.id, '''Напиши какой стиль ты бы хотел использовать(ОБЯЗАТЕЛЬНО ПИСАТЬ ЗАГЛАВНЫМИ):
                                  ANIME(Аниме)
                                  KANDINSKY(Кандинский)
                                  UHD(Детально)
                                  DEFAULT(По умолчанию)
                                ''')
    bot.register_next_step_handler(style_question, photo_style, promt)
def photo_style(message, promt):  
    user_style = message.text.upper()  
    if user_style not in ['ANIME', 'KANDINSKY', 'UHD', 'DEFAULT']:
        bot.send_message(message.chat.id, "Неверный стиль! Используй один из предложенных вариантов.")
        return
    
    photo_generation(message, promt, user_style)
    
def photo_generation(message, promt, user_style):  
    bot_send_generation = bot.send_message(message.chat.id, 'Генерирую...')
    
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        api = Text2ImageAPI('https://api-key.fusionbrain.ai/', api_token, secret_key)
        model_id = api.get_model()
        uuid = api.generate(prompt=promt, model=model_id, style=user_style)
        images = api.check_generation(uuid)
        
        if images is None:
            raise Exception("Ошибка генерации изображения")
            
        image_base64 = images[0]
        image_data = base64.b64decode(image_base64)
        file_name = f'generated_image{random.randint(0,1000)}.jpg'
        
        with open(f"img/{file_name}", "wb") as file:
            file.write(image_data)
            
        with open(f"img/{file_name}", "rb") as file:
            bot.send_photo(message.chat.id, file)
        bot.delete_message(message.chat.id, bot_send_generation.message_id )
            
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")



if __name__=="__main__":
    bot.polling(non_stop= True)
