# -*- coding: utf-8 -*-

# requires: coffeehouse>=2.2.0

import asyncio
import logging
import time

import coffeehouse
from telethon import functions, types

import random
from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class LydiaMod(loader.Module):
	"""Talks to a robot instead of a human"""
	strings = {"name": "Lydia anti-PM",
	           "enable_disable_error_group": "<b>The AI service cannot be"
	                                         " enabled or disabled in this chat. Is this a group chat?</b>",
	           "enable_error_user": "<b>The AI service cannot be"
	                                " enabled for this user. Perhaps it wasn't disabled?</b>",
	           "notif_off": "<b>Notifications from PMs are silenced.</b>",
	           "notif_on": "<b>Notifications from PMs are now activated.</b>",
	           "successfully_enabled": "<b>AI enabled for this user. </b>",
	           "successfully_enabled_for_chat": "<b>AI enabled for that user in this chat.</b>",
	           "cannot_find": "<b>Cannot find that user.</b>",
	           "successfully_disabled": "<b>AI disabled for this user.</b>",
	           "cleanup_ids": "<b>Successfully cleaned up lydia-disabled IDs</b>",
	           "cleanup_sessions": "<b>Successfully cleaned up lydia sessions.</b>",
	           "doc_client_key": "The API key for lydia, acquire from"
	                             " https://coffeehouse.intellivoid.net",
	           "doc_ignore_no_common": "Boolean to ignore users who have no chats in common with you",
	           "doc_notif": "Boolean for notifications from PMs.",
	           "doc_disabled": "Whether Lydia defaults to enabled"
	                           " in private chats (if True, you'll have to use forcelydia"}

	def __init__(self):
		self.config = loader.ModuleConfig("CLIENT_KEY", None, lambda m: self.strings("doc_client_key", m),
		                                  "IGNORE_NO_COMMON", False, lambda m: self.strings("doc_ignore_no_common", m),
		                                  "DISABLED", False, lambda m: self.strings("doc_disabled", m),
		                                  "NOTIFY", False, lambda m: self.strings("doc_notif", m))
		self._ratelimit = []
		self._cleanup = None
		self._lydia = None

	async def client_ready(self, client, db):
		self._db = db
		self._lydia = coffeehouse.LydiaAI(self.config["CLIENT_KEY"]) if self.config["CLIENT_KEY"] else None
		# Schedule cleanups
		self._cleanup = asyncio.ensure_future(self.schedule_cleanups())

	async def schedule_cleanups(self):
		"""Cleans up dead sessions and reschedules itself to run when the next session expiry takes place"""
		sessions = self._db.get(__name__, "sessions", {})
		if len(sessions) == 0:
			return
		nsessions = {}
		t = time.time()
		for ident, session in sessions.items():
			if not session["expires"] < t:
				nsessions.update({ident: session})
			else:
				break  # workaround server bug
		if len(nsessions) > 1:
			next = min(*[v["expires"] for k, v in nsessions.items()])
		elif len(nsessions) == 1:
			[next] = [v["expires"] for k, v in nsessions.items()]
		else:
			next = t + 86399
		if nsessions != sessions:
			self._db.set(__name__, "sessions", nsessions)
		# Don't worry about the 1 day limit below 3.7.1, if it isn't expired we will just reschedule,
		# as nothing will be matched for deletion.
		await asyncio.sleep(min(next - t, 86399))

		await self.schedule_cleanups()

	async def enlydiacmd(self, message):
		"""Enables Lydia for target user"""
		old = self._db.get(__name__, "allow", [])
		if message.is_reply:
			user = (await message.get_reply_message()).from_id
		else:
			user = getattr(message.to_id, "user_id", None)
		if user is None:
			await utils.answer(message, self.strings("enable_disable_error_group", message))
			return
		try:
			old.remove(user)
			self._db.set(__name__, "allow", old)
		except ValueError:
			await utils.answer(message, self.strings("enable_error_user", message))
			return
		await utils.answer(message, self.strings("successfully_enabled", message))

	async def forcelydiacmd(self, message):
		"""Enables Lydia for user in specific chat"""
		if message.is_reply:
			user = (await message.get_reply_message()).from_id
		else:
			user = getattr(message.to_id, "user_id", None)
		if user is None:
			await utils.answer(message, self.strings("cannot_find", message))
			return
		self._db.set(__name__, "force", self._db.get(__name__, "force", []) + [[utils.get_chat_id(message), user]])
		await utils.answer(message, self.strings("successfully_enabled_for_chat", message))

	async def dislydiacmd(self, message):
		"""Disables Lydia for the target user"""
		if message.is_reply:
			user = (await message.get_reply_message()).from_id
		else:
			user = getattr(message.to_id, "user_id", None)
		if user is None:
			await utils.answer(message, self.strings("enable_disable_error_group", message))
			return

		old = self._db.get(__name__, "force")
		try:
			old.remove([utils.get_chat_id(message), user])
			self._db.set(__name__, "force", old)
		except (ValueError, TypeError, AttributeError):
			pass
		self._db.set(__name__, "allow", self._db.get(__name__, "allow", []) + [user])
		await utils.answer(message, self.strings("successfully_disabled", message))

	async def cleanlydiadisabledcmd(self, message):
		""" Remove all lydia-disabled users from DB. """
		self._db.set(__name__, "allow", [])
		return await utils.answer(message, self.strings("cleanup_ids", message))

	async def cleanlydiasessionscmd(self, message):
		"""Remove all active and not active lydia sessions from DB"""
		self._db.set(__name__, "sessions", {})
		return await utils.answer(message, self.strings("cleanup_sessions", message))

	async def lydianotifoffcmd(self, message):
		"""Disable the notifications from PMs"""
		self._db[__name__]["__config__"]["NOTIFY"] = False
		self._db.save()
		await utils.answer(message, self.strings("notif_off", message))

	async def lydianotifoncmd(self, message):
		"""Enable the notifications from PMs"""
		self._db[__name__]["__config__"]["NOTIFY"] = True
		self._db.save()
		await utils.answer(message, self.strings("notif_on", message))

	async def watcher(self, message):
		if not self.config["CLIENT_KEY"]:
			logger.debug("no key set for lydia, returning")
			return
		if not isinstance(message, types.Message):
			return
		if self._lydia is None:
			self._lydia = coffeehouse.LydiaAI(self.config["CLIENT_KEY"])
		if (isinstance(message.to_id, types.PeerUser) and not self.get_allowed(message.from_id)) or \
				self.is_forced(utils.get_chat_id(message), message.from_id):
			user = await utils.get_user(message)
			if user.is_self or user.bot or user.verified:
				logger.debug("User is self, bot or verified.")
				return
			else:
				if not isinstance(message.message, str):
					return
				if len(message.message) == 0:
					return
				if self.config["IGNORE_NO_COMMON"] and not self.is_forced(utils.get_chat_id(message), message.from_id):
					fulluser = await message.client(functions.users.GetFullUserRequest(await utils.get_user(message)))
					if fulluser.common_chats_count == 0:
						return
				if not self._db[__name__]["__config__"].get("NOTIFY"):
					await message.mark_read()
				await message.client(functions.messages.SetTypingRequest(
					peer=await utils.get_user(message),
					action=types.SendMessageTypingAction()
				))
				try:
					# Get a session
					sessions = self._db.get(__name__, "sessions", {})
					session = sessions.get(utils.get_chat_id(message), None)
					if session is None or session["expires"] < time.time():
						session = await utils.run_sync(self._lydia.create_session)
						session = {"session_id": session.id, "expires": session.expires}
						logger.debug(session)
						sessions[utils.get_chat_id(message)] = session
						logger.debug(sessions)
						self._db.set(__name__, "sessions", sessions)
						if self._cleanup is not None:
							self._cleanup.cancel()
						self._cleanup = asyncio.ensure_future(self.schedule_cleanups())
					logger.debug(session)
					# AI Response method
					msg = message.message
					airesp = await utils.run_sync(self._lydia.think_thought, session["session_id"], str(msg))
					logger.debug("AI says %s", airesp)
					if random.randint(0, 1) and isinstance(message.to_id, types.PeerUser):
						await message.respond(airesp)
					else:
						await message.reply(airesp)
				finally:
					await message.client(functions.messages.SetTypingRequest(
						peer=await utils.get_user(message),
						action=types.SendMessageCancelAction()
					))

	def get_allowed(self, id):
		if self.config["DISABLED"]:
			return True
		return id in self._db.get(__name__, "allow", [])

	def is_forced(self, chat, user_id):
		forced = self._db.get(__name__, "force", [])
		return [chat, user_id] in forced
