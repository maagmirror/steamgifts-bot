import six
import configparser
import re
import os

from dotenv import load_dotenv

load_dotenv()

# Obtiene la cookie desde la variable de entorno
PHPSESSID = os.getenv("PHPSESSID")

from pyfiglet import figlet_format
from pyconfigstore import ConfigStore
from PyInquirer import (Token, ValidationError, Validator, print_json, prompt,
                        style_from_dict)
from prompt_toolkit import document

try:
    import colorama
    colorama.init()
except ImportError:
    colorama = None

try:
    from termcolor import colored
except ImportError:
    colored = None

config = configparser.ConfigParser()

style = style_from_dict({
    Token.QuestionMark: '#fac731 bold',
    Token.Answer: '#4688f1 bold',
    Token.Selected: '#0abf5b',  # default
    Token.Pointer: '#673ab7 bold',
})

def log(string, color, font="slant", figlet=False):
    if colored:
        if not figlet:
            six.print_(colored(string, color))
        else:
            six.print_(colored(figlet_format(
                string, font=font), color))
    else:
        six.print_(string)


class PointValidator(Validator):
    def validate(self, document: document.Document):
        value = document.text
        try:
            value = int(value)
        except Exception:
            raise ValidationError(message='Value should be greater than 0', cursor_position=len(document.text))

        if value <= 0:
            raise ValidationError(message='Value should be greater than 0', cursor_position=len(document.text))
        return True


def ask(type, name, message, validate=None, choices=[]):
    if os.getenv("DOCKER_ENV", "false").lower() == "true":
        if type == 'confirm':
            return {name: True}
        elif type == 'input':
            if name == 'min_points':
                return {name: '1'}
            return {name: 'default_value'}
        elif type == 'list':
            return {name: choices[0]}
    questions = [
        {
            'type': type,
            'name': name,
            'message': message,
            'validate': validate,
        },
    ]
    if choices:
        questions[0].update({
            'choices': choices,
        })
    answers = prompt(questions, style=style)
    return answers

def run():
    from main import SteamGifts as SG

    def askCookie():
        cookie = ask(type='input',
                     name='cookie',
                     message='Enter PHPSESSID cookie (Only needed to provide once):')
        config['DEFAULT']['cookie'] = cookie['cookie']

        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        return cookie['cookie']

    log("SteamGifts Bot", color="blue", figlet=True)
    log("Welcome to SteamGifts Bot!", "green")
    log("Modified by: github.com/maagmirror", "white")

    config.read('config.ini')

    # Usar cookie desde .env o config.ini
    if PHPSESSID:
        cookie = PHPSESSID
    elif config['DEFAULT'].get('cookie'):
        re_enter_cookie = ask(type='confirm',
            name='reenter',
            message='Do you want to enter a new cookie?')['reenter']
        if re_enter_cookie:
            cookie = askCookie()
        else:
            cookie = config['DEFAULT'].get('cookie')
    else:
        cookie = askCookie()

    pinned_games = ask(type='confirm',
                       name='pinned',
                       message='Should bot enter pinned games?')['pinned']

    gift_type = ask(type='list',
                 name='gift_type',
                 message='Select type:',
                 choices=[
                     'All',
                     'Wishlist',
                     'Recommended',
                     'Copies',
                     'DLC',
                     'New'
                 ])['gift_type']

    min_points = ask(type='input',
                     name='min_points',
                     message='Enter minimum points to start working (bot will try to enter giveaways until minimum value is reached):',
                     validate=PointValidator)['min_points']

    s = SG(cookie, gift_type, pinned_games, min_points)
    s.start()


if __name__ == '__main__':
    run()
