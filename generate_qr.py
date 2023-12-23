import os
import json
import qrcode
import telebot
from loguru import logger
from dotenv import load_dotenv

load_dotenv('.env')

bot = telebot.TeleBot(token=os.getenv('TELEBOT_TOKEN'))

def generate_qr_code(employee_id, employee_name):
    json_data = {
        'employee_id': employee_id,
        'employee_name': employee_name,
        'employee_status': 'active'
    }
    data = json.dumps(json_data)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    os.makedirs("qrcodes", exist_ok=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img_path = f"qrcodes/{employee_id}_{employee_name}.png"
    img.save(img_path)
    
    with open(img_path, 'rb') as photo:
        logger.info(f'[!!] Success send qr code to {employee_id}')
        bot.send_photo(chat_id=employee_id, photo=photo)

    os.remove(img_path)

@bot.message_handler(commands=['generate_qr_code'])
def handle_generate_qr(message):
    employee_id = message.from_user.id
    employee_name = message.from_user.username
    generate_qr_code(employee_id, employee_name)


bot.polling()