"""

    █▀▀ ▄▀█ █▄▀ █▀▀ █▀ ▀█▀ █░█░█ █ ▀▄▀
    █▄▄ █▀█ █░█ ██▄ ▄█ ░█░ ▀▄▀▄▀ █ █░█

    Copyleft 2022 t.me/cakestwix                                                            
    This program is free software; you can redistribute it and/or modify 

"""

__version__ = (1, 1, 1)

# requires: requests hentai
# scope: inline
# scope: geektg_only
# scope: geektg_min 3.1.15
# meta pic: https://seeklogo.com/images/H/hentai-haven-logo-B9D8C4B3B8-seeklogo.com.png
# meta developer: @CakesTwix

import asyncio
import logging

from hentai import Hentai, Utils
from requests.exceptions import HTTPError
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultPhoto
from aiogram.utils.markdown import hlink

from .. import loader, utils
from ..inline import GeekInlineQuery, rand

logger = logging.getLogger(__name__)

# Utils
def StringBuilder(Hentai):
    id_nh = Hentai.id
    eng_name = Hentai.title()
    link = Hentai.url
    total_pages = Hentai.num_pages
    total_favorites = Hentai.num_favorites
    tags = ""
    for tag in Hentai.tag:
        tags += f"{tag.name} "
    text = f"{hlink(eng_name, link)} [{id_nh}]\n\n"
    text += f"{tags} \n"
    text += f"❤️ {total_favorites} | 📄 {total_pages}"
    return text


def ListHentaiBuilder(Hentais):
    text = ""
    i = 1
    for Hentai in Hentais:
        id_nh = Hentai.id
        eng_name = Hentai.title()
        link = Hentai.url
        total_pages = Hentai.num_pages
        total_favorites = Hentai.num_favorites

        text += f"{i}: <a href={link}>{eng_name}</a> [{id_nh}] / "
        text += f"❤️ {total_favorites} | 📄 {total_pages} \n"
        i += 1
    return text


@loader.unrestricted
@loader.ratelimit
@loader.tds
class InlineNHentaiMod(loader.Module):
    """Hentai module 18+"""

    strings = {
        "name": "InlineNHentai",
        "no_tags": "Pls write tags :(",
        "no_tags_inline": "ℹ List tags: https://nhentai.net/tags/",
    }

    @loader.unrestricted
    @loader.ratelimit
    async def nhrandomcmd(self, message):
        """Random hentai manga"""
        await message.delete()
        hentai_info = Utils.get_random_hentai()
        text = StringBuilder(hentai_info)

        await message.client.send_file(message.chat_id, hentai_info.cover, caption=text)

    @loader.unrestricted
    @loader.ratelimit
    async def nhtagcmd(self, message):
        """Search hentai manga by tag"""
        args = utils.get_args(message)
        if args:
            hentai_info = Utils.search_by_query(args)
            text = ListHentaiBuilder(hentai_info)

            await utils.answer(message, text)
        else:
            await utils.answer(message, self.strings["no_tags"])
            await asyncio.sleep(5)
            await message.delete()

    @loader.unrestricted
    @loader.ratelimit
    async def nhidcmd(self, message):
        """Search hentai manga by id"""
        args = utils.get_args(message)
        if args[0].isdigit():
            try:
                hentai_info = Hentai(args[0])
                text = StringBuilder(hentai_info)
                await message.client.send_file(
                    message.chat_id, hentai_info.cover, caption=text
                )
            except HTTPError as e:
                await utils.answer(message, str(e))
                await asyncio.sleep(5)
                await message.delete()
        else:
            await utils.answer(message, "Pls id")
            await asyncio.sleep(5)
            await message.delete()

    # Inline
    async def nhsearch_inline_handler(self, query: GeekInlineQuery) -> None:
        """
        Search hentai manga by tag (Inline)
        @allow: all
        """
        text = query.args

        if not text:
            await query.answer(
                [
                    InlineQueryResultArticle(
                        id=1,
                        title=self.strings["no_tags"],
                        description=self.strings["no_tags_inline"],
                        input_message_content=InputTextMessageContent(
                            self.strings["no_tags_inline"], "HTML", disable_web_page_preview=True
                        ),
                        thumb_url="https://img.icons8.com/android/128/fa314a/price-tag.png",
                        thumb_width=128,
                        thumb_height=128,
                    )
                ],
                cache_time=0,
            )
            return
        
        else:
            inline_query = []
            hentais = Utils.search_by_query(text)
            for hentai in hentais:
                inline_query.append(
                InlineQueryResultPhoto(
                    id=rand(20),
                    title=hentai.title(),
                    description="Description",
                    caption=StringBuilder(hentai),
                    thumb_url=hentai.cover,  
                    photo_url=hentai.cover,
                    parse_mode="html",
                )
            )

            await query.answer(inline_query, cache_time=0)

