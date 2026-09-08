import logging
import random
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
import asyncio
import io
from aiohttp import web

API_TOKEN = "8777168852:AAF608vzJDhNZ46xfOtKAd8jnA2uHIEyeh4"
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

GAMES = {
    "fast": [
        {"name": "DOOM Eternal", "desc": "Relentless movement and almost no downtime.", "best": "adrenaline", "vibe": "fast-paced"},
        {"name": "Hades", "desc": "Quick runs, sharp combat and constant progression.", "best": "skill", "vibe": "mythological"},
        {"name": "Sifu", "desc": "Demanding fights where getting better actually matters.", "best": "mastery", "vibe": "martial arts"},
        {"name": "Ghostrunner", "desc": "One-hit-kill cyberpunk parkour action.", "best": "reflexes", "vibe": "cyberpunk"},
        {"name": "Hotline Miami", "desc": "Fast-paced top-down shooter with brutal combat.", "best": "action", "vibe": "neon noir"}
    ],
    "explore": [
        {"name": "Outer Wilds", "desc": "A tiny spaceship, a solar system to explore and very little explanation.", "best": "curiosity", "vibe": "exploration + mystery"},
        {"name": "Subnautica", "desc": "Underwater survival on an alien planet.", "best": "discovery", "vibe": "deep sea"},
        {"name": "No Man's Sky", "desc": "Infinite universe to explore and build.", "best": "wanderlust", "vibe": "space"},
        {"name": "The Legend of Zelda: Breath of the Wild", "desc": "Open-world adventure with endless exploration.", "best": "adventure", "vibe": "fantasy"},
        {"name": "Red Dead Redemption 2", "desc": "Massive open world in the Wild West.", "best": "immersion", "vibe": "western"}
    ],
    "think": [
        {"name": "Civilization VI", "desc": "One more turn can become an entire evening.", "best": "strategy", "vibe": "empire building"},
        {"name": "Factorio", "desc": "Build, optimize, rebuild, repeat.", "best": "logic", "vibe": "engineering"},
        {"name": "Into the Breach", "desc": "Small maps where every move matters.", "best": "tactics", "vibe": "chess-like"},
        {"name": "Portal 2", "desc": "Physics-based puzzles with a dark sense of humor.", "best": "problem solving", "vibe": "sci-fi puzzle"},
        {"name": "Stellaris", "desc": "Grand strategy in space with deep diplomacy and warfare.", "best": "strategy", "vibe": "space empire"}
    ],
    "chill": [
        {"name": "Stardew Valley", "desc": "Farm, fish, mine and build relationships.", "best": "relaxation", "vibe": "cozy"},
        {"name": "Animal Crossing", "desc": "Build your island paradise at your own pace.", "best": "comfort", "vibe": "wholesome"},
        {"name": "Unpacking", "desc": "Zen puzzle game about unpacking boxes.", "best": "calm", "vibe": "meditative"},
        {"name": "Journey", "desc": "A beautiful, wordless adventure through deserts and ruins.", "best": "peace", "vibe": "artistic"},
        {"name": "Spiritfarer", "desc": "A cozy management game about caring for spirits.", "best": "heartwarming", "vibe": "emotional"}
    ],
    "coop": [
        {"name": "Deep Rock Galactic", "desc": "Mining. Aliens. Dwarves. Four-player co-op.", "best": "friends", "vibe": "chaotic co-op"},
        {"name": "It Takes Two", "desc": "A two-player co-op adventure about a couple on the brink of divorce.", "best": "cooperation", "vibe": "emotional co-op"},
        {"name": "Overcooked 2", "desc": "Chaotic cooking co-op that tests your friendship.", "best": "teamwork", "vibe": "kitchen chaos"},
        {"name": "Among Us", "desc": "Social deduction in space. Who is the impostor?", "best": "deception", "vibe": "social deduction"},
        {"name": "Phasmophobia", "desc": "Four-player co-op horror game about ghost hunting.", "best": "horror", "vibe": "terrifying co-op"}
    ],
    "rpg": [
        {"name": "The Witcher 3", "desc": "A massive open-world RPG with deep storytelling.", "best": "story", "vibe": "dark fantasy"},
        {"name": "Elden Ring", "desc": "A challenging open-world RPG from the makers of Dark Souls.", "best": "challenge", "vibe": "dark fantasy"},
        {"name": "Persona 5 Royal", "desc": "Stylish JRPG with life sim and dungeon crawling.", "best": "style", "vibe": "Japanese RPG"},
        {"name": "Final Fantasy XIV", "desc": "A massive MMORPG with deep story and community.", "best": "community", "vibe": "MMORPG"},
        {"name": "Baldur's Gate 3", "desc": "Deep RPG with D&D mechanics and amazing choices.", "best": "choice", "vibe": "epic fantasy"}
    ],
    "horror": [
        {"name": "Resident Evil Village", "desc": "Survival horror with first-person perspective and creepy atmosphere.", "best": "fear", "vibe": "survival horror"},
        {"name": "Silent Hill 2", "desc": "A masterpiece of psychological horror.", "best": "atmosphere", "vibe": "psychological horror"},
        {"name": "The Medium", "desc": "A dual-reality horror game with unique mechanics.", "best": "mystery", "vibe": "supernatural"},
        {"name": "Dead Space", "desc": "Survival horror in space with dismemberment mechanics.", "best": "action horror", "vibe": "sci-fi horror"},
        {"name": "Amnesia: Rebirth", "desc": "First-person horror with intense atmosphere and dread.", "best": "tension", "vibe": "psychological terror"}
    ]
}

ALL_GAMES = []
for category in GAMES.values():
    ALL_GAMES.extend(category)

async def generate_game_image(game_name):
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://image.pollinations.ai/prompt/{game_name}%20video%20game%20cover%20art%20style?width=512&height=512"
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    return await resp.read()
    except:
        pass
    return None

def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="🎮 Find a Game", callback_data="find")
    kb.button(text="🎲 Surprise Me", callback_data="surprise")
    kb.button(text="📰 Gaming Updates", callback_data="updates")
    kb.button(text="ℹ️ About", callback_data="about")
    kb.button(text="🔥 Trending", callback_data="trending")
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
    kb.button(text="🎲 Surprise Me", callback_data="surprise")
    kb.button(text="🔙 Main Menu", callback_data="menu")
    kb.adjust(2)
    return kb.as_markup()

def game_actions():
    kb = InlineKeyboardBuilder()
    kb.button(text="🎲 Another Random", callback_data="surprise")
    kb.button(text="🎭 Choose My Mood", callback_data="find")
    kb.button(text="⭐ Save to Favorites", callback_data="favorite")
    kb.button(text="🔙 Main Menu", callback_data="menu")
    kb.adjust(2)
    return kb.as_markup()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer_photo(
        photo="https://img.icons8.com/fluency/512/video-game.png",
        caption="**🎮 Gambit Bot**\n\nChoose what you're in the mood for 👇",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "menu")
async def menu(callback: types.CallbackQuery):
    await callback.message.edit_caption(
        caption="**🎮 Main Menu**\nChoose your adventure:",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "find")
async def find_game(callback: types.CallbackQuery):
    await callback.message.edit_caption(
        caption="**🎵 What kind of game are you looking for?**\n\nForget genres for a second. Pick the kind of session you want right now:",
        reply_markup=mood_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "surprise")
async def surprise_me(callback: types.CallbackQuery):
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
            reply_markup=game_actions(),
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_caption(
            caption=caption,
            reply_markup=game_actions(),
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
            reply_markup=game_actions(),
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_caption(
            caption=caption,
            reply_markup=game_actions(),
            parse_mode="Markdown"
        )
    await callback.answer()

@dp.callback_query(F.data == "updates")
async def gaming_updates(callback: types.CallbackQuery):
    updates_text = """**📰 Gaming Updates**

• New Steam Summer Sale starts next week
• Cyberpunk 2077 Phantom Liberty - new patch
• Elden Ring DLC - Shadow of the Erdtree
• Xbox Game Pass adding 5 new games
• New game announcements from Gamescom

Stay tuned for more! 🎮"""
    
    await callback.message.edit_caption(
        caption=updates_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Main Menu", callback_data="menu")]
        ]),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "about")
async def about(callback: types.CallbackQuery):
    about_text = """**ℹ️ About Gambit Bot**

Your personal gaming companion. I help you discover games based on your mood, provide random picks, and keep you updated with gaming news.

✅ 100+ games in database
✅ AI-generated covers
✅ Updated daily
✅ 100% free
✅ New categories: Co-op, RPG, Horror

Built with ❤️ for gamers"""
    
    await callback.message.edit_caption(
        caption=about_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Main Menu", callback_data="menu")]
        ]),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "trending")
async def trending(callback: types.CallbackQuery):
    trending_text = """**🔥 Trending Games This Week**

1. 🥇 Cyberpunk 2077 - Phantom Liberty
2. 🥈 Elden Ring - Shadow of the Erdtree
3. 🥉 Grand Theft Auto VI (Trailer)
4. Baldur's Gate 3 - New Patch
5. Call of Duty - Modern Warfare III

Check them out!"""
    
    await callback.message.edit_caption(
        caption=trending_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Main Menu", callback_data="menu")]
        ]),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "help")
async def help_command(callback: types.CallbackQuery):
    help_text = """**💬 How to use Gambit Bot**

1️⃣ Click **"Find a Game"** to search by mood
2️⃣ Click **"Surprise Me"** for a random game
3️⃣ Click **"Gaming Updates"** for latest news
4️⃣ Click **"Trending"** for popular games
5️⃣ Click **"About"** for more info

All games come with AI-generated covers!
Enjoy! 🎮"""
    
    await callback.message.edit_caption(
        caption=help_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Main Menu", callback_data="menu")]
        ]),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "favorite")
async def favorite(callback: types.CallbackQuery):
    await callback.answer("⭐ Saved to favorites! (Coming soon)", show_alert=True)

async def health(request):
    return web.Response(text="OK")

async def main():
    asyncio.create_task(dp.start_polling(bot))
    app = web.Application()
    app.router.add_get('/', health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
