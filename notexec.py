# -*- coding: utf-8 -*-

# Module author: @DneZyeK

import itertools
import logging
import sys
import traceback
import types

import telethon
from meval import meval

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class ExecutorMod(loader.Module):
	"""Stores global notes (aka snips)"""
	strings = {"name": "Notexec",
	           "what_note": "<b>What notexec should be executed?</b>",
	           "no_note": "<b>Notexec not found</b>",
	           "execute_fail": ("<b>Failed to execute expression:</b>\n<code>{}</code>")
	           }

	async def notexeccmd(self, message):
		"""Gets the note specified"""
		args = utils.get_args(message)
		if not args:
			await utils.answer(message, self.strings("what_note", message))
			return

		asset_id = self._db.get("friendly-telegram.modules.notes", "notes", {}).get(args[0], None)
		logger.debug(asset_id)
		if asset_id is not None:
			asset = await self._db.fetch_asset(asset_id)
		else:
			asset_id = self._db.get("friendly-telegram.modules.notes", "notes", {}).get(args[0].lower(), None)
			asset = await self._db.fetch_asset(asset_id) if asset_id is not None else None
		if asset is None:
			await utils.answer(message, self.strings("no_note", message))
			return

		cmd = await self._db.fetch_asset(asset_id)

		try:
			await meval(cmd.raw_text, globals(), **await self.getattrs(message))
		except Exception:
			exc = sys.exc_info()
			exc = "".join(traceback.format_exception(exc[0], exc[1], exc[2].tb_next.tb_next.tb_next))
			await utils.answer(message, self.strings("execute_fail", message)
			                   .format(utils.escape_html(exc)))
			return

	async def client_ready(self, client, db):
		self.client = client
		self.db = db
		self._db = db

	async def getattrs(self, message):
		return {"message": message, "client": self.client, "self": self, "db": self.db,
		        "reply": await message.get_reply_message(), "event": message, "chat": message.to_id, **self.get_types(),
		        **self.get_functions()}

	def get_types(self):
		return self.get_sub(telethon.tl.types)

	def get_functions(self):
		return self.get_sub(telethon.tl.functions)

	def get_sub(self, it, _depth=1):
		"""Get all callable capitalised objects in an object recursively, ignoring _*"""
		return {**dict(filter(lambda x: x[0][0] != "_" and x[0][0].upper() == x[0][0] and callable(x[1]),
		                      it.__dict__.items())),
		        **dict(itertools.chain.from_iterable([self.get_sub(y[1], _depth + 1).items() for y in
		                                              filter(lambda x: x[0][0] != "_"
		                                                               and isinstance(x[1], types.ModuleType)
		                                                               and x[1] != it
		                                                               and x[1].__package__.rsplit(".", _depth)[0]
		                                                               == "telethon.tl",
		                                                     it.__dict__.items())]))}
