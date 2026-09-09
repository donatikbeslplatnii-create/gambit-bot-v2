import random
import aiohttp
import asyncio
import io
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram import F

API_TOKEN = "8578178174:AAHltDcOzQiyDBIyeP4MSvLLeJ8e8wH2XfY"
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ===== ИГРЫ =====
GAMES = [
    {"name": "DOOM Eternal", "desc": "Relentless movement and almost no downtime.", "best": "adrenaline", "vibe": "fast-paced"},
    {"name": "Hades", "desc": "Quick runs, sharp combat and constant progression.", "best": "skill", "vibe": "mythological"},
    {"name": "Sifu", "desc": "Demanding fights where getting better actually matters.", "best": "mastery", "vibe": "martial arts"},
    {"name": "Ghostrunner", "desc": "One-hit-kill cyberpunk parkour action.", "best": "reflexes", "vibe": "cyberpunk"},
    {"name": "Outer Wilds", "desc": "A tiny spaceship, a solar system to explore.", "best": "curiosity", "vibe": "exploration + mystery"},
    {"name": "Subnautica", "desc": "Underwater survival on an alien planet.", "best": "discovery", "vibe": "deep sea"},
    {"name": "No Man's Sky", "desc": "Infinite universe to explore and build.", "best": "wanderlust", "vibe": "space"},
    {"name": "Elden Ring", "desc": "A challenging open-world RPG.", "best": "challenge", "vibe": "dark fantasy"},
    {"name": "Stardew Valley", "desc": "Farm, fish, mine and build relationships.", "best": "relaxation", "vibe": "cozy"},
    {"name": "Animal Crossing", "desc": "Build your island paradise at your own pace.", "best": "comfort", "vibe": "wholesome"},
]

# ===== ГЕНЕРАЦИЯ КАРТИНКИ (100% РАБОЧИЙ МЕТОД) =====
async def get_image(game_name):
    try:
        async with aiohttp.ClientSession() as session:
            # Простой промпт без лишних символов
            url = f"https://image.pollinations.ai/prompt/{game_name}%20game%20cover%20art"
            async with session.get(url, timeout=15) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    print(f"Ошибка {response.status} для {game_name}")
                    return None
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

# ===== КНОПКИ =====
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 Surprise Me", callback_data="surprise")],
        [InlineKeyboardButton(text="📖 About", callback_data="about")]
    ])

# ===== ОБРАБОТЧИКИ =====
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🎮 **GOD GAMBIT**\n\nНажми на кнопку, чтобы получить игру с картинкой!",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "surprise")
async def surprise(callback: types.CallbackQuery):
    # Показываем статус
    await callback.message.edit_text("🎲 Генерирую картинку...")
    
    # Выбираем игру
    game = random.choice(GAMES)
    
    # Получаем картинку
    image_data = await get_image(game["name"])
    
    # Формируем текст
    text = f"**🎮 {game['name']}**\n\n{game['desc']}\n\n**Best for:** {game['best']}\n**Vibe:** {game['vibe']}"
    
    # Отправляем
    if image_data:
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=io.BytesIO(image_data),
            caption=text,
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            f"{text}\n\n⚠️ Картинка не загрузилась, но вот игра!",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )
    
    await callback.answer()

@dp.callback_query(F.data == "about")
async def about(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "**GOD GAMBIT**\n\nБот с картинками от нейросети!\n\nСделано с ❤️",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

# ===== ЗАПУСК =====
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
