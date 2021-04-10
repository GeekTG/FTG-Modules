# -*- coding: utf-8 -*-

# Module author: @D4n13l3k00

# requires: pillow

import io
import re

import PIL.ImageOps
from PIL import Image, ImageEnhance

from .. import loader, utils


@loader.tds
class ImageManagerMod(loader.Module):
    """ImageManager - Simple work with imgaes"""
    strings = {"name": "Image Manager"}

    @loader.owner
    async def delbgcmd(self, m):
        """Remove wite background(всё что >230)
        Return sticker webp"""
        s = "[ImageManager -> DelBg]\n"
        reply = await m.get_reply_message()
        im = await get_img_from_msg(reply)
        if not im: return await utils.answer(m, s + "Reply to image")
        await utils.answer(m, s + "Working...")
        im2 = Image.open(im).convert("RGBA")
        w, h = im2.size
        for x in range(w):
            for y in range(h):
                if im2.getpixel((x, y)) >= (230, 230, 230):
                    im2.putpixel((x, y), (0, 0, 0, 0))
        output = io.BytesIO()
        as_file = bool(utils.get_args_raw(m))
        output.name = "delbg." + ("png" if as_file else "webp")
        if not as_file: im2.thumbnail((512, 512))
        im2.save(output)
        output.seek(0)
        del im2
        await utils.answer(m, output, force_document=as_file, reply_to=reply.id)

    async def delbg2cmd(self, m):
        """Deletes black color
        Return sticker webp"""
        reply = await m.get_reply_message()
        im = await get_img_from_msg(reply)
        if not im: return await utils.answer(m, "Reply to image")
        im2 = Image.open(im).convert("RGBA")
        w, h = im2.size
        for x in range(w):
            for y in range(h):
                if im2.getpixel((x, y)) <= (30, 30, 30):
                    im2.putpixel((x, y), (0, 0, 0, 0))
        output = io.BytesIO()
        as_file = bool(utils.get_args_raw(m))
        output.name = "delbg." + ("png" if as_file else "webp")
        if not as_file: im2.thumbnail((512, 512))
        im2.save(output)
        output.seek(0)
        del im2
        await utils.answer(m, output, force_document=as_file, reply_to=reply.id)

    async def resizecmd(self, m):
        """<x:int> <y:int>
        Resize image"""
        reply = await m.get_reply_message()
        im = await get_img_from_msg(reply)
        if not im: return await utils.answer(m, "Reply to image")
        args = utils.get_args_raw(m)
        if not args: return await utils.answer(m, "Specify x:int y:int")
        rr = re.compile(r"^(\d+)\s+(\d+)$")
        if not rr.match(args): return await utils.answer(m, "Specify x:int y:int")
        x = int(rr.findall(args)[0][0])
        y = int(rr.findall(args)[0][1])
        im2 = Image.open(im)
        im2 = im2.resize((x, y))
        out = io.BytesIO()
        iswebp = True if reply.file.ext == ".webp" else False
        if iswebp: im2.thumbnail((512, 512))
        out.name = "resized." + (".webp" if iswebp else ".png")
        im2.save(out)
        out.seek(0)
        await utils.answer(m, out, reply_to=reply.id)

    async def rotatecmd(self, m):
        """<rotate:int>
        Rotate image"""
        reply = await m.get_reply_message()
        im = await get_img_from_msg(reply)
        if not im: return await utils.answer(m, "Reply to image")
        args = utils.get_args_raw(m)
        if not args: return await utils.answer(m, "Specify <rotate:int>")
        rr = re.compile(r"^(-*\d+)$")
        if not rr.match(args): return await utils.answer(m, "Specify <rotate:int>")
        c = int(rr.findall(args)[0])
        im2 = Image.open(im)
        im2 = im2.rotate(c, expand=True)
        out = io.BytesIO()
        iswebp = True if reply.file.ext == ".webp" else False
        if iswebp: im2.thumbnail((512, 512))
        out.name = "rotate." + (".webp" if iswebp else ".png")
        im2.save(out)
        out.seek(0)
        await utils.answer(m, out, reply_to=reply.id)

    async def invertcmd(self, m):
        """Invert image's colors"""
        reply = await m.get_reply_message()
        im = await get_img_from_msg(reply)
        if not im: return await utils.answer(m, "Reply to image")
        await utils.answer(m, await invert_image(im, reply.file.ext), reply_to=reply.id)

    async def contrstcmd(self, m):
        """<level:float or int>
        Change the image contrast"""
        reply = await m.get_reply_message()
        im = await get_img_from_msg(reply)
        if not im: return await utils.answer(m, "Reply to image")
        args = utils.get_args_raw(m)
        if not args: return await utils.answer(m, "Specify level:float or int")
        rr = re.compile(r"^(\d+|\d+\.\d+)$")
        if not rr.match(args): return await utils.answer(m, "Specify level:float or int")
        c = float(rr.findall(args)[0])
        await utils.answer(m, await contrast(im, c, reply.file.ext), reply_to=reply.id)

    async def convpcmd(self, m):
        """Sticker to image
        Image to sticker"""
        reply = await m.get_reply_message()
        im = await get_img_from_msg(reply)
        if not im: return await utils.answer(m, "Reply to image")
        im2 = Image.open(im)
        iswebp = True if reply.file.ext == ".webp" else False
        out = io.BytesIO()
        if iswebp:
            out.name = "conv.png"
        else:
            im2.thumbnail((512, 512)); out.name = "conv.webp"
        im2.save(out)
        out.seek(0)
        await utils.answer(m, out, reply_to=reply.id)

    async def brightcmd(self, m):
        """<level:float or int>
        Change the brightness of the image"""
        reply = await m.get_reply_message()
        im = await get_img_from_msg(reply)
        if not im: return await utils.answer(m, "Reply to image")
        args = utils.get_args_raw(m)
        if not args: return await utils.answer(m, "Specify level:float or int")
        rr = re.compile(r"^(\d+|\d+\.\d+)$")
        if not rr.match(args): return await utils.answer(m, "Specify level:float or int")
        c = float(rr.findall(args)[0])
        await utils.answer(m, setbright(im, c, reply.file.ext), reply_to=reply.id)

    async def sharpnesscmd(self, m):
        """<level:float or int>
        Change the sharpness of the image"""
        reply = await m.get_reply_message()
        im = await get_img_from_msg(reply)
        if not im: return await utils.answer(m, "Reply to image")
        args = utils.get_args_raw(m)
        if not args: return await utils.answer(m, "Specify <level:float or int>")
        rr = re.compile(r"^(\d+|\d+\.\d+)$")
        if not rr.match(args): return await utils.answer(m, "Specify <level:float or int>")
        c = float(rr.findall(args)[0])
        await utils.answer(m, setsharpness(im, c, reply.file.ext), reply_to=reply.id)


async def get_img_from_msg(reply):
    if reply and reply.file:
        if not reply.file.mime_type == "image":
            return io.BytesIO(await reply.download_media(bytes))
        else:
            return None
    else:
        return None


async def invert_image(im, ext):
    image = Image.open(im)
    file = io.BytesIO()
    iswebp = True if ext == ".webp" else False
    file.name = "bw." + (".webp" if iswebp else ".png")
    if image.mode == 'RGBA':
        r, g, b, a = image.split()
        rgb_image = Image.merge('RGB', (r, g, b))
        inverted_image = PIL.ImageOps.invert(rgb_image)
        r2, g2, b2 = inverted_image.split()
        final_transparent_image = Image.merge('RGBA', (r2, g2, b2, a))
        if iswebp:
            final_transparent_image.thumbnail((512, 512))
        final_transparent_image.save(file)
    else:
        inverted_image = PIL.ImageOps.invert(image)
        if iswebp:
            inverted_image.thumbnail((512, 512))
        inverted_image.save(file)
    file.seek(0)
    return file


async def contrast(im, level, ext):
    image = ImageEnhance.Contrast(Image.open(im)).enhance(level)
    out = io.BytesIO()
    iswebp = True if ext == ".webp" else False
    if iswebp:
        image.thumbnail((512, 512))
    out.name = "contrast." + (".webp" if iswebp else ".png")
    image.save(out)
    out.seek(0)
    return out


async def blwh(im, ext):
    image = Image.open(im).convert('L')
    out = io.BytesIO()
    iswebp = True if ext == ".webp" else False
    if iswebp:
        image.thumbnail((512, 512))
    out.name = "bw." + (".webp" if iswebp else ".png")
    image.save(out)
    out.seek(0)
    return out


def setbright(im, level, ext):
    iswebp = True if ext == ".webp" else False
    image = ImageEnhance.Brightness(Image.open(im)).enhance(level)
    if iswebp:
        image.thumbnail((512, 512))
    out = io.BytesIO()
    out.name = "brigth." + (".webp" if iswebp else ".png")
    image.save(out)
    out.seek(0)
    return out


def setsharpness(im, level, ext):
    iswebp = True if ext == ".webp" else False
    image = ImageEnhance.Sharpness(Image.open(im)).enhance(level)
    if iswebp:
        image.thumbnail((512, 512))
    out = io.BytesIO()
    out.name = "sharpness." + (".webp" if iswebp else ".png")
    image.save(out)
    out.seek(0)
    return out
