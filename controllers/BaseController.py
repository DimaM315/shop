from flask import request, make_response, url_for, redirect, session, render_template, abort
import models
import random


def valid_data_reg(args):
    for i in args:
        if len(i) < 3:
            return False
    return True


def find_trigger_char(text_data):
    cursor = 0
    digital_char = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')

    while cursor < len(text_data)-4:
        for i in (1, 2, 3, 4):
            if text_data[cursor+i-1] == text_data[cursor+i]:
                if i == 4:
                    return cursor+1
                continue
            break
        cursor += 1
    return False


def slugify(title):
    # title has checked on len
    assert len(title) >= 6 
    pattern = r'[^\w+]'
    return re.sub(pattern, '-', title)


def is_auth():
    login = session.get('login', False)
    password = session.get('password', False)
    if not login or not password:
        return False
    u = User.select().where(User.login==login).first()
    return u.password == password


class BaseController:
    def __init__(self):
        self.request = request

    def call(self, *args, **kwargs):
        try:
            return self._call(*args, **kwargs)
        except Exception as ex:
            return make_response(str(ex), 500)

    def __call(self, *args, **kwargs):
        raise NotImplementedError('_call')



