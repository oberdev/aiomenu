from typing import Callable, Awaitable, Union

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State

from aiomenu.keyboard import Keyboard, ButtonTemplateRowGenerator
from aiomenu.menulike import MenuLike

SimpleTextOrTextCallback = Union[Callable[[types.Message, FSMContext], Awaitable[str]], str]
SimpleBoolOrBoolCallback = Union[Callable[[types.Message, FSMContext], Awaitable[bool]], bool]
SimpleAiogramHandler = Callable[[types.Message, FSMContext], None]


class MenuTemplate(MenuLike):

    def __init__(self, body: SimpleTextOrTextCallback,
                 dp: Dispatcher, state: State = None):
        self._keyboard: Keyboard = Keyboard()
        self.body = body
        self.dp = dp
        self.state = state

    async def render_body(self, message: types.Message, **kwargs):
        return await self.body(message, **kwargs)

    async def _get_menu_info(self, message: types.Message, **kwargs):
        kwargs.pop('raw_state', None)
        text = await self.render_body(message, **kwargs)
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=await self._keyboard.render(message, **kwargs))
        return text, keyboard

    async def as_submenu(self, call: types.CallbackQuery, **kwargs):
        message = call.message
        print(call)
        text, keyboard = await self._get_menu_info(message, **kwargs)
        print(text)
        print(keyboard)
        if self.state:
            await self.state.set()
        return await message.edit_text(text, reply_markup=keyboard)

    async def as_answer(self, message: types.Message, **kwargs):
        text, keyboard = await self._get_menu_info(message, **kwargs)
        print(text)
        print(keyboard)
        if self.state:
            await self.state.set()
        return await message.answer(text, reply_markup=keyboard)

    # base row creators

    def manual_row(self, creator: ButtonTemplateRowGenerator):
        self._keyboard.add_creator(creator)

    def manual(self, button, hide: SimpleBoolOrBoolCallback = None, last_row=False):
        if hide:

            async def entry(message: types.Message, state: FSMContext):
                if await hide(message, state):
                    return
                return await button(message, state) if callable(button) else button

            self._keyboard.add(last_row, entry)

        else:
            self._keyboard.add(last_row, button)

    # feature row creators

    def url(self, text: SimpleTextOrTextCallback, url: SimpleTextOrTextCallback,
            hide: SimpleBoolOrBoolCallback = None, last_row=False):

        async def button(message: types.Message, state: FSMContext):
            return types.InlineKeyboardButton(await text(message, state) if callable(text) else text,
                                              url=await url(message, state) if callable(url) else url)

        self.manual(button, last_row=last_row, hide=hide)

    def interact(self, text: SimpleTextOrTextCallback, do: SimpleAiogramHandler, callback_data: str, *filters,
                 hide: SimpleBoolOrBoolCallback = None, last_row=False):

        self.dp.register_callback_query_handler(do, *filters, state=self.state)
        self.manual(types.InlineKeyboardButton(text=text, callback_data=callback_data),
                    last_row=last_row, hide=hide)

    def submenu(self, text: SimpleTextOrTextCallback, submenu: MenuLike, callback_data: str,
                hide: SimpleBoolOrBoolCallback = None, last_row=False):

        self.dp.register_callback_query_handler(submenu.as_submenu, state=self.state)
        self.manual(types.InlineKeyboardButton(text=text, callback_data=callback_data),
                    last_row=last_row, hide=hide)