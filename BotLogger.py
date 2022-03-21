"""
    █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
    █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█

    Copyright 2022 t.me/hikariatama
    Licensed under the Creative Commons CC BY-NC-ND 4.0

    Full license text can be found at:
    https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode

    Human-friendly one:
    https://creativecommons.org/licenses/by-nc-nd/4.0
"""

# meta pic: https://img.icons8.com/fluency/50/000000/event-log.png
# meta developer: @hikariatama

from .. import loader, utils, main
import logging
import time
import traceback
import asyncio

from telethon.tl.functions.channels import (
    InviteToChannelRequest,
    EditAdminRequest,
    CreateChannelRequest,
    EditPhotoRequest,
)

import requests
from telethon.tl.types import ChatAdminRights, Message

# requires: pytelegrambotapi


def chunks(lst: list, n: int) -> list:
    return [lst[i : i + n] for i in range(0, len(lst), n)]


@loader.tds
class BotLoggerMod(loader.Module):
    """Transfer your userbot logs to classic bot"""

    strings = {
        "name": "BotLogger",
        "no_token": "🚫 <b>You need to specify token</b>",
        "installing": "⛎ <b>Configuring logger...</b>",
        "installed": "🥳 <b>Logging installed!</b>",
        "error": "🚫 <b>Error occurred while installing logger!</b>",
    }

    async def install_logging(self, inline: bool) -> None:
        if not inline:
            import telebot

            bot = telebot.TeleBot(self.token)

        _formatter = logging.Formatter

        class MemoryHandler(logging.Handler):
            def __init__(self, target, capacity, person, mod):
                super().__init__(0)
                self.target = target
                self.capacity = capacity
                self.buffer = []
                self.handledbuffer = []
                self.tg_buff = ""
                self.start_time = time.time()
                self.logging_started = False
                self.lvl = logging.WARNING  # Default loglevel
                self._me = person
                self.mod = mod
                self._queue = []

            def setLevel(self, level):
                self.lvl = level

            def dump(self):
                return self.handledbuffer + self.buffer

            def dumps(self, lvl=0):
                return [
                    self.target.format(record)
                    for record in (self.buffer + self.handledbuffer)
                    if record.levelno >= lvl
                ]

            async def emit_to_tg(self):
                for chunk in chunks(
                    self.tg_buff.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;"),
                    4083,
                ):
                    self._queue += [f"<code>{chunk}</code>"]

                self.tg_buff = ""

            async def sender(self):
                chunk = self._queue.pop(0)

                if not chunk:
                    return

                if not inline:
                    await utils.run_sync(
                        bot.send_message,
                        self.mod._logchat,
                        f"<code>{chunk}</code>",
                        parse_mode="HTML",
                        disable_notification=True,
                    )
                else:
                    await self.mod.inline._bot.send_message(
                        self.mod._logchat,
                        f"<code>{chunk}</code>",
                        parse_mode="HTML",
                        disable_notification=True,
                    )

            def emit(self, record):
                if record.exc_info is not None:
                    exc = (
                        "\n🚫 Traceback:\n"
                        + "\n".join(
                            [
                                line
                                for line in traceback.format_exception(
                                    *record.exc_info
                                )[1:]
                                if "friendly-telegram/dispatcher.py" not in line
                                and "    await func(message)" not in line
                            ]
                        ).strip()
                    )
                else:
                    exc = ""

                if record.levelno >= 20:
                    try:
                        self.tg_buff += f"[{record.levelname}] {record.name}: {str(record.msg) % record.args}{exc}\n"
                    except TypeError:
                        self.tg_buff += (
                            f"[{record.levelname}] {record.name}: {record.msg}\n"
                        )

                    if exc:
                        asyncio.ensure_future(self.emit_to_tg())

                if len(self.buffer) + len(self.handledbuffer) >= self.capacity:
                    if self.handledbuffer:
                        del self.handledbuffer[0]
                    else:
                        del self.buffer[0]

                self.buffer += [record]

                if record.levelno >= self.lvl >= 0:
                    self.acquire()
                    try:
                        for precord in self.buffer:
                            self.target.handle(precord)
                        self.handledbuffer = (
                            self.handledbuffer[-(self.capacity - len(self.buffer)) :]
                            + self.buffer
                        )
                        self.buffer = []
                    finally:
                        self.release()

        async def emit_to_tg(handler):
            while True:
                if handler.tg_buff:
                    await handler.emit_to_tg()

                await asyncio.sleep(5)

        async def sender(handler):
            while True:
                if handler._queue:
                    await handler.sender()

                await asyncio.sleep(1)

        formatter = _formatter(logging.BASIC_FORMAT, "")
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logging.getLogger().handlers = []
        handl = MemoryHandler(handler, 500, self._me, self)

        logger = logging.getLogger()

        while logger.hasHandlers():
            logger.removeHandler(logger.handlers[0])

        logger.addHandler(handl)
        logger.setLevel(logging.NOTSET)
        logging.getLogger("telethon.client.uploads").setLevel(logging.WARNING)
        logging.getLogger("telethon.client.downloads").setLevel(logging.WARNING)
        logging.getLogger("telethon.network.mtprotosender").setLevel(logging.WARNING)
        logging.getLogger("telethon.client.telegrambaseclient").setLevel(
            logging.WARNING
        )
        # logging.getLogger("").setLevel(logging.WARNING)
        # logging.getLogger("").setLevel(logging.WARNING)
        logging.captureWarnings(True)

        chat, is_new = await self.find_db()
        self._logchat = int(f"-100{chat.id}")

        self._task = asyncio.ensure_future(emit_to_tg(handl))
        self._task2 = asyncio.ensure_future(sender(handl))

        if not is_new:
            logger.info("Bot logging installed")
            await handl.emit_to_tg()
            return

        logger.info("New logging chat created, init setup...")
        await handl.emit_to_tg()

        bot_username = (
            self.inline._bot_username if self._inline else bot.get_me().username
        )

        try:
            await self.client(InviteToChannelRequest(chat, [bot_username]))
        except Exception:
            logger.warning("Unable to invite logger to chat. Maybe he's already there?")

        try:
            await self.client(
                EditAdminRequest(
                    channel=chat,
                    user_id=bot_username,
                    admin_rights=ChatAdminRights(ban_users=True),
                    rank="Logger",
                )
            )
        except Exception:
            pass

        try:
            f = (
                await utils.run_sync(requests.get, "https://i.imgur.com/MWoMKp0.jpeg")
            ).content

            await self.client(
                EditPhotoRequest(
                    channel=chat,
                    photo=await self.client.upload_file(f, file_name="photo.jpg"),
                )
            )
        except Exception:
            pass

        logger.info("Bot logging installed")

    async def find_db(self) -> tuple:
        ver_ = "Hikka" if hasattr(main, "__version__") else "FTG"

        async for d in self.client.iter_dialogs():
            if d.title == f"{ver_.lower()}-logs":
                return (d.entity, False)

        return (
            (
                await self.client(
                    CreateChannelRequest(
                        f"{ver_.lower()}-logs",
                        f"👩‍🎤 Your {ver_} logs will appear in this chat",
                        megagroup=True,
                    )
                )
            ).chats[0],
            True,
        )

    async def client_ready(self, client, db) -> None:
        self.client = client
        self.db = db
        self._me = (await client.get_me()).id

        self.token = db.get(self.strings("name"), "token", False)
        self._inline = hasattr(self, "inline") and self.inline.init_complete

        if not self._inline:
            setattr(self, "setlogtokencmd", self.setlogtokencmd_)

        if not self.token and not self._inline:
            return

        await self.install_logging(self._inline)

    async def on_unload(self) -> None:
        if hasattr(self, "_task") and self._task:
            self._task.cancel()

        if hasattr(self, "_task2") and self._task2:
            self._task2.cancel()

    async def setlogtokencmd_(self, message: Message) -> None:
        """<BOT token> - Install logging
        1. Create bot in @BotFather
        2. Write any message to your bot
        3. Commit changes via .setlogtoken <token>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_token"))
            return

        try:
            import telebot

            bot = telebot.TeleBot(args)
            bot.send_message(self._me, self.strings("installing"), parse_mode="HTML")
        except Exception:
            await utils.answer(message, self.strings("error"))
            return

        self.token = args
        self.db.set(self.strings("name"), "token", args)

        await self.install_logging(self._inline)
        bot.send_message(self._me, self.strings("installed"), parse_mode="HTML")

        await utils.answer(message, self.strings("installed"))
