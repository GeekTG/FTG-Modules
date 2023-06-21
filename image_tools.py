# -*- coding: utf-8 -*-

# Module author: @GovnoCodules

import io
import logging
import random
import string
from io import BytesIO as ist
from random import randint, uniform

from PIL import Image, ImageDraw, ImageEnhance
from PIL import ImageOps
from PIL import ImageOps as IO
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.types import DocumentAttributeFilename
from telethon.tl.types import DocumentAttributeFilename as DAF

from .. import loader
from .. import utils
from .. import utils as U

logger = logging.getLogger(__name__)

_C = "png"
_B = "name"
_A = "image"
_R = "отражает"
_P = "часть."


@loader.tds
class ImageToolsMod(loader.Module):
    """Image tools module"""

    strings = {"name": "Image Tools"}

    async def llcmd(A, message):
        """Mirror the image"""
        await KZD(message, 1)

    async def rrcmd(A, message):
        """Mirror the image"""
        await KZD(message, 2)

    async def uucmd(A, message):
        """Mirror the image"""
        await KZD(message, 3)

    async def ddcmd(A, message):
        """Mirror the image"""
        await KZD(message, 4)

    @loader.unrestricted
    async def dotifycmd(self, message):
        """Image to RGB dots"""
        mode = False
        reply, pix = await parse(message)
        if reply:
            await dotify(message, reply, pix, mode)

    async def dotificmd(self, message):
        """Image to BW dots"""
        mode = True
        reply, pix = await parse(message)
        if reply:
            await dotify(message, reply, pix, mode)

    @loader.sudo
    async def soapcmd(self, message):
        """.soap <reply to photo>"""
        soap = 3
        a = utils.get_args(message)
        if a and a[0].isdigit():
            soap = int(a[0])
            if soap <= 0:
                soap = 3

        if message.is_reply:
            reply_message = await message.get_reply_message()
            data = await check_media(reply_message)
            if isinstance(data, bool):
                await utils.answer(message, "<code>Reply to pic or stick!</code>")
                return
        else:
            await utils.answer(message, "<code>Reply to pic or stick!</code>")
            return

        await message.edit("Soaping...")
        file = await message.client.download_media(data, bytes)
        media = await Soaping(file, soap)
        await message.delete()

        await message.client.send_file(message.to_id, media)

    async def pic2packcmd(self, message):
        """Create sticker pack with your photo"""
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("<b>Reply to photo❗</b>")
            return

        args = utils.get_args_raw(message)
        if not args:
            await message.edit("<b>Packname</b>❓")
            return
        chat = "@Stickers"
        name = "".join(
            random.choice(list(string.ascii_lowercase + string.ascii_uppercase))
            for _ in range(16)
        )
        image = io.BytesIO()
        await message.client.download_file(reply, image)
        image = Image.open(image)
        w, h = image.size
        www = max(w, h)
        await message.edit("🔪<b>Cropping...</b>")
        img = Image.new("RGBA", (www, www), (0, 0, 0, 0))
        img.paste(image, ((www - w) // 2, 0))
        face = img.resize((100, 100))
        fface = io.BytesIO()
        fface.name = name + ".png"
        images = await cropping(img)
        face.save(fface)
        fface.seek(0)
        await message.edit("<b>📤Uploading...</b>")
        async with message.client.conversation(chat) as conv:
            emoji = "▫️"
            try:
                x = await message.client.send_message(chat, "/cancel")
                await (
                    await conv.wait_event(
                        events.NewMessage(incoming=True, from_users=chat)
                    )
                ).delete()
                await x.delete()
                x = await message.client.send_message(chat, "/newpack")
                await (
                    await conv.wait_event(
                        events.NewMessage(incoming=True, from_users=chat)
                    )
                ).delete()
                await x.delete()
                x = await message.client.send_message(chat, args)
                await (
                    await conv.wait_event(
                        events.NewMessage(incoming=True, from_users=chat)
                    )
                ).delete()
                await x.delete()

                for im in images:
                    blank = io.BytesIO(im)
                    blank.name = name + ".png"
                    blank.seek(0)
                    x = await message.client.send_file(chat, blank, force_document=True)
                    await (
                        await conv.wait_event(
                            events.NewMessage(incoming=True, from_users=chat)
                        )
                    ).delete()
                    await x.delete()
                    x = await message.client.send_message(chat, emoji)
                    await (
                        await conv.wait_event(
                            events.NewMessage(incoming=True, from_users=chat)
                        )
                    ).delete()
                    await x.delete()

                x = await message.client.send_message(chat, "/publish")
                await (
                    await conv.wait_event(
                        events.NewMessage(incoming=True, from_users=chat)
                    )
                ).delete()
                await x.delete()
                x = await message.client.send_file(chat, fface, force_document=True)
                await (
                    await conv.wait_event(
                        events.NewMessage(incoming=True, from_users=chat)
                    )
                ).delete()
                await x.delete()
                x = await message.client.send_message(chat, name)
                ending = await conv.wait_event(
                    events.NewMessage(incoming=True, from_users=chat)
                )
                await x.delete()
                await ending.delete()
                for part in ending.raw_text.split():
                    if part.startswith("https://t.me/"):
                        break
                await message.edit("✅<b>Uploaded successful!</b>\n" + part)

            except YouBlockedUserError:
                await message.edit("<b>@Stickers BLOCKED⛔</b>")
                return

    async def deepcmd(self, message):
        """Deep the image"""
        try:
            frycount = int(utils.get_args(message)[0])
            if frycount < 1:
                raise ValueError
        except:
            frycount = 1

        if message.is_reply:
            reply_message = await message.get_reply_message()
            data = await check_media(reply_message)

            if isinstance(data, bool):
                await message.edit("Reply to photo please")
                return
        else:
            await message.edit("Reply to photo please")
            return

        await message.edit("Downloading...")
        image = io.BytesIO()
        await message.client.download_media(data, image)
        image = Image.open(image)

        await message.edit("Distorting...")
        for _ in range(frycount):
            image = await deepfry(image)

        fried_io = io.BytesIO()
        fried_io.name = "image.jpeg"
        image.save(fried_io, "JPEG")
        fried_io.seek(0)
        await message.delete()
        await message.reply(file=fried_io)


async def parse(message):
    reply = await message.get_reply_message()
    if not reply:
        await message.edit("<b>Reply to Image!</b>")
        return None, None
    args = utils.get_args(message)
    pix = 100
    if args:
        args = args[0]
        if args.isdigit():
            pix = int(args) if int(args) > 0 else 100
    return reply, pix


async def dotify(message, reply, pix, mode):
    await message.edit("<b>Putting dots...</b>")
    count = 24
    im_ = Image.open(io.BytesIO(await reply.download_media(bytes)))
    if im_.mode == "RGBA":
        temp = Image.new("RGB", im_.size, "#000")
        temp.paste(im_, (0, 0), im_)
        im_ = temp

    im = im_.convert("L")
    im_ = im if mode else im_
    [_.thumbnail((pix, pix)) for _ in [im, im_]]
    w, h = im.size
    img = Image.new(im_.mode, (w * count + (count // 2), h * count + (count // 2)), 0)
    ImageDraw.Draw(img)

    def cirsle(im, x, y, r, fill):
        x += r // 2
        y += r // 2
        draw = ImageDraw.Draw(im)
        draw.ellipse((x - r, y - r, x + r, y + r), fill)
        return im

    _x = _y = count // 2
    for x in range(w):
        for y in range(h):
            r = im.getpixel((x, y))
            fill = im_.getpixel((x, y))
            cirsle(img, _x, _y, r // count, fill)
            _y += count
        _x += count
        _y = count // 2

    out = io.BytesIO()
    out.name = "out.png"
    img.save(out)
    out.seek(0)
    await reply.reply(file=out)
    await message.delete()


async def Soaping(file, soap):
    img = Image.open(io.BytesIO(file))
    (x, y) = img.size
    img = img.resize((x // soap, y // soap), Image.ANTIALIAS)
    img = img.resize((x, y))
    soap_io = io.BytesIO()
    soap_io.name = "image.jpeg"
    img = img.convert("RGB")
    img.save(soap_io, "JPEG", quality=100)
    soap_io.seek(0)
    return soap_io


async def check_media(reply_message):
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


async def KZD(message, type):
    S = "sticker"
    A = message
    N = await A.get_reply_message()
    Q, J = await CM(N)
    if not Q or not N:
        await A.edit("<b>Реплай на стикер или фото!</b>")
        return
    O = "KZD." + J
    P = U.get_args_raw(A)
    if P:
        if P in [_A[:A] for A in range(1, len(_A) + 1)]:
            O = "KZD.png"
            J = _C
        if P in [S[:A] for A in range(1, len(S) + 1)]:
            O = "KZD.webp"
            J = "webp"
    R = ist()
    await A.edit("<b>Извиняюсь...</b>")
    await A.client.download_media(Q, R)
    E = Image.open(R)
    B, C = E.size
    if B % 2 != 0 and type in [1, 2] or C % 2 != 0 and type in [3, 4]:
        E = E.resize((B + 1, C + 1))
        C, B = E.size
    if type == 1:
        D = 0
        F = 0
        G = B // 2
        H = C
        K = G
        L = D
    if type == 2:
        D = B // 2
        F = 0
        G = B
        H = C
        K = F
        L = F
    if type == 3:
        D = 0
        F = 0
        G = B
        H = C // 2
        K = D
        L = H
    if type == 4:
        D = 0
        F = C // 2
        G = B
        H = C
        K = D
        L = D
    I = E.crop((D, F, G, H))
    if type in [1, 2]:
        I = IO.mirror(I)
    else:
        I = IO.flip(I)
    E.paste(I, (K, L))
    M = ist()
    M.name = O
    E.save(M, J)
    M.seek(0)
    await A.client.send_file(A.to_id, M, reply_to=N)
    await A.delete()


async def CM(R):
    D = False
    C = None
    A = R
    if A and A.media and A.photo:
        B = A.photo
        E = _C
    elif A and A.media and A.document:
        if DAF(file_name="AnimatedSticker.tgs") in A.media.document.attributes:
            return D, C
        if A.gif or A.video or A.audio or A.voice:
            return D, C
        B = A.media.document
        if _A not in B.mime_type:
            return D, C
        E = B.mime_type.split("/")[1]
    else:
        return D, C
    if not B or B is C:
        return D, C
    else:
        return B, E


async def cropping(img):
    (x, y) = img.size
    cy = 5
    cx = 5
    sx = x // cx
    sy = y // cy
    if (sx * cx, sy * cy) != (x, y):
        img = img.resize((sx * cx, sy * cy))
    (lx, ly) = (0, 0)
    media = []
    for _ in range(1, cy + 1):
        for o in range(1, cx + 1):
            mimg = img.crop((lx, ly, lx + sx, ly + sy))
            mimg = mimg.resize((512, 512))
            bio = io.BytesIO()
            bio.name = "image.png"
            mimg.save(bio, "PNG")
            media.append(bio.getvalue())
            lx += sx
        lx = 0
        ly += sy
    return media


async def deepfry(img: Image) -> Image:
    colours = (
        (randint(50, 200), randint(40, 170), randint(40, 190)),
        (randint(190, 255), randint(170, 240), randint(180, 250)),
    )

    img = img.copy().convert("RGB")

    # Crush image to hell and back
    img = img.convert("RGB")
    width, height = img.width, img.height
    img = img.resize(
        (int(width ** uniform(0.8, 0.9)), int(height ** uniform(0.8, 0.9))),
        resample=Image.LANCZOS,
    )
    img = img.resize(
        (int(width ** uniform(0.85, 0.95)), int(height ** uniform(0.85, 0.95))),
        resample=Image.BILINEAR,
    )
    img = img.resize(
        (int(width ** uniform(0.89, 0.98)), int(height ** uniform(0.89, 0.98))),
        resample=Image.BICUBIC,
    )
    img = img.resize((width, height), resample=Image.BICUBIC)
    img = ImageOps.posterize(img, randint(3, 7))

    # Generate colour overlay
    overlay = img.split()[0]
    overlay = ImageEnhance.Contrast(overlay).enhance(uniform(1.0, 2.0))
    overlay = ImageEnhance.Brightness(overlay).enhance(uniform(1.0, 2.0))

    overlay = ImageOps.colorize(overlay, colours[0], colours[1])

    # Overlay red and yellow onto main image and sharpen the hell out of it
    img = Image.blend(img, overlay, uniform(0.1, 0.4))
    img = ImageEnhance.Sharpness(img).enhance(randint(5, 300))

    return img
