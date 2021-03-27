# -*- coding: utf-8 -*-

# Module author: @Fl1yd

import io, logging, time
from .. import loader, utils, security
from PIL import Image
from telethon.errors import (ChatAdminRequiredError, UserAdminInvalidError, FloodWaitError, PhotoCropSizeSmallError)
from telethon.tl.types import (ChatAdminRights, ChatBannedRights)
from telethon.tl.functions.channels import (EditAdminRequest, EditBannedRequest, EditPhotoRequest)
from telethon.tl.functions.messages import EditChatAdminRequest

logger = logging.getLogger(__name__)

# ================== CONSTANS ========================

PROMOTE_RIGHTS = ChatAdminRights(post_messages=True,
                                 add_admins=None,
                                 invite_users=True,
                                 change_info=None,
                                 ban_users=True,
                                 delete_messages=True,
                                 pin_messages=True,
                                 edit_messages=True)

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

def register(cb):
    cb(AdminToolsMod())


class AdminToolsMod(loader.Module):
    """Chat administration."""
    strings = {'name': 'AdminTools',
               'not_pic': '<b>This isn`t an pic/sticker.</b>',
               'wait': '<b>Waiting...</b>',
               'pic_so_small': '<b>The image is too small, try another one.</b>',
               'pic_changed': '<b>Chat pic changed.</b>',
               'promote_none': '<b>No one to promote.</b>',
               'who': '<b>Who is it?</b>',
               'not_admin': '<b>I`m not an admin here.</b>',
               'promoted': '<b>{} promoted to admin rights.\nRank: {}</b>',
               'wtf_is_it': '<b>What is it?</b>',
               'this_isn`t_a_chat': '<b>This isn`t a chat!</b>',
               'demote_none': '<b>No one to demote.</b>',
               'demoted': '<b>{} demoted to admin rights.</b>',
               'pinning': '<b>Pin...</b>',
               'pin_none': '<b>Reply to the message to pin it.</b>',
               'unpinning': '<b>Unpin...</b>',
               'unpin_none': '<b>Nothing to unpin.</b>',
               'no_rights': '<b>I don`t have rights.</b>',
               'pinned': '<b>Pinned successfully!</b>',
               'unpinned': '<b>Unpinned successfully!</b>',
               'can`t_kick': '<b>Can`t kick.</b>',
               'kicking': '<b>Kick...</b>',
               'kick_none': '<b>No one to kick.</b>',
               'kicked': '<b>{} kicked from chat.</b>',
               'kicked_for_reason': '<b>{} kicked from chat.\nReason: {}.</b>',
               'banning': '<b>Ban...</b>',
               'banned': '<b>{} banned in chat.</b>',
               'banned_for_reason': '<b>{} banned in chat.\nReason: {}</b>',
               'ban_none': '<b>No one to ban.</b>',
               'unban_none': '<b>No one to unban.</b>',
               'unbanned': '<b>{} unbanned in chat.</b>',
               'mute_none': '<b>No one to mute.</b>',
               'muted': '<b>{} now muted for </b>',
               'no_args': '<b>Invalid arguments specified.</b>',
               'unmute_none': '<b>No one to unmute.</b>',
               'unmuted': '<b>{} now unmuted.</b>',
               'no_reply': '<b>No reply.</b>',
               'del_u_search': '<b>Search for deleted accounts...</b>',
               'del_u_kicking': '<b>Kick deleted accounts...\nOh~, I can do it?!</b>'}

    async def ecpcmd(self, gpic):
        """Command .ecp changes the pic of the chat.\nUse: .ecp <reply to pic/sticker>."""
        if gpic.chat:
            try:
                reply = await gpic.get_reply_message()
                chat = await gpic.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(gpic, self.strings('not_admin', gpic))
                if reply:
                    pic = await check_media(gpic, reply)
                    if not pic:
                        return await utils.answer(gpic, self.strings('not_pic', gpic))
                else:
                    return await utils.answer(gpic, self.strings('no_reply', gpic))
                await utils.answer(gpic, self.strings('wait', gpic))
                what = resizepic(pic)
                if what:
                    try:
                        await gpic.client(EditPhotoRequest(gpic.chat_id, await gpic.client.upload_file(what)))
                    except PhotoCropSizeSmallError:
                        return await utils.answer(gpic, self.strings('pic_so_small', gpic))
                await utils.answer(gpic, self.strings('pic_changed', gpic))
            except ChatAdminRequiredError:
                return await utils.answer(gpic, self.strings('no_rights', gpic))
        else:
            return await utils.answer(gpic, self.strings('this_isn`t_a_chat', gpic))

    async def promotecmd(self, promt):
        """Command .promote for promote user to admin rights.\nUse: .promote <@ or reply> <rank>."""
        if promt.chat:
            try:
                args = utils.get_args_raw(promt).split(' ')
                reply = await promt.get_reply_message()
                rank = 'admin'
                chat = await promt.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(promt, self.strings('not_admin', promt))
                if reply:
                    args = utils.get_args_raw(promt)
                    if args:
                        rank = args
                    else:
                        rank = rank
                    user = await utils.get_user(reply)
                else:
                    user = await promt.client.get_entity(args[0])
                    if len(args) == 1:
                        rank = rank
                    elif len(args) >= 2:
                        rank = utils.get_args_raw(promt).split(' ', 1)[1]
                try:
                    await promt.client(EditAdminRequest(promt.chat_id, user.id, PROMOTE_RIGHTS, rank))
                except ChatAdminRequiredError:
                    return await utils.answer(promt, self.strings('no_rights', promt))
                else:
                    return await utils.answer(promt, self.strings('promoted', promt).format(user.first_name, rank))
            except ValueError:
                return await utils.answer(promt, self.strings('no_args', promt))
        else:
            return await utils.answer(promt, self.strings('this_isn`t_a_chat', promt))

    async def demotecmd(self, demt):
        """Command .demote for demote user to admin rights.\nUse: .demote <@ or reply>."""
        if demt.chat:
            try:
                reply = await demt.get_reply_message()
                chat = await demt.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(demt, self.strings('not_admin', demt))
                if reply:
                    user = await utils.get_user(await demt.get_reply_message())
                else:
                    args = utils.get_args(demt)
                    if not args:
                        return await utils.answer(demt, self.strings('demote_none', demt))
                    user = await demt.client.get_entity(args[0])
                if not user:
                    return await utils.answer(demt, self.strings('who', demt))
                try:
                    if demt.is_channel:
                        await demt.client(EditAdminRequest(demt.chat_id, user.id, DEMOTE_RIGHTS, ""))
                    else:
                        await demt.client(EditChatAdminRequest(demt.chat_id, user.id, False))
                except:
                    return await utils.answer(demt, self.strings('no_rights', demt))
                else:
                    return await utils.answer(demt, self.strings('demoted', demt).format(user.first_name))
            except:
                return await utils.answer(demt, self.strings('wtf_is_it'))
        else:
            return await utils.answer(demt, self.strings('this_isn`t_a_chat', demt))

    async def pincmd(self, pint):
        """Command .pin for pin message in the chat.\nUse: .pin <reply>."""
        if pint.chat:
            reply = await pint.get_reply_message()
            if not reply:
                return await utils.answer(pint, self.strings('pin_none', pint))
            await utils.answer(pint, self.strings('pinning', pint))
            try:
                await pint.client.pin_message(pint.chat, message=reply.id, notify=False)
            except ChatAdminRequiredError:
                return await utils.answer(pint, self.strings('no_rights', pint))
            await utils.answer(pint, self.strings('pinned', pint))
        else:
            await utils.answer(pint, self.strings('this_isn`t_a_chat', pint))

    async def unpincmd(self, unpon):
        """Command .unpin for unpin message in the chat.\nUse: .unpin."""
        if unpon.chat:
            await utils.answer(unpon, self.strings('unpinning', unpon))
            try:
                await unpon.client.pin_message(unpon.chat, message=None, notify=None)
            except ChatAdminRequiredError:
                await utils.answer(unpon, self.strings('no_rights', unpon))
                return
            await utils.answer(unpon, self.strings('unpinned', unpon))
        else:
            await utils.answer(unpon, self.strings('this_isn`t_a_chat', unpon))

    async def kickcmd(self, kock):
        """Command .kick for kick the user.\nUse: .kick <@ or reply>."""
        if kock.chat:
            try:
                args = utils.get_args_raw(kock).split(' ')
                reason = utils.get_args_raw(kock)
                reply = await kock.get_reply_message()
                chat = await kock.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(kock, self.strings('not_admin', kock))
                if reply:
                    user = await utils.get_user(reply)
                    args = utils.get_args_raw(kock)
                    if args:
                        reason = args
                else:
                    user = await kock.client.get_entity(args[0])
                    if args:
                        if len(args) == 1:
                            args = utils.get_args_raw(kock)
                            user = await kock.client.get_entity(args)
                            reason = False
                        elif len(args) >= 2:
                            reason = utils.get_args_raw(kock).split(' ', 1)[1]
                try:
                    await utils.answer(kock, self.strings('kicking', kock))
                    await kock.client.kick_participant(kock.chat_id, user.id)
                except ChatAdminRequiredError:
                    return await utils.answer(kock, self.strings('no_rights', kock))
                else:
                    if reason:
                        return await utils.answer(kock, self.strings('kicked_for_reason', kock).format(user.first_name,
                                                                                                       reason))
                    if reason == False:
                        return await utils.answer(kock, self.strings('kicked', kock).format(user.first_name))
            except ValueError:
                return await utils.answer(kock, self.strings('no_args', kock))
        else:
            return await utils.answer(kock, self.strings('this_isn`t_a_chat', kock))

    async def bancmd(self, bon):
        """Command .ban for ban the user.\nUse: .ban <@ or reply>."""
        if bon.chat:
            try:
                args = utils.get_args_raw(bon).split(' ')
                reason = utils.get_args_raw(bon)
                reply = await bon.get_reply_message()
                chat = await bon.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(bon, self.strings('not_admin', bon))
                if reply:
                    user = await utils.get_user(reply)
                    args = utils.get_args_raw(bon)
                    if args:
                        reason = args
                else:
                    user = await bon.client.get_entity(args[0])
                    if args:
                        if len(args) == 1:
                            args = utils.get_args_raw(bon)
                            user = await bon.client.get_entity(args)
                            reason = False
                        elif len(args) >= 2:
                            reason = utils.get_args_raw(bon).split(' ', 1)[1]
                try:
                    await utils.answer(bon, self.strings('banning', bon))
                    await bon.client(
                        EditBannedRequest(bon.chat_id, user.id, ChatBannedRights(until_date=None, view_messages=True)))
                    async for msgs in bon.client.iter_messages(bon.to_id, from_user=user.id):
                        await msgs.delete()
                except ChatAdminRequiredError:
                    return await utils.answer(bon, self.strings('no_rights', bon))
                except UserAdminInvalidError:
                    return await utils.answer(bon, self.strings('no_rights', bon))
                except:
                    pass
                else:
                    if reason:
                        return await utils.answer(bon, self.strings('banned_for_reason', bon).format(user.first_name,
                                                                                                     reason))
                    if reason == False:
                        return await utils.answer(bon, self.strings('banned', bon).format(user.first_name, reason))
            except ValueError:
                return await utils.answer(bon, self.strings('no_args', bon))
        else:
            return await utils.answer(bon, self.strings('this_isn`t_a_chat', bon))

    async def unbancmd(self, unbon):
        """Command .unban for unban the user.\nUse: .unban <@ or reply>."""
        if unbon.chat:
            reply = await unbon.get_reply_message()
            chat = await unbon.get_chat()
            if not chat.admin_rights and not chat.creator:
                return await utils.answer(unbon, self.strings('not_admin', unbon))
            if reply:
                user = await utils.get_user(reply)
            else:
                args = utils.get_args(unbon)
                if not args:
                    return await utils.answer(unbon, self.strings('unban_none', unbon))
                user = await unbon.client.get_entity(args[0])
            if not user:
                return await utils.answer(unbon, self.strings('who', unbon))
            logger.debug(user)
            try:
                await unbon.client(
                    EditBannedRequest(unbon.chat_id, user.id, ChatBannedRights(until_date=None, view_messages=False)))
            except:
                return await utils.answer(unbon, self.strings('no_rights', unbon))
            else:
                return await utils.answer(unbon, self.strings('unbanned', unbon).format(user.first_name))
        else:
            return await utils.answer(unbon, self.strings('this_isn`t_a_chat', unbon))

    async def mutecmd(self, mot):
        """Command .mute for mute the user.\nUse: .mute <@ or reply> <time (1m, 1h, 1d)>."""
        if mot.chat:
            try:
                reply = await mot.get_reply_message()
                chat = await mot.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(mot, self.strings('not_admin', mot))
                if reply:
                    user = await utils.get_user(reply)

                else:
                    who = utils.get_args_raw(mot).split(' ')
                    user = await mot.client.get_entity(who[0])

                    if len(who) == 1:
                        timee = ChatBannedRights(until_date=True, send_messages=True)
                        await mot.client(EditBannedRequest(mot.chat_id, user.id, timee))
                        await mot.edit('<b>{} now muted.</b>'.format(user.first_name))
                        return

                    if not user:
                        return await utils.answer(mot, self.strings('mute_none', mot))
                    if user:
                        tim = who[1]
                        if tim:
                            if len(tim) != 2:
                                return await utils.answer(mot, self.strings('no_args', mot))
                            num = ''
                            t = ''
                            for q in tim:
                                if q.isdigit():
                                    num += q
                                else:
                                    t += q

                            text = f'<b>{num}'
                            if t == 'm':
                                num = int(num) * 60
                                text += ' mins.</b>'
                            elif t == 'h':
                                num = int(num) * 3600
                                text += ' hours.</b>'
                            elif t == 'd':
                                num = int(num) * 86400
                                text += ' days.</b>'
                            else:
                                return await utils.answer(mot, self.strings('no_args', mot))
                            timee = ChatBannedRights(until_date=time.time() + int(num), send_messages=True)
                            try:
                                await mot.client(EditBannedRequest(mot.chat_id, user.id, timee))
                                await utils.answer(mot, self.strings('muted', mot).format(
                                    utils.escape_html(user.first_name)) + text)
                                return
                            except:
                                await utils.answer(mot, self.strings('no_rights', mot))
                        else:
                            timee = ChatBannedRights(until_date=True, send_messages=True)
                            await mot.client(EditBannedRequest(mot.chat_id, user.id, timee))
                            await mot.edit('<b>{} now muted.</b>'.format(user.first_name))
                            return

                logger.debug(user)
                tim = utils.get_args(mot)
                if tim:
                    if len(tim[0]) < 2:
                        return await utils.answer(mot, self.strings('no_args', mot))
                    num = ''
                    t = ''
                    for q in tim[0]:
                        if q.isdigit():
                            num += q
                        else:
                            t += q

                    text = f'<b>{num}'
                    if t == 'm':
                        num = int(num) * 60
                        text += 'mins.</b>'
                    elif t == 'd':
                        num = int(num) * 86400
                        text += ' days.</b>'
                    elif t == 'h':
                        num = int(num) * 3600
                        text += ' hours.</b>'
                    else:
                        return await utils.answer(mot, self.strings('no_args', mot))
                    timee = ChatBannedRights(until_date=time.time() + int(num), send_messages=True)
                    try:
                        await mot.client(EditBannedRequest(mot.chat_id, user.id, timee))
                        await utils.answer(mot,
                                           self.strings('muted', mot).format(utils.escape_html(user.first_name)) + text)
                        return
                    except:
                        await utils.answer(mot, self.strings('no_rights', mot))
                else:
                    timee = ChatBannedRights(until_date=True, send_messages=True)
                    await mot.client(EditBannedRequest(mot.chat_id, user.id, timee))
                    await mot.edit('<b>{} now muted.</b>'.format(user.first_name))
                    return
            except:
                await utils.answer(mot, self.strings('mute_none', mot))
                return
        else:
            await utils.answer(mot, self.strings('this_isn`t_a_chat', mot))

    async def unmutecmd(self, unmot):
        """Command .unmute for unmute the user.\nUse: .unmute <@ or reply>."""
        if unmot.chat:
            try:
                reply = await unmot.get_reply_message()
                chat = await unmot.get_chat()
                if not chat.admin_rights and not chat.creator:
                    return await utils.answer(unmot, self.strings('not_admin', unmot))
                if reply:
                    user = await utils.get_user(reply)
                else:
                    args = utils.get_args(unmot)
                    if not args:
                        return await utils.answer(unmot, self.strings('unmute_none', unmot))
                    user = await unmot.client.get_entity(args[0])
                if not user:
                    return await utils.answer(unmot, self.strings('who', unmot))
                try:
                    await unmot.client(EditBannedRequest(unmot.chat_id, user.id, UNMUTE_RIGHTS))
                except:
                    return await utils.answer(unmot, self.strings('not_admin', unmot))
                else:
                    return await utils.answer(unmot,
                                              self.strings('unmuted', unmot).format(utils.escape_html(user.first_name)))
            except:
                return await utils.answer(unmot, self.strings('wtf_is_it', unmot))
        else:
            return await utils.answer(unmot, self.strings('this_isn`t_a_chat', unmot))

    async def deluserscmd(self, delus):
        """Command .delusers shows a list of all deleted accounts in the chat.\nUse: .delusers <clean>."""
        if not delus.is_group:
            await utils.answer(delus, self.strings('this_isn`t_a_chat', delus))
            return
        con = utils.get_args_raw(delus)
        del_u = 0

        del_status = '<b>No deleted accounts, chat cleared.</b>'
        if con != "clean":
            await utils.answer(delus, self.strings('del_u_search', delus))
            async for user in delus.client.iter_participants(delus.chat_id):
                if user.deleted:
                    del_u += 1

            if del_u == 1:
                del_status = f"<b>Found {del_u} deleted account, clean them with </b><code>.delusers clean</code><b>.</b>"
            if del_u > 0:
                del_status = f"<b>Found {del_u} deleted accounts, clean them with </b><code>.delusers clean</code><b>.</b>"
            await delus.edit(del_status)
            return

        chat = await delus.get_chat()
        if not chat.admin_rights and not chat.creator:
            return await utils.answer(delus, self.strings('not_admin', delus))
        await utils.answer(delus, self.strings('del_u_kicking', delus))
        del_u = 0
        del_a = 0

        async for user in delus.client.iter_participants(delus.chat_id):
            if user.deleted:
                try:
                    await delus.client(EditBannedRequest(delus.chat_id, user.id, BANNED_RIGHTS))
                except ChatAdminRequiredError:
                    return await utils.answer(delus, self.strings('no_rights', delus))
                except UserAdminInvalidError:
                    del_u -= 1
                    del_a += 1
                await delus.client(EditBannedRequest(delus.chat_id, user.id, UNBAN_RIGHTS))
                del_u += 1

        if del_u == 1:
            del_status = f"<b>Kicked {del_u} deleted account.</b>"
        if del_u > 0:
            del_status = f"<b>Kicked {del_u} deleted accounts.</b>"

        if del_a == 1:
            del_status = f"<b>Kicked {del_u} deleted account.\n" \
                         f"{del_a} deleted admin`s account not kicked.</b>"
        if del_a > 0:
            del_status = f"<b>Kicked {del_u} deleted account.\n" \
                         f"{del_a} deleted admin`s accounts not kicked.</b>"
        await delus.edit(del_status)


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
