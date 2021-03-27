# -*- coding: utf-8 -*-

from .. import loader, utils

import logging

from telethon import functions, types

logger = logging.getLogger(__name__)


@loader.tds
class AntiPMMod(loader.Module):
    """Prevents people sending you unsolicited private messages"""
    strings = {"name": "Anti PM",
               "limit_cfg_doc": "Max number of PMs before user is blocked, or None",
               "who_to_block": "<b>Specify whom to block</b>",
               "blocked": ("<b>I don't want any PM from</b> <a href='tg://user?id={}'>you</a>, "
                           "<b>so you have been blocked!</b>"),
               "who_to_unblock": "<b>Specify whom to unblock</b>",
               "unblocked": ("<b>Alright fine! I'll forgive them this time. PM has been unblocked for </b> "
                             "<a href='tg://user?id={}'>this user</a>"),
               "who_to_allow": "<b>Who shall I allow to PM?</b>",
               "allowed": "<b>I have allowed</b> <a href='tg://user?id={}'>you</a> <b>to PM now</b>",
               "who_to_report": "<b>Who shall I report?</b>",
               "reported": "<b>You just got reported spam!</b>",
               "who_to_deny": "<b>Who shall I deny to PM?</b>",
               "denied": ("<b>I have denied</b> <a href='tg://user?id={}'>you</a> "
                          "<b>of your PM permissions.</b>"),
               "notif_off": "<b>Notifications from denied PMs are silenced.</b>",
               "notif_on": "<b>Notifications from denied PMs are now activated.</b>",
               "go_away": ("Hey there! Unfortunately, I don't accept private messages from "
                            "strangers.\n\nPlease contact me in a group, or <b>wait</b> "
                            "for me to approve you."),
               "triggered": ("Hey! I don't appreciate you barging into my PM like this! "
                             "Did you even ask me for approving you to PM? No? Goodbye then."
                             "\n\nPS: you've been reported as spam already.")}

    def __init__(self):
        self.config = loader.ModuleConfig("PM_BLOCK_LIMIT", None, lambda m: self.strings("limit_cfg_doc", m))
        self._me = None
        self._ratelimit = []

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self._me = await client.get_me(True)

    async def blockcmd(self, message):
        """Block this user to PM without being warned"""
        user = await utils.get_target(message)
        if not user:
            await utils.answer(message, self.strings("who_to_block", message))
            return
        await message.client(functions.contacts.BlockRequest(user))
        await utils.answer(message, self.strings("blocked", message).format(user))

    async def unblockcmd(self, message):
        """Unblock this user to PM"""
        user = await utils.get_target(message)
        if not user:
            await utils.answer(message, self.strings("who_to_unblock", message))
            return
        await message.client(functions.contacts.UnblockRequest(user))
        await utils.answer(message, self.strings("unblocked", message).format(user))

    async def allowcmd(self, message):
        """Allow this user to PM"""
        user = await utils.get_target(message)
        if not user:
            await utils.answer(message, self.strings("who_to_allow", message))
            return
        self._db.set(__name__, "allow", list(set(self._db.get(__name__, "allow", [])).union({user})))
        await utils.answer(message, self.strings("allowed", message).format(user))

    async def reportcmd(self, message):
        """Report the user spam. Use only in PM"""
        user = await utils.get_target(message)
        if not user:
            await utils.answer(message, self.strings("who_to_report", message))
            return
        self._db.set(__name__, "allow", list(set(self._db.get(__name__, "allow", [])).difference({user})))
        if message.is_reply and isinstance(message.to_id, types.PeerChannel):
            # Report the message
            await message.client(functions.messages.ReportRequest(peer=message.chat_id,
                                                                  id=[message.reply_to_msg_id],
                                                                  reason=types.InputReportReasonSpam()))
        else:
            await message.client(functions.messages.ReportSpamRequest(peer=message.to_id))
        await utils.answer(message, self.strings("reported", message))

    async def denycmd(self, message):
        """Deny this user to PM without being warned"""
        user = await utils.get_target(message)
        if not user:
            await utils.answer(message, self.strings("who_to_deny", message))
            return
        self._db.set(__name__, "allow", list(set(self._db.get(__name__, "allow", [])).difference({user})))
        await utils.answer(message, self.strings("denied", message).format(user))

    async def notifoffcmd(self, message):
        """Disable the notifications from denied PMs"""
        self._db.set(__name__, "notif", True)
        await utils.answer(message, self.strings("notif_off", message))

    async def notifoncmd(self, message):
        """Enable the notifications from denied PMs"""
        self._db.set(__name__, "notif", False)
        await utils.answer(message, self.strings("notif_on", message))

    async def watcher(self, message):
        if not isinstance(message, types.Message):
            return
        if getattr(message.to_id, "user_id", None) == self._me.user_id:
            logger.debug("pm'd!")
            if message.sender_id in self._ratelimit:
                self._ratelimit.remove(message.sender_id)
                return
            else:
                self._ratelimit += [message.sender_id]
            user = await utils.get_user(message)
            if user.is_self or user.bot or user.verified:
                logger.debug("User is self, bot or verified.")
                return
            if self.get_allowed(message.sender_id):
                logger.debug("Authorised pm detected")
            else:
                await utils.answer(message, self.strings("go_away", message))
                if isinstance(self.config["PM_BLOCK_LIMIT"], int):
                    limit = self._db.get(__name__, "limit", {})
                    if limit.get(message.sender_id, 0) >= self.config["PM_BLOCK_LIMIT"]:
                        await utils.answer(message, self.strings("triggered", message))
                        await message.client(functions.contacts.BlockRequest(message.sender_id))
                        await message.client(functions.messages.ReportSpamRequest(peer=message.sender_id))
                        del limit[message.sender_id]
                        self._db.set(__name__, "limit", limit)
                    else:
                        self._db.set(__name__, "limit", {**limit, message.sender_id: limit.get(message.sender_id, 0) + 1})
                if self._db.get(__name__, "notif", False):
                    await message.client.send_read_acknowledge(message.chat_id)

    def get_allowed(self, id):
        return id in self._db.get(__name__, "allow", [])
