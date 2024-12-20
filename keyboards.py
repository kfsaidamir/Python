from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from database import get_all_categories, get_product_details, get_products_by_category_id, get_cart_product_for_delete

def phone_button():
    return ReplyKeyboardMarkup(keyboard=[[
        KeyboardButton(text='Share contact☎️', request_contact=True)
    ]], resize_keyboard=True)
    
    
def generate_main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='make an order🍴')],
        [KeyboardButton(text='History'), KeyboardButton(text='🧺basket'), KeyboardButton(text='Settings')] 
    ], resize_keyboard=True, one_time_keyboard=True)


def generate_category_menu():
    markup = InlineKeyboardMarkup(inline_keyboard=[])
    markup.inline_keyboard.append([InlineKeyboardButton(text='Our menu🍖', url= 'https://telegra.ph/Nashe-menyu-08-16' )])
    categories = get_all_categories()
    buttons = []
    for i in categories:
        btn = InlineKeyboardButton(text=i[1], callback_data=f'category_{i[0]}' )
        buttons.append(btn)
    markup.inline_keyboard.append(buttons)
    return markup

def product_by_category(category_id):
    markup = InlineKeyboardMarkup(inline_keyboard=[], row_width=2)
    products = get_products_by_category_id(category_id)
    buttons = []
    for i in products:
        btn = InlineKeyboardButton(text=i[1], callback_data=f'Product_{i[0]}')
        buttons.append(btn)
    markup.inline_keyboard.append(buttons)
    markup.inline_keyboard.append(
        [InlineKeyboardButton(text='Back', callback_data='main_menu')]
    )     
    return markup    
    
    
    
def generate_product_detail_menu(product_id, category_id, quantity):
    markup = InlineKeyboardMarkup(inline_keyboard=[], row_width=3)
    btn_del = InlineKeyboardButton(text='-', callback_data=f'btn_del_{product_id}')
    btn_info = InlineKeyboardButton(text=str(quantity), callback_data=f'btn_info_{product_id}')
    btn_add = InlineKeyboardButton(text= '+', callback_data=f'btn_add_{product_id}')
    buttons = [btn_del,btn_info,btn_add]
    markup.inline_keyboard.append(buttons)
    markup.inline_keyboard.append(
        [InlineKeyboardButton(text='Back', callback_data=f'back_{category_id}')]
    )   
    return markup
    

def generate_cart_menu(cart_id):
    markup = InlineKeyboardMarkup(inline_keyboard=[])
    markup.inline_keyboard.append(
        [InlineKeyboardButton(text='Pay', callback_data=f'order_{cart_id}')]
    )
    cart_products = get_cart_product_for_delete(cart_id)
    
    for cart_product_id, product_name in cart_products:
        markup.inline_keyboard.append(
            [InlineKeyboardButton(text=f'Delete - {product_name}', callback_data=f'delete_{cart_product_id}')]
    )
    return markup   
    