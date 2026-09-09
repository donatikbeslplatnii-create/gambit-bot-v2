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

# ===== НОВЫЙ ТОКЕН =====
API_TOKEN = "8578178174:AAGT2dTOjdnw7RS3KqFFyUg8ncRR4f0F1aY"
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ===== БАЗА ДАННЫХ =====
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id TEXT PRIMARY KEY, games TEXT)''')
    conn.commit()
    conn.close()

def save_game(user_id, game):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT games FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    games = json.loads(row[0]) if row and row[0] else []
    if game['name'] not in [g['name'] for g in games]:
        games.append(game)
    c.execute("INSERT OR REPLACE INTO users (user_id, games) VALUES (?, ?)",
              (user_id, json.dumps(games)))
    conn.commit()
    conn.close()

def get_games(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT games FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return json.loads(row[0]) if row and row[0] else []

# ===== ВСЕ 30 ИГР =====
ALL_GAMES = [
    {"name": "DOOM Eternal", "desc": "Relentless movement and almost no downtime.", "best": "adrenaline", "vibe": "fast-paced", "category": "fast", "img": "https://i.ibb.co/4Rz4hXcz/IMG-20260909-114219-254.jpg"},
    {"name": "Hades", "desc": "Quick runs, sharp combat and constant progression.", "best": "skill", "vibe": "mythological", "category": "fast", "img": "https://i.ibb.co/4Rz4hXcz/IMG-20260909-114219-254.jpg"},
    {"name": "Sifu", "desc": "Demanding fights where getting better actually matters.", "best": "mastery", "vibe": "martial arts", "category": "fast", "img": "https://i.ibb.co/6JWYZW6w/IMG-20260909-114131-062.jpg"},
    {"name": "Ghostrunner", "desc": "One-hit-kill cyberpunk parkour action.", "best": "reflexes", "vibe": "cyberpunk", "category": "fast", "img": "https://i.ibb.co/6JWYZW6w/IMG-20260909-114131-062.jpg"},
    {"name": "Hotline Miami", "desc": "Fast-paced top-down shooter with brutal combat.", "best": "action", "vibe": "neon noir", "category": "fast", "img": "https://i.ibb.co/8nCxTQT7/IMG-20260909-114136-853.jpg"},
    {"name": "Ultrakill", "desc": "Ultra-fast retro FPS with style mechanics.", "best": "speed", "vibe": "chaotic", "category": "fast", "img": "https://i.ibb.co/8nCxTQT7/IMG-20260909-114136-853.jpg"},
    
    {"name": "Outer Wilds", "desc": "A tiny spaceship, a solar system to explore.", "best": "curiosity", "vibe": "exploration", "category": "explore", "img": "https://i.ibb.co/tMvWJx5b/IMG-20260909-114211-960.jpg"},
    {"name": "Subnautica", "desc": "Underwater survival on an alien planet.", "best": "discovery", "vibe": "deep sea", "category": "explore", "img": "https://i.ibb.co/tMvWJx5b/IMG-20260909-114211-960.jpg"},
    {"name": "No Man's Sky", "desc": "Infinite universe to explore and build.", "best": "wanderlust", "vibe": "space", "category": "explore", "img": "https://i.ibb.co/XrTVJ535/IMG-20260909-114120-460.jpg"},
    {"name": "Breath of the Wild", "desc": "Open-world adventure with endless exploration.", "best": "adventure", "vibe": "fantasy", "category": "explore", "img": "https://i.ibb.co/XrTVJ535/IMG-20260909-114120-460.jpg"},
    {"name": "Red Dead Redemption 2", "desc": "Massive open world in the Wild West.", "best": "immersion", "vibe": "western", "category": "explore", "img": "https://i.ibb.co/DPX6r3Yj/IMG-20260909-114124-682.jpg"},
    {"name": "Journey", "desc": "A beautiful, wordless adventure through deserts.", "best": "peace", "vibe": "artistic", "category": "explore", "img": "https://i.ibb.co/DPX6r3Yj/IMG-20260909-114124-682.jpg"},
    
    {"name": "Civilization VI", "desc": "One more turn can become an entire evening.", "best": "strategy", "vibe": "empire building", "category": "think", "img": "https://i.ibb.co/9mNRLv68/IMG-20260909-114152-339.jpg"},
    {"name": "Factorio", "desc": "Build, optimize, rebuild, repeat.", "best": "logic", "vibe": "engineering", "category": "think", "img": "https://i.ibb.co/9mNRLv68/IMG-20260909-114152-339.jpg"},
    {"name": "Portal 2", "desc": "Physics-based puzzles with a dark sense of humor.", "best": "problem solving", "vibe": "sci-fi puzzle", "category": "think", "img": "https://i.ibb.co/XrpYfNVH/IMG-20260909-114141-322.jpg"},
    {"name": "Into the Breach", "desc": "Small maps where every move matters.", "best": "tactics", "vibe": "chess-like", "category": "think", "img": "https://i.ibb.co/XrpYfNVH/IMG-20260909-114141-322.jpg"},
    {"name": "Stellaris", "desc": "Grand strategy in space with deep diplomacy.", "best": "strategy", "vibe": "space empire", "category": "think", "img": "https://i.ibb.co/4Rz4hXcz/IMG-20260909-114219-254.jpg"},
    {"name": "Frostpunk", "desc": "Survival strategy in a frozen world.", "best": "management", "vibe": "dark survival", "category": "think", "img": "https://i.ibb.co/4Rz4hXcz/IMG-20260909-114219-254.jpg"},
    
    {"name": "Stardew Valley", "desc": "Farm, fish, mine and build relationships.", "best": "relaxation", "vibe": "cozy", "category": "chill", "img": "https://i.ibb.co/XrpYfNVH/IMG-20260909-114141-322.jpg"},
    {"name": "Animal Crossing", "desc": "Build your island paradise at your own pace.", "best": "comfort", "vibe": "wholesome", "category": "chill", "img": "https://i.ibb.co/XrpYfNVH/IMG-20260909-114141-322.jpg"},
    {"name": "Unpacking", "desc": "Zen puzzle game about unpacking boxes.", "best": "calm", "vibe": "meditative", "category": "chill", "img": "https://i.ibb.co/6JWYZW6w/IMG-20260909-114131-062.jpg"},
    {"name": "Spiritfarer", "desc": "A cozy management game about caring for spirits.", "best": "heartwarming", "vibe": "emotional", "category": "chill", "img": "https://i.ibb.co/6JWYZW6w/IMG-20260909-114131-062.jpg"},
    {"name": "Coffee Talk", "desc": "A visual novel about serving coffee and listening.", "best": "story", "vibe": "cozy", "category": "chill", "img": "https://i.ibb.co/8nCxTQT7/IMG-20260909-114136-853.jpg"},
    {"name": "Lake", "desc": "A relaxed adventure about delivering mail.", "best": "peaceful", "vibe": "slice of life", "category": "chill", "img": "https://i.ibb.co/8nCxTQT7/IMG-20260909-114136-853.jpg"},
    
    {"name": "The Witcher 3", "desc": "A massive open-world RPG with deep storytelling.", "best": "story", "vibe": "dark fantasy", "category": "rpg", "img": "https://i.ibb.co/tMvWJx5b/IMG-20260909-114211-960.jpg"},
    {"name": "Elden Ring", "desc": "A challenging open-world RPG from Dark Souls makers.", "best": "challenge", "vibe": "dark fantasy", "category": "rpg", "img": "https://i.ibb.co/tMvWJx5b/IMG-20260909-114211-960.jpg"},
    {"name": "Baldur's Gate 3", "desc": "Deep RPG with D&D mechanics and amazing choices.", "best": "choice", "vibe": "epic fantasy", "category": "rpg", "img": "https://i.ibb.co/9mNRLv68/IMG-20260909-114152-339.jpg"},
    {"name": "Disco Elysium", "desc": "A masterpiece RPG where you play as a detective.", "best": "writing", "vibe": "surreal", "category": "rpg", "img": "https://i.ibb.co/9mNRLv68/IMG-20260909-114152-339.jpg"},
    {"name": "Mass Effect Legendary", "desc": "The iconic sci-fi RPG trilogy.", "best": "story", "vibe": "space opera", "category": "rpg", "img": "https://i.ibb.co/DPX6r3Yj/IMG-20260909-114124-682.jpg"},
    {"name": "Dragon Age Inquisition", "desc": "Epic fantasy RPG with deep lore.", "best": "story", "vibe": "fantasy", "category": "rpg", "img": "https://i.ibb.co/DPX6r3Yj/IMG-20260909-114124-682.jpg"},
]

# ===== КНОПКИ =====
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚡ Fast & Intense", callback_data="cat_fast")],
        [InlineKeyboardButton(text="🌍 Explore", callback_data="cat_explore")],
        [InlineKeyboardButton(text="🧠 Think & Build", callback_data="cat_think")],
        [InlineKeyboardButton(text="😌 Chill", callback_data="cat_chill")],
        [InlineKeyboardButton(text="⚔️ RPG", callback_data="cat_rpg")],
        [InlineKeyboardButton(text="🎲 Surprise Me", callback_data="surprise")],
        [InlineKeyboardButton(text="👤 My Cabinet", callback_data="cabinet")]
    ])

def game_buttons(name):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💾 Save", callback_data=f"save_{name}")],
        [InlineKeyboardButton(text="🎲 Another", callback_data="surprise")],
        [InlineKeyboardButton(text="🔙 Menu", callback_data="menu")]
    ])

# ===== КОМАНДЫ =====
@dp.message(Command("start"))
async def start(msg):
    init_db()
    await msg.answer_photo(
        photo="https://i.ibb.co/4Rz4hXcz/IMG-20260909-114219-254.jpg",
        caption="🎮 **GOD GAMBIT**\n\nChoose your mood or try your luck!",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "menu")
async def back(call):
    await call.message.delete()
    await call.message.answer_photo(
        photo="https://i.ibb.co/4Rz4hXcz/IMG-20260909-114219-254.jpg",
        caption="🎮 **Main Menu**\nChoose your mood or try your luck!",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )
    await call.answer()

@dp.callback_query(F.data == "surprise")
async def surprise(call):
    game = random.choice(ALL_GAMES)
    text = f"**🎲 {game['name']}**\n{game['desc']}\n\nBest: {game['best']}\nVibe: {game['vibe']}"
    await call.message.delete()
    await call.message.answer_photo(
        photo=game['img'],
        caption=text,
        reply_markup=game_buttons(game['name']),
        parse_mode="Markdown"
    )
    await call.answer()

@dp.callback_query(F.data.startswith("cat_"))
async def category(call):
    cat = call.data.split("_")[1]
    games = [g for g in ALL_GAMES if g.get("category") == cat]
    if not games:
        await call.answer("No games in this category", show_alert=True)
        return
    game = random.choice(games)
    text = f"**🎮 {game['name']}**\n{game['desc']}\n\nBest: {game['best']}\nVibe: {game['vibe']}"
    await call.message.delete()
    await call.message.answer_photo(
        photo=game['img'],
        caption=text,
        reply_markup=game_buttons(game['name']),
        parse_mode="Markdown"
    )
    await call.answer()

@dp.callback_query(F.data.startswith("save_"))
async def save(call):
    name = call.data.split("_", 1)[1]
    game = next((g for g in ALL_GAMES if g["name"] == name), None)
    if game:
        save_game(str(call.from_user.id), game)
        await call.answer("✅ Game saved!", show_alert=True)
    else:
        await call.answer("❌ Not found")

@dp.callback_query(F.data == "cabinet")
async def cabinet(call):
    games = get_games(str(call.from_user.id))
    if not games:
        await call.answer("No games saved!", show_alert=True)
        return
    text = "👑 **Your Cabinet**\n\n"
    for i, g in enumerate(games, 1):
        text += f"{i}. {g['name']}\n"
    text += f"\n🔗 View your cabinet: https://gambit-cabinet.onrender.com?user_id={call.from_user.id}&username={call.from_user.username or 'Unknown'}"
    await call.message.delete()
    await call.message.answer_photo(
        photo="https://i.ibb.co/4Rz4hXcz/IMG-20260909-114219-254.jpg",
        caption=text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌐 Open Website", url=f"https://gambit-cabinet.onrender.com?user_id={call.from_user.id}&username={call.from_user.username or 'Unknown'}")],
            [InlineKeyboardButton(text="🔙 Menu", callback_data="menu")]
        ]),
        parse_mode="Markdown"
    )
    await call.answer()

async def main():
    init_db()
    logging.info("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
