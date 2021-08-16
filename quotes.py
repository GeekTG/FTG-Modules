# -*- coding: utf-8 -*-

# API & module author: @mishase

# requires: requests Pillow cryptg 

import hashlib
import json
import os
import requests
import io
import PIL
from uuid import uuid4 as uuid
from telethon import utils
from telethon.tl.types import (Message, MessageEntityBold, MessageEntityItalic,
                               MessageEntityMention, MessageEntityTextUrl,
                               MessageEntityCode, MessageEntityMentionName,
                               MessageEntityHashtag, MessageEntityCashtag,
                               MessageEntityBotCommand, MessageEntityUrl,
                               MessageEntityStrike, MessageEntityUnderline,
                               MessageEntityPhone,
                               ChatPhotoEmpty,
                               MessageMediaPhoto, MessageMediaDocument, MessageMediaWebPage,
                               Channel, User,
                               PeerUser, PeerBlocked, PeerChannel, PeerChat,
                               DocumentAttributeSticker,
                               ChannelParticipantsAdmins,
                               ChannelParticipantCreator)
from .. import loader, utils as ftgUtils

null = None
false = False
true = True


class dict(dict):
    def __setattr__(self, attr, value):
        self[attr] = value


BUILD_ID = "4aa6bc09-47fd-42f7-a125-d4bb00637fdd" # null to disable autoupdates
MODULE_PATH = "https://quotes.mishase.dev/f/module.py"


@loader.tds
class mQuotesMod(loader.Module):
    """Quote message using Mishase Quotes API"""
    strings = {
        "name": "mQuotes",
    }

    async def client_ready(self, client, db):
        self.client = client

    @loader.unrestricted
    @loader.ratelimit
    async def quotecmd(self, msg):
        """.quote <count> - quote a message"""
        args = ftgUtils.get_args_raw(msg)
        reply = await msg.get_reply_message()

        if not reply:
            return await msg.edit("No reply message")

        count = 1

        if args is not null and args.isdigit():
            count = int(args.strip())
            count = max(1, min(50, count))

        directory = str(uuid())
        os.mkdir(directory)

        messagePacker = MessagePacker(self.client, directory)

        i = 1

        if count == 1:
            await msg.edit(f"<b>Processing...</b>")
            await messagePacker.add(reply)
        if count > 1:
            it = self.client.iter_messages(
                reply.peer_id, offset_id=reply.id, reverse=true, add_offset=1, limit=count)

            async for message in it:
                await msg.edit(f"<b>Processing {i}/{count}</b>")
                i += 1
                await messagePacker.add(message)

        messages = messagePacker.messages

        if len(messages) == 0:
            return await msg.edit("No messages to quote")

        files = []
        for f in messagePacker.files.values():
            files.append(("files", open(f, "rb")))

        if len(files) == 0:
            files.append(("files", bytearray()))

        await msg.edit(f"<b>API Processing...</b>")

        resp = await ftgUtils.run_sync(
            requests.post,
            "https://quotes.mishase.dev/create",
            data={
                "data": json.dumps({"messages": messages}),
                "moduleBuild": BUILD_ID
            },
            files=files,
            timeout=99
        )

        for root, dirs, files in os.walk(directory):
            for name in files:
                os.remove(os.path.join(root, name))

        os.rmdir(directory)

        if resp.status_code == 418:
            if await update(self.allmodules.modules, msg):
                await self.allmodules.commands["quote"](msg)
            else:
                await msg.edit("<b>Update error</b>")
            return

        await msg.edit(f"<b>Sending...</b>")

        image = io.BytesIO()
        image.name = "quote.webp"

        PIL.Image.open(io.BytesIO(resp.content)).save(image, "WEBP")
        image.seek(0)

        await msg.reply(file=image)

        await msg.delete()

    @loader.unrestricted
    @loader.ratelimit
    async def fquotecmd(self, msg):
        """.fquote @username/id/<reply> text"""
        args = ftgUtils.get_args_raw(msg)
        reply = await msg.get_reply_message()
        splitArgs = args.split(maxsplit=1)
        if len(splitArgs) == 2 and (splitArgs[0].startswith('@') or splitArgs[0].isdigit()):
            user = splitArgs[0][1:] if splitArgs[0].startswith(
                '@') else int(splitArgs[0])
            text = splitArgs[1]
        elif reply:
            user = reply.sender_id
            text = args
        else:
            return await msg.edit("Incorrect args")

        directory = str(uuid())
        os.mkdir(directory)

        messagePacker = MessagePacker(self.client, directory)

        async def getMessage():
            entity = await self.client.get_entity(user)
            return Message(0, entity.id, message=text)

        msg.get_reply_message = getMessage

        await self.quotecmd(msg)


class MessagePacker:
    def __init__(self, client, directory):
        self.files = dict()
        self.messages = []
        self.client = client
        self.directory = directory

    async def add(self, msg):
        packed = await self.packMessage(msg)
        if packed is not null:
            self.messages.append(packed)

    async def packMessage(self, msg):
        obj = dict()

        text = msg.message
        if text is not null and len(text) > 0:
            obj.text = text

        entities = MessagePacker.encodeEntities(msg.entities or [])
        if len(entities) > 0:
            obj.entities = entities

        media = msg.media
        if media is not null:
            file = await self.downloadMedia(media)
            if file is not null:
                obj.picture = {
                    "file": file
                }

        if "text" not in obj and "picture" not in obj:
            return null

        obj.author = await self.encodeAuthor(msg)

        reply = await msg.get_reply_message()
        if reply is not null:
            obj.reply = await self.encodeReply(reply)

        return obj

    def encodeEntities(entities):
        encEntities = []
        for entity in entities:
            entityType = MessagePacker.getEntityType(entity)
            if entityType is not null:
                encEntities.append({
                    "type": entityType,
                    "offset": entity.offset,
                    "length": entity.length
                })
        return encEntities

    def getEntityType(entity):
        t = type(entity)
        if t is MessageEntityBold:
            return "bold"
        if t is MessageEntityItalic:
            return "italic"
        if t in [MessageEntityUrl, MessageEntityPhone]:
            return "url"
        if t is MessageEntityCode:
            return "monospace"
        if t is MessageEntityStrike:
            return "strikethrough"
        if t is MessageEntityUnderline:
            return "underline"
        if t in [MessageEntityMention, MessageEntityTextUrl, MessageEntityMentionName, MessageEntityHashtag,
                 MessageEntityCashtag, MessageEntityBotCommand]:
            return "bluetext"
        return null

    async def downloadMedia(self, inMedia, thumb=null):
        media = MessagePacker.getMedia(inMedia)
        if media is null:
            return null
        mid = str(media.id)
        if thumb is not null:
            mid += "." + str(thumb)
        if mid not in self.files:
            self.files[mid] = await self.client.download_media(media, self.directory, thumb=thumb)
        return os.path.basename(self.files[mid])

    def getMedia(media):
        t = type(media)
        if t is MessageMediaPhoto:
            return media.photo
        if t is MessageMediaDocument:
            for attribute in media.document.attributes:
                if isinstance(attribute, DocumentAttributeSticker):
                    return media.document
        elif t is MessageMediaWebPage:
            if media.webpage.type == "photo":
                return media.webpage.photo
        return null

    async def downloadProfilePicture(self, entity):
        media = entity.photo
        if media is null or isinstance(media, ChatPhotoEmpty):
            return null
        mid = str(media.photo_id)
        if mid not in self.files:
            self.files[mid] = await self.client.download_profile_photo(entity, self.directory)
        return os.path.basename(self.files[mid])

    async def encodeAuthor(self, msg):
        obj = dict()

        uid, name, picture, adminTitle = await self.getAuthor(msg)

        obj.id = uid
        obj.name = name
        if picture is not null:
            obj.picture = {
                "file": picture
            }
        if adminTitle is not null:
            obj.adminTitle = adminTitle

        return obj

    async def getAuthor(self, msg, full=true):
        uid = null
        name = null
        picture = null
        adminTitle = null

        chat = msg.peer_id
        peer = msg.from_id or chat
        fwd = msg.fwd_from
        if fwd is not null:
            peer = fwd.from_id
            name = fwd.post_author or fwd.from_name

        t = type(peer)
        if t is int:
            uid = peer
        elif t in PeerUser:
            uid = peer.user_id
        elif t in PeerChannel:
            uid = peer.channel_id
        elif t in PeerChat:
            uid = peer.chat_id
        elif t is PeerBlocked:
            uid = peer.peer_id
        elif peer is null:
            uid = int(hashlib.shake_256(
                name.encode("utf-8")).hexdigest(6), 16)

        if name is null:
            entity = null
            try:
                entity = await self.client.get_entity(peer)
            except:
                entity = await msg.get_chat()

            name = utils.get_display_name(entity)

            if full:
                picture = await self.downloadProfilePicture(entity)

                if isinstance(chat, (PeerChannel, PeerChat)):
                    admins = await self.client.get_participants(chat, filter=ChannelParticipantsAdmins)
                    for admin in admins:
                        participant = admin.participant
                        if participant.user_id == uid:
                            adminTitle = participant.rank
                            if adminTitle is null:
                                if isinstance(participant, ChannelParticipantCreator):
                                    adminTitle = "owner"
                                else:
                                    adminTitle = "admin"
                            break

        return uid, name, picture, adminTitle

    async def encodeReply(self, reply):
        obj = dict()

        text = reply.message
        if text is not null and len(text) > 0:
            obj.text = text

        name = (await self.getAuthor(reply, full=false))[1]

        obj.author = name

        media = reply.media
        if media is not null:
            file = await self.downloadMedia(media, -1)
            if file is not null:
                obj.thumbnail = {
                    "file": file
                }

        return obj


async def update(modules, message, url=MODULE_PATH):
    loader = next(filter(lambda x: "LoaderMod" ==
                  x.__class__.__name__, modules))
    try:
        if await loader.download_and_install(url, message):
            loader._db.set(__name__, "loaded_modules",
                           list(set(loader._db.get(__name__, "loaded_modules", [])).union([url])))
            return True
        else:
            return False
    except Exception as e:
        return False
