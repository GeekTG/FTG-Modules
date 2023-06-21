# -*- coding: utf-8 -*-

# Module author: @ftgmodulesbyfl1yd

from .. import loader, utils


@loader.tds
class WelcomeMod(loader.Module):
    """Приветствие новых пользователей в чате."""

    strings = {"name": "Welcome"}

    async def client_ready(self, client, db):
        self.db = db
        self.client = client

    async def welcomecmd(self, message):
        """Включить/выключить приветствие новых пользователей в чате.
        Используй: .welcome <clearall (по желанию)>."""
        welcome = self.db.get("Welcome", "welcome", {})
        chatid = str(message.chat_id)
        args = utils.get_args_raw(message)
        if args == "clearall":
            self.db.set("Welcome", "welcome", {})
            return await message.edit(
                "<b>[Welcome Mode]</b> Все настройки модуля сброшены."
            )

        if chatid in welcome:
            welcome.pop(chatid)
            self.db.set("Welcome", "welcome", welcome)
            return await message.edit("<b>[Welcome Mode]</b> Деактивирован!")

        welcome.setdefault(chatid, {})
        welcome[chatid].setdefault("message", "Добро пожаловать в чат!")
        welcome[chatid].setdefault("is_reply", False)
        self.db.set("Welcome", "welcome", welcome)
        await message.edit("<b>[Welcome Mode]</b> Активирован!")

    async def setwelcomecmd(self, message):
        """Установить новое приветствие новых пользователей в
        чате.\nИспользуй: .setwelcome <текст (можно использовать {name}; {
        chat})>; ничего."""
        welcome = self.db.get("Welcome", "welcome", {})
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        chatid = str(message.chat_id)
        chat = await message.client.get_entity(int(chatid))
        try:
            if not args and not reply:
                return await message.edit(
                    f"<b>Приветствие новых "
                    f"пользователей в "
                    f'"{chat.title}":</b>\n\n'
                    f"<b>Статус:</b> Включено.\n"
                    f'<b>Приветствие:</b> {welcome[chatid]["message"]}\n\n '
                    f"<b>~ Установить новое приветствие "
                    f"можно с помощью команды:</b> "
                    f".setwelcome <текст>."
                )
            else:
                if reply:
                    welcome[chatid]["message"] = reply.id
                    welcome[chatid]["is_reply"] = True
                else:
                    welcome[chatid]["message"] = args
                    welcome[chatid]["is_reply"] = False
                self.db.set("Welcome", "welcome", welcome)
                return await message.edit(
                    "<b>Новое приветствие установлено " "успешно!</b>"
                )
        except KeyError:
            return await message.edit(
                f'<b>Приветствие новых пользователей в "{chat.title}":</b>\n\n '
                f"<b>Статус:</b> Отключено"
            )

    async def watcher(self, message):
        """Интересно, почему он именно watcher называется... 🤔"""
        try:
            welcome = self.db.get("Welcome", "welcome", {})
            chatid = str(message.chat_id)
            if chatid not in welcome:
                return
            if message.user_joined or message.user_added:
                user = await message.get_user()
                chat = await message.get_chat()
                if not welcome[chatid]["is_reply"]:
                    return await message.reply(
                        (welcome[chatid]["message"]).format(
                            name=user.first_name, chat=chat.title
                        )
                    )
                msg = await self.client.get_messages(
                    int(chatid), ids=welcome[chatid]["message"]
                )
                await message.reply(msg)
        except:
            pass
