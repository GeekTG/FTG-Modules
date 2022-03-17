# -*- coding: utf-8 -*-

# Module author: @Fl1yd

import io
import time

from PIL import Image
from telethon.errors import (
    ChatAdminRequiredError,
    PhotoCropSizeSmallError,
    UserAdminInvalidError,
)
from telethon.tl.functions.channels import (
    EditAdminRequest,
    EditBannedRequest,
    EditPhotoRequest,
)
from telethon.tl.functions.messages import EditChatAdminRequest
from telethon.tl.types import ChatAdminRights, ChatBannedRights

from .. import loader, utils

# ================== CONSTANS ========================

DEMOTE_RIGHTS = ChatAdminRights(
    post_messages=None,
    add_admins=None,
    invite_users=None,
    change_info=None,
    ban_users=None,
    delete_messages=None,
    pin_messages=None,
    edit_messages=None,
)

UNMUTE_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=None,
    send_messages=False,
    send_media=False,
    send_stickers=False,
    send_gifs=False,
    send_games=False,
    send_inline=False,
    embed_links=False,
)

BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)

UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)


# =====================================================


@loader.tds
class AdminToolsMod(loader.Module):
    """Admin Tools"""

    strings = {
        "name": "Admin Tools",
        "not_pic": "<b>This isn`t an pic/sticker.</b>",
        "wait": "<b>Waiting...</b>",
        "pic_so_small": "<b>The image is too small, try another one.</b>",
        "pic_changed": "<b>Chat pic changed.</b>",
        "promote_none": "<b>No one to promote.</b>",
        "who": "<b>Who is it?</b>",
        "not_admin": "<b>I`m not an admin here.</b>",
        "promoted": "<b>{} promoted to admin rights.\nRank: {}</b>",
        "wtf_is_it": "<b>What is it?</b>",
        "this_isn`t_a_chat": "<b>This isn`t a chat!</b>",
        "demote_none": "<b>No one to demote.</b>",
        "demoted": "<b>{} demoted to admin rights.</b>",
        "pinning": "<b>Pin...</b>",
        "pin_none": "<b>Reply to the message to pin it.</b>",
        "unpinning": "<b>Unpin...</b>",
        "unpin_none": "<b>Nothing to unpin.</b>",
        "no_rights": "<b>I don`t have rights.</b>",
        "pinned": "<b>Pinned successfully!</b>",
        "unpinned": "<b>Unpinned successfully!</b>",
        "can`t_kick": "<b>Can`t kick.</b>",
        "kicking": "<b>Kick...</b>",
        "kick_none": "<b>No one to kick.</b>",
        "kicked": "<b>{} kicked from chat.</b>",
        "kicked_for_reason": "<b>{} kicked from chat.\nReason: {}.</b>",
        "banning": "<b>Ban...</b>",
        "banned": "<b>{} banned in chat.</b>",
        "banned_for_reason": "<b>{} banned in chat.\nReason: {}</b>",
        "ban_none": "<b>No one to ban.</b>",
        "unban_none": "<b>No one to unban.</b>",
        "unbanned": "<b>{} unbanned in chat.</b>",
        "mute_none": "<b>No one to mute.</b>",
        "muted": "<b>{} now muted for </b>",
        "no_args": "<b>Invalid arguments specified.</b>",
        "unmute_none": "<b>No one to unmute.</b>",
        "unmuted": "<b>{} now unmuted.</b>",
        "no_reply": "<b>No reply.</b>",
        "del_u_search": "<b>Search for deleted accounts...</b>",
        "del_u_kicking": "<b>Kick deleted accounts...\nOh~, I can do it?!</b>",
    }

    async def ecpcmd(self, message):
        """Command .ecp changes the pic of the chat.\nUse: .ecp <reply to pic/sticker>."""
        if not message.chat:
            return await utils.answer(
                message, self.strings("this_isn`t_a_chat", message)
            )
        try:
            reply = await message.get_reply_message()

            chat = await message.get_chat()
            if not chat.admin_rights and not chat.creator:
                return await utils.answer(message, self.strings("not_admin", message))

            if not reply:
                return await utils.answer(message, self.strings("no_reply", message))

            pic = await check_media(message, reply)
            if not pic:
                return await utils.answer(message, self.strings("not_pic", message))
            await utils.answer(message, self.strings("wait", message))

            what = resizepic(pic)
            if what:
                try:
                    await message.client(
                        EditPhotoRequest(
                            message.chat_id, await message.client.upload_file(what)
                        )
                    )
                except PhotoCropSizeSmallError:
                    return await utils.answer(
                        message, self.strings("pic_so_small", message)
                    )
            await utils.answer(message, self.strings("pic_changed", message))
        except ChatAdminRequiredError:
            return await utils.answer(message, self.strings("no_rights", message))

    async def promotecmd(self, message):
        """Command .promote for promote user to admin rights.\nUse: .promote <@ or reply> <rank>."""
        if not message.chat:
            return await utils.answer(
                message, self.strings("this_isn`t_a_chat", message)
            )
        try:
            args = utils.get_args_raw(message).split(" ")
            reply = await message.get_reply_message()
            rank = "admin"

            chat = await message.get_chat()
            adm_rights = chat.admin_rights
            if not adm_rights and not chat.creator:
                return await utils.answer(message, self.strings("not_admin", message))

            if reply:
                args = utils.get_args_raw(message)
                rank = args or rank
                user = await message.client.get_entity(reply.sender_id)
            else:
                user = await message.client.get_entity(
                    args[0] if not args[0].isnumeric() else int(args[0])
                )
                if len(args) == 1:
                    rank = rank
                elif len(args) >= 2:
                    rank = utils.get_args_raw(message).split(" ", 1)[1]
            try:
                await message.client(
                    EditAdminRequest(
                        message.chat_id,
                        user.id,
                        ChatAdminRights(
                            add_admins=False,
                            invite_users=adm_rights.invite_users,
                            change_info=False,
                            ban_users=adm_rights.ban_users,
                            delete_messages=adm_rights.delete_messages,
                            pin_messages=adm_rights.pin_messages,
                        ),
                        rank,
                    )
                )
            except ChatAdminRequiredError:
                return await utils.answer(message, self.strings("no_rights", message))
            else:
                return await utils.answer(
                    message,
                    self.strings("promoted", message).format(user.first_name, rank),
                )
        except ValueError:
            return await utils.answer(message, self.strings("no_args", message))

    async def demotecmd(self, message):
        """Command .demote for demote user to admin rights.\nUse: .demote <@ or reply>."""
        if message.is_private:
            return await utils.answer(
                message, self.strings("this_isn`t_a_chat", message)
            )
        try:
            reply = await message.get_reply_message()

            chat = await message.get_chat()
            if not chat.admin_rights and not chat.creator:
                return await utils.answer(message, self.strings("not_admin", message))

            if reply:
                user = await message.client.get_entity(reply.sender_id)
            else:
                args = utils.get_args_raw(message)
                if not args:
                    return await utils.answer(
                        message, self.strings("demote_none", message)
                    )
                user = await message.client.get_entity(
                    args if not args.isnumeric() else int(args)
                )

            try:
                if message.is_channel:
                    await message.client(
                        EditAdminRequest(message.chat_id, user.id, DEMOTE_RIGHTS, "")
                    )
                else:
                    await message.client(
                        EditChatAdminRequest(message.chat_id, user.id, False)
                    )
            except ChatAdminRequiredError:
                return await utils.answer(message, self.strings("no_rights", message))
            else:
                return await utils.answer(
                    message, self.strings("demoted", message).format(user.first_name)
                )
        except ValueError:
            return await utils.answer(message, self.strings("no_args"))

    async def pincmd(self, message):
        """Command .pin for pin message in the chat.\nUse: .pin <reply>."""
        if message.is_private:
            await utils.answer(message, self.strings("this_isn`t_a_chat", message))
            return

        reply = await message.get_reply_message()
        if not reply:
            return await utils.answer(message, self.strings("pin_none", message))

        await utils.answer(message, self.strings("pinning", message))
        try:
            await message.client.pin_message(
                message.chat, message=reply.id, notify=False
            )
        except ChatAdminRequiredError:
            return await utils.answer(message, self.strings("no_rights", message))
        await utils.answer(message, self.strings("pinned", message))

    async def unpincmd(self, message):
        """Command .unpin for unpin message in the chat.\nUse: .unpin."""
        if message.is_private:
            await utils.answer(message, self.strings("this_isn`t_a_chat", message))
            return

        await utils.answer(message, self.strings("unpinning", message))

        try:
            await message.client.pin_message(message.chat, message=None, notify=None)
        except ChatAdminRequiredError:
            return await utils.answer(message, self.strings("no_rights", message))
        await utils.answer(message, self.strings("unpinned", message))

    async def kickcmd(self, message):
        """Command .kick for kick the user.\nUse: .kick <@ or reply>."""
        if message.is_private:
            return await utils.answer(
                message, self.strings("this_isn`t_a_chat", message)
            )
        try:
            args = utils.get_args_raw(message).split(" ")
            reason = utils.get_args_raw(message)
            reply = await message.get_reply_message()

            chat = await message.get_chat()
            if not chat.admin_rights and not chat.creator:
                return await utils.answer(message, self.strings("not_admin", message))

            if not chat.admin_rights.ban_users:
                return await utils.answer(message, self.strings("no_rights", message))

            if reply:
                user = await message.client.get_entity(reply.sender_id)
                args = utils.get_args_raw(message)
                if args:
                    reason = args
            else:
                user = await message.client.get_entity(
                    args[0] if not args[0].isnumeric() else int(args[0])
                )
                if args:
                    if len(args) == 1:
                        args = utils.get_args_raw(message)
                        user = await message.client.get_entity(
                            args if not args.isnumeric() else int(args)
                        )
                        reason = False
                    elif len(args) >= 2:
                        reason = utils.get_args_raw(message).split(" ", 1)[1]

            await utils.answer(message, self.strings("kicking", message))
            try:
                await message.client.kick_participant(message.chat_id, user.id)
            except UserAdminInvalidError:
                return await utils.answer(message, self.strings("no_rights", message))
            if not reason:
                return await utils.answer(
                    message, self.strings("kicked", message).format(user.first_name)
                )
            return await utils.answer(
                message,
                self.strings("kicked_for_reason", message).format(
                    user.first_name, reason
                ),
            )

        except ValueError:
            return await utils.answer(message, self.strings("no_args", message))

    async def bancmd(self, message):
        """Command .ban for ban the user.\nUse: .ban <@ or reply>."""
        if message.is_private:
            return await utils.answer(
                message, self.strings("this_isn`t_a_chat", message)
            )
        try:
            args = utils.get_args_raw(message).split(" ")
            reason = utils.get_args_raw(message)
            reply = await message.get_reply_message()

            chat = await message.get_chat()
            if not chat.admin_rights and not chat.creator:
                return await utils.answer(message, self.strings("not_admin", message))

            if not chat.admin_rights.ban_users:
                return await utils.answer(message, self.strings("no_rights", message))

            if reply:
                user = await message.client.get_entity(reply.sender_id)
                args = utils.get_args_raw(message)
                if args:
                    reason = args
            else:
                user = await message.client.get_entity(
                    args[0] if not args[0].isnumeric() else int(args[0])
                )
                if args:
                    if len(args) == 1:
                        args = utils.get_args_raw(message)
                        user = await message.client.get_entity(
                            args if not args.isnumeric() else int(args)
                        )
                        reason = False
                    elif len(args) >= 2:
                        reason = utils.get_args_raw(message).split(" ", 1)[1]
            try:
                await utils.answer(message, self.strings("banning", message))
                await message.client(
                    EditBannedRequest(
                        message.chat_id,
                        user.id,
                        ChatBannedRights(until_date=None, view_messages=True),
                    )
                )
            except UserAdminInvalidError:
                return await utils.answer(message, self.strings("no_rights", message))
            if not reason:
                return await utils.answer(
                    message, self.strings("banned", message).format(user.first_name)
                )
            return await utils.answer(
                message,
                self.strings("banned_for_reason", message).format(
                    user.first_name, reason
                ),
            )
        except ValueError:
            return await utils.answer(message, self.strings("no_args", message))

    async def unbancmd(self, message):
        """Command .unban for unban the user.\nUse: .unban <@ or reply>."""
        if message.is_private:
            return await utils.answer(
                message, self.strings("this_isn`t_a_chat", message)
            )
        try:
            reply = await message.get_reply_message()

            chat = await message.get_chat()
            if not chat.admin_rights and not chat.creator:
                return await utils.answer(message, self.strings("not_admin", message))

            if not chat.admin_rights.ban_users:
                return await utils.answer(message, self.strings("no_rights", message))

            if reply:
                user = await message.client.get_entity(reply.sender_id)
            else:
                args = utils.get_args_raw(message)
                if not args:
                    return await utils.answer(
                        message, self.strings("unban_none", message)
                    )
                user = await message.client.get_entity(
                    args if not args.isnumeric() else int(args)
                )
            await message.client(
                EditBannedRequest(
                    message.chat_id,
                    user.id,
                    ChatBannedRights(until_date=None, view_messages=False),
                )
            )

            return await utils.answer(
                message, self.strings("unbanned", message).format(user.first_name)
            )
        except ValueError:
            return await utils.answer(message, self.strings("no_args", message))

    async def mutecmd(self, message):
        """Command .mute for mute the user.\nUse: .mute <@ or reply> <time (1m, 1h, 1d)>."""
        if message.is_private:
            await utils.answer(message, self.strings("this_isn`t_a_chat", message))
            return

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
                user = await message.client.get_entity(
                    args[0] if not args[0].isnumeric() else int(args[0])
                )
                if args:
                    if len(args) == 1:
                        args = utils.get_args_raw(message)
                        user = await message.client.get_entity(
                            args if not args.isnumeric() else int(args)
                        )
                        timee = False
                    elif len(args) >= 2:
                        timee = utils.get_args_raw(message).split(" ", 1)[1]
        except ValueError:
            return await utils.answer(message, self.strings("no_args", message))

        if timee:
            n = ""
            t = ""

            for _ in timee:
                if _.isdigit():
                    n += _
                else:
                    t += _

            text = f"<b>{n}"

            if t == "m":
                n = int(n) * 60
                text += " m.</b>"

            elif t == "h":
                n = int(n) * 3600
                text += " h.</b>"

            elif t == "d":
                n = int(n) * 86400
                text += " d.</b>"

            else:
                return await utils.answer(message, self.strings("no_args", message))

            try:
                tm = ChatBannedRights(
                    until_date=time.time() + int(n), send_messages=True
                )
                await message.client(EditBannedRequest(message.chat_id, user.id, tm))
                return await utils.answer(
                    message,
                    self.strings("muted", message).format(user.first_name) + text,
                )
            except UserAdminInvalidError:
                return await utils.answer(message, self.strings("no_rights", message))
        else:
            try:
                tm = ChatBannedRights(until_date=True, send_messages=True)
                await message.client(EditBannedRequest(message.chat_id, user.id, tm))
                return await message.edit(
                    "<b>{} is now muted.</b>".format(user.first_name)
                )
            except UserAdminInvalidError:
                return await utils.answer(message, self.strings("no_rights", message))

    async def unmutecmd(self, message):
        """Command .unmute for unmute the user.\nUse: .unmute <@ or reply>."""
        if message.is_private:
            return await utils.answer(
                message, self.strings("this_isn`t_a_chat", message)
            )
        try:
            reply = await message.get_reply_message()

            chat = await message.get_chat()
            if not chat.admin_rights and not chat.creator:
                return await utils.answer(message, self.strings("not_admin", message))

            if not chat.admin_rights.ban_users:
                return await utils.answer(message, self.strings("no_rights", message))

            if reply:
                user = await message.client.get_entity(reply.sender_id)
            else:
                args = utils.get_args_raw(message)
                if not args:
                    return await utils.answer(
                        message, self.strings("unmute_none", message)
                    )
                user = await message.client.get_entity(
                    args if not args.isnumeric() else int(args)
                )
            await message.client(
                EditBannedRequest(message.chat_id, user.id, UNMUTE_RIGHTS)
            )

            return await utils.answer(
                message, self.strings("unmuted", message).format(user.first_name)
            )
        except ValueError:
            return await utils.answer(message, self.strings("no_args", message))

    async def deluserscmd(self, message):
        """Command .delusers shows a list of all deleted accounts in the chat.\nUse: .delusers <clean>."""
        if message.is_private:
            return await utils.answer(
                message, self.strings("this_isn`t_a_chat", message)
            )

        con = utils.get_args_raw(message)
        del_status = "<b>No deleted accouns found.</b>"

        if con != "clean":
            await utils.answer(message, self.strings("del_u_search", message))
            del_u = len(
                [
                    _
                    async for _ in message.client.iter_participants(message.chat_id)
                    if _.deleted
                ]
            )
            del_status = f"<b>Found {del_u} deleted accounts, clear them with </b><code>.delusers clean</code><b>.</b>"
            return await message.edit(del_status)

        chat = await message.get_chat()
        if not chat.admin_rights and not chat.creator:
            return await utils.answer(message, self.strings("not_admin", message))

        if not chat.admin_rights.ban_users:
            return await utils.answer(message, self.strings("no_rights", message))

        await utils.answer(message, self.strings("del_u_kicking", message))
        del_u = 0
        del_a = 0
        async for user in message.client.iter_participants(message.chat_id):
            if user.deleted:
                try:
                    await message.client(
                        EditBannedRequest(message.chat_id, user.id, BANNED_RIGHTS)
                    )
                except UserAdminInvalidError:
                    del_u -= 1
                    del_a += 1
                await message.client(
                    EditBannedRequest(message.chat_id, user.id, UNBAN_RIGHTS)
                )
                del_u += 1
        if del_u > 0:
            del_status = f"<b>Kicked {del_u} deleted account(s).</b>"

        if del_a > 0:
            del_status = (
                f"<b>Kicked {del_u} deleted account(s).\n"
                f"{del_a} deleted admins account are not kicked.</b>"
            )
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
    out.name = "outsider.png"
    im.save(out)
    return out.getvalue()


async def check_media(message, reply):
    data = reply.photo or reply.sticker if reply else None
    if not data:
        return None

    data = await message.client.download_file(data, bytes)
    try:
        Image.open(io.BytesIO(data))
        return data
    except Exception:
        return False
