from enum import Enum
from json import load
from os.path import join
from sys import platform


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
    gets a langauge string from a file.
    :param path: a file path separated by .
    :return: the language string
    """
    result = _language
    for part in path.split('.'):
        result = result[part]
    return result


def get_command_key():
    return 'Command' if 'darwin' in platform else 'Control'


set_language(Language.KOREAN_KOREA)
