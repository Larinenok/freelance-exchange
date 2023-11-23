from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
# from rest_framework.authtoken.models import Token

import json
import os.path


class Star(models.Model):
    count = models.IntegerField()

    def __str__(self):
        return str(self.count)

    class Meta:
        verbose_name = 'Звездочки пользователя'
        verbose_name_plural = 'Звездочки пользователя'


class StarsJson():
    @staticmethod
    def default_value() -> list[dict]:
        return [{
            'username': None,
            'star': 0
        }]

    @staticmethod
    def parse(src) -> list[dict]:
        if (type(src) is dict):
            return [src]

        if (type(src) is list):
            return src

        return json.loads(src)

    @staticmethod
    def add_star(src, username: str, value: int) -> list[dict]:
        stars = StarsJson.parse(src)

        if (0 <= value and value <= 5):
            for (i, star) in enumerate(stars):
                if (star == {}):
                    stars.pop(i)
                    continue

                if (star['username'] == username):
                    star['star'] = value
                    return stars

            stars.append({
                'username': username,
                'star': value
            })
        else:
            raise Exception("Value must be 0 <= value <= 5")

        return stars


    @staticmethod
    def remove_star(src, username: str) -> list[dict]:
        stars = StarsJson.parse(src)
        r_stars = stars[::-1]

        if (len(stars) > 0):
            index = len(stars) - 1

            for star in r_stars:
                if star['username'] == username:
                    stars.pop(index)

                index -= 1

        if (len(stars) < 1):
            stars.append({})

        return stars
