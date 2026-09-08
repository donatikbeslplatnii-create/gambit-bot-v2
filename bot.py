import logging
import random
import aiohttp
import sqlite3
import hashlib
import json
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
import asyncio
import io
from aiohttp import web

API_TOKEN = "8870829356:AAF213sRQFgdwqVlBCsuqGTlYbvrqizihMY"
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ============================================
# БАЗА ДАННЫХ
# ============================================
def init_db():
    conn = sqlite3.connect('gambit_users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, username TEXT, saved_games TEXT, created_at TIMESTAMP)''')
    conn.commit()
    conn.close()

def save_game_to_db(user_id, username, game_name, game_data):
    conn = sqlite3.connect('gambit_users.db')
    c = conn.cursor()
    
    c.execute("SELECT saved_games FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()
    
    if result:
        games = json.loads(result[0]) if result[0] else []
        if game_name not in [g['name'] for g in games]:
            games.append(game_data)
            c.execute("UPDATE users SET saved_games=? WHERE user_id=?", (json.dumps(games), user_id))
    else:
        c.execute("INSERT INTO users (user_id, username, saved_games, created_at) VALUES (?, ?, ?, ?)",
                 (user_id, username, json.dumps([game_data]), datetime.now()))
    
    conn.commit()
    conn.close()
    return True

def get_user_games(user_id):
    conn = sqlite3.connect('gambit_users.db')
    c = conn.cursor()
    c.execute("SELECT saved_games FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()
    conn.close()
    
    if result and result[0]:
        return json.loads(result[0])
    return []

# ============================================
# ИГРЫ
# ============================================
GAMES = {
    "fast": [
        {"name": "DOOM Eternal", "desc": "Relentless movement and almost no downtime.", "best": "adrenaline", "vibe": "fast-paced"},
        {"name": "Hades", "desc": "Quick runs, sharp combat and constant progression.", "best": "skill", "vibe": "mythological"},
        {"name": "Sifu", "desc": "Demanding fights where getting better actually matters.", "best": "mastery", "vibe": "martial arts"},
        {"name": "Ghostrunner", "desc": "One-hit-kill cyberpunk parkour action.", "best": "reflexes", "vibe": "cyberpunk"},
        {"name": "Hotline Miami", "desc": "Fast-paced top-down shooter with brutal combat.", "best": "action", "vibe": "neon noir"},
        {"name": "ULTRAKILL", "desc": "Ultra-fast retro FPS with style mechanics.", "best": "speed", "vibe": "chaotic"},
        {"name": "Titanfall 2", "desc": "Fast-paced shooter with wall-running and giant mechs.", "best": "movement", "vibe": "sci-fi action"},
        {"name": "Metal Gear Rising: Revengeance", "desc": "Over-the-top cyber ninja action with metal soundtrack.", "best": "style", "vibe": "cyber samurai"}
    ],
    "explore": [
        {"name": "Outer Wilds", "desc": "A tiny spaceship, a solar system to explore and very little explanation.", "best": "curiosity", "vibe": "exploration + mystery"},
        {"name": "Subnautica", "desc": "Underwater survival on an alien planet.", "best": "discovery", "vibe": "deep sea"},
        {"name": "No Man's Sky", "desc": "Infinite universe to explore and build.", "best": "wanderlust", "vibe": "space"},
        {"name": "The Legend of Zelda: Breath of the Wild", "desc": "Open-world adventure with endless exploration.", "best": "adventure", "vibe": "fantasy"},
        {"name": "Red Dead Redemption 2", "desc": "Massive open world in the Wild West.", "best": "immersion", "vibe": "western"},
        {"name": "Elden Ring", "desc": "A challenging open-world RPG from the makers of Dark Souls.", "best": "challenge", "vibe": "dark fantasy"},
        {"name": "Skyrim", "desc": "The legendary open-world RPG that defined a generation.", "best": "freedom", "vibe": "epic fantasy"},
        {"name": "Horizon Zero Dawn", "desc": "Open-world adventure with robot dinosaurs and rich lore.", "best": "exploration", "vibe": "post-apocalyptic"}
    ],
    "think": [
        {"name": "Civilization VI", "desc": "One more turn can become an entire evening.", "best": "strategy", "vibe": "empire building"},
        {"name": "Factorio", "desc": "Build, optimize, rebuild, repeat.", "best": "logic", "vibe": "engineering"},
        {"name": "Into the Breach", "desc": "Small maps where every move matters.", "best": "tactics", "vibe": "chess-like"},
        {"name": "Portal 2", "desc": "Physics-based puzzles with a dark sense of humor.", "best": "problem solving", "vibe": "sci-fi puzzle"},
        {"name": "Stellaris", "desc": "Grand strategy in space with deep diplomacy and warfare.", "best": "strategy", "vibe": "space empire"},
        {"name": "Baba Is You", "desc": "A puzzle game where you change the rules by pushing words.", "best": "creativity", "vibe": "mind-bending"},
        {"name": "Frostpunk", "desc": "Survival strategy in a frozen post-apocalyptic world.", "best": "management", "vibe": "dark survival"},
        {"name": "Kerbal Space Program", "desc": "Build your own rockets and explore the solar system.", "best": "engineering", "vibe": "space exploration"}
    ],
    "chill": [
        {"name": "Stardew Valley", "desc": "Farm, fish, mine and build relationships.", "best": "relaxation", "vibe": "cozy"},
        {"name": "Animal Crossing", "desc": "Build your island paradise at your own pace.", "best": "comfort", "vibe": "wholesome"},
        {"name": "Unpacking", "desc": "Zen puzzle game about unpacking boxes.", "best": "calm", "vibe": "meditative"},
        {"name": "Journey", "desc": "A beautiful, wordless adventure through deserts and ruins.", "best": "peace", "vibe": "artistic"},
        {"name": "Spiritfarer", "desc": "A cozy management game about caring for spirits.", "best": "heartwarming", "vibe": "emotional"},
        {"name": "A Short Hike", "desc": "A relaxing adventure on a mountain island.", "best": "chill", "vibe": "wholesome"},
        {"name": "Coffee Talk", "desc": "A visual novel about serving coffee and listening to stories.", "best": "story", "vibe": "cozy"},
        {"name": "Lake", "desc": "A relaxed adventure about delivering mail in a small town.", "best": "peaceful", "vibe": "slice of life"}
    ],
    "coop": [
        {"name": "Deep Rock Galactic", "desc": "Mining. Aliens. Dwarves. Four-player co-op.", "best": "friends", "vibe": "chaotic co-op"},
        {"name": "It Takes Two", "desc": "A two-player co-op adventure about a couple on the brink of divorce.", "best": "cooperation", "vibe": "emotional co-op"},
        {"name": "Overcooked 2", "desc": "Chaotic cooking co-op that tests your friendship.", "best": "teamwork", "vibe": "kitchen chaos"},
        {"name": "Among Us", "desc": "Social deduction in space. Who is the impostor?", "best": "deception", "vibe": "social deduction"},
        {"name": "Phasmophobia", "desc": "Four-player co-op horror game about ghost hunting.", "best": "horror", "vibe": "terrifying co-op"},
        {"name": "Payday 2", "desc": "Co-op heist action. Plan, execute, escape.", "best": "teamwork", "vibe": "criminal"},
        {"name": "Sea of Thieves", "desc": "Pirate co-op adventure on the high seas.", "best": "friends", "vibe": "pirate"},
        {"name": "Left 4 Dead 2", "desc": "Classic co-op zombie shooter with intense action.", "best": "teamwork", "vibe": "zombie survival"}
    ],
    "rpg": [
        {"name": "The Witcher 3", "desc": "A massive open-world RPG with deep storytelling.", "best": "story", "vibe": "dark fantasy"},
        {"name": "Elden Ring", "desc": "A challenging open-world RPG from the makers of Dark Souls.", "best": "challenge", "vibe": "dark fantasy"},
        {"name": "Persona 5 Royal", "desc": "Stylish JRPG with life sim and dungeon crawling.", "best": "style", "vibe": "Japanese RPG"},
        {"name": "Final Fantasy XIV", "desc": "A massive MMORPG with deep story and community.", "best": "community", "vibe": "MMORPG"},
        {"name": "Baldur's Gate 3", "desc": "Deep RPG with D&D mechanics and amazing choices.", "best": "choice", "vibe": "epic fantasy"},
        {"name": "Disco Elysium", "desc": "A masterpiece RPG where you play as a detective with amnesia.", "best": "writing", "vibe": "surreal"},
        {"name": "Divinity: Original Sin 2", "desc": "Turn-based tactical RPG with incredible freedom.", "best": "tactics", "vibe": "fantasy"},
        {"name": "Mass Effect Legendary Edition", "desc": "The iconic sci-fi RPG trilogy with unforgettable characters.", "best": "story", "vibe": "space opera"}
    ],
    "horror": [
        {"name": "Resident Evil Village", "desc": "Survival horror with first-person perspective and creepy atmosphere.", "best": "fear", "vibe": "survival horror"},
        {"name": "Silent Hill 2", "desc": "A masterpiece of psychological horror.", "best": "atmosphere", "vibe": "psychological horror"},
        {"name": "The Medium", "desc": "A dual-reality horror game with unique mechanics.", "best": "mystery", "vibe": "supernatural"},
        {"name": "Dead Space", "desc": "Survival horror in space with dismemberment mechanics.", "best": "action horror", "vibe": "sci-fi horror"},
        {"name": "Amnesia: Rebirth", "desc": "First-person horror with intense atmosphere and dread.", "best": "tension", "vibe": "psychological terror"},
        {"name": "Outlast", "desc": "First-person survival horror with no weapons.", "best": "fear", "vibe": "run or die"},
        {"name": "Alien Isolation", "desc": "Survival horror on a spaceship with a deadly alien.", "best": "stealth", "vibe": "sci-fi horror"},
        {"name": "Fatal Frame: Mask of the Lunar Eclipse", "desc": "Japanese horror with a camera as your weapon.", "best": "atmosphere", "vibe": "J-horror"}
    ],
    "cyberpunk": [
        {"name": "Cyberpunk 2077", "desc": "Open-world RPG in a dystopian future. Live as a mercenary in Night City.", "best": "immersion", "vibe": "neon noir"},
        {"name": "Deus Ex: Human Revolution", "desc": "Cyberpunk RPG with stealth, combat, and deep choices.", "best": "choice", "vibe": "cyber noir"},
        {"name": "System Shock 2", "desc": "A classic cyberpunk horror FPS with deep RPG elements.", "best": "atmosphere", "vibe": "sci-fi horror"},
        {"name": "Shadowrun: Hong Kong", "desc": "Turn-based RPG in a cyberpunk world with magic and technology.", "best": "story", "vibe": "cyberpunk fantasy"},
        {"name": "Observer", "desc": "A cyberpunk horror game where you play as a detective with neural implants.", "best": "atmosphere", "vibe": "dark cyberpunk"}
    ],
    "medieval": [
        {"name": "Kingdom Come: Deliverance", "desc": "Realistic medieval RPG without fantasy elements.", "best": "realism", "vibe": "historical"},
        {"name": "Mount & Blade II: Bannerlord", "desc": "Medieval sandbox with massive battles and kingdom management.", "best": "freedom", "vibe": "epic warfare"},
        {"name": "Crusader Kings 3", "desc": "Grand strategy RPG about dynasty management in the Middle Ages.", "best": "strategy", "vibe": "medieval politics"},
        {"name": "For Honor", "desc": "Medieval PvP combat with knights, vikings, and samurai.", "best": "combat", "vibe": "brutal"}
    ],
    "masterpieces": [
        {"name": "The Witcher 3", "desc": "A massive open-world RPG with deep storytelling.", "best": "story", "vibe": "dark fantasy"},
        {"name": "Elden Ring", "desc": "A challenging open-world RPG from the makers of Dark Souls.", "best": "challenge", "vibe": "dark fantasy"},
        {"name": "Red Dead Redemption 2", "desc": "Massive open world in the Wild West.", "best": "immersion", "vibe": "western"},
        {"name": "God of War", "desc": "An emotional journey through Norse mythology with brutal combat.", "best": "story", "vibe": "mythological"},
        {"name": "Grand Theft Auto V", "desc": "The ultimate open-world crime simulator with three protagonists.", "best": "freedom", "vibe": "sandbox"},
        {"name": "The Last of Us Part II", "desc": "A brutal, emotional journey through a post-apocalyptic world.", "best": "story", "vibe": "emotional"},
        {"name": "Half-Life 2", "desc": "The game that changed first-person shooters forever.", "best": "atmosphere", "vibe": "sci-fi"},
        {"name": "The Legend of Zelda: Breath of the Wild", "desc": "Open-world adventure with endless exploration.", "best": "adventure", "vibe": "fantasy"},
        {"name": "Baldur's Gate 3", "desc": "Deep RPG with D&D mechanics and amazing choices.", "best": "choice", "vibe": "epic fantasy"}
    ]
}

ALL_GAMES = []
for category in GAMES.values():
    ALL_GAMES.extend(category)

# ============================================
# ГЕНЕРАЦИЯ КАРТИНОК
# ============================================
async def generate_game_image(game_name):
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://image.pollinations.ai/prompt/{game_name}%20video%20game%20cover%20art%20style?width=512&height=512"
            async with session.get(url, timeout=15) as resp:
                if resp.status == 200:
                    return await resp.read()
    except:
        pass
    return None

# ============================================
# КЛАВИАТУРЫ
# ============================================
def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="🎮 Find a Game", callback_data="find")
    kb.button(text="🎲 Surprise Me", callback_data="surprise")
    kb.button(text="👤 My Cabinet", callback_data="cabinet")
    kb.button(text="🔥 Trending", callback_data="trending")
    kb.button(text="🏆 Hall of Fame", callback_data="halloffame")
    kb.button(text="💬 Help", callback_data="help")
    kb.adjust(2)
    return kb.as_markup()

def mood_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="⚡ Fast & Intense", callback_data="mood_fast")
    kb.button(text="🌍 Explore Something", callback_data="mood_explore")
    kb.button(text="🧠 Think & Build", callback_data="mood_think")
    kb.button(text="😌 Slow & Chill", callback_data="mood_chill")
    kb.button(text="👨‍👨‍👦 Co-op & Friends", callback_data="mood_coop")
    kb.button(text="⚔️ RPG & Story", callback_data="mood_rpg")
    kb.button(text="👻 Horror", callback_data="mood_horror")
    kb.button(text="💎 Cyberpunk", callback_data="mood_cyberpunk")
    kb.button(text="🏰 Medieval", callback_data="mood_medieval")
    kb.button(text="🌟 Masterpieces", callback_data="mood_masterpieces")
    kb.button(text="🎲 Surprise Me", callback_data="surprise")
    kb.button(text="🔙 Main Menu", callback_data="menu")
    kb.adjust(2)
    return kb.as_markup()

def game_actions(game_name):
    kb = InlineKeyboardBuilder()
    kb.button(text="🎲 Another Random", callback_data="surprise")
    kb.button(text="🎭 Choose My Mood", callback_data="find")
    kb.button(text="💾 Save to Cabinet", callback_data=f"save_{game_name}")
    kb.button(text="🔙 Main Menu", callback_data="menu")
    kb.adjust(2)
    return kb.as_markup()

# ============================================
# ОБРАБОТЧИКИ БОТА (С КАРТИНКАМИ)
# ============================================
@dp.message(Command("start"))
async def start(message: types.Message):
    init_db()
    await message.answer(
        text="**🎮 GOD GAMBIT**\n\nChoose what you're in the mood for 👇",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "menu")
async def menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        text="**🎮 Main Menu**\nChoose your adventure:",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "find")
async def find_game(callback: types.CallbackQuery):
    await callback.message.edit_text(
        text="**🎵 What kind of game are you looking for?**\n\nForget genres for a second. Pick the kind of session you want right now:",
        reply_markup=mood_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "surprise")
async def surprise_me(callback: types.CallbackQuery):
    await callback.message.edit_text(
        text="🎲 Rolling the dice...",
        reply_markup=None
    )
    await asyncio.sleep(0.5)
    
    game = random.choice(ALL_GAMES)
    image_data = await generate_game_image(game["name"])
    
    caption = f"""**🎲 RANDOM PICK**

**{game['name']}**
{game['desc']}

**Best for:** {game['best']}
**Vibe:** {game['vibe']}

Want another roll? 👇"""
    
    if image_data:
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=io.BytesIO(image_data),
            caption=caption,
            reply_markup=game_actions(game["name"]),
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            text=caption,
            reply_markup=game_actions(game["name"]),
            parse_mode="Markdown"
        )
    await callback.answer()

@dp.callback_query(F.data.startswith("mood_"))
async def show_games_by_mood(callback: types.CallbackQuery):
    mood = callback.data.split("_")[1]
    games = GAMES.get(mood, [])
    
    if not games:
        await callback.answer("No games found!")
        return
    
    await callback.message.edit_text(
        text=f"🎯 Searching for {mood} games...",
        reply_markup=None
    )
    await asyncio.sleep(0.5)
    
    game = random.choice(games)
    image_data = await generate_game_image(game["name"])
    
    caption = f"""**🎮 {game['name']}**

{game['desc']}

**Best for:** {game['best']}
**Vibe:** {game['vibe']}

Want another? Choose below 👇"""
    
    if image_data:
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=io.BytesIO(image_data),
            caption=caption,
            reply_markup=game_actions(game["name"]),
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            text=caption,
            reply_markup=game_actions(game["name"]),
            parse_mode="Markdown"
        )
    await callback.answer()

@dp.callback_query(F.data.startswith("save_"))
async def save_game(callback: types.CallbackQuery):
    game_name = callback.data.split("save_")[1]
    user_id = callback.from_user.id
    username = callback.from_user.username or callback.from_user.first_name
    
    game_data = None
    for category in GAMES.values():
        for game in category:
            if game["name"] == game_name:
                game_data = game
                break
        if game_data:
            break
    
    if game_data:
        save_game_to_db(user_id, username, game_name, game_data)
        await callback.answer("✅ Game saved to your cabinet!", show_alert=True)
    else:
        await callback.answer("❌ Game not found!", show_alert=True)

@dp.callback_query(F.data == "cabinet")
async def cabinet(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username or callback.from_user.first_name
    games = get_user_games(user_id)
    
    if not games:
        await callback.answer("❌ You have no saved games yet!", show_alert=True)
        return
    
    site_url = "https://gambit-cabinet.onrender.com"
    
    text = "**👑 YOUR GAME CABINET**\n\n"
    for i, game in enumerate(games[:10], 1):
        text += f"{i}. **{game['name']}**\n"
    
    if len(games) > 10:
        text += f"\n... and {len(games) - 10} more games!"
    
    text += f"\n\n📊 Total: {len(games)} games\n"
    text += f"🔗 Open your cabinet: [Click here]({site_url}?user_id={user_id}&username={username})"
    
    kb = InlineKeyboardBuilder()
    kb.button(text="🗑️ Clear All", callback_data="clear_cabinet")
    kb.button(text="🔙 Main Menu", callback_data="menu")
    kb.adjust(2)
    
    await callback.message.edit_text(
        text=text,
        reply_markup=kb.as_markup(),
        parse_mode="Markdown",
        disable_web_page_preview=False
    )
    await callback.answer()

@dp.callback_query(F.data == "clear_cabinet")
async def clear_cabinet(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    conn = sqlite3.connect('gambit_users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET saved_games='[]' WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
    await callback.answer("🗑️ Cabinet cleared!", show_alert=True)
    await cabinet(callback)

@dp.callback_query(F.data == "trending")
async def trending(callback: types.CallbackQuery):
    trending_text = """**🔥 TRENDING GAMES THIS WEEK**

1. 🥇 Cyberpunk 2077 - Phantom Liberty DLC
2. 🥈 Elden Ring - Shadow of the Erdtree
3. 🥉 GTA VI - New Trailer
4. Baldur's Gate 3 - New Patch
5. Call of Duty - Modern Warfare III

Based on community activity. 🔥"""
    
    await callback.message.edit_text(
        text=trending_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Main Menu", callback_data="menu")]
        ]),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "halloffame")
async def hall_of_fame(callback: types.CallbackQuery):
    fame_text = """**🏆 HALL OF FAME**

The greatest games of all time:

1. 🥇 The Witcher 3: Wild Hunt
2. 🥈 Elden Ring
3. 🥉 Red Dead Redemption 2
4. Half-Life 2
5. The Legend of Zelda: Breath of the Wild
6. Baldur's Gate 3
7. Grand Theft Auto V
8. The Last of Us
9. Disco Elysium
10. Mass Effect 2

These games defined generations. 🎮"""
    
    await callback.message.edit_text(
        text=fame_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Main Menu", callback_data="menu")]
        ]),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "help")
async def help_command(callback: types.CallbackQuery):
    help_text = """**💬 HOW TO USE GOD GAMBIT**

1️⃣ **Find a Game** — choose by mood
2️⃣ **Surprise Me** — random legendary pick
3️⃣ **My Cabinet** — view saved games
4️⃣ **Save Game** — add to your cabinet

🔥 **Your cabinet is a website** with all saved games!

**Powered by GOD IS BOT** 👑"""
    
    await callback.message.edit_text(
        text=help_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Main Menu", callback_data="menu")]
        ]),
        parse_mode="Markdown"
    )
    await callback.answer()

# ============================================
# ЗАПУСК
# ============================================
async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
