# -*- coding: utf-8 -*-

# Module author: @GovnoCodules

from .. import loader, utils


@loader.tds
class CalculatorMod(loader.Module):
	"""Calculator module"""
	strings = {'name': 'Calculator'}

	async def calccmd(self, message):
		""".calc 2 * 2"""
		question = utils.get_args_raw(message)
		reply = await message.get_reply_message()
		if not question:
			if not reply:
				await utils.answer(message, "<b>2+2=5</b>")
				return
			else:
				question = reply.raw_text
		try:
			answer = eval(question)
			answer = f"<b>{question}=</b><code>{answer}</code>"
		except Exception as e:
			answer = f"<b>{question}=</b><code>{e}</code>"
		await utils.answer(message, answer)
