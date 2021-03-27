# -*- coding: utf-8 -*-

# Module author: @GovnoCodules

import requests
from .. import loader, utils


@loader.tds
class WeatherMod(loader.Module):
    """Weather Module"""
    strings = {'name': 'Weather'}

    async def pwcmd(self, message):
        """"Кидает погоду картинкой.\nИспользование: .pw <город>; ничего."""
        args = utils.get_args_raw(message).replace(' ', '+')
        await message.edit("Узнаем погоду...")
        city = requests.get(
            f"https://wttr.in/{args if args != None else ''}.png").content
        await message.client.send_file(message.to_id, city)
        await message.delete()

    async def awcmd(self, message):
        """Кидает погоду ascii-артом.\nИспользование: .aw <город>; ничего."""
        city = utils.get_args_raw(message)
        await message.edit("Узнаем погоду...")
        r = requests.get(
            f"https://wttr.in/{city if city != None else ''}?0?q?T&lang=ru")
        await message.edit(f"<code>Город: {r.text}</code>")

    @loader.sudo
    async def wcmd(self, message):
        """.w <город>"""
        message.edit("<b>Погода by wttr.in</b>")
        city = utils.get_args(message)
        msg = []
        if city:
            await message.edit("Обрабатываем запрос...")
            for i in city:
                r = requests.get(
                    "https://wttr.in/" + i + "?format=%l:+%c+%t,+%w+%m"
                )
                msg.append(r.text)
            await message.edit("".join(msg))
        else:
            await message.edit("Обрабатываем запрос...")
            r = requests.get("https://wttr.in/?format=%l:+%c+%t,+%w+%m")
            await message.edit(r.text)