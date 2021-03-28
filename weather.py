# -*- coding: utf-8 -*-

# Module author: @GovnoCodules

import requests
from .. import loader, utils


@loader.tds
class WeatherMod(loader.Module):
    """Weather Module"""
    strings = {'name': 'Weather'}

    async def pwcmd(self, message):
        """"Picture of weather.\n.aw <city>"""
        args = utils.get_args_raw(message).replace(' ', '+')
        city = requests.get(
            f"https://wttr.in/{args if args != None else ''}.png").content
        await message.client.send_file(message.to_id, city)
        await message.delete()

    async def awcmd(self, message):
        """ASCII-art of weather.\n.aw <city>"""
        city = utils.get_args_raw(message)
        r = requests.get(
            f"https://wttr.in/{city if city != None else ''}?0?q?T&lang=ru")
        await message.edit(f"<code>Город: {r.text}</code>")

    @loader.sudo
    async def wcmd(self, message):
        """.w <city>"""
        city = utils.get_args(message)
        msg = []
        if city:
            for i in city:
                r = requests.get(
                    "https://wttr.in/" + i + "?format=%l:+%c+%t,+%w+%m"
                )
                msg.append(r.text)
            await message.edit("".join(msg))
        else:
            r = requests.get("https://wttr.in/?format=%l:+%c+%t,+%w+%m")
            await message.edit(r.text)