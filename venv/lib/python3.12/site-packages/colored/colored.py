#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import platform
from typing import Any

from .library import Library
from .hexadecimal import Hex
from .exceptions import InvalidColor, InvalidHexColor, InvalidStyle


TTY_AWARE = True
IS_TTY = sys.stdout.isatty() and sys.stderr.isatty()

_win_vterm_mode = None


class Colored:

    def __init__(self, color: Any):
        self.color: str = str(color).lower()
        self.hex_color: str = str()
        self.hex = Hex()
        self.ESC: str = Library.ESC
        self.END: str = Library.END
        self.FOREGROUND: str = Library.FOREGROUND
        self.BACKGROUND: str = Library.BACKGROUND
        self.COLORS: dict = Library.COLORS
        self.HEX_COLORS: dict = Library.HEX_COLORS
        self.STYLES: dict = Library.STYLES

        self.enable_windows_terminal_mode()

    def attribute(self) -> str:
        """ Return an attribute. """
        self._is_style_exist()

        if not self.enabled():
            return str()

        if self.color.isdigit():
            return f'{self.ESC}{self.color}{self.END}'

        return f'{self.ESC}{self.STYLES[self.color]}{self.END}'

    def foreground(self) -> str:
        """ Returns a foreground color. """
        self._is_color_exist()

        if not self.enabled():
            return str()

        if self.color.isdigit():
            return f'{self.FOREGROUND}{self.color}{self.END}'
        elif self.color.startswith('#'):
            return f'{self.FOREGROUND}{self.hex_color}{self.END}'

        return f'{self.FOREGROUND}{self.COLORS[self.color]}{self.END}'

    def background(self) -> str:
        """ Returns a background color. """
        self._is_color_exist()

        if not self.enabled():
            return str()

        if self.color.isdigit():
            return f'{self.BACKGROUND}{self.color}{self.END}'
        elif self.color.startswith('#'):
            return f'{self.BACKGROUND}{self.hex_color}{self.END}'

        return f'{self.BACKGROUND}{self.COLORS[self.color]}{self.END}'

    def _is_color_exist(self) -> None:
        """ Checks for valid color by name or by hex style name or number,
            and raise a InvalidColor or InvalidHexColor exception if it doesn't exist. """
        if self.color.startswith('#'):
            if self.color not in self.HEX_COLORS.values():
                raise InvalidColor(f'{InvalidHexColor.__name__}: {self.color}')
            self.hex_color: str = self.hex.find(self.color)

        elif self.color not in self.COLORS.keys() and self.color not in self.COLORS.values():
            raise InvalidColor(f'{InvalidColor.__name__}: {self.color}')

    def _is_style_exist(self) -> None:
        """ Checks for valid style and raise a InvalidStyle exception
            if it doesn't exist. """
        if self.color not in self.STYLES.keys() and self.color not in self.STYLES.values():
            raise InvalidStyle(f'{InvalidStyle.__name__}: {self.color}')

    @staticmethod
    def enable_windows_terminal_mode() -> Any:
        """ Contribution by:
            Andreas Fredrik Klasson
            Magnus Heskestad
            Dimitris Papadopoulos

        Enable virtual terminal processing in Windows terminal. Does
        nothing if not on Windows. This is based on the rejected
        enhancement <https://bugs.python.org/issue29059>. """
        global _win_vterm_mode
        if _win_vterm_mode is not None:
            return _win_vterm_mode

        # Note: Cygwin should return something like 'CYGWIN_NT...'
        _win_vterm_mode = platform.system().lower() == 'windows'
        if _win_vterm_mode is False:
            return

        from ctypes import windll, wintypes, byref, c_void_p
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        INVALID_HANDLE_VALUE = c_void_p(-1).value
        STD_OUTPUT_HANDLE = wintypes.DWORD(-11)

        hStdout = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        if hStdout == INVALID_HANDLE_VALUE:
            _win_vterm_mode = False
            return

        mode = wintypes.DWORD(0)
        ok = windll.kernel32.GetConsoleMode(wintypes.HANDLE(hStdout), byref(mode))
        if not ok:
            _win_vterm_mode = False
            return

        mode = wintypes.DWORD(mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
        ok = windll.kernel32.SetConsoleMode(wintypes.HANDLE(hStdout), mode)
        if not ok:
            # Something went wrong, probably a version too old
            # to support the VT100 mode.
            # To be more certain we could check kernel32.GetLastError
            # for STATUS_INVALID_PARAMETER, but since we only enable
            # one flag we can be certain enough.
            _win_vterm_mode = False
            return

    @staticmethod
    def enabled() -> bool:
        """ Contribution by Andreas Motl. """
        # https://github.com/chalk/supports-color#info
        # Use the environment variable FORCE_COLOR=1 (level 1), FORCE_COLOR=2
        # (level 2), or FORCE_COLOR=3 (level 3) to forcefully enable color, or
        # FORCE_COLOR=0 to forcefully disable. The use of FORCE_COLOR overrides
        # all other color support checks.
        if 'FORCE_COLOR' in os.environ:
            if int(os.environ['FORCE_COLOR']) == 0:
                return False
            return True

        # https://no-color.org/
        # Check for the presence of a NO_COLOR environment variable that, when
        # present (regardless of its value), prevents the addition of ANSI
        # color.
        if 'NO_COLOR' in os.environ:
            return False

        # Also disable coloring when not printing to a TTY.
        if TTY_AWARE and not IS_TTY:
            return False

        # In all other cases, enable coloring.
        return True


def style(color: Any) -> str:
    """ Alias for Colored().attribute() """
    return Colored(color).attribute()


def fore(color: Any) -> str:
    """ Alias for Colored().foreground() """
    return Colored(color).foreground()


def back(color: Any) -> str:
    """ Alias for Colored().background() """
    return Colored(color).background()


def cprint(text: str, foreground='', background='', formatting='', reset=True, **kwargs) -> None:
    """ Looks like a patch to a built-in python print() function that allows
    to pass colored text and style, to this function. """
    styling: str = Colored(formatting).attribute()
    back_color: str = Colored(background).background()
    fore_color: str = Colored(foreground).foreground()
    terminator: str = Colored('reset').attribute() if reset else ''
    print(f"{styling}{back_color}{fore_color}{text}{terminator}",  **kwargs)


def stylize(text: str, formatting: str, reset=True) -> str:
    """ Conveniently styles your text as and resets ANSI codes at its end. """
    terminator: str = style('reset') if reset else ''
    return f'{"".join(formatting)}{text}{terminator}'


def _c0wrap(attr: str) -> str:
    """ Contribution by brrzap.
    Wrap a set of ANSI styles in C0 control codes for readline safety. """
    C0_SOH: str = '\x01'   # mark the beginning of nonprinting characters
    C0_STX: str = '\x02'   # mark the end of nonprinting characters
    return f'{C0_SOH}{"".join(attr)}{C0_STX}'


def stylize_interactive(text: str, formatting: str, reset=True) -> str:
    """ Contribution by:
        Jay Deiman
        brrzap

    stylize() variant that adds C0 control codes (SOH/STX) for readline
    safety. """
    # problem: readline includes bare ANSI codes in width calculations.
    # solution: wrap nonprinting codes in SOH/STX when necessary.
    # see: https://gitlab.com/dslackw/colored/issues/5
    terminator: str = _c0wrap(style('reset')) if reset else ''
    return f'{_c0wrap(formatting)}{text}{terminator}'


def set_tty_aware(awareness=True) -> None:
    """ Contribution by:
        Andreas Motl
        Jay Deiman

    Makes all interactions here tty aware. This means that if either
    stdout or stderr are directed to something other than a tty,
    colorization will not be added. """
    global TTY_AWARE
    TTY_AWARE = awareness
