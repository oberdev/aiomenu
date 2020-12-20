import logging

from aiogram import Bot, Dispatcher, executor, types

# Configure logging
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.callback_data import CallbackData

from aiomenu.menu import MenuTemplate
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)


async def start(message: types.Message, state: FSMContext):
    return 'Hello'


async def check(message: types.Message, state: FSMContext):
    return True


async def action(call: types.CallbackQuery, state: FSMContext):
    return 'popka'


callback_data = CallbackData('action', 'do')


class TestState(StatesGroup):
    one = State()
    two = State()


# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
menu = MenuTemplate(action, dp=dp)
main_menu = MenuTemplate(start, dp=dp)
main_menu.submenu('Нажать', menu, callback_data.new(do='sex'))
menu.submenu('Вернуться', main_menu, callback_data.new(do='back'))


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message, state):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await main_menu.as_answer(message, state=state)


@dp.message_handler()
async def echo(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)

    await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
