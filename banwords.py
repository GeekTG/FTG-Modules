# -*- coding: utf-8 -*-

# Module author: @Fl1yd

import requests
from telethon.tl.functions.channels import EditBannedRequest as eb
from telethon.tl.types import ChatBannedRights as cb

from .. import loader, utils


@loader.tds
class BanWordsMod(loader.Module):
    """Плохие слова."""

    strings = {"name": "Ban Words"}

    async def client_ready(self, client, db):
        self.db = db

    async def addbwcmd(self, message):
        """Добавить слово в список "Плохих слов". Используй: .addbw <слово>."""
        if not message.is_private:
            chat = await message.get_chat()
            if not chat.admin_rights and not chat.creator:
                return await message.edit("<b>Я не админ здесь.</b>")
            else:
                if not chat.admin_rights.delete_messages:
                    return await message.edit("<b>У меня нет нужных прав.</b>")

        words = self.db.get("BanWords", "bws", {})
        args = utils.get_args_raw(message).lower()
        if not args:
            return await message.edit("<b>[BanWords]</b> Нет аргументов.")

        chat_id = str(message.chat_id)
        if chat_id not in words:
            words.setdefault(chat_id, [])

        if "stats" not in words:
            words.update(
                {"stats": {chat_id: {"action": "none", "antimat": False, "limit": 5}}}
            )

        if args not in words[chat_id]:
            if ", " in args:
                args = args.split(", ")
                words[chat_id].extend(args)
                self.db.set("BanWords", "bws", words)
                await message.edit(
                    f"<b>[BanWords]</b> В список чата добавлены слова - \"<code>{'; '.join(args)}</code>\"."
                )
            else:
                words[chat_id].append(args)
                self.db.set("BanWords", "bws", words)
                await message.edit(
                    f'<b>[BanWords]</b> В список чата добавлено слово - "<code>{args}</code>".'
                )
        else:
            return await message.edit(
                "<b>[BanWords]</b> Такое слово уже есть в списке слов чата."
            )

    async def rmbwcmd(self, message):
        """Удалить слово из список "Плохих слов". Используй: .rmbw <слово или all/clearall (по желанию)>.\nall - удаляет все слова из списка.\nclearall - удаляет все сохраненные данные модуля."""
        words = self.db.get("BanWords", "bws", {})
        args = utils.get_args_raw(message)
        if not args:
            return await message.edit("<b>[BanWords]</b> Нет аргументов.")
        chat_id = str(message.chat_id)

        try:
            if args == "all":
                words.pop(chat_id)
                words["stats"].pop(chat_id)
                self.db.set("BanWords", "bws", words)
                return await message.edit(
                    "<b>[BanWords]</b> Из списка чата удалены все слова."
                )

            if args == "clearall":
                self.db.set("BanWords", "bws", {})
                return await message.edit(
                    "<b>[BanWords]</b> Все списки из всех чатов были удалены."
                )

            words[chat_id].remove(args)
            if len(words[chat_id]) == 0:
                words.pop(chat_id)
            self.db.set("BanWords", "bws", words)
            await message.edit(
                f'<b>[BanWords]</b> Из списка чата удалено слово - "<code>{args}</code>".'
            )
        except (KeyError, ValueError):
            return await message.edit(
                "<b>[BanWords]</b> Этого слова нет в словаре этого чата."
            )

    async def bwscmd(self, message):
        """Посмотреть список "Плохих слов". Используй: .bws."""
        words = self.db.get("BanWords", "bws", {})
        chat_id = str(message.chat_id)

        try:
            ls = words[chat_id]
            if len(ls) == 0:
                raise KeyError
        except KeyError:
            return await message.edit("<b>[BanWords]</b> В этом чате нет списка слов.")

        word = "".join(f"• <code>{_}</code>\n" for _ in ls)
        await message.edit(f"<b>[BanWords]</b> Список слов в этом чате:\n\n{word}")

    async def bwstatscmd(self, message):
        """Статистика "Плохих слов". Используй: .bwstats <clear* (по желанию)>.\n* - сбросить настройки чата."""
        words = self.db.get("BanWords", "bws", {})
        chat_id = str(message.chat_id)
        args = utils.get_args_raw(message)

        if args == "clear":
            try:
                words["stats"].pop(chat_id)
                words["stats"].update(
                    {chat_id: {"antimat": False, "action": "none", "limit": 5}}
                )
                self.db.set("BanWords", "bws", words)
                return await message.edit("<b>[BanWords]</b> Настройки чата сброшены.")
            except KeyError:
                return await message.edit(
                    "<b>[BanWords]</b> Нет статистики пользователей."
                )

        try:
            w = ""
            for _ in words["stats"][chat_id]:
                if (
                    _ not in ["action", "antimat", "limit"]
                    and words["stats"][chat_id][_] != 0
                ):
                    user = await message.client.get_entity(int(_))
                    w += f'• <a href="tg://user?id={int(_)}">{user.first_name}</a>: <code>{words["stats"][chat_id][_]}</code>\n'
            return await message.edit(
                f"<b>[BanWords]</b> Кто использовал спец.слова:\n\n{w}"
            )
        except KeyError:
            return await message.edit(
                "<b>[BanWords]</b> В этом чате нет тех, кто использовал спец.слова."
            )

    async def swbwcmd(self, message):
        """Переключить режим "Плохих слов". Используй: .swbw <режим(antimat/kick/ban/mute/none)>, или .swbw limit <кол-во:int>."""
        if not message.is_private:
            chat = await message.get_chat()
            if chat.admin_rights or chat.creator:
                if chat.admin_rights.delete_messages is False:
                    return await message.edit("<b>У меня нет нужных прав.</b>")

            else:
                return await message.edit("<b>Я не админ здесь.</b>")
        words = self.db.get("BanWords", "bws", {})
        args = utils.get_args_raw(message)
        chat_id = str(message.chat_id)

        if chat_id not in words:
            words.setdefault(chat_id, [])
        if "stats" not in words:
            words.update(
                {"stats": {chat_id: {"action": "none", "antimat": False, "limit": 5}}}
            )

        if not args:
            return await message.edit(
                f"<b>[BanWords]</b> Настройки чата:\n\n"
                f"<b>Лимит спец.слов:</b> {words['stats'][chat_id]['limit']}\n"
                f"<b>При достижении лимита спец.слов будет выполняться действие:</b> {words['stats'][chat_id]['action']}\n"
                f"<b>Статус режима \"антимат\":</b> {words['stats'][chat_id]['antimat']}"
            )
        if "limit" in args:
            try:
                limit = int(utils.get_args_raw(message).split(" ", 1)[1])
                words["stats"][chat_id].update({"limit": limit})
                self.db.set("BanWords", "bws", words)
                return await message.edit(
                    f"<b>[BanWords]</b> Лимит спец.слов был установлен на {words['stats'][chat_id]['limit']}."
                )
            except (IndexError, ValueError):
                return await message.edit(
                    f"<b>[BanWords]</b> Лимит спец.слов в этом чате - {words['stats'][chat_id]['limit']}\n"
                    f"Установить новый можно командой .bwsw limit <кол-во:int>."
                )

        if args == "antimat":
            if words["stats"][chat_id]["antimat"]:
                words["stats"][chat_id]["antimat"] = False
                self.db.set("BanWords", "bws", words)
                return await message.edit('<b>[BanWords]</b> Режим "антимат" выключен.')
            else:
                words["stats"][chat_id]["antimat"] = True
                self.db.set("BanWords", "bws", words)
                return await message.edit('<b>[BanWords]</b> Режим "антимат" включен.')
        else:
            if args == "kick":
                words["stats"][chat_id].update({"action": "kick"})
            elif args == "ban":
                words["stats"][chat_id].update({"action": "ban"})
            elif args == "mute":
                words["stats"][chat_id].update({"action": "mute"})
            elif args == "none":
                words["stats"][chat_id].update({"action": "none"})
            else:
                return await message.edit(
                    "<b>[BanWords]</b> Такого режима нет в списке. Есть: kick/ban/mute/none."
                )
            self.db.set("BanWords", "bws", words)
            return await message.edit(
                f"<b>[BanWords]</b> Теперь при достижении лимита спец.слов будет выполняться действие: {words['stats'][chat_id]['action']}."
            )

    async def watcher(self, message):
        """Обновление от 19.03: Фикс говнокода."""
        try:
            if message.sender_id == (await message.client.get_me()).id:
                return
            words = self.db.get("BanWords", "bws", {})
            chat_id = str(message.chat_id)
            user_id = str(message.sender_id)
            user = await message.client.get_entity(int(user_id))

            if chat_id not in str(words):
                return
            action = words["stats"][chat_id]["action"]
            if words["stats"][chat_id]["antimat"] is True:
                r = requests.get("https://api.fl1yd.ml/badwords")
                ls = r.text.split(", ")
            else:
                ls = words[chat_id]

            for _ in ls:
                if _.lower() in message.raw_text.lower().split():
                    if user_id not in words["stats"][chat_id]:
                        words["stats"][chat_id].setdefault(user_id, 0)

                    count = words["stats"][chat_id][user_id]
                    words["stats"][chat_id].update({user_id: count + 1})
                    self.db.set("BanWords", "bws", words)

                    if count == words["stats"][chat_id]["limit"]:
                        try:
                            if action == "kick":
                                await message.client.kick_participant(
                                    int(chat_id), int(user_id)
                                )
                            elif action == "ban":
                                await message.client(
                                    eb(
                                        int(chat_id),
                                        user_id,
                                        cb(until_date=None, view_messages=True),
                                    )
                                )
                            elif action == "mute":
                                await message.client(
                                    eb(
                                        int(chat_id),
                                        user.id,
                                        cb(until_date=True, send_messages=True),
                                    )
                                )
                            words["stats"][chat_id].pop(user_id)
                            self.db.set("BanWords", "bws", words)
                            await message.respond(
                                f"<b>[BanWords]</b> {user.first_name} достиг лимит ({words['stats'][chat_id]['limit']}) спец.слова, и был ограничен в чате."
                            )
                        except:
                            pass
                    await message.client.delete_messages(message.chat_id, message.id)
        except:
            pass
