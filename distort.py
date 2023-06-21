# -*- coding: utf-8 -*-

# Module author: @GovnoCodules

# requires: lottie cairosvg pillow wand

import io
import os
from random import choice, randint

from PIL import Image as IM
from telethon.tl.types import DocumentAttributeFilename
from wand.image import Image

from .. import loader, utils


@loader.tds
class DistortMod(loader.Module):
    """Stickers or photo distort"""

    strings = {
        "name": "Distort",
        "bad_input": "<b>Reply to image or stick!</b>",
        "processing": "<b>Distorting...</b>",
        "bad_input_tgs": "<b>Reply to animated sticker</b>",
    }

    async def client_ready(self, client, db):
        self.client = client

    @loader.unrestricted
    async def tgscmd(self, message):
        """Animated stickers distort"""
        reply = await message.get_reply_message()
        if not reply:
            await utils.answer(message, self.strings("bad_input_tgs", message))
            return
        if not reply.file:
            await utils.answer(message, self.strings("bad_input_tgs", message))
            return
        if not reply.file.name.endswith(".tgs"):
            await utils.answer(message, self.strings("bad_input_tgs", message))
            return
        message = await utils.answer(message, self.strings("processing", message))
        await reply.download_media("tgs.tgs")
        os.system("lottie_convert.py tgs.tgs json.json")
        with open("json.json", "r") as f:
            stick = f.read()
            f.close()

        for i in range(1, randint(6, 10)):
            stick = choice(
                [
                    stick.replace(f"[{i}]", f"[{(i + i) * 3}]"),
                    stick.replace(f".{i}", f".{i}{i}"),
                ]
            )

        with open("json.json", "w") as f:
            f.write(stick)
            f.close()
        os.system("lottie_convert.py json.json tgs.tgs")
        with open("tgs.tgs", "rb") as f:
            file = io.BytesIO(f.read())
            file.name = "tgs.tgs"
            await utils.answer(message, file)
        os.remove("tgs.tgs")
        os.remove("json.json")

    @loader.sudo
    async def distortcmd(self, message):
        """.distort <reply to photo>
        .distort im
        .distort 50
        .distort 50 im
        .distort im 50
        im => sends as photo
        50 => (from 0 to 100) percent of distortion, 0 is maximum distortion"""
        if message.is_reply:
            reply_message = await message.get_reply_message()
            data, mime = await check_media(reply_message)
            if isinstance(data, bool):
                await utils.answer(message, self.strings("bad_input", message))
                return
        else:
            await utils.answer(message, self.strings("bad_input", message))
            return
        rescale_rate = 70
        a = utils.get_args(message)
        force_file = False
        if a:
            if "im" in a:
                force_file = True
                a.remove("im")
            if len(a) > 0:
                if a[0].isdigit():
                    rescale_rate = int(a[0])
                    if rescale_rate <= 0:
                        rescale_rate = 70

        message = await utils.answer(message, self.strings("processing", message))
        file = await self.client.download_media(data, bytes)
        file, img = io.BytesIO(file), io.BytesIO()
        img.name = "img.png"
        IM.open(file).save(img, "PNG")
        media = await distort(io.BytesIO(img.getvalue()), rescale_rate)
        out, im = io.BytesIO(), IM.open(media)
        if force_file:
            mime = "png"
        out.name = f"out.{mime}"
        im.save(out, mime.upper())
        out.seek(0)

        await utils.answer(message, out)

    async def jpegdcmd(self, message):
        """JPEG style distort"""
        if message.is_reply:
            reply_message = await message.get_reply_message()
            data = await check_mediaa(reply_message)
            if isinstance(data, bool):
                await utils.answer(message, self.strings("bad_input", message))
                return
        else:
            await utils.answer(message, self.strings("bad_input", message))
            return

        message = await utils.answer(message, self.strings("processing", message))
        image = io.BytesIO()
        await self.client.download_media(data, image)
        image = IM.open(image)
        fried_io = io.BytesIO()
        fried_io.name = "image.jpeg"
        image = image.convert("RGB")
        image.save(fried_io, "JPEG", quality=0)
        fried_io.seek(0)
        await utils.answer(message, fried_io)


async def distort(file, rescale_rate):
    img = Image(file=file)
    x, y = img.size[0], img.size[1]
    popx = int(rescale_rate * (x // 100))
    popy = int(rescale_rate * (y // 100))
    img.liquid_rescale(popx, popy, delta_x=1, rigidity=0)
    img.resize(x, y)
    out = io.BytesIO()
    out.name = "output.png"
    img.save(file=out)
    return io.BytesIO(out.getvalue())


async def check_media(reply_message):
    mime = None
    if reply_message and reply_message.media:
        if reply_message.photo:
            data = reply_message.photo
            mime = "image/jpeg"
        elif reply_message.document:
            if (
                DocumentAttributeFilename(file_name="AnimatedSticker.tgs")
                in reply_message.media.document.attributes
            ):
                return False, mime
            if (
                reply_message.gif
                or reply_message.video
                or reply_message.audio
                or reply_message.voice
            ):
                return False, mime
            data = reply_message.media.document
            mime = reply_message.media.document.mime_type
            if "image/" not in mime:
                return False, mime
        else:
            return False, mime
    else:
        return False, mime

    if not data or data is None:
        return False, mime
    else:
        mime = mime.split("/")[1]
        return data, mime


async def check_mediaa(reply_message):
    if reply_message and reply_message.media:
        if reply_message.photo:
            data = reply_message.photo
        elif reply_message.document:
            if (
                DocumentAttributeFilename(file_name="AnimatedSticker.tgs")
                in reply_message.media.document.attributes
            ):
                return False
            if (
                reply_message.gif
                or reply_message.video
                or reply_message.audio
                or reply_message.voice
            ):
                return False
            data = reply_message.media.document
        else:
            return False
    else:
        return False

    if not data or data is None:
        return False
    else:
        return data
