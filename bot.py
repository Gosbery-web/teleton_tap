import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

BOT_TOKEN = "8503589283:AAHlMBBvWWt6iRoAwKbMGbhF2vnSdOQSOvk"

# URL игры
WEBAPP_URL = "https://keen-cobbler-b980ba.netlify.app/index.html"

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🎮 Играть",
                    web_app=WebAppInfo(
                        url=f"{WEBAPP_URL}?uid={message.from_user.id}"
                    )
                )
            ]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "Добро пожаловать в TeleTon Tap Factory!\nЖми кнопку «Играть» 👇",
        reply_markup=kb
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
