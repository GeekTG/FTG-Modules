from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from .. import loader, utils
import asyncio

def register(cb):
    cb(ValuteMod())
class ValuteMod(loader.Module):
    """Конвертер Валют"""
    strings = {'name': 'ERTB Converter'}
    async def ertbcmd(self, message):
        """.ertb + количество + валюта"""
        state = utils.get_args_raw(message)
        await message.edit("<b>Данные получены</b>")
        chat = '@exchange_rates_vsk_bot'
        async with message.client.conversation(chat) as conv:
            try:
                await message.edit("<b>Конвертирую...</b>")
                response = conv.wait_event(events.NewMessage(incoming=True, from_users=1210425892))
                bot_send_message = await message.client.send_message(chat, format(state))
                bot_response = response = await response
            except YouBlockedUserError:
                await message.edit('<b>Убери из ЧС:</b> ' + chat)
                return
            await bot_send_message.delete()
            await message.edit(response.text)
            await bot_response.delete()
