import random
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

TOKEN = "ТВОЙ_ТОКЕН_СЮДА"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

DATA_FILE = "sites.json"
USER_FILE = "users.json"


# ---------- ЗАГРУЗКА ----------
def load_sites():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_sites(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def load_users():
    try:
        with open(USER_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(data):
    with open(USER_FILE, "w") as f:
        json.dump(data, f)


# ---------- ЛОГИКА ----------
def get_random_site(user_id):
    sites = load_sites()
    users = load_users()

    viewed = users.get(str(user_id), [])

    # фильтр плохих сайтов
    good_sites = [s for s in sites if s["likes"] >= s["dislikes"]]

    if not good_sites:
        good_sites = sites

    # убираем просмотренные
    available = [s for s in good_sites if s["id"] not in viewed]

    if not available:
        users[str(user_id)] = []
        save_users(users)
        available = good_sites

    site = random.choice(available)

    users.setdefault(str(user_id), []).append(site["id"])
    save_users(users)

    return site


# ---------- КНОПКИ ----------
def keyboard(site_id):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("👍", callback_data=f"like_{site_id}"),
        InlineKeyboardButton("👎", callback_data=f"dislike_{site_id}")
    )
    kb.add(
        InlineKeyboardButton("🎲 Новый сайт", callback_data="new")
    )
    return kb


# ---------- ХЕНДЛЕРЫ ----------
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    site = get_random_site(message.from_user.id)
    await message.answer(
        f"🌐 Случайный сайт:\n\n{site['url']}",
        reply_markup=keyboard(site["id"])
    )


@dp.callback_query_handler(lambda c: True)
async def callback(call: types.CallbackQuery):
    data = call.data
    sites = load_sites()

    if data == "new":
        site = get_random_site(call.from_user.id)
        await call.message.edit_text(
            f"🌐 Случайный сайт:\n\n{site['url']}",
            reply_markup=keyboard(site["id"])
        )
        return

    action, site_id = data.split("_")
    site_id = int(site_id)

    for site in sites:
        if site["id"] == site_id:
            if action == "like":
                site["likes"] += 1
            elif action == "dislike":
                site["dislikes"] += 1

    save_sites(sites)

    await call.answer("Оценка сохранена 👍")


# ---------- ЗАПУСК ----------
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)