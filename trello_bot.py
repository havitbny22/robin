
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import requests

TRELLO_KEY = os.environ['TRELLO_KEY']
TRELLO_TOKEN = os.environ['TRELLO_TOKEN']
BOARD_ID = os.environ['BOARD_ID']
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']

def get_cards():
    url = f"https://api.trello.com/1/boards/{BOARD_ID}/cards"
    params = {'key': TRELLO_KEY, 'token': TRELLO_TOKEN}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_member_name(member_id):
    url = f"https://api.trello.com/1/members/{member_id}"
    params = {'key': TRELLO_KEY, 'token': TRELLO_TOKEN}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        member = response.json()
        return member.get('fullName', 'نامشخص')
    else:
        return 'نامشخص'

def get_list_name(list_id):
    url = f"https://api.trello.com/1/lists/{list_id}"
    params = {'key': TRELLO_KEY, 'token': TRELLO_TOKEN}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('name', 'لیست نامشخص')
    else:
        return 'لیست نامشخص'

def find_card_holder(card_name):
    cards = get_cards()
    if not cards:
        return "❌ خطا در دریافت اطلاعات از Trello"

    for card in cards:
        if card_name.lower() in card['name'].lower():
            member_ids = card.get('idMembers', [])
            list_id = card.get('idList', None)
            list_name = get_list_name(list_id) if list_id else 'نامشخص'

            if member_ids:
                member_name = get_member_name(member_ids[0])
                return f"📄 سند در لیست: {list_name}\n👤 مسئول: {member_name}"
            else:
                return f"📄 سند در لیست: {list_name}\n⚠️ کسی روی این سند نیست."

    return "❓ سند مورد نظر پیدا نشد."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لطفاً شماره یا نام سند رو بفرست تا بگم در کدوم لیسته و دست کیه.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    card_name = update.message.text.strip()
    holder_info = find_card_holder(card_name)
    await update.message.reply_text(holder_info)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 ربات در حال اجراست...")
    app.run_polling()

if __name__ == '__main__':
    main()
