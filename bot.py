import logging
import random
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
import io

API_TOKEN = "8720853997:AAG0vI9JFSM2_610JyV-JdpORCAvegXyoew"  # ЗАМЕНИ НА СВОЙ ТОКЕН!
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

GAMES = {
    "fast": [
        {"name": "DOOM Eternal", "desc": "Relentless movement and almost no downtime.", "best": "adrenaline", "vibe": "fast-paced"},
        {"name": "Hades", "desc": "Quick runs, sharp combat and constant progression.", "best": "skill", "vibe": "mythological"},
    ],
    "explore": [
        {"name": "Outer Wilds", "desc": "A tiny spaceship, a solar system to explore.", "best": "curiosity", "vibe": "exploration"},
    ],
    "think": [
        {"name": "Civilization VI", "desc": "One more turn can become an entire evening.", "best": "strategy", "vibe": "empire building"},
    ],
    "chill": [
        {"name": "Stardew Valley", "desc": "Farm, fish, mine and build relationships.", "best": "relaxation", "vibe": "cozy"},
    ]
}

ALL_GAMES = []
for category in GAMES.values():
    ALL_GAMES.extend(category)

async def generate_game_image(game_name):
    async with aiohttp.ClientSession() as session:
        url = f"https://image.pollinations.ai/prompt/{game_name}%20video%20game%20cover%20art?width=512&height=512"
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.read()
    return None

def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🎮 Find a Game", callback_data="find"),
        InlineKeyboardButton("🎲 Surprise Me", callback_data="surprise"),
        InlineKeyboardButton("🔙 Main Menu", callback_data="menu")
    )
    return kb

def mood_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("⚡ Fast & Intense", callback_data="mood_fast"),
        InlineKeyboardButton("🌍 Explore Something", callback_data="mood_explore"),
        InlineKeyboardButton("🧠 Think & Build", callback_data="mood_think"),
        InlineKeyboardButton("😌 Slow & Chill", callback_data="mood_chill"),
        InlineKeyboardButton("🔙 Main Menu", callback_data="menu")
    )
    return kb

def game_actions():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🎲 Another Random", callback_data="surprise"),
        InlineKeyboardButton("🎭 Choose My Mood", callback_data="find"),
        InlineKeyboardButton("🔙 Main Menu", callback_data="menu")
    )
    return kb

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer_photo(
        photo="https://img.icons8.com/fluency/512/video-game.png",
        caption="**🎮 Gambit Bot**\n\nChoose what you're in the mood for:",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

@dp.callback_query_handler(lambda c: c.data == "menu")
async def menu(callback: types.CallbackQuery):
    await callback.message.edit_caption(
        caption="**🎮 Main Menu**",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "find")
async def find_game(callback: types.CallbackQuery):
    await callback.message.edit_caption(
        caption="**🎵 What kind of game?**",
        reply_markup=mood_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("mood_"))
async def show_games(callback: types.CallbackQuery):
    mood = callback.data.split("_")[1]
    games = GAMES.get(mood, [])
    if games:
        game = random.choice(games)
        caption = f"**🎮 {game['name']}**\n\n{game['desc']}\n\n**Best for:** {game['best']}\n**Vibe:** {game['vibe']}"
        await callback.message.edit_caption(
            caption=caption,
            reply_markup=game_actions(),
            parse_mode="Markdown"
        )
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "surprise")
async def surprise(callback: types.CallbackQuery):
    game = random.choice(ALL_GAMES)
    caption = f"**🎲 RANDOM PICK**\n\n**{game['name']}**\n{game['desc']}\n\n**Best for:** {game['best']}\n**Vibe:** {game['vibe']}"
    await callback.message.edit_caption(
        caption=caption,
        reply_markup=game_actions(),
        parse_mode="Markdown"
    )
    await callback.answer()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)