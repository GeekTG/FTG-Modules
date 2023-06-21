# -*- coding: utf-8 -*-

# Module author: @trololo_1

import subprocess

try:
    import emoji
except:
    mod_inst = subprocess.Popen("pip install emoji", shell=True)
    mod_inst.wait()
    import emoji

import string

from .. import loader, utils


@loader.tds
class RPMod(loader.Module):
    """Модуль RPMod + дополнение после команды.+реплика.(указывать реплику на второй строке)"""

    strings = {"name": "RPMod"}

    async def client_ready(self, client, db):
        self.db = db
        if not self.db.get("RPMod", "exlist", False):
            exlist = []
            self.db.set("RPMod", "exlist", exlist)
        if not self.db.get("RPMod", "status", False):
            self.db.get("RPMod", "status", 1)
        if not self.db.get("RPMod", "rprezjim", False):
            self.db.set("RPMod", "rprezjim", 1)
        if not self.db.get("RPMod", "rpnick", False):
            me = await client.get_me()
            self.db.set("RPMod", "rpnick", me.first_name)
        if not self.db.get("RPMod", "rpcomands", False):
            comands = {
                "чмок": "чмокнул",
                "кусь": "кусьнул",
                "пиц": "радостные звуки питсы",
                "поцеловать": "поцеловал",
                "ррр": "злые звуки питсы",
                "выебать": "выебал",
                "трахнуть": "трахнул",
                "выпороть": "выпорол",
                "шлепнуть": "шлепнул",
                "отлизать": "отлизал у",
                "прижать": "прижал",
                "погладить": "погладил",
                "да.": "пизда",
                "где.": "в пизде",
                "нет.": "пидора ответ",
                "бывает.": "ну это пиздец конечно на самом деле",
                "мрр.": "мурчание питсы",
                "ррррр.": "злая питса",
                "обнять": "обнял",
            }
            self.db.set("RPMod", "rpcomands", comands)
        if not self.db.get("RPMod", "rpemoji", False):
            emojiComands = {"лизь": "👅"}
            self.db.set("RPMod", "rpemoji", emojiComands)

    async def dobrpcmd(self, message):
        """Используй: .dobrp (команда) / (действие) / (эмодзи) чтобы добавить команду. Можно и без эмодзи(но и второго
        разделителя). Используй только одно слово в качестве команды."""
        await message.edit("<code>Команда добавляется...</coode>")
        args = utils.get_args_raw(message)
        dict_rp = self.db.get("RPMod", "rpcomands")
        dict_rp_copy = dict_rp.copy()
        try:
            key_rp = str(args.split("/")[0]).strip()
            value_rp = str(args.split("/", maxsplit=2)[1]).strip()
            lenght_args = []
            for i in args.split("/"):
                lenght_args.append(i)
            count_emoji = 0

            if len(lenght_args) >= 3:
                emoji_rp = str(args.split("/", maxsplit=2)[2]).strip()
                dict_emoji_rp = self.db.get("RPMod", "rpemoji")
                dict_emoji_rp_copy = dict_emoji_rp.copy()
                r = emoji_rp
                lst = []
                count_emoji = 1
                for x in r:
                    if x in emoji.UNICODE_EMOJI["en"].keys():
                        lst.append(x)
                    if (
                        x.isalpha()
                        or x.isspace()
                        or x.isdigit()
                        or x in string.punctuation
                    ):
                        await message.edit(
                            "<b>Были введены не только эмодзи(пробел тоже символ). </b>"
                        )
                        return
                if len(lst) > 3:
                    await message.edit("<b>Было введено более 3 эмодзи. </b>")
                    return
                if not emoji_rp or not emoji_rp.strip():
                    await message.edit(
                        "<b>Разделитель для эмодзи есть, а их нет? хм.</b>"
                    )
                    return
                if len(lst) == 0:
                    await message.edit(
                        "<b>В 3 секции были введены не эмодзи. Если были введены эмодзи, но всё равно выходит ошибка, обратись к: </b>@trololo_1"
                    )
                    return

            key_len = [len(x) for x in key_rp.split()]

            if len(dict_rp) >= 70:
                await message.edit("<b>Достигнут лимит рп команд.</b>")
            else:
                if not key_rp or not key_rp.strip():
                    await message.edit("<b>Вы не ввели название рп команды.</b>")
                else:
                    if not value_rp or not value_rp.strip():
                        await message.edit(
                            "<b>Вы не ввели действие для рп команды.</b>"
                        )
                    else:
                        if int(len(key_len)) > 1:
                            await message.edit(
                                "<b>В качестве рп команды было введено больше одного слова.</b>"
                            )
                        else:
                            if key_rp == "all":
                                await message.edit(
                                    "<b>Использовать '<code>all</code>' в качестве названия команды запрещено!</b>"
                                )
                            else:
                                if count_emoji == 1:
                                    dict_emoji_rp_copy[key_rp] = emoji_rp
                                    dict_rp_copy[key_rp] = value_rp
                                    self.db.set("RPMod", "rpcomands", dict_rp_copy)
                                    self.db.set("RPMod", "rpemoji", dict_emoji_rp_copy)
                                    await message.edit(
                                        f"<b>Команда '<code>{key_rp}</code>' успешно добавлена с эмодзи '{emoji_rp}'!</b>"
                                    )
                                else:
                                    dict_rp_copy[key_rp] = value_rp
                                    self.db.set("RPMod", "rpcomands", dict_rp_copy)
                                    await message.edit(
                                        f"<b>Команда '<code>{key_rp}</code>' успешно добавлена!</b>"
                                    )
        except:
            await message.edit(
                "<b>Вы не ввели разделитель /, либо вовсе ничего не ввели.</b>"
            )

    async def delrpcmd(self, message):
        """Используй: .delrp (команда) чтобы удалить команду.\n Используй: .delrp all чтобы удалить все команды."""
        await message.edit("Команда удаляется..")
        args = utils.get_args_raw(message)
        dict_rp = self.db.get("RPMod", "rpcomands")
        dict_emoji_rp = self.db.get("RPMod", "rpemoji")
        dict_emoji_rp_copy = dict_emoji_rp.copy()
        dict_rp_copy = dict_rp.copy()

        key_rp = str(args)
        count = 0
        if key_rp == "all":
            dict_rp_copy.clear()
            dict_emoji_rp_copy.clear()
            self.db.set("RPMod", "rpcomands", dict_rp_copy)
            self.db.set("RPMod", "rpemoji", dict_emoji_rp_copy)
            await message.edit("<b>Список рп команд очищен.</b>")
            return
        if not key_rp or not key_rp.strip():
            await message.edit("<b>Вы не ввели команду.</b>")
        else:
            try:
                for i in dict_emoji_rp_copy:
                    if i == key_rp:
                        count = 1
                        break
                if count == 1:
                    dict_rp_copy.pop(key_rp)
                    dict_emoji_rp_copy.pop(key_rp)
                    self.db.set("RPMod", "rpcomands", dict_rp_copy)
                    self.db.set("RPMod", "rpemoji", dict_emoji_rp_copy)
                else:
                    dict_rp_copy.pop(key_rp)
                    self.db.set("RPMod", "rpcomands", dict_rp_copy)
                await message.edit(
                    f"<b>Команда '<code>{key_rp}</code>' успешно удалена!</b>"
                )
            except KeyError:
                await message.edit("<b>Команда не найдена.</b>")

    async def rpmodcmd(self, message):
        """Используй: .rpmod чтобы включить/выключить RP режим.\nИспользуй: .rpmod toggle чтобы сменить режим на отправку или изменение смс."""
        status = self.db.get("RPMod", "status")
        rezjim = self.db.get("RPMod", "rprezjim")
        args = utils.get_args_raw(message)
        if not args:
            if status == 1:
                self.db.set("RPMod", "status", 2)
                await message.edit("<b>RP Режим <code>выключен</code></b>")
            else:
                self.db.set("RPMod", "status", 1)
                await message.edit("<b>RP Режим <code>включен</code></b>")
        elif args.strip() == "toggle":
            if rezjim == 1:
                self.db.set("RPMod", "rprezjim", 2)
                await message.edit(
                    "<b>RP Режим изменён на <code>отправку смс.</code></b>"
                )
            else:
                self.db.set("RPMod", "rprezjim", 1)
                await message.edit(
                    "<b>RP Режим изменён на <code>изменение смс.</code></b>"
                )
        else:
            await message.edit("Что то не так.. ")

    async def rplistcmd(self, message):
        """Используй: .rplist чтобы посмотреть список рп команд."""
        com = self.db.get("RPMod", "rpcomands")
        emojies = self.db.get("RPMod", "rpemoji")
        l = len(com)

        listComands = f"У вас рп команд: <b>{l}</b> из <b>70</b>. "
        if len(com) == 0:
            await message.edit("<b>Увы, у вас нету рп команд. :(</b>")
            return
        for i in com:
            if i in emojies.keys():
                listComands += f"\n• <b><code>{i}</code> - {com[i]} |</b> {emojies[i]}"
            else:
                listComands += f"\n• <b><code>{i}</code> - {com[i]}</b>"
        await message.edit(listComands)

    async def rpnickcmd(self, message):
        "Используй: .rpnick (ник) чтобы сменить свой ник. Если без аргументов, то вернётся ник из тг."
        r = utils.get_args_raw(message).strip()
        if not r:
            me = await message.client.get_me()
            self.db.set("RPMod", "rpnick", me.first_name)
            await message.edit(f"<b>Ник изменён на {me.first_name}</b>")
            return
        lst = []
        nick = ""
        for x in r:
            if x in emoji.UNICODE_EMOJI["en"].keys():
                lst.append(x)
            if x not in emoji.UNICODE_EMOJI["en"].keys():
                nick += x
        if len(lst) > 3:
            await message.edit(f"<b>Ник '{r}' содержит более трёх эмодзи.</b>")
        else:
            if len(lst) + len(nick) >= 45:
                await message.edit(
                    "<b>Ник превышает лимит в 45 символов(возможно эмодзи имеют длину более 1 символа).</b>"
                )
            else:
                self.db.set("RPMod", "rpnick", r)
                await message.edit(f"<b>Ник изменён на {r}</b>")

    async def rpbackcmd(self, message):
        "Используй: .rpback чтобы выгрузить список своих рп команд.\nИспользуй .rpback / (список чьих то команд) / (список чьих то эмодзи) чтобы добавить себе список команд. можно без эмодзи, но первый разделитель обязателен."
        args = utils.get_args_raw(message).strip()
        comand = self.db.get("RPMod", "rpcomands")
        emojies = self.db.get("RPMod", "rpemoji")
        if not args:
            if len(comand) == 0:
                await message.edit("<b>У вас нет рп команд.</b>")
            elif len(emojies) == 0:
                await message.edit(f"<code>.rpback / {comand} </code>")
            else:
                await message.edit(f"<code>.rpback / {comand} / {emojies}</code>")
        if args:
            try:
                comands = str(args.split("/")[1]).strip()

                lenght_args = []
                for i in args.split("/"):
                    lenght_args.append(i)
                count_emoji = 0

                if len(lenght_args) >= 3:
                    emoji_rp = str(args.split("/")[2]).strip()
                    count_emoji = 1
                    emj = eval(emoji_rp)
                    if not dict == type(emj):
                        await message.edit(
                            "<b>Синтаксис секции эмодзи не является корректным(словарём в питоне).</b>"
                        )
                    else:
                        if len(emj) == 0:
                            await message.edit("<b>Словарь эмодзи пуст.</b>")
                            return
                        for x in emj.values():
                            lst = []
                            if x in emoji.UNICODE_EMOJI["en"].keys():
                                lst.append(x)
                            if not x or not x.strip():
                                await message.edit(
                                    "<b>Пустое значение в словаре для эмодзи? Да ты гений.</b>"
                                )
                                return
                            if (
                                x.isalpha()
                                or x.isspace()
                                or x.isdigit()
                                or x in string.punctuation
                            ):
                                await message.edit(
                                    "<b>Были введены не только эмодзи в словаре для эмодзи(пробел тоже символ). </b>"
                                )
                                return
                            if len(lst) > 3:
                                await message.edit(
                                    "<b>Было введено более 3 эмодзи в словаре для эмодзи. </b>"
                                )
                                return

                        for x in emj:
                            key_len = [len(l) for l in x.split()]
                            if int(len(key_len)) > 1:
                                await message.edit(
                                    "<b>В качестве ключа было введено больше одного слова в словаре эмодзи.</b>"
                                )
                                return
                            if not x or not x.strip():
                                await message.edit(
                                    "<b>Пустой ключ в словаре для эмодзи? Да ты умничка.</b>"
                                )
                                return
                com = eval(comands)
                if dict == type(com):
                    if len(com) == 0:
                        await message.edit("<b>Словарь команд пуст.</b>")
                        return
                    for x in com:
                        key_len_cmd = [len(l) for l in x.split()]
                        if int(len(key_len_cmd)) > 1:
                            await message.edit(
                                "<b>В качестве ключа было введено больше одного слова в словаре команд.</b>"
                            )
                            return
                        if not x or not x.strip():
                            await message.edit(
                                "<b>Пустой ключ в словаре для команд? Мой хороший, так дела не делаются.</b>"
                            )
                            return
                    for x in com.values():
                        if not x or not x.strip():
                            await message.edit(
                                "<b>Пустое значение в словаре для команд? Не сегодня, мой золотой.</b>"
                            )
                            return
                    if count_emoji == 1:
                        comand_copy = comand.copy()
                        emojies_copy = emojies.copy()
                        merge_emj = {**emojies_copy, **emj}
                        merge_com = {**comand_copy, **com}
                        self.db.set("RPMod", "rpcomands", merge_com)
                        self.db.set("RPMod", "rpemoji", merge_emj)
                        await message.edit(
                            "<b>Успешное обновлени словаря команд и эмодзи! Вы можете просмотреть их благодаря команде '<code>.rplist</code>'.</b>"
                        )
                    else:
                        comand_copy = comand.copy()
                        merge_com = {**comand_copy, **com}
                        self.db.set("RPMod", "rpcomands", merge_com)
                        await message.edit(
                            "<b>Успешное обновлени словаря команд! Вы можете просмотреть его благодаря команде '<code>.rplist</code>'.</b>"
                        )
                else:
                    await message.edit(
                        "<b>Синтаксис секции команд не является корректным(словарём в питоне).</b>"
                    )
            except:
                await message.edit(
                    "<b>Что то не так с разделителями /.\nЛибо не корректный словарь.(либо вообще пусто)</b>"
                )

    async def rpblockcmd(self, message):
        """Используй: .rpblock чтобы добавить/удалить исключение(использовать в нужном чате).\nИспользуй: .rpblock list чтобы просмотреть чаты в исключениях.\nИспользуй .rpblock (ид) чтобы удалить чат из исключений."""
        args = utils.get_args_raw(message)
        ex = self.db.get("RPMod", "exlist")
        ex_copy = ex.copy()
        if not args:
            a = await message.client.get_entity(message.to_id)
            if a.id in ex_copy:
                ex_copy.remove(a.id)
                self.db.set("RPMod", "exlist", ex_copy)
                try:
                    name = a.title
                except:
                    name = a.first_name
                await message.edit(
                    f"<i>Чат <b><u>{name}</u></b>(<code>{a.id}</code>) удален из исключений.</i>"
                )
            else:
                ex_copy.append(a.id)
                self.db.set("RPMod", "exlist", ex_copy)
                try:
                    name = a.title
                except:
                    name = a.first_name
                await message.edit(
                    f"<i>Чат <b><u>{name}</u></b>(<code>{a.id}</code>) добавлен в исключения.</i>"
                )
        elif args.isdigit():
            args = args.strip()
            args = int(args)
            if args in ex_copy:
                a = await message.client.get_entity(args)
                ex_copy.remove(args)
                self.db.set("RPMod", "exlist", ex_copy)
                try:
                    name = a.title
                except:
                    name = a.first_name
                await message.edit(
                    f"<i>Чат <b><u>{name}</u></b>(<code>{args}</code>) удален из исключений.</i>"
                )
            else:
                await message.edit("<b>Неверный ид.</b>")
        elif args == "list":
            ex_len = len(ex_copy)
            if ex_len == 0:
                await message.edit("<b>Список исключений пуст.</b>")
                return
            sms = f"<i> Чаты, которые есть в исключениях({ex_len}):</i>"
            for i in ex_copy:
                a = await message.client.get_entity(i)
                try:
                    name = a.title
                except:
                    name = a.first_name
                sms += f"\n• <b><u>{name}</u></b>(<code>{i}</code>)"
            await message.edit(sms)
        else:
            await message.edit("Что то пошло не так..")

    async def watcher(self, message):
        try:
            status = self.db.get("RPMod", "status")
            comand = self.db.get("RPMod", "rpcomands")
            rezjim = self.db.get("RPMod", "rprezjim")
            emojies = self.db.get("RPMod", "rpemoji")
            nick = self.db.get("RPMod", "rpnick")
            ex = self.db.get("RPMod", "exlist")

            args = message.text.lower()
            chat_rp = await message.client.get_entity(message.to_id)
            lines = []
            detail = []
            round = 1
            for line in args.splitlines():
                lines.append(line)
            for i in lines[0].split(" ", maxsplit=1):
                if round == 1:
                    detail.append(i)
                else:
                    detail.append(" " + i)
                round += 1
            if len(detail) < 2:
                detail.append(" ")
            reply = await message.get_reply_message()
            user = await message.client.get_entity(reply.sender_id)
            me = await message.client.get_me()
            if status == 1:
                if chat_rp.id not in ex:
                    if message.sender_id == me.id:
                        for i in comand:
                            if detail[0] == i:
                                if detail[0] in emojies.keys():
                                    if len(lines) < 2:
                                        if rezjim == 1:
                                            await message.edit(
                                                f"{emojies[detail[0]]} | <a href=tg://user?id={me.id}>{nick}</a> {comand[detail[0]]} <a href=tg://user?id={user.id}>{user.first_name}</a>"
                                                + detail[1]
                                            )
                                        else:
                                            await message.respond(
                                                f"{emojies[detail[0]]} | <a href=tg://user?id={me.id}>{nick}</a> {comand[detail[0]]} <a href=tg://user?id={user.id}>{user.first_name}</a>"
                                                + detail[1]
                                            )
                                    else:
                                        if rezjim == 1:
                                            await message.edit(
                                                f"{emojies[detail[0]]} | <a href=tg://user?id={me.id}>{nick}</a> {comand[detail[0]]} <a href=tg://user?id={user.id}>{user.first_name}</a>"
                                                + detail[1]
                                                + f"\n<b>С репликой: </b>{lines[1]}"
                                            )
                                        else:
                                            await message.respond(
                                                f"{emojies[detail[0]]} | <a href=tg://user?id={me.id}>{nick}</a> {comand[detail[0]]} <a href=tg://user?id={user.id}>{user.first_name}</a>"
                                                + detail[1]
                                                + f"\n<b>С репликой: </b>{lines[1]}"
                                            )
                                else:
                                    if len(lines) < 2:
                                        if rezjim == 1:
                                            await message.edit(
                                                f"<a href=tg://user?id={me.id}>{nick}</a> {comand[detail[0]]} <a href=tg://user?id={user.id}>{user.first_name}</a>"
                                                + detail[1]
                                            )
                                        else:
                                            await message.respond(
                                                f"<a href=tg://user?id={me.id}>{nick}</a> {comand[detail[0]]} <a href=tg://user?id={user.id}>{user.first_name}</a>"
                                                + detail[1]
                                            )
                                    else:
                                        if rezjim == 1:
                                            await message.edit(
                                                f"<a href=tg://user?id={me.id}>{nick}</a> {comand[detail[0]]} <a href=tg://user?id={user.id}>{user.first_name}</a>"
                                                + detail[1]
                                                + f"\n<b>С репликой: </b>{lines[1]}"
                                            )
                                        else:
                                            await message.respond(
                                                f"<a href=tg://user?id={me.id}>{nick}</a> {comand[detail[0]]} <a href=tg://user?id={user.id}>{user.first_name}</a>"
                                                + detail[1]
                                                + f"\n<b>С репликой: </b>{lines[1]}"
                                            )
        except:
            pass
