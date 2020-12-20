import pytest
from aiogram import types
from aiogram.dispatcher import FSMContext

from aiomenu.menu import MenuTemplate


class TestMenuTemplate:

    @pytest.mark.asyncio
    async def test_static_body(self):
        STATIC_TEXT = 'boo'

        async def body(message: types.Message, state: FSMContext):
            return STATIC_TEXT

        menu = MenuTemplate(body)
        text = await menu.render_body(None, None)
        assert text == STATIC_TEXT

    @pytest.mark.asyncio
    async def test_body_from_message(self):
        TEXT = 'boo'

        class MockMessage:
            def __init__(self, text):
                self.text = text

        async def body(message: types.Message, state: FSMContext):
            return message.text

        message = MockMessage(TEXT)

        menu = MenuTemplate(body)
        text = await menu.render_body(message, None)
        assert text == TEXT

    @pytest.mark.asyncio
    async def test_body_from_state(self):
        STATE = {"bar": "foo"}

        class MockState:
            def __init__(self, data):
                self.data = data

            async def get_data(self):
                return self.data

        async def body(message: types.Message, state: FSMContext):
            return await state.get_data()

        state = MockState(STATE)

        menu = MenuTemplate(body)
        text = await menu.render_body(None, state)
        assert text == STATE

