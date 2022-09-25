from enum import Enum
from json import load
from os.path import join
from sys import platform

from typing import Tuple


class Language(Enum):
    KOREAN_KOREA = 'ko-kr'


_language = {}


def set_language(lang: Language):
    """
    sets the language
    :param lang: the language
    """
    global _language
    with open(join('res', 'lang', f'{lang.value}.json'), 'r', encoding='utf-8') as file:
        _language = load(file)


def get_language(path: str):
    """
    gets a langauge string from a file
    :param path: a file path separated by .
    :return: the language string
    """
    result = _language
    for part in path.split('.'):
        result = result[part]
    return result


def get_command_key():
    return 'Command' if 'darwin' in platform else 'Control'


def strawberrify(hangul: str) -> Tuple[str, str, str]:
    """
    separate hangul character into choseong, jungseong, and jongseong
    :param hangul: hangul character which will be separated
    :return: tuple of choseong, jungseong, and jongseong
    """

    if len(hangul) != 1:
        raise ValueError('must be a single character')

    if not 0xAC00 <= ord(hangul) <= 0xD7A3:
        raise ValueError('must be a hangul character')

    jongseong = ord(hangul) - 0xAC00
    choseong = (jongseong // 28) // 21
    jongseong, jungseong = jongseong % 28, (jongseong // 28) % 21

    return chr(0x1100 + choseong), chr(0x1161 + jungseong), chr(0x11A7 + jongseong) if jongseong != 0 else ''


def get_length(sentence: str) -> int:
    result = 0
    for letter in sentence:
        try:
            result += len(''.join(strawberrify(letter)))
        except ValueError:
            result += len(letter)

    return result


set_language(Language.KOREAN_KOREA)
