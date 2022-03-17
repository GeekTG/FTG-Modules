# -*- coding: utf-8 -*-

# Module author: @GovnoCodules

from io import BytesIO

from PIL import Image
from requests import get, post
from telethon.tl.types import DocumentAttributeFilename

from .. import loader, utils


@loader.tds
class QRtoolsMod(loader.Module):
    """Generator and reader of QR codes"""

    strings = {"name": "QR Code"}

    @loader.owner
    async def makeqrcmd(self, message):
        """.makeqr <text or reply>"""
        text = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        file = False
        if not text or text.lower() == ".file":
            if text and text == ".file":
                file = True
            if not reply or not reply.message:
                await message.edit("<b>Нет текста для кодирования!</b>")
                return
            text = reply.raw_text
        else:
            if text.startswith(".file"):
                file = True
                text = text[5:].strip()
        url = "https://api.qrserver.com/v1/create-qr-code/?data={}&size=512x512&charset-source=UTF-8&charset-target=UTF-8&ecc=L&color=0-0-0&bgcolor=255-255-255&margin=1&qzone=1&format=png"
        r = get(url.format(text), stream=True)
        qrcode = BytesIO()
        qrcode.name = "qr.png" if file else "qr.webp"
        Image.open(BytesIO(r.content)).save(qrcode)
        qrcode.seek(0)
        await message.delete()
        await message.client.send_file(
            message.to_id, qrcode, reply_to=reply, force_document=file
        )

    @loader.owner
    async def readqrcmd(self, message):
        """.readqr <qrcode or reply to qrcode>"""
        ok = await check(message)
        if not ok:
            reply = await message.get_reply_message()
            ok = await check(reply)
        if not ok:
            text = (
                "<b>Это не изображение!</b>" if reply else "<b>Нечего не передано!</b>"
            )
            await message.edit(text)
            return
        file = BytesIO()
        file.name = "qr.png"
        data = await message.client.download_file(ok)
        Image.open(BytesIO(data)).save(file)
        url = "https://api.qrserver.com/v1/read-qr-code/?outputformat=json"
        resp = post(url, files={"file": file.getvalue()})
        text = resp.json()[0]["symbol"][0]["data"]
        if not text:
            text = "<b>Невозможно распознать или QR пуст!<b>"
        await utils.answer(message, text)


async def check(msg):
    if msg and msg.media:
        if msg.photo:
            ok = msg.photo
        elif msg.document:
            if (
                DocumentAttributeFilename(file_name="AnimatedSticker.tgs")
                in msg.media.document.attributes
            ):
                return False
            if msg.gif or msg.video or msg.audio or msg.voice:
                return False
            ok = msg.media.document
        else:
            return False
    else:
        return False
    if not ok or ok is None:
        return False
    else:
        return ok
