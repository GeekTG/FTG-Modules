# -*- coding: utf-8 -*-

# Module author: @GovnoCodules, @ftgmodulesbyfl1yd, @D4n13l3k00

# requires: Pillow

import io
import textwrap
from asyncio.exceptions import CancelledError, TimeoutError
from textwrap import wrap

import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps
from telethon import events, functions
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.events import NewMessage

from .. import loader, utils

CHAT = "@demotilifebot"


@loader.tds
class DemotivatorMod(loader.Module):
    """Deotivators"""

    strings = {"name": "Demotivator"}

    async def client_ready(self, client, db):
        self.client = client

    @loader.owner
    async def demoticmd(self, message):
        """Demotiving photo without compression"""
        await cmds(message, 0)

    async def demotcmd(self, message):
        """Demotiving photo"""
        await cmds(message, 1)

    async def bottomcmd(self, message):
        """Imposes text in the photo from below"""
        return await procces_img(message, 1)

    async def topcmd(self, message):
        """Imposes text on the photo at the top"""
        return await procces_img(message, 2)

    async def centercmd(self, message):
        """Imposes text on the photo at the center"""
        return await procces_img(message, 3)

    async def demotirandcmd(self, message):
        """Random demotiving photo without compression"""
        await cmdrands(message, 0)

    async def demotrandcmd(self, message):
        """Random demotiving photo"""
        await cmdrands(message, 1)

    async def nqcmd(self, message):
        """Quotes from the message"""
        chat = "@ShittyQuoteBot"
        text = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if not text and not reply:
            await message.edit("<b>No reply</b>")
            return
        await message.edit("<b>Demotivating...</b>")
        async with message.client.conversation(chat) as conv:
            if text:
                try:
                    response = conv.wait_event(
                        events.NewMessage(incoming=True, from_users=1389323591)
                    )
                    await message.client.send_message(chat, text)
                    response = await response
                except YouBlockedUserError:
                    return await message.edit("<b>Unblock @ShittyQuoteBot</b>")
            else:
                try:
                    user = await utils.get_user(reply)
                    response = conv.wait_event(
                        events.NewMessage(incoming=True, from_users=1389323591)
                    )
                    await message.client.send_message(
                        chat, f"{reply.raw_text} (с) {user.first_name}"
                    )
                    response = await response
                except YouBlockedUserError:
                    return await message.edit("<b>Unblock @ShittyQuoteBot</b>")
        if response.text:
            await message.client.send_message(message.to_id, f"<b> {response.text}</b>")
            await message.delete()
        if response.media:
            await message.client.send_file(
                message.to_id, response.media, reply_to=reply.id if reply else None
            )
            await message.delete()
        await message.client(
            functions.messages.DeleteHistoryRequest(
                peer="ShittyQuoteBot", max_id=0, just_clear=False, revoke=True
            )
        )

    async def mqcmd(self, message):
        """Quotes from the message 2"""
        bw = not utils.get_args(message)
        reply = await message.get_reply_message()
        if not reply or not reply.raw_text:
            return await message.edit("<b>Reply to message!</b>")

        sender = reply.sender_id

        if not sender:
            sender = message.chat.id
        if sender == 1087968824:
            sender = message.chat.id
        pfp = await message.client.download_profile_photo(sender, bytes)
        await message.edit("<b>Demotivating...</b>")
        if not pfp:
            pfp = b"BM:\x00\x00\x00\x00\x00\x00\x006\x00\x00\x00(\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x18\x00\x00\x00\x00\x00\x04\x00\x00\x00\xc4\x0e\x00\x00\xc4\x0e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\x00"
        text = "\n".join(wrap(reply.raw_text, 30))
        text = "“" + text + "„"
        bf = requests.get(
            "https://raw.githubusercontent.com/KeyZenD/l/master/times.ttf"
        ).content
        font = ImageFont.truetype(io.BytesIO(bf), 50)
        im = Image.open(io.BytesIO(pfp))
        if bw:
            im = im.convert("L")
        im = im.convert("RGBA").resize((1024, 1024))
        w, h = im.size
        w_, h_ = 20 * (w // 100), 20 * (h // 100)
        im_ = Image.new("RGBA", (w - w_, h - h_), (0, 0, 0))
        im_.putalpha(150)
        im.paste(im_, (w_ // 2, h_ // 2), im_)
        draw = ImageDraw.Draw(im)
        _w, _h = draw.textsize(text=text, font=font)
        x, y = (w - _w) // 2, (h - _h) // 2
        draw.text((x, y), text=text, font=font, fill="#fff", align="center")
        output = io.BytesIO()
        im.save(output, "PNG")
        output.seek(0)
        await reply.reply(file=output)
        await message.delete()


async def cmds(message, type_):
    event, is_reply = await check_media(message)
    if not event:
        if message.client._conversations.get(1376531590) is not None:
            return await message.edit("<b>Please wait.</b>")

        reply = await message.get_reply_message()
        if (
            not reply
            or not reply.media
            or not any(
                True
                for _ in ("sticker", "photo", "video", "video_note", "animation")
                if getattr(reply, _, None) is not None
            )
        ):
            return await message.edit("<b>Reply to photo/video/sticker/gif</b>")
        if reply.file.size > 4194304:
            return await message.edit("<b>Video only up to 4mb</b>")
        args = utils.get_args_raw(message) or reply.message
        if not args:
            return await message.edit("<b>No text</b>")
        if len(args) > 500:
            return await message.edit("<b>Text only up to 500 symbols</b>")

        await message.edit("<b>Demotivating...</b>")
        async with message.client.conversation(CHAT, timeout=160) as conv:
            try:
                response = conv.wait_event(NewMessage(incoming=True, from_users=CHAT))
                msg = await reply.forward_to(CHAT)
                await msg.reply(f"/demoti {args}")
                response = await response
                if not response.media:
                    if response.raw_text.startswith("[400]"):
                        return await message.edit("<b>Please wait 10 sec</b>")
                    response = await conv.wait_event(
                        NewMessage(incoming=True, from_users=CHAT)
                    )

            except YouBlockedUserError:
                return await message.edit(f"<b>Unblock {CHAT}</b>")

            except (TimeoutError, CancelledError):
                return await message.edit("<b>Bot isn`t responding</b>")

            if response.media is None:
                return await message.edit("<b>Error</b>")

            await message.client.send_file(
                message.to_id, response.media, reply_to=reply
            )
            await message.delete()
            await message.client(
                functions.messages.DeleteHistoryRequest(
                    peer=CHAT, max_id=0, just_clear=False, revoke=True
                )
            )
            return
    text = utils.get_args_raw(message)

    if not text:
        await message.edit("<b>Reply to photo with text</b>")
        return
    await message.edit("Demotivating...")
    bytes_image = await event.download_media(bytes)
    demotivator = await demotion(font_bytes, bytes_image, text, type_)
    await message.edit("Sending...")
    if is_reply:
        await message.delete()
        return await event.reply(file=demotivator)
    return await event.edit(file=demotivator, text="")


async def cmdrands(message, type_):
    event, is_reply = await check_media(message)
    if not event:
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("<b>Reply to media</b>")
            return
        try:
            media = reply.media
        except Exception:
            return await message.edit("<b>Only media</b>")

        chat = "@super_rjaka_demotivator_bot"
        await message.edit("<b>Demotivating...</b>")
        async with message.client.conversation(chat) as conv:
            try:
                response = conv.wait_event(
                    events.NewMessage(incoming=True, from_users=1016409811)
                )
                mm = await message.client.send_file(chat, media, caption=args)
                response = await response
                await mm.delete()
            except YouBlockedUserError:
                await message.reply("<b>Разблокируй @super_rjaka_demotivator_bot</b>")
                return
            await message.edit("<b>Sending...</b>")
            await message.delete()
            await response.delete()
            await message.client.send_file(
                message.to_id,
                response.media,
                reply_to=await message.get_reply_message(),
            )
            await message.client(
                functions.messages.DeleteHistoryRequest(
                    peer="super_rjaka_demotivator_bot",
                    max_id=0,
                    just_clear=False,
                    revoke=True,
                )
            )
    text = utils.get_args_raw(message)

    if not text:
        await message.edit("<b>Reply to photo with text</b>")
        return
    await message.edit("<b>Demotivating...</b>")
    bytes_image = await event.download_media(bytes)
    demotivator = await demotion(font_bytes, bytes_image, text, type_)
    await message.edit("<b>Sending...</b>")
    if is_reply:
        await message.delete()
        return await event.reply(file=demotivator)
    return await event.edit(file=demotivator, text="")


async def check_media(message):
    reply = await message.get_reply_message()
    is_reply = True
    if not reply:
        reply = message
        is_reply = False
    if not reply.file:
        return False, ...
    mime = reply.file.mime_type.split("/")[0].lower()
    if mime != "image":
        return False, ...
    return reply, is_reply


async def textwrap(text, length=50, splitter="&&"):
    out = []
    lines = text.rsplit(splitter, 1)
    for text in lines:
        txt = []
        parts = text.split("&&")
        for part in parts:
            part = "\n".join(wrap(part, length))
            txt.append(part)
        text = "\n".join(txt)
        out.append(text)
    return out


async def draw_main(
    bytes_image,
    type_,
    frame_width_1=5,
    frame_fill_1=(0, 0, 0),
    frame_width_2=3,
    frame_fill_2=(255, 255, 255),
    expand_proc=10,
    main_fill=(0, 0, 0),
):
    main_ = Image.open(io.BytesIO(bytes_image))
    main = Image.new("RGB", main_.size, "black")
    main.paste(main_, (0, 0))
    if type_ == 1:
        main = main.resize((700, 550))
    main = ImageOps.expand(main, frame_width_1, frame_fill_1)
    main = ImageOps.expand(main, frame_width_2, frame_fill_2)
    w, h = main.size
    h_up = expand_proc * (h // 100)
    im = Image.new("RGB", (w + (h_up * 2), h + h_up), main_fill)
    im.paste(main, (h_up, h_up))
    return im


async def _draw_text(
    text,
    font_bytes,
    font_size,
    font_add=30,
    main_fill=(0, 0, 0),
    text_fill=(255, 255, 255),
    text_align="center",
):
    font = ImageFont.truetype(io.BytesIO(font_bytes), font_size)
    w_txt, h_txt = ImageDraw.Draw(Image.new("RGB", (1, 1))).multiline_textsize(
        text=text, font=font
    )
    txt = Image.new("RGB", (w_txt, h_txt + font_add), main_fill)
    ImageDraw.Draw(txt).text(
        (0, 0), text=text, font=font, fill=text_fill, align=text_align
    )
    return txt


async def text_joiner(text_img_1, text_img_2, main_fill=(0, 0, 0)):
    w_txt_1, h_txt_1 = text_img_1.size
    w_txt_2, h_txt_2 = text_img_2.size
    w = max(w_txt_1, w_txt_2)
    h = h_txt_1 + h_txt_2
    text = Image.new("RGB", (w, h), main_fill)
    text.paste(text_img_1, ((w - w_txt_1) // 2, 0))
    text.paste(text_img_2, ((w - w_txt_2) // 2, h_txt_1))
    return text


async def draw_text(text, font_bytes, font_size):
    text = await textwrap(text)
    if len(text) == 1:
        text = await _draw_text(text[0], font_bytes, font_size[0])
    else:
        text_img_1 = await _draw_text(text[0], font_bytes, font_size[0])
        text_img_2 = await _draw_text(text[-1], font_bytes, font_size[1])
        text = await text_joiner(text_img_1, text_img_2)
    return text


async def text_finaller(text, main, expand_width_proc=25, main_fill=(0, 0, 0)):
    x = min(main.size)
    w_txt, h_txt = text.size
    w_proc = expand_width_proc * (w_txt // 100)
    h_proc = expand_width_proc * (h_txt // 100)
    back = Image.new("RGB", (w_txt + (w_proc * 2), h_txt + (h_proc * 2)), main_fill)
    back.paste(text, (w_proc, h_proc))
    back.thumbnail((x, x))
    return back


async def joiner(text_img, main_img, format_save="JPEG"):
    w_im, h_im = main_img.size
    w_txt, h_txt = text_img.size
    text_img.thumbnail((min(w_im, h_im), min(w_im, h_im)))
    w_txt, h_txt = text_img.size
    main_img = main_img.crop((0, 0, w_im, h_im + h_txt))
    main_img.paste(text_img, ((w_im - w_txt) // 2, h_im))
    output = io.BytesIO()
    main_img.save(output, format_save)
    output.seek(0)
    return output.getvalue()


async def demotion(font_bytes, bytes_image, text, type):
    main = await draw_main(bytes_image, type)
    font_size = [20 * (min(main.size) // 100), 15 * (min(main.size) // 100)]
    text = await draw_text(text, font_bytes, font_size)
    text = await text_finaller(text, main)
    output = await joiner(text, main)
    return output


async def demotionrand(font_bytes, bytes_image, text, type):
    main = await draw_main(bytes_image, type)
    font_size = [20 * (min(main.size) // 100), 15 * (min(main.size) // 100)]
    text = await draw_text(text, font_bytes, font_size)
    text = await text_finaller(text, main)
    output = await joiner(text, main)
    return output


tttxxx = [
    "А че",
    "заставляет задуматься",
    "Жалко пацана",
    "ты че сука??",
    "ААХАХАХАХХАХА\n\nААХАХААХАХА",
    "ГИГАНТ МЫСЛИ\n\nотец русской демократии",
    "Он",
    "ЧТО БЛЯТЬ?",
    "охуенная тема",
    "ВОТ ОНИ\n\nтипичные комедиклабовские шутки",
    "НУ НЕ БЛЯДИНА?",
    "Узнали?",
    "Согласны?",
    "Вот это мужик",
    "ЕГО ИДЕИ\n\nбудут актуальны всегда",
    "\n\nПРИ СТАЛИНЕ ОН БЫ СИДЕЛ",
    "о вадим",
    "2 месяца на дваче\n\nи это, блядь, нихуя не смешно",
    "Что дальше?\n\nЧайник с функцией жопа?",
    "\n\nИ нахуя мне эта информация?",
    "Верхний текст",
    "нижний текст",
    "Показалось",
    "Суды при анкапе",
    "Хуйло с района\n\n\n\nтакая шелупонь с одной тычки ляжет",
    "Брух",
    "Расскажи им\n\nкак ты устал в офисе",
    "Окурок блять\n\nесть 2 рубля?",
    "Аниме ставшее легендой",
    "СМИРИСЬ\n\n\n\nты никогда не станешь настолько же крутым",
    "а ведь это идея",
    "\n\nЕсли не лайкнешь у тебя нет сердца",
    "Вместо тысячи слов",
    "ШАХ И МАТ!!!",
    "Самый большой член в мире\n\nУ этой девушки",
    "Немного\n\nперфекционизма",
    "кто",
    "\n\nэта сука уводит чужих мужей",
    "Кто он???",
    "\n\nВы тоже хотели насрать туда в детстве?",
    "\n\nВся суть современного общества\n\nв одном фото",
    "Он обязательно выживет!",
    "\n\nВы тоже хотите подрочить ему?",
    "\n\nИ вот этой хуйне поклоняются русские?",
    "Вот она суть\n\n\n\nчеловеческого общества в одной картинке",
    "Вы думали это рофл?\n\nНет это жопа",
    "\n\nПри сталине такой хуйни не было\n\nА у вас было?",
    "Он грыз провода",
    "Назло старухам\n\nна радость онанистам",
    "Где-то в Челябинске",
    "Агитация за Порошенко",
    "ИДЕАЛЬНО",
    "Грыз?",
    "Ну давай расскажи им\n\nкакая у тебя тяжелая работа",
    "\n\nЖелаю в каждом доме такого гостя",
    "Шкура на вырост",
    "НИКОГДА\n\nне сдавайся",
    "Оппа гангнам стайл\n\nуууу сэкси лейди оп оп",
    "Они сделали это\n\nсукины дети, они справились",
    "Эта сука\n\nхочет денег",
    "Это говно, а ты?",
    "\n\nВот она нынешняя молодежь",
    "Погладь кота\n\nпогладь кота сука",
    "Я обязательно выживу",
    "\n\nВот она, настоящая мужская дружба\n\nбез политики и лицимерия",
    "\n\nОБИДНО ЧТО Я ЖИВУ В СТРАНЕ\n\nгде гантели стоят в 20 раз "
    "дороже чем бутылка водки",
    "Царь, просто царь",
    "\n\nНахуй вы это в учебники вставили?\n\nИ ещё ебаную контрольную " "устроили",
    "\n\nЭТО НАСТОЯЩАЯ КРАСОТА\n\nа не ваши голые бляди",
    "\n\nТема раскрыта ПОЛНОСТЬЮ",
    "\n\nРОССИЯ, КОТОРУЮ МЫ ПОТЕРЯЛИ",
    "ЭТО - Я\n\nПОДУМАЙ МОЖЕТ ЭТО ТЫ",
    "почему\n\nчто почему",
    "КУПИТЬ БЫ ДЖЫП\n\nБЛЯТЬ ДА НАХУЙ НАДО",
    "\n\n\n\nмы не продаём бомбастер лицам старше 12 лет",
    "МРАЗЬ",
    "Правильная аэрография",
    "Вот она русская\n\nСМЕКАЛОЧКА",
    "Он взял рехстаг!\n\nА чего добился ты?",
    "На аватарку",
    "Фотошоп по-деревенски",
    "Инструкция в самолете",
    "Цирк дю Солей",
    "Вкус детства\n\nшколоте не понять",
    "Вот оно - СЧАСТЬЕ",
    "Он за тебя воевал\n\nа ты даже не знаешь его имени",
    "Зато не за компьютером",
    "\n\nНе трогай это на новый год",
    "Мой первый рисунок\n\nмочой на снегу",
    "\n\nМайские праздники на даче",
    "Ваш пиздюк?",
    "Тест драйв подгузников",
    "Не понимаю\n\nкак это вообще выросло?",
    "Супермен в СССР",
    "Единственный\n\nкто тебе рад",
    "Макдональдс отдыхает",
    "Ну че\n\n как дела на работе пацаны?",
    "Вся суть отношений",
    "Беларусы, спасибо!",
    "\n\nУ дверей узбекского военкомата",
    "Вместо 1000 слов",
    "Один вопрос\n\nнахуя?",
    "Ответ на санкции\n\nЕВРОПЫ",
    "ЦЫГАНСКИЕ ФОКУСЫ",
    "Блять!\n\nда он гений!",
    "\n\nУкраина ищет новые источники газа",
    "ВОТ ЭТО\n\nНАСТОЯЩИЕ КАЗАКИ а не ряженные",
    "Нового года не будет\n\nСанта принял Ислам",
    "\n\nОн был против наркотиков\n\nа ты и дальше убивай себя",
    "Всем похуй!\n\nВсем похуй!",
    "БРАТЬЯ СЛАВЯНЕ\n\nпомните друг о друге",
    "\n\nОН ПРИДУМАЛ ГОВНО\n\nа ты даже не знаешь его имени",
    "\n\nкраткий курс истории нацболов",
    "Эпоха ренессанса",
]


async def procces_img(message, way):
    cols = {
        "white": 1,
        "whit": 1,
        "whi": 1,
        "wh": 1,
        "w": 1,
        "black": 2,
        "blac": 2,
        "bla": 2,
        "bl": 2,
        "b": 2,
    }
    col = 1
    reply = await message.get_reply_message()
    txt = utils.get_args_raw(message)
    await message.edit("Waiting...")

    if txt in cols:
        col = cols[txt]
        txt = None
    if not txt:
        txt = "я лошара."
    if not reply:
        await message.edit("Reply to photo/sticker")
        return
    if txt.split(" ")[0] in cols:
        col = cols[txt.split(" ")[0]]
        txt = " ".join(txt.split(" ")[1:])

    bytes_font = requests.get(
        "https://github.com/Fl1yd/FTG-modules/blob/master/stuff/font3.ttf?raw=true"
    ).content
    bytes_back = await reply.download_media(bytes)
    font = io.BytesIO(bytes_font)
    font = ImageFont.truetype(font, 72)
    img = Image.open(io.BytesIO(bytes_back))

    W, H = img.size
    txt = txt.replace("\n", "𓃐")
    text = "\n".join(wrap(txt, 30))
    t = text
    t = t.replace("𓃐", "\n")

    draw = ImageDraw.Draw(img)
    w, h = draw.multiline_textsize(t, font=font)
    imtext = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(imtext)

    if col == 2:
        draw.multiline_text((10, 10), t, (0, 0, 0), font=font, align="center")
    else:
        draw.multiline_text((10, 10), t, (255, 255, 255), font=font, align="center")
    imtext.thumbnail((W, H))
    w, h = imtext.size

    if way == 1:
        img.paste(imtext, ((W - w) // 2, (H - h) // 1), imtext)
    if way == 2:
        img.paste(imtext, ((W - w) // 2, (H - h) // 15), imtext)
    if way == 3:
        img.paste(imtext, ((W - w) // 2, (H - h) // 2), imtext)

    output = io.BytesIO()
    output.name = "клоун.png"
    img.save(output, "png")
    output.seek(0)
    await message.client.send_file(message.to_id, output, reply_to=reply)
    await message.delete()


font_bytes = requests.get(
    "https://raw.githubusercontent.com/KeyZenD/l/master/times.ttf"
).content
#######################
