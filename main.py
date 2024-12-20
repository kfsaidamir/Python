# pip install aiogram
# pip install python-dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, LabeledPrice, FSInputFile
from aiogram.filters import Command


from keyboards import *
from database import *
from dotenv import load_dotenv

import os 
import asyncio
import datetime

load_dotenv()

TOKEN = os.getenv('TOKEN')
PAYMENT = os.getenv('PAYMENT')

bot = Bot(TOKEN)
dp = Dispatcher()

@dp.message(Command('start'))
async def command_start(message: Message):
    full_name = message.from_user.full_name
    await  message.answer(f'Добро пожаловать, {full_name} \nВас привествует saidamir' )
    await register_user(message)
    
async def register_user(message:Message):
    chat_id = message.chat.id
    full_name = message.from_user.full_name
    user = first_select_user(chat_id)
    if user:
        await message.answer('authorization was successfully')
        await show_main_menu(message)
    else:
        first_register_user(chat_id, full_name)
        await message.answer('For end register - share contact',  reply_markup=phone_button())
        
@dp.message(F.contact)
async def finish_register(message:Message):
    chat_id = message.chat.id
    phone = message.contact.phone_number
    update_user_to_finish_register(chat_id, phone)
    await create_carts_for_user(message)
    await message.answer('Registration was successfully!')
    await show_main_menu(message)
    
async def create_carts_for_user(message:Message):
    chat_id = message.chat.id
    try:
        insert_to_cart(chat_id)
    except:
        pass

async def show_main_menu(message:Message):
    await message.answer('Choose:', reply_markup=generate_main_menu())
    

@dp.pre_checkout_query(lambda query: True)
async def checkout(pre_checkout_query):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True, error_message='Something went worng' )


@dp.message(F.content_type.in_({'successful_payment'}))
async def get_payment(message:Message):
    chat_id = message.chat.id
    cart_id = get_user_cart_id(chat_id)
    
    if drop_cart_products_default(cart_id):
        await bot.send_message(chat_id, 'Successfully payment!' )
        
        
        
        
    
    
    
@dp.message(lambda message: 'make an order🍴' in message.text)
async def make_order(message:Message):
    await message.answer('Choose the category: ', reply_markup=generate_category_menu())
    
 
 
@dp.callback_query(lambda call: 'category' in call.data)
async def show_products(call: CallbackQuery):
     chat_id = call.message.chat.id
     msg_id = call.message.message_id
     _, category_id = call.data.split('_')
     await bot.edit_message_text('Choose the product', chat_id=chat_id, message_id=msg_id, reply_markup=product_by_category(category_id)) 
     
     
@dp.callback_query(lambda call: 'main_menu' in call.data)
async def return_to_category(call:CallbackQuery):
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    await bot.edit_message_text('Choose the category: ', chat_id=chat_id, message_id=msg_id, reply_markup=generate_category_menu())
    


@dp.callback_query(lambda call: 'Product' in call.data)
async def show_detail_product(call:CallbackQuery):
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    _, product_id = call.data.split('_')
    product = get_product_details(product_id) 
    await bot.delete_message(chat_id, message_id=msg_id)
    img = FSInputFile(product[-1])
    await bot.send_photo(chat_id=chat_id, photo=img, caption=f'''{product[2]}
    Description: {product[-2]}
    Price: {product[3]} uzs
''', reply_markup=generate_product_detail_menu(product_id, category_id=product[1], quantity=0))
     
@dp.callback_query(lambda call: 'back' in call.data)
async def return_to_product_category(call:CallbackQuery):
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    _,  category_id = call.data.split('_')
    await bot.delete_message(chat_id, message_id=msg_id)
    await bot.send_message(chat_id, 'Choose the product:  ', reply_markup=product_by_category(category_id))      
     


@dp.callback_query(lambda call: 'btn' in call.data)
async def add_product_cart(call:CallbackQuery):
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    _, action ,product_id = call.data.split('_')
    product = get_product_details(product_id)
    cart_id = get_user_cart_id(chat_id)
    
    try:
        quantity = get_quantity(cart_id,product[2])
    except:
        quantity = 0
    if action == 'del':
        if quantity < 1:
            pass 
        else:
            quantity -= 1
    elif action == 'add':
        quantity += 1
    final_price = quantity * product[3]
    if insert_or_update_cart_product(cart_id, product[2], quantity,final_price):
        await bot.answer_callback_query(call.id, 'Product was succeffully added!')
    else:
        await bot.answer_callback_query(call.id, 'Quantity was changed')
    await bot.edit_message_reply_markup(chat_id=chat_id, message_id=msg_id, reply_markup=generate_product_detail_menu(product_id, category_id=product[1],quantity=quantity) )  
     
     
@dp.message(F.text == '🧺basket')
async def show_cart(message:Message, edit_message:bool = False ):
    chat_id = message.chat.id
    cart_id = get_user_cart_id(chat_id)
    
    try:
        update_total_product_total_price(cart_id)  
    except Exception as e :
        print(e)
        await message.answer('Backet is blocked')
        return
    
    cart_products = get_cart_products(cart_id)
    total_products , total_price = get_total_products_price(cart_id)     
    
    
    if total_price and total_products:
        text = 'Your basket: \n\n'
        i = 0
        for product_name, quantity, final_price in cart_products:
            i += 1
            text += f'''{i}.{product_name}
Quantity: {quantity}
Overal cost: {final_price} sum\n\n '''
        text += f'''Total products: {0 if total_price is None else total_products}
Total: {0 if total_price is None else total_price}'''
        if edit_message:
            await bot.edit_message_text(text, chat_id=chat_id, message_id=message.message_id,reply_markup=generate_cart_menu(cart_id))
        else:
            await bot.send_message(chat_id,text,reply_markup=generate_cart_menu(cart_id))
    else:
          await bot.delete_message(chat_id,message_id=message.message_id)
          await bot.send_message(chat_id, 'Basket is empty' )      


@dp.callback_query(lambda call: 'delete' in call.data)
async def delete_cart_product(call:CallbackQuery):
    _, cart_product_id = call.data.split('_')
    message = call.message
    if delete_cart_products_from_db(cart_product_id):
        await bot.answer_callback_query(call.id, text='Product was sucssefully deleted')
        await show_cart(message,edit_message=True) 


@dp.callback_query(lambda call: 'order' in call.data)
async def create_order(call:CallbackQuery):
    chat_id = call.message.chat.id
    _, cart_id = call.data.split('_')
    time_order = datetime.datetime.now().strftime('%H:%M')
    date_order = datetime.datetime.now().strftime('%d.%m.%Y') 


    cart_products = get_cart_products(cart_id)
    total_products, total_price = get_total_products_price(cart_id)
    
    save_order_check(cart_id, total_price, total_products, time_order, date_order)
    order_check_id = get_order_check_id(cart_id)
    
    text = 'Your basket: \n\n'
    i = 0
    
    for product_name, quantity, final_price in cart_products:
        i += 1
        text += f'''{i}. {product_name}
        
Quantity: {quantity}
Total price: {final_price}\n\n'''
        save_order(order_check_id,product_name, quantity, final_price)    
    text += f''' Total: {0 if total_products is None else total_products } 
Total : {0 if total_price is None else total_price}sum'''

    await bot.send_invoice(
        chat_id=chat_id,
        title=f'Order №{cart_products}',
        description=text,
        payload='bot-defined  invoice payload',
        provider_token=PAYMENT,
        currency='UZS',
        prices=[
            LabeledPrice(label='Total price', amount=int(total_price*100)),
            LabeledPrice(label='Delivery', amount=1000000)
        ],
        start_parameter='start_parameter'
    )


@dp.message(F.text == 'History')
async def show_history(message:Message):
    chat_id = message.chat.id
    cart_id = get_user_cart_id(chat_id)
    order_check_id = get_order_check_id(cart_id)
    history = get_detail_order(order_check_id)
    
    text = 'Your history: \n\n'
    d = 0
    
    for product_name, quantity, final_price in history:
        d += 1
        text += f''' {d}. {product_name, quantity, final_price}'''
    
    await bot.send_message(chat_id, text=text, reply_markup=generate_main_menu())    


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    
     
if __name__ == '__main__':
    asyncio.run(main())

