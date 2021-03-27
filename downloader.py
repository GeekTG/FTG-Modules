# -*- coding: utf-8 -*-

# Module author: @GovnoCodules, @ftgmodulesbyfl1yd

from .. import loader, utils
from requests import get
import io
from telethon.tl.types import MessageEntityUrl, MessageEntityTextUrl
import os
from asyncio import sleep
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon import functions


@loader.tds
class DownloaderMod(loader.Module):
    """Downloader module"""
    strings = {'name': 'Downloader'}

    async def dlrcmd(self, message):
        """Команда .dlr <реплай на файл> <название (по желанию)> скачивает
        файл, либо сохраняет текст в файл на который был сделан реплай. """
        name = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if reply:
            await message.edit('Скачиваем...')
            if reply.text:
                text = reply.text
                fname = f'{name or message.id + reply.id}.txt'
                file = open(fname, 'w')
                file.write(text)
                file.close()
                await message.edit(
                    f'Файл сохранён как: <code>{fname}</code>.\n\nВы можете '
                    f'отправить его в этот чат с помощью команды <code>.ulf '
                    f'{fname}</code>.')
            else:
                ext = reply.file.ext
                fname = f'{name or message.id + reply.id}{ext}'
                await message.client.download_media(reply, fname)
                await message.edit(
                    f'Этот файл сохранён как: <code>{fname}</code>.\n\nВы '
                    f'можете отправить его в этот чат с помощью команды '
                    f'<code>.ulf {fname}</code>.')
        else:
            return await message.edit('Нет реплая.')

    async def ulfcmd(self, message):
        """Команда .ulf <d>* <название файла> отправляет файл в чат.\n* -
        удалить файл после отправки. """
        name = utils.get_args_raw(message)
        d = False
        if 'd ' in name:
            d = True
        if name:
            try:
                name = name.replace('d ', '')
                await message.edit(f'Отправляем <code>{name}</code>...')
                if d == True:
                    await message.client.send_file(message.to_id, f'{name}')
                    await message.edit(
                        f'Отправляем <code>{name}</code>... Успешно!\nУдаляем '
                        f'<code>{name}</code>...')
                    os.remove(name)
                    await message.edit(
                        f'Отправляем <code>{name}</code>... Успешно!\nУдаляем '
                        f'<code>{name}</code>... Успешно!')
                    await sleep(0.5)
                else:
                    await message.client.send_file(message.to_id, name)
            except:
                return await message.edit('Такой файл не существует.')
            await message.delete()
        else:
            return await message.edit('Нет аргументов.')

    async def dltiktokcmd(self, message):
        """TikTok video downloader"""
        chat = '@ttsavebot'
        reply = await message.get_reply_message()
        async with message.client.conversation(chat) as conv:
            text = utils.get_args_raw(message)
            if reply:
                text = await message.get_reply_message()
            await message.edit("<b>Downloading...</b>")
            try:
                response = conv.wait_event(
                    events.NewMessage(incoming=True, from_users=1087584961))
                response2 = conv.wait_event(
                    events.NewMessage(incoming=True, from_users=1087584961))
                response3 = conv.wait_event(
                    events.NewMessage(incoming=True, from_users=1087584961))
                mm = await message.client.send_message(chat, text)
                response = await response
                response2 = await response2
                response3 = await response3
                await mm.delete()
            except YouBlockedUserError:
                await message.edit('<code>Разблокируй @ttsavebot</code>')
                return
            await message.client.send_file(message.to_id, response3.media,
                                         reply_to=reply)
            await message.delete()
            await message.client(functions.messages.DeleteHistoryRequest(
                peer='ttsavebot',
                max_id=0,
                just_clear=False,
                revoke=True
            ))

    async def dlfilecmd(self, message):
        """File downloader (small files)"""
        await downloading(message)

    async def dlbigfilecmd(self, message):
        """File downloader (big files)"""
        await downloading(message, True)


async def downloading(message, big=False):
    args = utils.get_args_raw(message)
    reply = await message.get_reply_message()
    if not args:
        if not reply:
            await message.edit("<b>Ссылки нету!</b>")
            return
        message = reply
    else:
        message = message

    if not message.entities:
        await message.edit("<b>Ссылки нету!</b>")
        return

    urls = []
    for ent in message.entities:
        if type(ent) in [MessageEntityUrl, MessageEntityTextUrl]:
            url_ = True
            if type(ent) == MessageEntityUrl:
                offset = ent.offset
                length = ent.length
                url = message.raw_text[offset:offset + length]
            else:
                url = ent.url
            if not url.startswith("http"):
                url = "http://" + url
            urls.append(url)

    if not urls:
        await message.edit("<b>Ссылки нету!</b>")
        return
    for url in urls:
        try:
            await message.edit("<b>Загрузка...</b>\n" + url)
            fname = url.split("/")[-1]
            text = get(url, stream=big)
            if big:
                f = open(fname, "wb")
                for chunk in text.iter_content(1024):
                    f.write(chunk)
                f.close()
                await message.edit("<b>Отправка...</b>\n" + url)
                await message.client.send_file(message.to_id, open(fname, "rb"),
                                             reply_to=reply)
                os.remove(fname)
            else:
                file = io.BytesIO(text.content)
                file.name = fname
                file.seek(0)
                await message.edit("<b>Отправка...</b>\n" + url)
                await message.client.send_file(message.to_id, file, reply_to=reply)

        except Exception as e:
            await message.reply(
                "<b>Ошибка при загрузке!</b>\n" + url + "\n<code>" + str(
                    e) + "</code>")

    await message.delete()