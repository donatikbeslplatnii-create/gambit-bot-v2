import random
import sqlite3
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram import F
import asyncio

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

# ИГРЫ С ССЫЛКАМИ НА КАРТИНКИ
GAMES = [
    {"name": "DOOM Eternal", "desc": "Fast shooter", "best": "action", "vibe": "fast", "img": "https://i.ibb.co/sFpXhX0/doom.jpg"},
    {"name": "Hades", "desc": "Roguelike action", "best": "skill", "vibe": "myth", "img": "https://i.ibb.co/hLbKq8J/hades.jpg"},
    {"name": "Outer Wilds", "desc": "Space exploration", "best": "mystery", "vibe": "space", "img": "https://i.ibb.co/rvZ2J4P/outer.jpg"},
    {"name": "Stardew Valley", "desc": "Farming RPG", "best": "relax", "vibe": "cozy", "img": "https://i.ibb.co/Fh9sVgJ/stardew.jpg"},
    {"name": "Elden Ring", "desc": "Dark fantasy RPG", "best": "challenge", "vibe": "dark", "img": "https://i.ibb.co/G9pWqGn/elden.jpg"},
    {"name": "Subnautica", "desc": "Underwater survival", "best": "explore", "vibe": "deep", "img": "https://i.ibb.co/YkRZxJZ/subnautica.jpg"},
    {"name": "The Witcher 3", "desc": "Open-world RPG", "best": "story", "vibe": "fantasy", "img": "https://i.ibb.co/7Xx8zVK/witcher.jpg"},
    {"name": "Cyberpunk 2077", "desc": "Sci-fi RPG", "best": "immersion", "vibe": "neon", "img": "https://i.ibb.co/DtX8hCv/cyberpunk.jpg"},
]

def menu():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 Surprise Me", callback_data="surprise")],
        [InlineKeyboardButton(text="👤 Cabinet", callback_data="cabinet")]
    ])
    return kb

@dp.message(Command("start"))
async def start(msg):
    init_db()
    await msg.answer("🎮 **GOD GAMBIT**\nНажми Surprise!", reply_markup=menu(), parse_mode="Markdown")

@dp.callback_query(F.data == "surprise")
async def surprise(call):
    game = random.choice(GAMES)
    text = f"**🎮 {game['name']}**\n{game['desc']}\n\nBest: {game['best']}\nVibe: {game['vibe']}"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💾 Save", callback_data=f"save_{game['name']}")],
        [InlineKeyboardButton(text="🔍 More Info", url=game['img'])],
        [InlineKeyboardButton(text="🔙 Menu", callback_data="menu")]
    ])
    await call.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(F.data.startswith("save_"))
async def save(call):
    name = call.data.split("_")[1]
    for g in GAMES:
        if g["name"] == name:
            save_game(str(call.from_user.id), g)
            await call.answer("✅ Saved!", show_alert=True)
            return
    await call.answer("❌ Error")

@dp.callback_query(F.data == "cabinet")
async def cabinet(call):
    games = get_games(str(call.from_user.id))
    if not games:
        await call.answer("No games!", show_alert=True)
        return
    text = "👑 **Your Cabinet**\n\n"
    for i, g in enumerate(games, 1):
        text += f"{i}. {g['name']}\n"
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Menu", callback_data="menu")]
    ]), parse_mode="Markdown")
    await call.answer()

@dp.callback_query(F.data == "menu")
async def menu_cmd(call):
    await call.message.edit_text("🎮 **Menu**", reply_markup=menu(), parse_mode="Markdown")
    await call.answer()

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
