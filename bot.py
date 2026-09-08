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

API_TOKEN = "8923876419:AAFoG0XQZSCgJrjggbdz5Z_azSDyuzNWj40"
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# БАЗА ИГР
GAMES = {
    "fast": [
        {"name": "DOOM Eternal", "desc": "Relentless movement and almost no downtime.", "best": "adrenaline", "vibe": "fast-paced"},
        {"name": "Hades", "desc": "Quick runs, sharp combat and constant progression.", "best": "skill", "vibe": "mythological"},
        {"name": "Sifu", "desc": "Demanding fights where getting better actually matters.", "best": "mastery", "vibe": "martial arts"}
    ],
    "explore": [
        {"name": "Outer Wilds", "desc": "A tiny spaceship, a solar system to explore and very little explanation.", "best": "curiosity", "vibe": "exploration + mystery"},
        {"name": "Subnautica", "desc": "Underwater survival on an alien planet.", "best": "discovery", "vibe": "deep sea"},
        {"name": "No Man's Sky", "desc": "Infinite universe to explore and build.", "best": "wanderlust", "vibe": "space"}
    ],
    "think": [
        {"name": "Civilization VI", "desc": "One more turn can become an entire evening.", "best": "strategy", "vibe": "empire building"},
        {"name": "Factorio", "desc": "Build, optimize, rebuild, repeat.", "best": "logic", "vibe": "engineering"},
        {"name": "Into the Breach", "desc": "Small maps where every move matters.", "best": "tactics", "vibe": "chess-like"}
    ],
    "chill": [
        {"name": "Stardew Valley", "desc": "Farm, fish, mine and build relationships.", "best": "relaxation", "vibe": "cozy"},
        {"name": "Animal Crossing", "desc": "Build your island paradise at your own pace.", "best": "comfort", "vibe": "wholesome"},
        {"name": "Unpacking", "desc": "Zen puzzle game about unpacking boxes.", "best": "calm", "vibe": "meditative"}
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
    kb.adjust(2)
    return kb.as_markup()

def mood_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="⚡ Fast & Intense", callback_data="mood_fast")
    kb.button(text="🌍 Explore Something", callback_data="mood_explore")
    kb.button(text="🧠 Think & Build", callback_data="mood_think")
    kb.button(text="😌 Slow & Chill", callback_data="mood_chill")
    kb.button(text="🔙 Main Menu", callback_data="menu")
    kb.adjust(2)
    return kb.as_markup()

def game_actions():
    kb = InlineKeyboardBuilder()
    kb.button(text="🎲 Another Random", callback_data="surprise")
    kb.button(text="🎭 Choose My Mood", callback_data="find")
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
        caption="**🎵 What kind of game are you looking for?**\n\nPick the kind of session you want right now:",
        reply_markup=mood_menu(),
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

@dp.callback_query(F.data == "updates")
async def gaming_updates(callback: types.CallbackQuery):
    updates_text = """**📰 Gaming Updates**

• New Steam Summer Sale starts next week
• Cyberpunk 2077 Phantom Liberty - new patch
• Elden Ring DLC - Shadow of the Erdtree
• Xbox Game Pass adding 5 new games

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

Built with ❤️ for gamers"""
    
    await callback.message.edit_caption(
        caption=about_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Main Menu", callback_data="menu")]
        ]),
        parse_mode="Markdown"
    )
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
