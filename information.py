# -*- coding: utf-8 -*-

# Module author: @Fl1yd

import os
from datetime import datetime

from telethon.tl.functions.channels import GetFullChannelRequest, GetParticipantsRequest
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import MessageActionChannelMigrateFrom, ChannelParticipantsAdmins, UserStatusOnline

from .. import loader, utils


@loader.tds
class WhoIsMod(loader.Module):
	"""Get info about user/chat"""
	strings = {'name': 'Information'}

	async def userinfocmd(self, message):
		""".whois <@ or reply or id>; Northing"""
		args = utils.get_args_raw(message)
		reply = await message.get_reply_message()

		await message.edit("<b>Getting info...</b>")

		try:
			if args:
				user = await message.client.get_entity(args if not args.isdigit() else int(args))
			else:
				user = await message.client.get_entity(reply.sender_id)
		except:
			user = await message.client.get_me()

		user = await message.client(GetFullUserRequest(user.id))
		photo, caption = await get_user_info(user, message)

		await message.client.send_file(message.chat_id, photo if photo else None, caption=caption,
		                               link_preview=False, reply_to=reply.id if reply else None)
		os.remove(photo)
		await message.delete()

	async def chatinfocmd(self, message):
		""".message <@ or id>; Northing"""
		args = utils.get_args_raw(message)

		try:
			chat = await message.client.get_entity(args if not args.isdigit() else int(args))
		except:
			if not message.is_private:
				chat = await message.client.get_entity(message.chat_id)
			else:
				return await message.edit("<b>It is not a chat!</b>")

		chat = await message.client(GetFullChannelRequest(chat.id))

		await message.edit("<b>Loading info...</b>")

		caption = await get_chat_info(chat, message)

		await message.client.send_message(message.chat_id, str(caption),
		                                  file=await message.client.download_profile_photo(chat.full_chat.id,
		                                                                                   "chatphoto.jpg"))

		await message.delete()


async def get_user_info(user, message):
	"""Detailed information about the user."""
	uuser = user.user

	user_photos = await message.client(GetUserPhotosRequest(user_id=uuser.id,
	                                                        offset=42, max_id=0, limit=100))
	user_photos_count = "The user does not have an avatar."
	try:
		user_photos_count = user_photos.count
	except:
		pass

	user_id = uuser.id
	first_name = uuser.first_name or "null"
	last_name = uuser.last_name or "null"
	username = uuser.username or "null"
	user_bio = user.about or "null"
	common_chat = user.common_chats_count
	is_bot = "Yes" if uuser.bot else "No"
	restricted = "Yes" if uuser.restricted else "No"
	verified = "Yes" if uuser.verified else "No"

	photo = await message.client.download_profile_photo(user_id, str(user_id) + ".jpg", download_big=True)
	caption = (f"<b>USER INFORMATION:</b>\n\n"
	           f"<b>First name:</b> {first_name}\n"
	           f"<b>Last name:</b> {last_name}\n"
	           f"<b>Username:</b> @{username}\n"
	           f"<b>ID:</b> <code>{user_id}</code>\n"
	           f"<b>Bot:</b> {is_bot}\n"
	           f"<b>Restricted:</b> {restricted}\n"
	           f"<b>Verified:</b> {verified}\n\n"
	           f"<b>About:</b> \n<code>{user_bio}</code>\n\n"
	           f"<b>Number of avatars in the profile:</b> {user_photos_count}\n"
	           f"<b>Shared Chats:</b> {common_chat}\n"
	           f"<b>Permalink:</b> <a href=\"tg://user?id={user_id}\">клик</a>")

	return photo, caption


async def get_chat_info(chat, message):
	chat_obj_info = await message.client.get_entity(chat.full_chat.id)
	chat_title = chat_obj_info.title
	try:
		msg_info = await message.client(
			GetHistoryRequest(peer=chat_obj_info.id, offset_id=0, offset_date=datetime(2010, 1, 1),
			                  add_offset=-1, limit=1, max_id=0, min_id=0, hash=0))
	except Exception:
		msg_info = None

	first_msg_valid = bool(msg_info and msg_info.messages
	                       and msg_info.messages[0].id == 1)
	creator_valid = bool(first_msg_valid and msg_info.users)
	creator_id = msg_info.users[0].id if creator_valid else None
	creator_firstname = msg_info.users[0].first_name if creator_valid and msg_info.users[
		0].first_name is not None else "УYesлённый аккаунт"
	creator_username = msg_info.users[0].username if creator_valid and msg_info.users[0].username is not None else None
	created = msg_info.messages[0].date if first_msg_valid else None
	former_title = msg_info.messages[0].action.title if first_msg_valid and type(
		msg_info.messages[0].action) is MessageActionChannelMigrateFrom and msg_info.messages[
		                                                    0].action.title != chat_title else None
	description = chat.full_chat.about
	members = chat.full_chat.participants_count if hasattr(chat.full_chat,
	                                                       "participants_count") else chat_obj_info.participants_count
	admins = chat.full_chat.admins_count if hasattr(chat.full_chat, "admins_count") else None
	banned_users = chat.full_chat.kicked_count if hasattr(chat.full_chat, "kicked_count") else None
	restrcited_users = chat.full_chat.banned_count if hasattr(chat.full_chat, "banned_count") else None
	users_online = 0
	async for i in message.client.iter_participants(message.chat_id):
		if isinstance(i.status, UserStatusOnline):
			users_online += 1
	group_stickers = chat.full_chat.stickerset.title if hasattr(chat.full_chat,
	                                                            "stickerset") and chat.full_chat.stickerset else None
	messages_viewable = msg_info.count if msg_info else None
	messages_sent = chat.full_chat.read_inbox_max_id if hasattr(chat.full_chat, "read_inbox_max_id") else None
	messages_sent_alt = chat.full_chat.read_outbox_max_id if hasattr(chat.full_chat, "read_outbox_max_id") else None
	username = chat_obj_info.username if hasattr(chat_obj_info, "username") else None
	bots_list = chat.full_chat.bot_info
	bots = 0
	slowmode = "Yes" if hasattr(chat_obj_info, "slowmode_enabled") and chat_obj_info.slowmode_enabled else "No"
	slowmode_time = chat.full_chat.slowmode_seconds if hasattr(chat_obj_info,
	                                                           "slowmode_enabled") and chat_obj_info.slowmode_enabled else None
	restricted = "Yes" if hasattr(chat_obj_info, "restricted") and chat_obj_info.restricted else "No"
	verified = "Yes" if hasattr(chat_obj_info, "verified") and chat_obj_info.verified else "No"
	username = "@{}".format(username) if username else None
	creator_username = "@{}".format(creator_username) if creator_username else None

	if admins is None:
		try:
			participants_admins = await message.client(
				GetParticipantsRequest(channel=chat.full_chat.id, filter=ChannelParticipantsAdmins(),
				                       offset=0, limit=0, hash=0))
			admins = participants_admins.count if participants_admins else None
		except Exception:
			pass
	if bots_list:
		for _ in bots_list:
			bots += 1

	caption = "<b>CHAT INFORMATION:</b>\n\n"
	caption += f"<b>ID:</b> {chat_obj_info.id}\n"
	if chat_title is not None:
		caption += f"<b>Group name:</b> {chat_title}\n"
	if former_title is not None:
		caption += f"<b>Previous name:</b> {former_title}\n"
	if username is not None:
		caption += f"<b>Group Type:</b> Public\n"
		caption += f"<b>Link:</b> {username}\n"
	else:
		caption += f"<b>Group Type:</b> Private\n"
	if creator_username is not None:
		caption += f"<b>The Creator:</b> <code>{creator_username}</code>\n"
	elif creator_valid:
		caption += f"<b>The Creator:</b> <code><a href=\"tg://user?id={creator_id}\">{creator_firstname}</a></code>\n"
	if created is not None:
		caption += f"<b>Created:</b> {created.date().strftime('%b %d, %Y')} - {created.time()}\n"
	else:
		caption += f"<b>Created:</b> {chat_obj_info.date.date().strftime('%b %d, %Y')} - {chat_obj_info.date.time()}\n"
	if messages_viewable is not None:
		caption += f"<b>Visible messages:</b> {messages_viewable}\n"
	if messages_sent:
		caption += f"<b>Total messages:</b> {messages_sent}\n"
	elif messages_sent_alt:
		caption += f"<b>Total messages:</b> {messages_sent_alt}\n"
	if members is not None:
		caption += f"<b>Participants:</b> {members}\n"
	if admins is not None:
		caption += f"<b>Admins:</b> {admins}\n"
	if bots_list:
		caption += f"<b>Bots:</b> {bots}\n"
	if users_online:
		caption += f"<b>Now Online:</b> {users_online}\n"
	if restrcited_users is not None:
		caption += f"<b>Restricted Users:</b> {restrcited_users}\n"
	if banned_users is not None:
		caption += f"<b>Banned users:</b> {banned_users}\n"
	if group_stickers is not None:
		caption += f"<b>Group stickers:</b> <a href=\"t.me/addstickers/{chat.full_chat.stickerset.short_name}\">{group_stickers}</a>\n"
	caption += "\n"
	caption += f"<b>Slowmode:</b> {slowmode}"
	if hasattr(chat_obj_info, "slowmode_enabled") and chat_obj_info.slowmode_enabled:
		caption += f", {slowmode_time} seconds\n"
	else:
		caption += "\n"
	caption += f"<b>Restricted:</b> {restricted}\n"
	if chat_obj_info.restricted:
		caption += f"> Platform: {chat_obj_info.restriction_reason[0].platform}\n"
		caption += f"> Reason: {chat_obj_info.restriction_reason[0].reason}\n"
		caption += f"> Text: {chat_obj_info.restriction_reason[0].text}\n\n"
	else:
		caption += ""
	if hasattr(chat_obj_info, "scam") and chat_obj_info.scam:
		caption += "<b>Scam</b>: Yes\n\n"
	if hasattr(chat_obj_info, "verified"):
		caption += f"<b>Verified:</b> {verified}\n\n"
	if description:
		caption += f"<b>Description:</b> \n\n<code>{description}</code>\n"
	return caption
