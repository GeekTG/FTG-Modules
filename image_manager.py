# -*- coding: utf-8 -*-

# Module author: @D4n13l3k00

# requires: pillow

from .. import loader, utils
import io
from PIL import Image, ImageDraw, ImageEnhance
import PIL.ImageOps
import re


@loader.tds
class ImageManagerMod(loader.Module):
    """ImageManager - простая работа с фото через Pillow"""
    strings = {"name": "ImageManager"}

    @loader.owner
    async def delbgcmd(self, m):
        """Удалить белый фон(всё что >230)
        Возвращает стикер webp
        Если после команды что-либо указать, отправится как файл png"""
        s = "[ImageManager -> DelBg]\n"
        reply = await m.get_reply_message()
        im = await get_img_from_msg(reply)
        if not im:
            await m.edit(s + "Реплай на изображение")
            return
        await m.edit(s + "Работаю...")
        im2 = Image.open(im).convert("RGBA")
        w, h = im2.size
        for x in range(w):
            for y in range(h):
                if im2.getpixel((x, y)) >= (230, 230, 230):
                    im2.putpixel((x, y), (0, 0, 0, 0))
        output = io.BytesIO()
        as_file = bool(utils.get_args_raw(m))
        output.name = "delbg." + ("png" if as_file else "webp")
        if not as_file:
            im2.thumbnail((512, 512))
        im2.save(output)
        output.seek(0)
        del im2
        await m.client.send_file(m.to_id, output, force_document=as_file, reply_to=reply.id)
        await m.delete()

    async def delbg2cmd(self, m):
        """Удалить черный фон(всё что <30)
        Возвращает стикер webp
        Если после команды что-либо указать, отправится как файл png"""
        s = "[ImageManager -> DelBg]\n"
        reply = await m.get_reply_message()
        im = await get_img_from_msg(reply)
        if not im:
            await m.edit(s + "Реплай на изображение")
            return
        await m.edit(s + "Работаю...")
        im2 = Image.open(im).convert("RGBA")
        w, h = im2.size
        for x in range(w):
            for y in range(h):
                if im2.getpixel((x, y)) <= (30, 30, 30):
                    im2.putpixel((x, y), (0, 0, 0, 0))
        output = io.BytesIO()
        as_file = bool(utils.get_args_raw(m))
        output.name = "delbg." + ("png" if as_file else "webp")
        if not as_file:
            im2.thumbnail((512, 512))
        im2.save(output)
        output.seek(0)
        del im2
        await m.client.send_file(m.to_id, output, force_document=as_file, reply_to=reply.id)
        await m.delete()

    async def resizecmd(self, m):
        """<x:int> <y:int>
        Изменить размер фото"""
        s = "[ImageManager -> Resize]\n"
        reply = await m.get_reply_message()
        im = await get_img_from_msg(reply)
        if not im:
            await m.edit(s + "Реплай на изображение")
            return
        args = utils.get_args_raw(m)
        if not args:
            await m.edit(s + "Укажите <x:int> <y:int>")
            return
        rr = re.compile(r"^(\d+)\s+(\d+)$")
        if not rr.match(args):
            await m.edit(s + "Укажите <x:int> <y:int>")
            return
        x = int(rr.findall(args)[0][0])
        y = int(rr.findall(args)[0][1])
        await m.edit(s + "Работаю...")
        im2 = Image.open(im)
        im2 = im2.resize((x, y))
        out = io.BytesIO()
        iswebp = True if reply.file.ext == ".webp" else False
        if iswebp:
            im2.thumbnail((512, 512))
        out.name = "resized." + (".webp" if iswebp else ".png")
        im2.save(out)
        out.seek(0)
        await m.client.send_file(m.to_id, out, reply_to=reply.id)
        await m.delete()

    async def rotatecmd(self, m):
        """<rotate:int>
        Повернуть изображение"""
        s = "[ImageManager -> Rotate]\n"
        reply = await m.get_reply_message()
        im = await get_img_from_msg(reply)
        if not im:
            await m.edit(s + "Реплай на изображение")
            return
        args = utils.get_args_raw(m)
        if not args:
            await m.edit(s + "Укажите <rotate:int>")
            return
        rr = re.compile(r"^(-*\d+)$")
        if not rr.match(args):
            await m.edit(s + "Укажите <rotate:int>")
            return
        c = int(rr.findall(args)[0])
        im2 = Image.open(im)
        im2 = im2.rotate(c, expand=True)
        out = io.BytesIO()
        iswebp = True if reply.file.ext == ".webp" else False
        if iswebp:
            im2.thumbnail((512, 512))
        out.name = "rotate." + (".webp" if iswebp else ".png")
        im2.save(out)
        out.seek(0)
        await m.client.send_file(m.to_id, out, reply_to=reply.id)
        await m.delete()

    async def invertcmd(self, m):
        """Инвертировать цвета фото"""
        s = "[ImageManager -> Invert]\n"
        reply = await m.get_reply_message()
        im = await get_img_from_msg(reply)
        if not im:
            await m.edit(s + "Реплай на изображение")
            return
        await m.edit(s + "Работаю...")
        await m.client.send_file(m.to_id, await invert_image(im, reply.file.ext), reply_to=reply.id)
        await m.delete()

    async def contrstcmd(self, m):
        """<level:float or int>
        Изменить контрастность изображения"""
        s = "[ImageManager -> Contrast]\n"
        reply = await m.get_reply_message()
        im = await get_img_from_msg(reply)
        if not im:
            await m.edit(s + "Реплай на изображение")
            return
        await m.edit(s + "Работаю...")
        args = utils.get_args_raw(m)
        if not args:
            await m.edit(s + "Укажите <level:float or int>")
            return
        rr = re.compile(r"^(\d+|\d+\.\d+)$")
        if not rr.match(args):
            await m.edit(s + "Укажите <level:float or int>")
            return
        c = float(rr.findall(args)[0])
        await m.client.send_file(m.to_id, await contrast(im, c, reply.file.ext), reply_to=reply.id)
        await m.delete()

    async def convpcmd(self, m):
        """Стикер в фото
        Фото в стикер"""
        s = "[ImageManager -> Converter]\n"
        reply = await m.get_reply_message()
        im = await get_img_from_msg(reply)
        if not im:
            await m.edit(s + "Реплай на изображение")
            return
        await m.edit(s + "Работаю...")
        im2 = Image.open(im)
        iswebp = True if reply.file.ext == ".webp" else False
        out = io.BytesIO()
        if iswebp:
            out.name = "conv.png"
        else:
            im2.thumbnail((512, 512))
            out.name = "conv.webp"
        im2.save(out)
        out.seek(0)
        await m.client.send_file(m.to_id, out, reply_to=reply.id)
        await m.delete()

    async def brightcmd(self, m):
        """<level:float or int>
        Изменить яркость фото"""
        s = "[ImageManager -> Bright]\n"
        reply = await m.get_reply_message()
        im = await get_img_from_msg(reply)
        if not im:
            await m.edit(s + "Реплай на изображение")
            return
        await m.edit(s + "Работаю...")
        args = utils.get_args_raw(m)
        if not args:
            await m.edit(s + "Укажите <level:float or int>")
            return
        rr = re.compile(r"^(\d+|\d+\.\d+)$")
        if not rr.match(args):
            await m.edit(s + "Укажите <level:float or int>")
            return
        c = float(rr.findall(args)[0])
        await m.client.send_file(m.to_id, setbright(im, c, reply.file.ext), reply_to=reply.id)
        await m.delete()

    async def sharpnesscmd(self, m):
        """<level:float or int>
        Изменить чёткость фото(если указать много, будет deepfry)"""
        s = "[ImageManager -> Sharpness]\n"
        reply = await m.get_reply_message()
        im = await get_img_from_msg(reply)
        if not im:
            await m.edit(s + "Реплай на изображение")
            return
        await m.edit(s + "Работаю...")
        args = utils.get_args_raw(m)
        if not args:
            await m.edit(s + "Укажите <level:float or int>")
            return
        rr = re.compile(r"^(\d+|\d+\.\d+)$")
        if not rr.match(args):
            await m.edit(s + "Укажите <level:float or int>")
            return
        c = float(rr.findall(args)[0])
        await m.client.send_file(m.to_id, setsharpness(im, c, reply.file.ext), reply_to=reply.id)
        await m.delete()


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
