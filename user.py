# -*- coding: utf-8 -*-

# Module author: @dekftgmodules, @ftgmodulesbyfl1yd

import os
from asyncio import sleep

from telethon import functions
from telethon.errors.rpcerrorlist import UsernameOccupiedError
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest
from telethon.tl.functions.users import GetFullUserRequest

from .. import loader, utils


@loader.tds
class UserMod(loader.Module):
	"""User Tools"""
	strings = {'name': 'User'}

	def __init__(self):
		self.name = self.strings['name']
		self._me = None
		self._ratelimit = []

	async def client_ready(self, client, db):
		self.client = client
		self.db = db
		self.me = await client.get_me()
		self.db.set(__name__, "first_copy", True)
		self.db.set(__name__, "avatar_copy", 0)

	async def copycmd(self, message):
		""".copy <s> <a> <reply/@username>
		<s> - Silent mode
		<a> - Delete avatars"""
		first_copy = self.db.get(__name__, "first_copy")
		if first_copy:
			us = await message.client(GetFullUserRequest(message.sender_id))
			self.db.set(__name__, "about", us.about[:70])
			self.db.set(__name__, "first", message.sender.first_name)
			self.db.set(__name__, "last", message.sender.last_name)
			self.db.set(__name__, "first_copy", False)
			self.db.set(__name__, "avatar_count", 0)

		reply = await message.get_reply_message()
		user = None
		s = False
		a = False
		if utils.get_args_raw(message):
			args = utils.get_args_raw(message).split(" ")
			for i in args:
				if "s" == i.lower():
					s = True
				elif "а" == i.lower() or "a" == i.lower():
					a = True
				else:
					try:
						user = await message.client.get_entity(i)
						break
					except:
						continue
		if user is None and reply is not None: user = reply.sender
		if user is None and reply is None:
			if not s: await message.edit("Who?")
			return
		if s: await message.delete()
		if not s:
			for i in range(11):
				await message.edit(
					f"Getting access to the user [{i * 10}%]\n[{(i * '#').ljust(10, '–')}]")
				await sleep(0.1)
		if a:
			avs = await message.client.get_profile_photos('me')
			if len(avs) > 0:
				await message.client(functions.photos.DeletePhotosRequest(
					await message.client.get_profile_photos('me')))
		full = await message.client(GetFullUserRequest(user.id))
		if not s: await message.edit("Getting avatar... [35%]\n[###–––––––]")
		if full.profile_photo:
			self.db.set(__name__, "avatar_count", self.db.get(__name__, "avatar_count") + 1)
			up = await message.client.upload_file(
				await message.client.download_profile_photo(user, bytes))
			if not s: await message.edit(
				"Getting avatar... [50%]\n[#####–––––]")
			await message.client(functions.photos.UploadProfilePhotoRequest(up))
		if not s: await message.edit("Getting data...  [99%]\n[#########–]")
		await message.client(UpdateProfileRequest(
			user.first_name if user.first_name is not None else "",
			user.last_name if user.last_name is not None else "",
			full.about[:70] if full.about is not None else ""
		))
		if not s: await message.edit("Account cloned!")

	async def restusercmd(self, message):
		"""Restore user to state before copying"""
		await message.edit("<b>Restoring account...</b>")
		us = self.db.get(__name__, "about")
		first = self.db.get(__name__, "first")
		last = self.db.get(__name__, "last")
		await message.client(UpdateProfileRequest(
			first if first is not None else "",
			last if last is not None else "",
			us if us is not None else ""
		))
		count = self.db.get(__name__, "avatar_count")
		ava = await message.client.get_profile_photos('me', limit=count)
		await message.client(functions.photos.DeletePhotosRequest(ava))
		self.db.set(__name__, "first_copy", True)
		await message.edit("<b>Account restored</b>")
		await sleep(1)
		await message.delete()

	async def avacmd(self, message):
		"""Send all user avatars"""
		id = utils.get_args_raw(message)
		user = await message.get_reply_message()
		chat = message.input_chat
		if user:
			photos = await self.client.get_profile_photos(user.sender)
			u = True
		else:
			photos = await self.client.get_profile_photos(chat)
			u = False
		if id.strip() == "":
			if len(photos) > 0:
				await self.client.send_file(message.chat_id, photos)
			else:
				try:
					if u:
						photo = await self.client.download_profile_photo(
							user.sender)
					else:
						photo = await self.client.download_profile_photo(
							message.input_chat)
					await self.client.send_file(message.chat_id, photo)
				except:
					await message.edit("<code>This user has no photos</code>")
					return
		else:
			try:
				id = int(id)
				if id <= 0:
					await message.edit(
						"<code>ID number you entered is invalid</code>")
					return
			except:
				await message.edit(
					"<code>ID number you entered is invalid</code>")
				return
			if int(id) <= (len(photos)):
				send_photos = await self.client.download_media(photos[id - 1])
				await self.client.send_file(message.chat_id, send_photos)
			else:
				await message.edit("<code>No photo found with that id</code>")
				return
		await message.delete()

	async def setavacmd(self, message):
		"""Set avatar"""
		reply = await check_mediaa(message)
		if not reply:
			try:
				reply = await message.get_reply_message()
				if not reply:
					return await message.edit(
						"No reply on gif / animated sticker / video message .")
				await message.edit("Downloading...")
				if reply.video:
					await message.client.download_media(reply.media,
					                                    "ava.mp4")
					await message.edit("Converting...")
					os.system(
						"ffmpeg -i ava.mp4 -c copy -an gifavaa.mp4 -y")
					os.system(
						"ffmpeg -i gifavaa.mp4 -vf scale=360:360 gifava.mp4 -y")
				else:
					await message.client.download_media(reply.media,
					                                    "tgs.tgs")
					await message.edit("Converting...")
					os.system(
						"lottie_convert.py tgs.tgs tgs.gif; mv tgs.gif gifava.mp4")
				await message.edit("Installing ava...")
				await message.client(
					functions.photos.UploadProfilePhotoRequest(
						video=await message.client.upload_file("gifava.mp4"),
						video_start_ts=0.0))
				await message.edit("Ava installed.")
				os.system("rm -rf ava.mp4 gifava.mp4 gifavaa.mp4 tgs*")
			except:
				await message.edit(
					"Damn, what a fool I am, I don't know a gif/animated sticker/video from any other file.\n\n" +
					"<b>THIS FILE IS NOT SUPPORTED!!!</b>(or just some tech.error c: )")
				try:
					os.system("rm -rf ava.mp4 gifava.mp4 gifavaa.mp4 tgs*")
				except:
					pass
				return
		else:
			reply = await message.get_reply_message()
			try:
				reply.media.photo
			except:
				await message.edit("Give me a photo pls")
				return
			await message.edit("Downloading...")
			photo = await message.client.download_media(message=reply.photo)
			up = await message.client.upload_file(photo)
			await message.edit("Uploading avatar...")
			await message.client(functions.photos.UploadProfilePhotoRequest(up))
			await message.delete()
			os.remove(photo)

	async def delavacmd(self, message):
		"""Delete main avatar"""
		ava = await message.client.get_profile_photos('me', limit=1)
		if len(ava) > 0:
			await message.edit("Deleting avatar...")
			await message.client(functions.photos.DeletePhotosRequest(ava))
			await message.edit("Avatar deleted!")
		else:
			await message.edit(
				"You doesn't have avatar!")

	async def delavascmd(self, message):
		"""Delete all user avatars"""
		ava = await message.client.get_profile_photos('me')
		if len(ava) > 0:
			await message.edit("Deleting avatars...")
			await message.client(functions.photos.DeletePhotosRequest(
				await message.client.get_profile_photos('me')))
			await message.edit("All avatars deleted!")
		else:
			await message.edit(
				"You don't have avatars!")

	async def setnamecmd(self, message):
		"""Set name"""
		args = utils.get_args_raw(message).split('/')
		if len(args) == 1:
			firstname = args[0]
			lastname = ' '
		elif len(args) == 2:
			firstname = args[0]
			lastname = args[1]
		await message.client(
			UpdateProfileRequest(first_name=firstname, last_name=lastname))
		await message.edit('Name changed successfully!')

	async def setbiocmd(self, message):
		"""Set bio"""
		args = utils.get_args_raw(message)
		if not args:
			return await message.edit('No arguments.')
		await message.client(UpdateProfileRequest(about=args))
		await message.edit('Bio changed successfully!')

	async def setusercmd(self, message):
		"""Set username"""
		args = utils.get_args_raw(message)
		if not args:
			return await message.edit('No arguments.')
		try:
			await message.client(UpdateUsernameRequest(args))
			await message.edit('Username changed successfully!')
		except UsernameOccupiedError:
			await message.edit('This username is already occupied!')


async def check_mediaa(message):
	reply = await message.get_reply_message()
	if not reply:
		return False
	if not reply.file:
		return False
	mime = reply.file.mime_type.split("/")[0].lower()
	if mime != "image":
		return False
	return reply
