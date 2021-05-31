# By @vreply @pernel_kanic @nim1love @db0mb3r and geyporn by @tshipenchko

import requests

from .. import loader, utils


def register(cb):
	cb(TextGeneratorMod())


class TextGeneratorMod(loader.Module):
	"Generating text using machine learning"

	strings = {'name': 'TextGenerator',
	           'no_text': '<strong>Empty message</strong>',
	           'wait': '<strong>Generating text...</strong>'}

	async def pfcmd(self, message):
		"""Generates text with Porfirevich: porfirevich.ru"""
		text = utils.get_args_raw(message)
		reply = await message.get_reply_message()

		if text:
			if reply:
				text = reply.raw_text + text
		else:
			if reply:
				text = reply.raw_text
			else:
				return await utils.answer(message, self.strings('no_text', message))

		message = await utils.answer(message, self.strings('wait', message))
		response = (await utils.run_sync(requests.post, "https://pelevin.gpt.dobro.ai/generate/",
		                                 json={"prompt": text, "length": 30})).json()

		return await utils.answer(message, '<strong>' + text + '</strong>' + response["replies"][-1])

	async def gptcmd(self, message):
		"""Generates text with ruGPT-3 XL: russiannlp.github.io/rugpt-demo/"""
		text = utils.get_args_raw(message)
		reply = await message.get_reply_message()

		if text:
			if reply:
				text = reply.raw_text + text
		else:
			if reply:
				text = reply.raw_text
			else:
				return await utils.answer(message, self.strings('no_text', message))

		message = await utils.answer(message, self.strings('wait', message))
		response = (await utils.run_sync(requests.post,
		                                 "https://api.aicloud.sbercloud.ru/public/v1/public_inference/gpt3/predict",
		                                 json={"text": text})).json()
		return await utils.answer(message, '<strong>' + text + '</strong>' +
		                          response["predictions"].split(text.split()[-1], maxsplit=1)[1])
