from abc import ABC, abstractmethod

from aiogram import types
from aiogram.dispatcher import FSMContext


class MenuLike(ABC):

    @abstractmethod
    async def as_submenu(self, message: types.CallbackQuery, **kwargs):
        pass
