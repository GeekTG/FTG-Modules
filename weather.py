# -*- coding: utf-8 -*-

# Module author: @govnocodules + @ftgmodulesbyfl1yd

import requests

from .. import loader, utils


@loader.tds
class WeatherMod(loader.Module):
    """Weather Module"""

    strings = {"name": "Weather"}

    async def pwcmd(self, m):
        """ "Picture of weather.\n.aw <city>"""
        args = utils.get_args_raw(m).replace(" ", "%20")
        city = requests.get(
            f"https://wttr.in/{args if args is not None else ''}.png"
        ).content
        await utils.answer(m, city)

    async def awcmd(self, m):
        """ASCII-art of weather.\n.aw <city>"""
        city = utils.get_args_raw(m).replace(" ", "%20")
        r = requests.get(f"https://wttr.in/{city if city is not None else ''}?0?q?T")
        await utils.answer(m, f"<code>City: {r.text}</code>")

    async def wcmd(self, m):
        """.w <city>"""
        city = utils.get_args_raw(m).replace(" ", "%20")
        if city:
            r = requests.get("https://wttr.in/" + city + "?format=%l:+%c+%t,+%w+%m")
        else:
            r = requests.get("https://wttr.in/?format=%l:+%c+%t,+%w+%m")

        await utils.answer(m, r.text)
