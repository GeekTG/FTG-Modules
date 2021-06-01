# -*- coding: utf-8 -*-

# Module author: @ftgmodulesbyfl1yd

from asyncio import sleep, gather

from .. import loader, utils


@loader.tds
class SpamMod(loader.Module):
	"""Spam Module"""
	strings = {'name': 'Spam'}

	async def spamcmd(self, message):
		"""Simple spam. Use .spam <count:int> <args or reply>."""
		try:
			await message.delete()
			args = utils.get_args(message)
			count = int(args[0].strip())
			reply = await message.get_reply_message()
			if reply:
				if reply.media:
					for _ in range(count):
						await message.client.send_file(message.to_id, reply.media)
					return
				else:
					for _ in range(count):
						await message.client.send_message(message.to_id, reply)
			else:
				message.message = " ".join(args[1:])
				for _ in range(count):
					await gather(*[message.respond(message)])
		except:
			return await message.client.send_message(message.to_id, '.spam <count:int> <args or reply>.')

	async def cspamcmd(self, message):
		"""Character spam. Use .cspam <args or reply>."""
		await message.delete()
		reply = await message.get_reply_message()
		msg = reply.text if reply else utils.get_args_raw(message)
		msg = msg.replace(' ', '')
		for m in msg:
			await message.respond(m)

	async def wspamcmd(self, message):
		"""Word spam. Use .wspam <args or reply>."""
		await message.delete()
		reply = await message.get_reply_message()
		msg = reply.text if reply else utils.get_args_raw(message)
		msg = msg.split()
		for m in msg:
			await message.respond(m)

	async def delayspamcmd(self, message):
		"""Delay spam. Use .delayspam <time(sec):int> <count:int> <args or reply>."""
		try:
			await message.delete()
			args = utils.get_args_raw(message)
			reply = await message.get_reply_message()
			time = int(args.split(' ', 2)[0])
			count = int(args.split(' ', 2)[1])
			if reply:
				for _ in range(count):
					if reply.media:
						await message.client.send_file(message.to_id, reply.media, reply_to=reply.id)
					else:
						await reply.reply(args.split(' ', 2)[2])
					await sleep(time)
			else:
				spammsg = args.split(' ', 2)[2]
				for _ in range(count):
					await message.respond(spammsg)
					await sleep(time)
		except:
			return await message.client.send_message(message.to_id,
			                                         '.delayspam <time(sec):int> <count:int> <args or reply>.')

	async def replayspamcmd(self, message):
		"""Reply spam. Use a reply to a message: .replayspam <count:int> <args>."""
		try:
			await message.delete()
			args = utils.get_args_raw(message)
			count = int(args.split(' ', 2)[0])
			reply = await message.get_reply_message()
			for _ in range(count):
				await reply.reply(args.split(' ', 2)[1])
			return
		except:
			return await message.client.send_message(message.to_id, '.replayspam <count:int> <args>.')
