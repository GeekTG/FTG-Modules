# -*- coding: utf-8 -*-

# Module author: Official Repo

import asyncio
import logging

from telethon.tl.types import InputMediaDice

from random import random
from .. import loader, utils, security

logger = logging.getLogger(__name__)


@loader.tds
class RandomMod(loader.Module):
	"""Random Module"""
	strings = {"name": "Random",
	           "yes_words_cfg_doc": "Yes words",
	           "no_words_cfg_doc": "No words"
	           }

	def __init__(self):
		self.config = loader.ModuleConfig(
			"YES_WORDS", ["Yes", "Yup", "Absolutely", "Non't"], lambda m: self.strings("yes_words_cfg_doc"),
			"NO_WORDS", ["No", "Nope", "Nah", "Yesn't"], lambda m: self.strings("no_words_cfg_doc"),
			"POSSIBLE_VALUES", {"": [1, 2, 3, 4, 5, 6],
			                    "🎲": [1, 2, 3, 4, 5, 6],
			                    "🎯": [1, 2, 3, 4, 5, 6],
			                    "🏀": [1, 2, 3, 4, 5]},
			"Mapping of emoji to possible values")

	@loader.unrestricted
	async def dicecmd(self, message):
		"""Rolls a die (optionally with the specified value)
		   .dice <emoji> <outcomes> <count>"""
		args = utils.get_args(message)
		if await self.allmodules.check_security(message, security.OWNER | security.SUDO):
			try:
				emoji = args[0]
			except IndexError:
				emoji = "🎲"
			possible = self.config["POSSIBLE_VALUES"].get(emoji, None)
			if possible is None:
				emoji = "🎲"
				possible = self.config["POSSIBLE_VALUES"][emoji]
			values = set()
			try:
				for val in args[1].split(","):
					value = int(val)
					if value in possible:
						values.add(value)
			except (ValueError, IndexError):
				values.clear()
			try:
				count = int(args[2])
			except (ValueError, IndexError):
				count = 1
			rolled = -1
			done = 0
			chat = message.to_id
			client = message.client
			while True:
				task = client.send_message(chat, file=InputMediaDice(emoji))
				if message:
					message = (await asyncio.gather(message.delete(), task))[1]
				else:
					message = await task
				rolled = message.media.value
				logger.debug("Rolled %d", rolled)
				if rolled in values or not values:
					done += 1
					message = None
					if done == count:
						break
		else:
			try:
				emoji = args[0]
			except IndexError:
				emoji = "🎲"
			await message.reply(file=InputMediaDice(emoji))

	@loader.unrestricted
	async def yesnocmd(self, message):
		"""Make a life choice"""
		yes = self.config["YES_WORDS"]
		no = self.config["NO_WORDS"]
		response = random.choice(yes) if random.getrandbits(1) else random.choice(no)
		await utils.answer(message, response)
