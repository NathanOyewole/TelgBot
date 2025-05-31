#!/usr/bin/env python
# -*- coding: utf-8 -*-


class InvalidColor(Exception):
    """ Custom Exception for invalid colors. """
    def __init__(self, message: str):
        super(Exception, self).__init__(message)
        self.message: str = message

    def __str__(self) -> str:
        return self.message


class InvalidHexColor(Exception):
    """ Custom Exception for invalid hex colors. """
    def __init__(self, message: str):
        super(Exception, self).__init__(message)
        self.message: str = message

    def __str__(self) -> str:
        return self.message


class InvalidStyle(Exception):
    """ Custom Exception for invalid style. """
    def __init__(self, message: str):
        super(Exception, self).__init__(message)
        self.message: str = message

    def __str__(self) -> str:
        return self.message
