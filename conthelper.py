# -*- coding: utf-8 -*-

# Module author: @Yahikor0

from telethon import functions

from .. import loader, utils


@loader.tds
class ConthelperMod(loader.Module):
	"""
	Commands:
	"""

	def __init__(self):
		self.me = None

	async def client_ready(self, client, db):
		self.db = db
		self.client = client
		self.me = await client.get_me(True)

	async def reportcmd(self, message):
		"""Use: .report to report somebody."""
		reply = await message.get_reply_message()
		user = await message.client.get_entity(reply.sender_id)
		try: 
			user = await message.client.get_entity(reply.sender_id)
			await message.client(functions.messages.ReportSpamRequest(peer=user.id))
			await message.edit(f"<b><code>{user.first_name}</code> get report for spam!</b>")
		except:
			await message.edit("<b>no reply.</b>")
		
	async def blockcmd(self, message):
		"""Use: .block to block somebody."""
		reply = await message.get_reply_message()
		user = await message.client.get_entity(reply.sender_id)
		try: 
			user = await message.client.get_entity(reply.sender_id)
			await message.client(functions.contacts.BlockRequest(id=[user.id]))
			await message.edit(f"<code>{user.first_name}</code> added to the blacklist. ")
		except:
			await message.edit("<b>no reply.</b>")

	async def unblockcmd(self, message):
		"""Use: .unblock to unblock somebody."""
		reply = await message.get_reply_message()
		user = await message.client.get_entity(reply.sender_id)
		try: 
			user = await message.client.get_entity(reply.sender_id)
			await message.client(functions.contacts.UnblockRequest(id=[user.id]))
			await message.edit(f"<code>{user.first_name}</code> removed from the blacklist. ")
		except:
			await message.edit("<b>no reply.</b>")

	async def delcontcmd(self, message):
		"""Use: .delcont to delete somebody from contacts."""
		reply = await message.get_reply_message()
		user = await message.client.get_entity(reply.sender_id)
		try: 
			user = await message.client.get_entity(reply.sender_id)
			await message.client(functions.contacts.DeleteContactsRequest(id=[user.id]))
			await message.edit(f"<code>{user.first_name}</code> deleted from contacts ")
		except:
			await message.edit("<b>no reply.</b>")
		
			
	async def addcontcmd(self, message):
		"""Use: .addcont to add somebody in contacts."""
		args = utils.get_args_raw(message)
		reply = await message.get_reply_message()
		if not reply:
			return await message.edit("<b>Where reply?</b>")
		else:
			user = await message.client.get_entity(reply.sender_id)
		try:
			await message.client(functions.contacts.AddContactRequest(id=user.id,
			                                                          first_name=args,
			                                                          last_name=' ',
			                                                          phone='phone',
			                                                          add_phone_privacy_exception=False))
			await message.edit(f"<code>{user.first_name}</code> added to contacts as <code>{args}.</code>")
		except:
			await message.edit("<b>no reply.</b>")
