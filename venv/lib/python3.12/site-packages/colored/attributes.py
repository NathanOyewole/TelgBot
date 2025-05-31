#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .library import Library
from .exceptions import InvalidStyle


class MetaStyle(type):
    """ Overrides AttributeError when __getattr__ called. """
    def __getattr__(cls, color):
        raise InvalidStyle(f'{InvalidStyle.__name__}: {color}')


class Style(metaclass=MetaStyle):

    ESC: str = Library.ESC
    END: str = Library.END
    STYLES: dict = Library.STYLES

    for style, code in STYLES.items():
        vars()[style] = f'{ESC}{code}{END}'
        vars()[style.upper()] = f'{ESC}{code}{END}'
