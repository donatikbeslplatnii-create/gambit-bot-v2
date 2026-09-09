import random
import sqlite3
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram import F
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
API_TOKEN = "8578178174:AAHltDcOzQiyDBIyeP4MSvLLeJ8e8wH2XfY"
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# БАЗА ДАННЫХ
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, games TEXT)')
    conn.commit()
    conn.close()

def save_game(user_id, game):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT games FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row:
        games = json.loads(row[0])
        if game['name'] not in [g['name'] for g in games]:
            games.append(game)
        c.execute("UPDATE users SET games=? WHERE user_id=?", (json.dumps(games), user_id))
    else:
        c.execute("INSERT INTO users VALUES (?, ?)", (user_id, json.dumps([game])))
    conn.commit()
    conn.close()

def get_games(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT games FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return json.loads(row[0]) if row else []

# ===== ИГРЫ С ВНЕШНИМИ КАРТИНКАМИ =====
GAMES = [
    {"name": "DOOM Eternal", "desc": "Relentless movement", "best": "action", "vibe": "fast", "img": "https://i.ibb.co/sFpXhX0/doom.jpg"},
    {"name": "Hades", "desc": "Sharp combat", "best": "skill", "vibe": "myth", "img": "https://i.ibb.co/hLbKq8J/hades.jpg"},
    {"name": "Outer Wilds", "desc": "Space exploration", "best": "mystery", "vibe": "space", "img": "https://i.ibb.co/rvZ2J4P/outer.jpg"},
    {"name": "Stardew Valley", "desc": "Farming RPG", "best": "relax", "vibe": "cozy", "img": "https://i.ibb.co/Fh9sVgJ/stardew.jpg"},
    {"name": "Elden Ring", "desc": "Dark fantasy RPG", "best": "challenge", "vibe": "dark", "img": "https://i.ibb.co/G9pWqGn/elden.jpg"},
    {"name": "Subnautica", "desc": "Underwater survival", "best": "explore", "vibe": "deep", "img": "https://i.ibb.co/YkRZxJZ/subnautica.jpg"},
    {"name": "The Witcher 3", "desc": "Open-world RPG", "best": "story", "vibe": "fantasy", "img": "https://i.ibb.co/7Xx8zVK/witcher.jpg"},
    {"name": "Cyberpunk 2077", "desc": "Sci-fi RPG", "best": "immersion", "vibe": "neon", "img": "https://i.ibb.co/DtX8hCv/cyberpunk.jpg"},
]

# ===== КНОПКИ =====
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 Surprise Me", callback_data="surprise")],
        [InlineKeyboardButton(text="📋 All Games", callback_data="all")],
        [InlineKeyboardButton(text="👤 My Cabinet", callback_data="cabinet")]
    ])

@dp.message(Command("start"))
async def start(msg):
    init_db()
    await msg.answer(
        "🎮 **GOD GAMBIT**\n\nНажми Surprise, чтобы получить игру с картинкой!",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "surprise")
async def surprise(call):
    try:
        game = random.choice(GAMES)
        text = f"**{game['name']}**\n{game['desc']}\n\n🎯 {game['best']}\n✨ {game['vibe']}"
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💾 Save", callback_data=f"save_{game['name']}")],
            [InlineKeyboardButton(text="🎲 Another", callback_data="surprise")],
            [InlineKeyboardButton(text="🔙 Menu", callback_data="menu")]
        ])
        
        await call.message.delete()
        await call.message.answer_photo(
            photo=game['img'],
            caption=text,
            reply_markup=kb,
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"Surprise error: {e}")
        await call.message.edit_text("❌ Ошибка, попробуй ещё раз", reply_markup=main_menu())
    await call.answer()

@dp.callback_query(F.data == "all")
async def all_games(call):
    try:
        text = "📋 **All Games**\n\n"
        for i, game in enumerate(GAMES, 1):
            text += f"{i}. {game['name']}\n"
        await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Menu", callback_data="menu")]
        ]), parse_mode="Markdown")
    except Exception as e:
        logging.error(f"All games error: {e}")
    await call.answer()

@dp.callback_query(F.data.startswith("save_"))
async def save(call):
    try:
        name = call.data.split("_", 1)[1]
        for g in GAMES:
            if g["name"] == name:
                save_game(str(call.from_user.id), g)
                await call.answer("✅ Сохранено!", show_alert=True)
                return
        await call.answer("❌ Игра не найдена", show_alert=True)
    except Exception as e:
        logging.error(f"Save error: {e}")
        await call.answer("❌ Ошибка")

@dp.callback_query(F.data == "cabinet")
async def cabinet(call):
    try:
        games = get_games(str(call.from_user.id))
        if not games:
            await call.answer("Нет сохранённых игр!", show_alert=True)
            return
        text = "👑 **Твой кабинет**\n\n"
        for i, g in enumerate(games, 1):
            text += f"{i}. {g['name']}\n"
        await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Menu", callback_data="menu")]
        ]), parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Cabinet error: {e}")
    await call.answer()

@dp.callback_query(F.data == "menu")
async def back(call):
    try:
        await call.message.edit_text(
            "🎮 **Главное меню**\n\nВыбери действие:",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"Menu error: {e}")
    await call.answer()

async def main():
    init_db()
    logging.info("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
