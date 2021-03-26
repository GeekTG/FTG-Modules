# -*- coding: utf-8 -*-

# Module author: @Fl1yd

import io
import time

from PIL import Image
from telethon.errors import ChatAdminRequiredError, UserAdminInvalidError, PhotoCropSizeSmallError
from telethon.tl.functions.channels import EditAdminRequest, EditBannedRequest, EditPhotoRequest, \
    DeleteUserHistoryRequest
from telethon.tl.functions.messages import EditChatAdminRequest
from telethon.tl.types import ChatAdminRights, ChatBannedRights

from .. import loader, utils

# ================== КОНСТАНТЫ ========================

DEMOTE_RIGHTS = ChatAdminRights(post_messages=None,
                                add_admins=None,
                                invite_users=None,
                                change_info=None,
                                ban_users=None,
                                delete_messages=None,
                                pin_messages=None,
                                edit_messages=None)

UNMUTE_RIGHTS = ChatBannedRights(until_date=None,
                                 view_messages=None,
                                 send_messages=False,
                                 send_media=False,
                                 send_stickers=False,
                                 send_gifs=False,
                                 send_games=False,
                                 send_inline=False,
                                 embed_links=False)

BANNED_RIGHTS = ChatBannedRights(until_date=None,
                                 view_messages=True,
                                 send_messages=True,
                                 send_media=True,
                                 send_stickers=True,
                                 send_gifs=True,
                                 send_games=True,
                                 send_inline=True,
                                 embed_links=True)

UNBAN_RIGHTS = ChatBannedRights(until_date=None,
                                view_messages=None,
                                send_messages=None,
                                send_media=None,
                                send_stickers=None,
                                send_gifs=None,
                                send_games=None,
                                send_inline=None,
                                embed_links=None)


# =====================================================

@loader.tds
class AdminToolsMod(loader.Module):
    """Администрирование чата"""
    strings = {'name': 'AdminTools',
               'no_reply': '<b>Нет реплая на картинку/стикер.</b>',
               'not_pic': '<b>Это не картинка/стикер</b>',
               'wait': '<b>Минуточку...</b>',
               'pic_so_small': '<b>Картинка слишком маленькая, попробуйте другую.</b>',
               'pic_changed': '<b>Картинка чата изменена.</b>',
               'promote_none': '<b>Некого повышать.</b>',
               'who': '<b>Кто это?</b>',
               'not_admin': '<b>Я здесь не админ.</b>',
               'promoted': '<b>{} повышен в правах администратора.\nРанг: {}</b>',
               'wtf_is_it': '<b>Что это?</b>',
               'this_isn`t_a_chat': '<b>Это не чат!</b>',
               'demote_none': '<b>Некого понижать.</b>',
               'demoted': '<b>{} понижен в правах администратора.</b>',
               'pinning': '<b>Пин...</b>',
               'pin_none': '<b>Ответь на сообщение чтобы закрепить его.</b>',
               'unpinning': '<b>Анпин...</b>',
               'unpin_none': '<b>Нечего откреплять.</b>',
               'no_rights': '<b>У меня нет прав.</b>',
               'pinned': '<b>Закреплено успешно!</b>',
               'unpinned': '<b>Откреплено успешно!</b>',
               'can`t_kick': '<b>Не могу кикнуть пользователя.</b>',
               'kicking': '<b>Кик...</b>',
               'kick_none': '<b>Некого кикать.</b>',
               'kicked': '<b>{} кикнут из чата.</b>',
               'kicked_for_reason': '<b>{} кикнут из чата.\nПричина: {}.</b>',
               'banning': '<b>Бан...</b>',
               'banned': '<b>{} забанен в чате.</b>',
               'banned_for_reason': '<b>{} забанен в чате.\nПричина: {}</b>',
               'ban_none': '<b>Некому давать бан.</b>',
               'unban_none': '<b>Некого разбанить.</b>',
               'unbanned': '<b>{} разбанен в чате.</b>',
               'mute_none': '<b>Некому давать мут.</b>',
               'muted': '<b>{} теперь в муте на </b>',
               'no_args': '<b>Неверно указаны аргументы.</b>',
               'unmute_none': '<b>Некого размутить.</b>',
               'unmuted': '<b>{} теперь не в муте.</b>',
               'no_reply': '<b>Нет реплая.</b>',
               'deleting': '<b>Удаление...</b>',
               'no_args_or_reply': '<b>Нет аргументов или реплая.</b>',
               'deleted': '<b>Все сообщения от {} удалены.</b>',
               'del_u_search': '<b>Поиск удалённых аккаунтов...</b>',
               'del_u_kicking': '<b>Кик удалённых аккаунтов...\nОх~, я могу это сделать?!</b>'}

    async def ecpcmd(self, message):
        """Команда .ecp изменяет картинку чата.\nИспользование: .ecp <реплай на картинку/стикер>."""
        if message.chat:
            try:
                reply = await message.get_reply_message()

                chat = await message.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))

                if reply:
                    pic = await check_media(message, reply)
                    if not pic:
                        return await utils.answer(message, self.strings('not_pic', message))
                else:
                    return await utils.answer(message, self.strings('no_reply', message))

                await utils.answer(message, self.strings('wait', message))

                what = resizepic(pic)
                if what:
                    try:
                        await message.client(EditPhotoRequest(message.chat_id, await message.client.upload_file(what)))
                    except PhotoCropSizeSmallError:
                        return await utils.answer(message, self.strings('pic_so_small', message))
                await utils.answer(message, self.strings('pic_changed', message))
            except ChatAdminRequiredError:
                return await utils.answer(message, self.strings('no_rights', message))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def promotecmd(self, message):
        """Команда .promote повышает пользователя в правах администратора.\nИспользование: .promote <@ или реплай> <ранг>."""
        if message.chat:
            try:
                args = utils.get_args_raw(message).split(' ')
                reply = await message.get_reply_message()
                rank = 'одмэн'

                chat = await message.get_chat()
                adm_rights = chat.admin_rights
                if not adm_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))

                if reply:
                    args = utils.get_args_raw(message)
                    if args:
                        rank = args
                    else:
                        rank = rank
                    user = await message.client.get_entity(reply.sender_id)
                else:
                    user = await message.client.get_entity(args[0] if not args[0].isnumeric() else int(args[0]))
                    if len(args) == 1:
                        rank = rank
                    elif len(args) >= 2:
                        rank = utils.get_args_raw(message).split(' ', 1)[1]
                try:
                    await message.client(EditAdminRequest(message.chat_id, user.id, ChatAdminRights(add_admins=False,
                                                                                                    invite_users=adm_rights.invite_users,
                                                                                                    change_info=False,
                                                                                                    ban_users=adm_rights.ban_users,
                                                                                                    delete_messages=adm_rights.delete_messages,
                                                                                                    pin_messages=adm_rights.pin_messages),
                                                          rank))
                except ChatAdminRequiredError:
                    return await utils.answer(message, self.strings('no_rights', message))
                else:
                    return await utils.answer(message, self.strings('promoted', message).format(user.first_name, rank))
            except ValueError:
                return await utils.answer(message, self.strings('no_args', message))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def demotecmd(self, message):
        """Команда .demote понижает пользователя в правах администратора.\nИспользование: .demote <@ или реплай>."""
        if not message.is_private:
            try:
                reply = await message.get_reply_message()

                chat = await message.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))

                if reply:
                    user = await message.client.get_entity(reply.sender_id)
                else:
                    args = utils.get_args_raw(message)
                    if not args:
                        return await utils.answer(message, self.strings('demote_none', message))
                    user = await message.client.get_entity(args if not args.isnumeric() else int(args))

                try:
                    if message.is_channel:
                        await message.client(EditAdminRequest(message.chat_id, user.id, DEMOTE_RIGHTS, ""))
                    else:
                        await message.client(EditChatAdminRequest(message.chat_id, user.id, False))
                except ChatAdminRequiredError:
                    return await utils.answer(message, self.strings('no_rights', message))
                else:
                    return await utils.answer(message, self.strings('demoted', message).format(user.first_name))
            except ValueError:
                return await utils.answer(message, self.strings('no_args'))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def pincmd(self, message):
        """Команда .pin закрепляет сообщение в чате.\nИспользование: .pin <реплай>."""
        if not message.is_private:
            reply = await message.get_reply_message()
            if not reply:
                return await utils.answer(message, self.strings('pin_none', message))

            await utils.answer(message, self.strings('pinning', message))
            try:
                await message.client.pin_message(message.chat, message=reply.id, notify=False)
            except ChatAdminRequiredError:
                return await utils.answer(message, self.strings('no_rights', message))
            await utils.answer(message, self.strings('pinned', message))
        else:
            await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def unpincmd(self, message):
        """Команда .unpin открепляет закрепленное сообщение в чате.\nИспользование: .unpin."""
        if not message.is_private:
            await utils.answer(message, self.strings('unpinning', message))

            try:
                await message.client.pin_message(message.chat, message=None, notify=None)
            except ChatAdminRequiredError:
                return await utils.answer(message, self.strings('no_rights', message))
            await utils.answer(message, self.strings('unpinned', message))
        else:
            await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def kickcmd(self, message):
        """Команда .kick кикает пользователя.\nИспользование: .kick <@ или реплай>."""
        if not message.is_private:
            try:
                args = utils.get_args_raw(message).split(' ')
                reason = utils.get_args_raw(message)
                reply = await message.get_reply_message()

                chat = await message.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))
                else:
                    if chat.admin_rights.ban_users == False:
                        return await utils.answer(message, self.strings('no_rights', message))

                if reply:
                    user = await message.client.get_entity(reply.sender_id)
                    args = utils.get_args_raw(message)
                    if args:
                        reason = args
                else:
                    user = await message.client.get_entity(args[0] if not args[0].isnumeric() else int(args[0]))
                    if args:
                        if len(args) == 1:
                            args = utils.get_args_raw(message)
                            user = await message.client.get_entity(args if not args.isnumeric() else int(args))
                            reason = False
                        elif len(args) >= 2:
                            reason = utils.get_args_raw(message).split(' ', 1)[1]

                await utils.answer(message, self.strings('kicking', message))
                try:
                    await message.client.kick_participant(message.chat_id, user.id)
                except UserAdminInvalidError:
                    return await utils.answer(message, self.strings('no_rights', message))
                if not reason:
                    return await utils.answer(message, self.strings('kicked', message).format(user.first_name))
                if reason:
                    return await utils.answer(message,
                                              self.strings('kicked_for_reason', message).format(user.first_name,
                                                                                                reason))

                return await utils.answer(message, self.strings('kicked', message).format(user.first_name))
            except ValueError:
                return await utils.answer(message, self.strings('no_args', message))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def bancmd(self, message):
        """Команда .ban даёт бан пользователю.\nИспользование: .ban <@ или реплай>."""
        if not message.is_private:
            try:
                args = utils.get_args_raw(message).split(' ')
                reason = utils.get_args_raw(message)
                reply = await message.get_reply_message()

                chat = await message.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))
                else:
                    if chat.admin_rights.ban_users == False:
                        return await utils.answer(message, self.strings('no_rights', message))

                if reply:
                    user = await message.client.get_entity(reply.sender_id)
                    args = utils.get_args_raw(message)
                    if args:
                        reason = args
                else:
                    user = await message.client.get_entity(args[0] if not args[0].isnumeric() else int(args[0]))
                    if args:
                        if len(args) == 1:
                            args = utils.get_args_raw(message)
                            user = await message.client.get_entity(args if not args.isnumeric() else int(args))
                            reason = False
                        elif len(args) >= 2:
                            reason = utils.get_args_raw(message).split(' ', 1)[1]
                try:
                    await utils.answer(message, self.strings('banning', message))
                    await message.client(EditBannedRequest(message.chat_id, user.id,
                                                           ChatBannedRights(until_date=None, view_messages=True)))
                except UserAdminInvalidError:
                    return await utils.answer(message, self.strings('no_rights', message))
                if not reason:
                    return await utils.answer(message, self.strings('banned', message).format(user.first_name))
                if reason:
                    return await utils.answer(message,
                                              self.strings('banned_for_reason', message).format(user.first_name,
                                                                                                reason))
                return await utils.answer(message, self.strings('banned', message).format(user.first_name))
            except ValueError:
                return await utils.answer(message, self.strings('no_args', message))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def unbancmd(self, message):
        """Команда .unban для разбана пользователя.\nИспользование: .unban <@ или реплай>."""
        if not message.is_private:
            try:
                reply = await message.get_reply_message()

                chat = await message.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))
                else:
                    if chat.admin_rights.ban_users == False:
                        return await utils.answer(message, self.strings('no_rights', message))

                if reply:
                    user = await message.client.get_entity(reply.sender_id)
                else:
                    args = utils.get_args_raw(message)
                    if not args:
                        return await utils.answer(message, self.strings('unban_none', message))
                    user = await message.client.get_entity(args if not args.isnumeric() else int(args))
                await message.client(
                    EditBannedRequest(message.chat_id, user.id, ChatBannedRights(until_date=None, view_messages=False)))

                return await utils.answer(message, self.strings('unbanned', message).format(user.first_name))
            except ValueError:
                return await utils.answer(message, self.strings('no_args', message))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def mutecmd(self, message):
        """Команда .mute даёт мут пользователю.\nИспользование: .mute <@ или реплай> <время (1m, 1h, 1d)>; ничего."""
        if not message.is_private:
            args = utils.get_args_raw(message).split()
            reply = await message.get_reply_message()
            timee = False

            try:
                if reply:
                    user = await message.client.get_entity(reply.sender_id)
                    args = utils.get_args_raw(message)
                    if args:
                        timee = args
                else:
                    user = await message.client.get_entity(args[0] if not args[0].isnumeric() else int(args[0]))
                    if args:
                        if len(args) == 1:
                            args = utils.get_args_raw(message)
                            user = await message.client.get_entity(args if not args.isnumeric() else int(args))
                            timee = False
                        elif len(args) >= 2:
                            timee = utils.get_args_raw(message).split(' ', 1)[1]
            except ValueError:
                return await utils.answer(message, self.strings('no_args', message))

            if timee:
                n = ''
                t = ''

                for _ in timee:
                    if _.isdigit():
                        n += _
                    else:
                        t += _

                text = f"<b>{n}"

                if t == "m":
                    n = int(n) * 60
                    text += " мин.</b>"

                elif t == "h":
                    n = int(n) * 3600
                    text += " час.</b>"

                elif t == "d":
                    n = int(n) * 86400
                    text += " дн.</b>"

                else:
                    return await utils.answer(message, self.strings('no_args', message))

                try:
                    tm = ChatBannedRights(until_date=time.time() + int(n), send_messages=True)
                    await message.client(EditBannedRequest(message.chat_id, user.id, tm))
                    return await utils.answer(message, self.strings('muted', message).format(user.first_name) + text)
                except UserAdminInvalidError:
                    return await utils.answer(message, self.strings('no_rights', message))
            else:
                try:
                    tm = ChatBannedRights(until_date=True, send_messages=True)
                    await message.client(EditBannedRequest(message.chat_id, user.id, tm))
                    return await message.edit('<b>{} теперь в муте.</b>'.format(user.first_name))
                except UserAdminInvalidError:
                    return await utils.answer(message, self.strings('no_rights', message))
        else:
            await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def unmutecmd(self, message):
        """Команда .unmute для размута пользователя.\nИспользование: .unmute <@ или реплай>."""
        if not message.is_private:
            try:
                reply = await message.get_reply_message()

                chat = await message.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(message, self.strings('not_admin', message))
                else:
                    if chat.admin_rights.ban_users == False:
                        return await utils.answer(message, self.strings('no_rights', message))

                if reply:
                    user = await message.client.get_entity(reply.sender_id)
                else:
                    args = utils.get_args_raw(message)
                    if not args:
                        return await utils.answer(message, self.strings('unmute_none', message))
                    user = await message.client.get_entity(args if not args.isnumeric() else int(args))
                await message.client(EditBannedRequest(message.chat_id, user.id, UNMUTE_RIGHTS))

                return await utils.answer(message, self.strings('unmuted', message).format(user.first_name))
            except ValueError:
                return await utils.answer(message, self.strings('no_args', message))
        else:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))

    async def delallmsgscmd(self, message):
        """Команда .delallmsgs удаляет все сообщения от пользователя.\nИспользование: .delallmsgs <@ или реплай>."""
        if not message.is_private:
            chat = await message.get_chat()
            if not chat.admin_rights and not chat.creator:
                return await message.edit("<b>Я не админ здесь.</b>")
            else:
                if chat.admin_rights.delete_messages == False:
                    return await message.edit("<b>У меня нет нужных прав.</b>")

        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if not args and not reply:
            return await utils.answer(message, self.strings('no_args_or_reply', message))

        await utils.answer(message, self.strings('deleting', message))

        if args:
            user = await message.client.get_entity(args)
        if reply:
            user = await message.client.get_entity(reply.sender_id)

        await message.client(DeleteUserHistoryRequest(message.to_id, user.id))
        await message.client.send_message(message.to_id, self.strings('deleted', message).format(user.first_name))
        await message.delete()

    async def deluserscmd(self, message):
        """Команда .delusers показывает список всех удалённых аккаунтов в чате.\nИспользование: .delusers <clean>."""
        if message.is_private:
            return await utils.answer(message, self.strings('this_isn`t_a_chat', message))

        con = utils.get_args_raw(message)
        del_u = 0
        del_status = '<b>Нет удалённых аккаунтов, чат очищен.</b>'

        if con != "clean":
            await utils.answer(message, self.strings('del_u_search', message))
            async for user in message.client.iter_participants(message.chat_id):
                if user.deleted:
                    del_u += 1
            if del_u == 1:
                del_status = f"<b>Найден {del_u} удаленный аккаунт в чате, очистите их с помощью </b><code>.delusers clean</code><b>.</b>"
            if del_u > 0:
                del_status = f"<b>Найдено {del_u} удаленных аккаунтов в чате, очистите их с помощью </b><code>.delusers clean</code><b>.</b>"
            return await message.edit(del_status)

        chat = await message.get_chat()
        if not chat.admin_rights and not chat.creator:
            return await utils.answer(message, self.strings('not_admin', message))
        else:
            if chat.admin_rights.ban_users == False:
                return await utils.answer(message, self.strings('no_rights', message))

        await utils.answer(message, self.strings('del_u_kicking', message))
        del_u = 0
        del_a = 0
        async for user in message.client.iter_participants(message.chat_id):
            if user.deleted:
                try:
                    await message.client(EditBannedRequest(message.chat_id, user.id, BANNED_RIGHTS))
                except UserAdminInvalidError:
                    del_u -= 1
                    del_a += 1
                await message.client(EditBannedRequest(message.chat_id, user.id, UNBAN_RIGHTS))
                del_u += 1
        if del_u == 1:
            del_status = f"<b>Кикнут {del_u} удалённый аккаунт.</b>"
        if del_u > 0:
            del_status = f"<b>Кикнуто {del_u} удалённых аккаунтов.</b>"

        if del_a == 1:
            del_status = f"<b>Кикнут {del_u} удалённый аккаунт.\n" \
                         f"{del_a} удалённый аккаунт админа не кикнут.</b>"
        if del_a > 0:
            del_status = f"<b>Кикнуто {del_u} удалённых аккаунтов.\n" \
                         f"{del_a} удалённых аккаунта админов не кикнуты.</b>"
        await message.edit(del_status)


def resizepic(reply):
    im = Image.open(io.BytesIO(reply))
    w, h = im.size
    x = min(w, h)
    x_ = (w - x) // 2
    y_ = (h - x) // 2
    _x = x_ + x
    _y = y_ + x
    im = im.crop((x_, y_, _x, _y))
    out = io.BytesIO()
    out.name = "outsuder.png"
    im.save(out)
    return out.getvalue()


async def check_media(message, reply):
    if reply and reply.media:
        if reply.photo:
            data = reply.photo
        elif reply.video:
            data = reply.video
        elif reply.document:
            if reply.gif or reply.audio or reply.voice:
                return None
            data = reply.media.document
        else:
            return None
    else:
        return None
    if not data or data is None:
        return None
    else:
        data = await message.client.download_file(data, bytes)
        try:
            Image.open(io.BytesIO(data))
            return data
        except:
            return None
