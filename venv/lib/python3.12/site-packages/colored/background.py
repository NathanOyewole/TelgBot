#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .library import Library
from .exceptions import InvalidColor


class MetaBack(type):
    """ Overrides AttributeError when __getattr__ called. """
    def __getattr__(cls, color):
        raise InvalidColor(f'{InvalidColor.__name__}: {color}')


class Back(metaclass=MetaBack):

    END: str = Library.END
    COLORS: dict = Library.COLORS
    BACKGROUND: str = Library.BACKGROUND

    for color, code in COLORS.items():
        vars()[color] = f'{BACKGROUND}{code}{END}'
        vars()[color.upper()] = f'{BACKGROUND}{code}{END}'
