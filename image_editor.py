#   Coded by D4n13l3k00    #
#     t.me/D4n13l3k00      #
# This code under AGPL-3.0 #

# requires: Pillow aiohttp fake-useragent

import hashlib
import io
import re
from datetime import date

import aiohttp
from fake_useragent import UserAgent
from PIL import Image, ImageEnhance, ImageOps
from telethon import types

from .. import loader, utils


@loader.tds
class ImageEditorMod(loader.Module):
    "ImageEditor - Simple tool for working with images"
    strings = {
        "name": "ImageEditor",
        "downloading": "<b>[{}]</b> Downloading...",
        "working": "<b>[{}]</b> Working...",
        "exporting": "<b>[{}]</b> Exporting...",
        "set_value": "<b>[{}]</b> Specify the level...",
        "set_size": "<b>[{}]</b> Specify the size...",
        "reply": "<b>[{}]</b> reply to image...",
        "set_time": "<b>[{}]</b> Specify the time in the format start(ms):end(ms)",
    }

    @loader.owner
    async def resizeicmd(self, m: types.Message):
        '.resizei <w> <h> - Resize image'
        _pref = 'Resize'
        args = utils.get_args_raw(m)
        r = re.compile(r'^(\d+)\s+(\d+)$')
        if not args or not r.match(args):
            return await utils.answer(m, self.strings("set_size", m).format(_pref))
        w, h = [int(i) for i in r.match(args).groups()]
        im = await get_image(self, m, _pref)
        if not im:
            return
        out = im.image.resize((w, h))
        await go_out(self, m, im, out, _pref)

    @loader.owner
    async def rmbgicmd(self, m: types.Message):
        '.rmbgi - Remove background via AI [Powered by Indian\'s AI]'
        _pref = 'RemoveBg'
        im = await get_image(self, m, _pref)
        if not im:
            return
        b = io.BytesIO()
        b.name = 'i.png'
        im.image.save(b, 'PNG')
        b.seek(0)
        out = None
        async with aiohttp.ClientSession(headers={'User-Agent':UserAgent().chrome}) as s:
            form = aiohttp.FormData()
            form.add_field('file', b)
            form.add_field('filenameOverride', 'true')
            form.add_field(
                'path', f"__editor/{date.year}-{date.month}-{date.day}/{hashlib.md5(b.read()).hexdigest()}")
            b.seek(0)
            async with s.post(
                'https://api.erase.bg/service/panel/assets/v1.0/upload/direct',
                    data=form) as r:
                _url = (await r.json())['url']
            async with s.get(_url.replace('dummy-cloudname/original', 'dummy-cloudname/erase.bg()')) as r:
                i = io.BytesIO(await r.read())
                i.name = 'ImageEditor.jpeg'
                out = Image.open(i)
        await go_out(self, m, im, out, _pref, True)

    @loader.owner
    async def inverticmd(self, m: types.Message):
        '.inverti - Invert colors'
        _pref = 'Invert'
        im = await get_image(self, m, _pref)
        if not im:
            return
        out = ImageOps.invert(im.image)
        await go_out(self, m, im, out, _pref)

    @loader.owner
    async def bwicmd(self, m: types.Message):
        '.bwi - BlackWhite'
        _pref = 'BlackWhite'
        im = await get_image(self, m, _pref)
        if not im:
            return
        out = im.image.convert('L')
        await go_out(self, m, im, out, _pref)

    @loader.owner
    async def convicmd(self, m: types.Message):
        '.convi - Sticker to image | Image to sticker'
        _pref = 'Converter'
        im = await get_image(self, m, _pref)
        if not im:
            return
        im.is_webp = not im.is_webp
        await go_out(self, m, im, im.image, _pref)

    @loader.owner
    async def rotateicmd(self, m: types.Message):
        '.rotatei <degrees> - Rotate image'
        _pref = 'Rotate'
        args = utils.get_args_raw(m)
        r = re.compile(r'^(\d+)$')
        if not args or not r.match(args):
            return await utils.answer(m, self.strings("set_value", m).format(_pref))
        degrees = int(r.match(args).groups()[0])
        im = await get_image(self, m, _pref)
        if not im:
            return
        out = im.image.rotate(degrees, expand=True)
        await go_out(self, m, im, out, _pref)

    @loader.owner
    async def contrasticmd(self, m: types.Message):
        '.contrasti <float> - Change contrast'
        _pref = 'Contrast'
        args = utils.get_args_raw(m)
        r = re.compile(r'^(\d*\.?\d*)$')
        if not args or not r.match(args):
            return await utils.answer(m, self.strings("set_value", m).format(_pref))
        level = float(r.match(args).groups()[0])
        im = await get_image(self, m, _pref)
        if not im:
            return
        out = ImageEnhance.Contrast(im.image).enhance(level)
        await go_out(self, m, im, out, _pref)

    @loader.owner
    async def sharpnessicmd(self, m: types.Message):
        '.sharpnessi <float> - Change sharpness'
        _pref = 'Sharpness'
        args = utils.get_args_raw(m)
        r = re.compile(r'^(\d*\.?\d*)$')
        if not args or not r.match(args):
            return await utils.answer(m, self.strings("set_value", m).format(_pref))
        level = float(r.match(args).groups()[0])
        im = await get_image(self, m, _pref)
        if not im:
            return
        out = ImageEnhance.Sharpness(im.image).enhance(level)
        await go_out(self, m, im, out, _pref)

    @loader.owner
    async def brighticmd(self, m: types.Message):
        '.brighti <float> - Change bright'
        _pref = 'Color'
        args = utils.get_args_raw(m)
        r = re.compile(r'^(\d*\.?\d*)$')
        if not args or not r.match(args):
            return await utils.answer(m, self.strings("set_value", m).format(_pref))
        level = float(r.match(args).groups()[0])
        im = await get_image(self, m, _pref)
        if not im:
            return
        out = ImageEnhance.Brightness(im.image).enhance(level)
        await go_out(self, m, im, out, _pref)

    @loader.owner
    async def coloricmd(self, m: types.Message):
        '.colori <float> - Change color factor'
        _pref = 'Color'
        args = utils.get_args_raw(m)
        r = re.compile(r'^(\d*\.?\d*)$')
        if not args or not r.match(args):
            return await utils.answer(m, self.strings("set_value", m).format(_pref))
        level = float(r.match(args).groups()[0])
        im = await get_image(self, m, _pref)
        if not im:
            return
        out = ImageEnhance.Color(im.image).enhance(level)
        await go_out(self, m, im, out, _pref)


class ImageEditorClass():
    image: Image.Image = None
    message = None
    is_webp: bool = None
    pref: str = None
    reply = None


async def get_image(self, m, pref: str) -> ImageEditorClass:
    r = await m.get_reply_message()
    if r and r.file and r.file.mime_type.split("/")[0] in ["image"]:
        im = ImageEditorClass()
        im.pref = pref
        im.reply = r
        im.is_webp = r.file.ext == ".webp"
        m = await utils.answer(m, self.strings("downloading", m).format(pref))
        im.image = Image.open(io.BytesIO(await r.download_media(bytes)))
        im.message = await utils.answer(m, self.strings("working", m).format(pref))
        return im
    await utils.answer(m, self.strings("reply", m).format(pref))


async def go_out(self, m, im: ImageEditorClass, out: Image.Image, pref, force_document=False):
    m = await utils.answer(m, self.strings("exporting", m).format(pref))
    iba = io.BytesIO()
    if im.is_webp:
        out.thumbnail((512, 512))
    out.save(iba, format='WEBP' if im.is_webp else 'PNG')
    iba.name = 'ImageEditor.'+('webp' if im.is_webp else 'png')
    iba.seek(0)
    await utils.answer(
        m,
        iba,
        reply_to=im.reply.id,
        supports_streaming=True,
        force_document=force_document if not im.is_webp else False
    )
