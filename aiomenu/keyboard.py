import typing
from itertools import chain

from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, Message

InlineKeyboard = typing.List[typing.List[InlineKeyboardButton]]

ButtonTemplateRow = typing.List[InlineKeyboardButton]

UncreatedTemplate = typing.Callable[[Message, FSMContext], InlineKeyboardButton]
RowOfUncreatedTemplates = typing.List[UncreatedTemplate]
ButtonTemplateRowGenerator = typing.Callable[[Message, FSMContext], typing.List[ButtonTemplateRow]]
KeyboardTemplateEntry = typing.Union[RowOfUncreatedTemplates, ButtonTemplateRowGenerator]


def is_row(entry: KeyboardTemplateEntry) -> bool:
    return isinstance(entry, list)


class Keyboard:
    def __init__(self):
        self._entries: typing.List[KeyboardTemplateEntry] = []

    def add_creator(self, creator: ButtonTemplateRowGenerator):
        self._entries.append(creator)

    def add(self, last_row: bool, *buttons: RowOfUncreatedTemplates):
        if last_row and is_row(self._entries[-1]):
            self._entries[-1] += buttons
            return

        self._entries.append([*buttons])

    async def render(self, message: Message, **kwargs):
        list_of_row_lists = [await entry_to_row(entry, message, **kwargs) for entry in self._entries]
        return list_of_row_lists


async def entry_to_row(entry: KeyboardTemplateEntry, message: Message, **kwargs):
    if is_row(entry):
        buttons_in_row = [await button(message, **kwargs) if callable(button) else button for button in entry]
        return buttons_in_row

    return await entry(message, **kwargs)


def remove_empty_buttons(keyboard: InlineKeyboard):
    for row in keyboard:
        for key, button in enumerate(row):
            if button is None:
                row.pop(key)
    return keyboard
