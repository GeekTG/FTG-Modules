# -*- coding: utf-8 -*-

# Hackintosh5 is gay

# API author: @mishase
# Fixed by: @fast_geek
# Module authors: @mishase, @rf0x1d, @D4n13l3k00
# Special thanks to: @h3xcode

# requires: Pillow requests lottie cairosvg

import hashlib
import io
import json
import logging
import os

import PIL
import requests
import telethon
from telethon.tl.types import (MessageEntityBold, MessageEntityItalic,
                               MessageEntityMention, MessageEntityTextUrl,
                               MessageEntityCode, MessageEntityMentionName,
                               MessageEntityHashtag, MessageEntityCashtag,
                               MessageEntityBotCommand, MessageEntityUrl,
                               MessageEntityStrike, MessageEntityUnderline,
                               MessageEntityPhone, ChannelParticipantsAdmins,
                               ChannelParticipantCreator,
                               PeerChannel,
                               User, PeerUser,
                               MessageMediaUnsupported)

from .. import loader, utils

logger = logging.getLogger(__name__)

BUILD_ID = "b890541d-be52-4b9d-8ced-f5359d9d7109"  # None to disable autoupdates
MODULE_PATH = "https://quotes.mishase.dev/f/module.py"


@loader.tds
class mQuotesMod(loader.Module):
	"""Quotes a message using Mishase Quotes API"""
	strings = {
		"name": "mQuotes",
		"silent_processing_cfg_doc": ("Process quote "
		                              "silently(mostly"
		                              " w/o editing)"),
		"module_endpoint_cfg_doc": "Module endpoint URL",
		"quote_limit_cfg_doc": "Limit for messages per quote",
		"max_width_cfg_doc": "Maximum quote width in pixels",
		"scale_factor_cfg_doc": "Quote quality (up to 5.5)",
		"square_avatar_cfg_doc": "Square avatar in quote",
		"text_color_cfg_doc": "Color of text in quote",
		"reply_line_color_cfg_doc": "Reply line color",
		"reply_thumb_radius_cfg_doc": ("Reply media thumbnail "
		                               "radius in pixels"),
		"admintitle_color_cfg_doc": "Admin title color",
		"message_radius_cfg_doc": "Message radius in px",
		"picture_radius_cfg_doc": "Media picture radius in px",
		"background_color_cfg_doc": "Quote background color",
		"quote_limit_reached": ("The maximum number "
		                        "of messages in "
		                        "multiquote - {}."),
		"fq_incorrect_args": ("<b>Args incorrect.</b> \"@$username (ID)"
		                      "$text\" or \"$reply $text\""),
		"updating": "<b>Updating...</b>",
		"update_error": "<b>Update error</b>",
		"processing": "<b>Processing...</b>",
		"unreachable_error": "<b>API Host is unreachable now. Please try again later.</b>",
		"server_error": "<b>API Error occured :)</b>",
		"no_reply": "<b>You didn't reply to a message.</b>",
		"creator": "Owner",
		"admin": "Admin",
		"channel": "Channel",
		"media_type_photo": "Photo",
		"media_type_video": "📹Video",
		"media_type_videomessage": "📹Video message",
		"media_type_voice": "🎵Voice message",
		"media_type_audio": "🎧Music: {} - {}",
		"media_type_contact": "👤Contact: {}",
		"media_type_poll": "📊Poll: ",
		"media_type_quiz": "📊Quiz: ",
		"media_type_location": "📍Location",
		"media_type_gif": "🖼GIF",
		"media_type_sticker": "Sticker",
		"media_type_file": "💾File",
		"dice_type_dice": "Dice",
		"dice_type_dart": "Dart",
		"ball_thrown": "Ball thrown",
		"ball_kicked": "Ball kicked",
		"dart_thrown": "Dart thrown",
		"dart_almostthere": "almost there!",
		"dart_missed": "missed!",
		"dart_bullseye": "bullseye!"
	}

	def __init__(self):
		self.config = loader.ModuleConfig("SILENT_PROCESSING", False,
		                                  lambda: self.strings["silent_processing_cfg_doc"],
		                                  "QUOTE_MESSAGES_LIMIT", 15,
		                                  lambda: self.strings["quote_limit_cfg_doc"],
		                                  "MAX_WIDTH", 384,
		                                  lambda: self.strings["max_width_cfg_doc"],
		                                  "SCALE_FACTOR", 5,
		                                  lambda: self.strings["scale_factor_cfg_doc"],
		                                  "SQUARE_AVATAR", False,
		                                  lambda: self.strings["square_avatar_cfg_doc"],
		                                  "TEXT_COLOR", "white",
		                                  lambda: self.strings["text_color_cfg_doc"],
		                                  "REPLY_LINE_COLOR", "white",
		                                  lambda: self.strings["reply_line_color_cfg_doc"],
		                                  "REPLY_THUMB_BORDER_RADIUS", 2,
		                                  lambda: self.strings["reply_thumb_radius_cfg_doc"],
		                                  "ADMINTITLE_COLOR", "#969ba0",
		                                  lambda: self.strings["admintitle_color_cfg_doc"],
		                                  "MESSAGE_BORDER_RADIUS", 10,
		                                  lambda: self.strings["message_radius_cfg_doc"],
		                                  "PICTURE_BORDER_RADIUS", 8,
		                                  lambda: self.strings["picture_radius_cfg_doc"],
		                                  "BACKGROUND_COLOR", "#162330",
		                                  lambda: self.strings["background_color_cfg_doc"])

	async def client_ready(self, client, db):
		self.client = client

	@loader.unrestricted
	@loader.ratelimit
	async def mquotecmd(self, message):
		""".mquote <reply> - quote a message"""
		await self.quotecmd(message)

	@loader.unrestricted
	@loader.ratelimit
	async def quotecmd(self, message):
		""".quote <reply> - quote a message"""
		if not self.config["SILENT_PROCESSING"]:
			mmm = await utils.answer(
				message,
				self.strings(
					"processing",
					message
				)
			)
		args = utils.get_args_raw(message)
		reply = await message.get_reply_message()
		if not reply:
			return await utils.answer(
				mmm,
				self.strings("no_reply", message)
			)
		if not args or not args.isdigit():
			count = 1
		else:
			count = int(args.strip())
			if count <= 0:
				count = 1
			if count > self.config["QUOTE_MESSAGES_LIMIT"]:
				return await utils.answer(
					mmm,
					self.strings(
						"quote_limit_reached",
						message
					).format(
						self.config["QUOTE_MESSAGES_LIMIT"]
					)
				)
		messages = list()
		messages_client = list()
		media_files = dict()
		current_message = reply.id
		end_message = current_message + count
		while current_message != end_message:
			msg = await self.client.get_messages(
				message.to_id,
				ids=current_message
			)
			if msg:
				messages_client.append(msg)
			current_message += 1
		for msg in messages_client:
			text = msg.raw_text
			markdown = await get_markdown(msg)
			admintitle = str()
			if isinstance(msg.to_id, PeerChannel) and msg.fwd_from:
				user = msg.forward.chat
			else:
				user = await msg.get_sender()
			if msg.fwd_from:
				if msg.fwd_from.saved_from_peer:
					if isinstance(msg.fwd_from.saved_from_peer, PeerUser):
						user_id = msg.fwd_from.saved_from_peer.user_id
					elif isinstance(msg.fwd_from.saved_from_peer, PeerChannel):
						user_id = msg.fwd_from.saved_from_peer.channel_id
					else:
						user_id = None
				elif isinstance(msg.fwd_from.from_id, PeerChannel):
					user_id = msg.fwd_from.from_id.channel_id
				elif isinstance(msg.fwd_from.from_id, PeerUser):
					user_id = msg.fwd_from.from_id.user_id
				else:
					user_id = None
				if not user_id:
					name = msg.fwd_from.from_name
					user_id = int(hashlib.shake_256(name.encode("utf-8")).hexdigest(6), 16)
					pfp = None
				else:
					sender = await self.client.get_entity(user_id)
					name = telethon.utils.get_display_name(sender)
					pfp = media_files.get(
						"@av{}".format(str(user_id).lstrip("-")),
						None
					)
					if msg.fwd_from.saved_from_peer:
						profile_photo_url = msg.forward.chat
					elif msg.fwd_from.from_name:
						name = msg.fwd_from.from_name
						profile_photo_url = None
					elif msg.forward.sender:
						name = telethon.utils. \
							get_display_name(msg.forward.sender)
						profile_photo_url = msg.forward.sender.id
					elif msg.forward.chat:
						profile_photo_url = user
					if msg.fwd_from is not None and msg.fwd_from.post_author is not None:
						name += f" ({msg.fwd_from.post_author})"
					if not pfp:
						pfp = await self.client \
							.download_profile_photo(profile_photo_url, "mishase_cache/")
						if pfp:
							media_files[
								"@av{}".format(str(user_id).lstrip("-"))
							] = pfp
			else:
				user_id = msg.sender_id if \
					msg.sender_id != 1087968824 \
					else message.chat_id
				if not message.chat or (user_id != message.chat_id or isinstance(message.chat, User)):
					sender = await self.client.get_entity(user_id)
					name = telethon.utils.get_display_name(sender)
					pfp = media_files.get(
						"@av{}".format(str(user_id).lstrip("-")),
						None
					)
					if not pfp:
						pfp = await self.client \
							.download_profile_photo(msg.sender_id, "mishase_cache/")
						if pfp:
							media_files[
								"@av{}".format(str(user_id).lstrip("-"))
							] = pfp
				else:
					name = message.chat.title
					try:
						dl_chat_pfp = await self.client \
							.download_profile_photo(user_id, "mishase_cache/")
						no_pfp = False
					except Exception as e:
						logger.error(e, exc_info=True)
						no_pfp = True
					if no_pfp is False:
						media_files[
							"@av{}".format(str(user_id).lstrip("-"))
						] = dl_chat_pfp
			media_files = await check_media(self.client, msg, media_files, False)
			message_reply = await msg.get_reply_message()
			if message_reply:
				reply_text = message_reply.raw_text
				media_caption = await get_media_caption(message_reply)
				if media_caption != "":
					if not reply_text:
						reply_text = media_caption
					else:
						reply_text = "{} \"{}\"".format(
							media_caption,
							reply_text
						)
				if message_reply.fwd_from:
					if message_reply.forward.chat:
						reply_sender = message_reply.forward.chat
						reply_name = telethon.utils.get_display_name(
							reply_sender
						)
						media_files = await check_media(
							self.client,
							message_reply,
							media_files,
							True
						)
						reply_message = {
							"author": reply_name,
							"text": reply_text,
						}
						if "@mediareply{}".format(message_reply.id) in media_files:
							reply_message["thumbnail"] = {
								"file": "@mediareply{}".format(message_reply.id)
							}
					elif message_reply.fwd_from.sender_id:
						reply_sender = message_reply.fwd_from.sender_id
						reply_user = await self.client.get_entity(reply_sender)
						reply_name = telethon.utils.get_display_name(
							reply_user
						)
						media_files = await check_media(
							self.client,
							message_reply,
							media_files,
							True
						)
						reply_message = {
							"author": reply_name,
							"text": reply_text,
						}
						if "@mediareply{}".format(message_reply.id) in media_files:
							reply_message["thumbnail"] = {
								"file": "@mediareply{}".format(message_reply.id)
							}
					else:
						media_files = await check_media(
							self.client,
							message_reply,
							media_files,
							True
						)
						reply_message = {
							"author": message_reply.fwd_from.from_name,
							"text": reply_text,
						}
						if "@mediareply" in media_files:
							reply_message["thumbnail"] = {
								"file": "@mediareply"
							}
				elif message_reply.sender_id:
					reply_sender = message_reply.sender
					reply_name = telethon.utils.get_display_name(reply_sender)
					media_files = await check_media(
						self.client,
						message_reply,
						media_files,
						True
					)
					reply_message = {
						"author": reply_name,
						"text": reply_text
					}
					if "@mediareply{}".format(message_reply.id) in media_files:
						reply_message["thumbnail"] = {
							"file": "@mediareply{}".format(message_reply.id)
						}
				else:
					reply_name = message.chat
					media_files = await check_media(
						self.client,
						message_reply,
						media_files,
						True
					)
					reply_message = {
						"author": reply_name,
						"text": reply_text
					}
					if "@mediareply{}".format(message_reply.id) in media_files:
						reply_message["thumbnail"] = {
							"file": "@mediareply{}".format(message_reply.id)
						}
			else:
				reply_message = None
			if message.chat:
				if msg.sender_id and not msg.fwd_from:
					admins = await self.client \
						.get_participants(message.to_id, filter=ChannelParticipantsAdmins)
					if msg.sender in admins:
						admin = admins[admins.index(msg.sender)].participant
						if not admin:
							admintitle = " "
						else:
							admintitle = admin.rank
						if not admintitle:
							if type(admin) == ChannelParticipantCreator:
								admintitle = self.strings(
									"creator",
									message
								)
							else:
								admintitle = self.strings(
									"admin",
									message
								)
				elif msg.fwd_from.saved_from_peer:
					admintitle = self.strings(
						"channel",
						message
					)
				elif msg.fwd_from.from_id:
					admintitle = self.strings(
						"channel",
						message
					)
				else:
					admintitle = reply.post_author if \
						reply.post_author else " "
			message_to_append = {
				"text": text,
				"reply": reply_message,
				"entities": markdown,
				"author": {
					"id": str(user_id).lstrip("-"),
					"name": name,
					"adminTitle": admintitle
				}
			}
			if f'@av{str(user_id).lstrip("-")}' in media_files:
				message_to_append["author"]["picture"] = {
					"file": f'@av{str(user_id).lstrip("-")}'
				}
			if "@media{}".format(msg.id) in media_files:
				message_to_append["picture"] = {
					"file": "@media{}".format(msg.id)
				}
			messages.append(message_to_append)
		data = {
			"messages": messages,
			"maxWidth": self.config["MAX_WIDTH"],
			"scaleFactor": self.config["SCALE_FACTOR"],
			"squareAvatar": self.config["SQUARE_AVATAR"],
			"textColor": self.config["TEXT_COLOR"],
			"replyLineColor": self.config["REPLY_LINE_COLOR"],
			"adminTitleColor": self.config["ADMINTITLE_COLOR"],
			"messageBorderRadius": self.config["MESSAGE_BORDER_RADIUS"],
			"replyThumbnailBorderRadius": self.config["REPLY_THUMB_BORDER_RADIUS"],
			"pictureBorderRadius": self.config["PICTURE_BORDER_RADIUS"],
			"backgroundColor": self.config["BACKGROUND_COLOR"],
		}
		files = []
		for file in media_files.keys():
			files.append(
				(
					"files",
					(
						file,
						open(
							media_files[file],
							"rb"
						),
						"image/jpg"
					)
				)
			)
		if not files:
			files.append(
				(
					"files",
					(
						"file",
						bytearray(),
						"text/text"
					)
				)
			)
		try:
			req = await utils.run_sync(
				requests.post,
				"https://quotes.mishase.dev/create",
				data={"data": json.dumps(data), "moduleBuild": BUILD_ID},
				files=files,
				timeout=100
			)
		except (requests.ConnectionError, requests.exceptions.Timeout):
			await clean_files()
			return await utils.answer(
				mmm,
				self.strings("unreachable_error", message)
			)
		except:
			pass
		await clean_files()
		if req.status_code >= 520:
			return await utils.answer(
				mmm,
				self.strings("unreachable_error", message)
			)
		if req.status_code >= 500:
			return await utils.answer(
				mmm,
				self.strings("server_error", message)
			)
		if req.status_code == 418:
			if not self.config["SILENT_PROCESSING"]:
				await utils.answer(mmm, self.strings("updating", message))
			if await update(self.allmodules.modules, message):
				return await self.allmodules.commands["quote"](message)
			else:
				return await utils.answer(mmm, self.strings("update_error", message))
		image = io.BytesIO()
		image.name = "quote.webp"
		try:
			PIL.Image.open(io.BytesIO(req.content)).save(image, "WEBP")
			image.seek(0)
			return await utils.answer(mmm, image)
		except Exception as e:
			logger.error(e, exc_info=True)
			return await utils.answer(
				mmm,
				self.strings(
					"server_error",
					message
				)
			)

	@loader.unrestricted
	@loader.ratelimit
	async def fquotecmd(self, message):
		""".fquote @<username> <text> or <reply> <text> - fake quote"""
		if not self.config["SILENT_PROCESSING"]:
			mmm = await utils.answer(
				message,
				self.strings(
					"processing",
					message
				)
			)
		args = utils.get_args_raw(message)
		reply = await message.get_reply_message()
		spl_args = args.split(maxsplit=1)
		if len(spl_args) == 2 and (spl_args[0].startswith('@') or spl_args[0].isdigit()):
			user = spl_args[0][1:] if spl_args[0].startswith('@') else int(spl_args[0])
			text = spl_args[1]
		elif reply:
			user = reply.sender_id
			text = " ".join(spl_args)
		else:
			await utils.answer(
				mmm,
				self.strings(
					"fq_incorrect_args",
					message
				)
			)
			return
		try:
			user = await self.client.get_entity(user)
			name = telethon.utils.get_display_name(user)
			avatar = await self.client.download_profile_photo(user.id, "mishase_cache/") if not str(user).isdigit() else \
				await self.client.download_profile_photo(user, "mishase_cache/")
		except:
			await utils.answer(
				mmm,
				self.strings(
					"fq_incorrect_args",
					message
				)
			)
			return
		files = []
		msg = {
			"text": text,
			"reply": None,
			"entities": [],
			"author": {
				"id": str(user.id) if not str(user).isdigit() else str(user),
				"name": name,
				"adminTitle": ' ',
			}
		}
		if avatar:
			msg['author']['picture'] = {'file': f'@av{str(user.id).lstrip("-")}'}
			files.append(("files", (
				f'@av{str(user.id if not str(user).isdigit() else user).lstrip("-")}', open(avatar, "rb"),
				"image/jpg")))
		else:
			files.append(("files", ("file", bytearray(), "text/text")))
		data = {
			"messages": [msg],
			"maxWidth": self.config["MAX_WIDTH"],
			"scaleFactor": self.config["SCALE_FACTOR"],
			"squareAvatar": self.config["SQUARE_AVATAR"],
			"textColor": self.config["TEXT_COLOR"],
			"replyLineColor": self.config["REPLY_LINE_COLOR"],
			"adminTitleColor": self.config["ADMINTITLE_COLOR"],
			"messageBorderRadius": self.config["MESSAGE_BORDER_RADIUS"],
			"replyThumbnailBorderRadius": self.config["REPLY_THUMB_BORDER_RADIUS"],
			"pictureBorderRadius": self.config["PICTURE_BORDER_RADIUS"],
			"backgroundColor": self.config["BACKGROUND_COLOR"],
		}
		try:
			req = await utils.run_sync(
				requests.post,
				"https://quotes.mishase.dev/create",
				data={"data": json.dumps(data), "moduleBuild": BUILD_ID},
				files=files,
				timeout=100
			)
		except (requests.ConnectionError, requests.exceptions.Timeout):
			await clean_files()
			return await utils.answer(
				mmm,
				self.strings("unreachable_error", message)
			)
		await clean_files()
		if req.status_code >= 520:
			return await utils.answer(
				mmm,
				self.strings("unreachable_error", message)
			)
		if req.status_code >= 500:
			return await utils.answer(
				mmm,
				self.strings("server_error", message)
			)
		if req.status_code == 418:
			if not self.config["SILENT_PROCESSING"]:
				await utils.answer(mmm, self.strings("updating", message))
			if await update(self.allmodules.modules, message):
				return await self.allmodules.commands["quote"](message)
			else:
				return await utils.answer(mmm, self.strings("update_error", message))
		image = io.BytesIO()
		image.name = "fquote.webp"
		try:
			PIL.Image.open(io.BytesIO(req.content)).save(image, "WEBP")
			image.seek(0)
			return await utils.answer(mmm, image)
		except Exception as e:
			logger.error(e, exc_info=True)
			return await utils.answer(
				mmm,
				self.strings(
					"server_error",
					message
				)
			)


async def clean_files():
	return os.system("rm -rf mishase_cache/*")


async def update(modules, message, url=MODULE_PATH):
	loader = next(filter(lambda x: "LoaderMod" == x.__class__.__name__, modules))
	try:
		if await loader.download_and_install(url, message):
			loader._db.set(__name__, "loaded_modules",
			               list(set(loader._db.get(__name__, "loaded_modules", [])).union([url])))
			return True
		else:
			return False
	except Exception as e:
		logger.error(e, exc_info=True)
		return False


async def check_media(client, reply, media_files: dict, is_reply: bool):
	allowed_exts = [".png", ".webp", ".jpg", ".jpeg", ".tgs", ".mp4"]
	if reply and reply.media:
		if reply.photo:
			data = reply.photo
		elif reply.document:
			if reply.audio or reply.voice:
				return media_files
			elif reply.file.ext not in allowed_exts:
				return media_files
			data = reply.media.document
		else:
			return media_files
	else:
		return media_files
	if not data or data is None:
		return media_files
	else:
		if reply.file.ext == ".tgs":
			if not is_reply:
				data = await client.download_media(data, "mishase_cache/")
				new = data + ".png"
				os.system(f"lottie_convert.py \"{data}\" \"{new}\" --frame 5")
				data = new
			else:
				data = await client.download_media(data, thumb=-1)
		elif reply.file.ext == ".mp4":
			data = await client.download_media(data, thumb=-1)
		else:
			data = await client.download_media(data, "mishase_cache/")
		if not is_reply:
			media_files["@media{}".format(reply.id)] = data
		else:
			media_files["@mediareply{}".format(reply.id)] = data
		return media_files


async def get_media_caption(reply_message):
	if reply_message and reply_message.media:
		if type(reply_message.media) == MessageMediaUnsupported:
			return "Unsupported message media"
		if reply_message.photo:
			return mQuotesMod.strings["media_type_photo"]
		dice = False
		try:
			dice = True if reply_message.dice else False
		except AttributeError:
			try:
				dice = True if type(reply_message.media) == telethon.tl.types.MessageMediaDice else False
			except AttributeError:
				pass
		if dice:
			dice_type = ""
			dice_text = reply_message.media.value
			if reply_message.media.emoticon == "🎲":
				dice_type = mQuotesMod.strings["dice_type_dice"]
				return "{} {}: {}".format(reply_message.media.emoticon, dice_type, dice_text)
			elif reply_message.media.emoticon == "🎯":
				if dice_text == 1:
					dice_text = mQuotesMod.strings["dart_missed"]
				elif dice_text == 5:
					dice_text = mQuotesMod.strings["dart_almostthere"]
				elif dice_text == 6:
					dice_text = mQuotesMod.strings["dart_bullseye"]
				else:
					return "{} {}".format(reply_message.media.emoticon, mQuotesMod.strings["dart_thrown"])
				dice_type = mQuotesMod.strings["dice_type_dart"]
				return "{} {}: {}".format(reply_message.media.emoticon, dice_type, dice_text)
			elif reply_message.media.emoticon == "🏀":
				return "{} {}".format(reply_message.media.emoticon, mQuotesMod.strings["ball_thrown"])
			elif reply_message.media.emoticon == b"\xe2\x9a\xbd".decode():
				return "{} {}".format(reply_message.media.emoticon, mQuotesMod.strings["ball_kicked"])
			else:
				return "Unsupported dice type ({}): {}" \
					.format(reply_message.media.emoticon, reply_message.media.value)
		elif reply_message.poll:
			if reply_message.poll.poll.quiz:
				return mQuotesMod.strings["media_type_quiz"] + reply_message.poll.poll.question
			else:
				return mQuotesMod.strings["media_type_poll"] + reply_message.poll.poll.question
		elif reply_message.geo:
			return mQuotesMod.strings["media_type_location"]
		elif reply_message.contact:
			name = reply_message.contact.first_name + reply_message.contact.last_name
			return mQuotesMod.strings["media_type_contact"].format(
				name
			)
		elif reply_message.document:
			if reply_message.gif:
				return mQuotesMod.strings["media_type_gif"]
			elif reply_message.video:
				if reply_message.video.attributes[0].round_message:
					return mQuotesMod.strings["media_type_videomessage"]
				else:
					return mQuotesMod.strings["media_type_video"]
			elif reply_message.audio:
				return mQuotesMod.strings["media_type_audio"].format(
					reply_message.audio.attributes[0].performer,
					reply_message.audio.attributes[0].title
				)
			elif reply_message.voice:
				return mQuotesMod.strings["media_type_voice"]
			elif reply_message.sticker:
				emoji = reply_message.file.emoji
				caption = "{} {}".format(
					emoji,
					mQuotesMod.strings["media_type_sticker"]
				) if emoji \
					else mQuotesMod.strings["media_type_sticker"]
				return caption
			elif reply_message.file:
				try:
					file_name = reply_message.file.name
					file_size = await humanize(
						reply_message.file.size
					)
					return "{} {} ({})".format(
						mQuotesMod.strings["media_type_file"],
						file_name,
						file_size
					)
				except Exception:
					return mQuotesMod.strings["media_type_file"]
		else:
			return ""
	else:
		return ""
	return ""


async def humanize(num: float, suffix: str = "B") -> str:
	for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
		if abs(num) < 1024.0:
			return "%3.1f%s%s" % (num, unit, suffix)
		num /= 1024.0
	return "%.1f%s%s" % (num, "Yi", suffix)


async def get_markdown(message):
	entities = []
	if not message.entities:
		return []
	for entity in message.entities:
		entity_type = type(entity)
		start = entity.offset
		end = entity.length
		if entity_type is MessageEntityBold:
			etype = "bold"
		elif entity_type is MessageEntityItalic:
			etype = "italic"
		elif entity_type in [MessageEntityUrl, MessageEntityPhone]:
			etype = "url"
		elif entity_type is MessageEntityCode:
			etype = "monospace"
		elif entity_type is MessageEntityStrike:
			etype = "strikethrough"
		elif entity_type is MessageEntityUnderline:
			etype = "underline"
		elif entity_type in [MessageEntityMention, MessageEntityTextUrl, MessageEntityMentionName, MessageEntityHashtag,
		                     MessageEntityCashtag, MessageEntityBotCommand]:
			etype = "bluetext"
		entities.append({"type": etype, "offset": start, "length": end})
	return entities
