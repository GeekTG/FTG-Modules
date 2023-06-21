# API & module author: @mishase

# requires: requests Pillow cryptg

import hashlib
import io
import json
import logging

import PIL
import requests
from telethon import utils
from telethon.tl.types import (
    ChannelParticipantCreator,
    ChannelParticipantsAdmins,
    ChatPhotoEmpty,
    DocumentAttributeSticker,
    Message,
    MessageEntityBold,
    MessageEntityBotCommand,
    MessageEntityCashtag,
    MessageEntityCode,
    MessageEntityHashtag,
    MessageEntityItalic,
    MessageEntityMention,
    MessageEntityMentionName,
    MessageEntityPhone,
    MessageEntityStrike,
    MessageEntityTextUrl,
    MessageEntityUnderline,
    MessageEntityUrl,
    MessageMediaDocument,
    MessageMediaPhoto,
    MessageMediaWebPage,
    PeerBlocked,
    PeerChannel,
    PeerChat,
    PeerUser,
    User,
)

from .. import loader
from .. import utils as ftgUtils

logger = logging.getLogger(__name__)

null = None
false = False
true = True

PIL.Image.MAX_IMAGE_PIXELS = null


class dict(dict):
    def __setattr__(self, attr, value):
        self[attr] = value


BUILD_ID = "96b0cc3e-dca7-4b79-8db2-43a478b00f9a"  # null to disable autoupdates
MODULE_PATH = "https://quotes.mishase.dev/f/module.py"


@loader.tds
class mQuotesMod(loader.Module):
    """Quote a message using Mishase Quotes API"""

    strings = {"name": "Quotes"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            "QUOTE_MESSAGES_LIMIT",
            50,
            "Messages limit",
            "MAX_WIDTH",
            384,
            "Max width (px)",
            "SCALE_FACTOR",
            5,
            "Scale factor",
            "SQUARE_AVATAR",
            false,
            "Square avatar",
            "TEXT_COLOR",
            "white",
            "Text color",
            "REPLY_LINE_COLOR",
            "white",
            "Reply line color",
            "REPLY_THUMB_BORDER_RADIUS",
            2,
            "Reply thumbnail radius (px)",
            "ADMINTITLE_COLOR",
            "#969ba0",
            "Admin title color",
            "MESSAGE_BORDER_RADIUS",
            10,
            "Message radius (px)",
            "PICTURE_BORDER_RADIUS",
            8,
            "Picture radius (px)",
            "BACKGROUND_COLOR",
            "#162330",
            "Background color",
        )

    async def client_ready(self, client, db):
        self.client = client

    @loader.unrestricted
    @loader.ratelimit
    async def quotecmd(self, msg):
        """Quote a message. Args: ?<count> ?file"""
        args = ftgUtils.get_args_raw(msg)
        reply = await msg.get_reply_message()

        if not reply:
            return await msg.edit("No reply message")

        if not msg.out:
            msg = await msg.reply("_")

        count = 1
        forceDocument = false

        if args:
            args = args.split()
            forceDocument = "file" in args
            try:
                count = next(int(arg) for arg in args if arg.isdigit())
                count = max(1, min(self.config["QUOTE_MESSAGES_LIMIT"], count))
            except StopIteration:
                pass

        messagePacker = MessagePacker(self.client)

        if count == 1:
            await msg.edit("<b>Processing...</b>")
            await messagePacker.add(reply)
        if count > 1:
            it = self.client.iter_messages(
                reply.peer_id,
                offset_id=reply.id,
                reverse=true,
                add_offset=1,
                limit=count,
            )

            i = 1
            async for message in it:
                await msg.edit(f"<b>Processing {i}/{count}</b>")
                i += 1
                await messagePacker.add(message)

        messages = messagePacker.messages

        if not messages:
            return await msg.edit("No messages to quote")

        files = []
        for f in messagePacker.files.values():
            files.append(("files", f))

        if not files:
            files.append(("files", bytearray()))

        await msg.edit("<b>API Processing...</b>")

        resp = await ftgUtils.run_sync(
            requests.post,
            "https://quotes.mishase.dev/create",
            data={
                "data": json.dumps(
                    {
                        "messages": messages,
                        "maxWidth": self.config["MAX_WIDTH"],
                        "scaleFactor": self.config["SCALE_FACTOR"],
                        "squareAvatar": self.config["SQUARE_AVATAR"],
                        "textColor": self.config["TEXT_COLOR"],
                        "replyLineColor": self.config["REPLY_LINE_COLOR"],
                        "adminTitleColor": self.config["ADMINTITLE_COLOR"],
                        "messageBorderRadius": self.config["MESSAGE_BORDER_RADIUS"],
                        "replyThumbnailBorderRadius": self.config[
                            "REPLY_THUMB_BORDER_RADIUS"
                        ],
                        "pictureBorderRadius": self.config["PICTURE_BORDER_RADIUS"],
                        "backgroundColor": self.config["BACKGROUND_COLOR"],
                    }
                ),
                "moduleBuild": BUILD_ID,
            },
            files=files,
            timeout=99,
        )

        if resp.status_code == 418:
            if await update(self.allmodules.modules, msg):
                await self.allmodules.commands["quote"](msg)
            else:
                await msg.edit("<b>Update error</b>")
            return

        await msg.edit("<b>Sending...</b>")

        image = io.BytesIO()
        image.name = "quote.webp"

        PIL.Image.open(io.BytesIO(resp.content)).save(image, "WEBP")
        image.seek(0)

        await self.client.send_message(
            msg.peer_id, file=image, force_document=forceDocument
        )

        await msg.delete()

    @loader.unrestricted
    @loader.ratelimit
    async def fquotecmd(self, msg):
        """Fake message quote. Args: @<username>/<id>/<reply> <text>"""
        args = ftgUtils.get_args_raw(msg)
        reply = await msg.get_reply_message()
        splitArgs = args.split(maxsplit=1)
        if len(splitArgs) == 2 and (
            splitArgs[0].startswith("@") or splitArgs[0].isdigit()
        ):
            user = (
                splitArgs[0][1:] if splitArgs[0].startswith("@") else int(splitArgs[0])
            )
            text = splitArgs[1]
        elif reply:
            user = reply.sender_id
            text = args
        else:
            return await msg.edit("Incorrect args")

        try:
            uid = (await self.client.get_entity(user)).id
        except Exception:
            return await msg.edit("User not found")

        async def getMessage():
            return Message(0, uid, message=text)

        msg.message = ""
        msg.get_reply_message = getMessage

        await self.quotecmd(msg)


class MessagePacker:
    def __init__(self, client):
        self.files = dict()
        self.messages = []
        self.client = client

    async def add(self, msg):
        packed = await self.packMessage(msg)
        if packed:
            self.messages.append(packed)

    async def packMessage(self, msg):
        obj = dict()

        text = msg.message
        if text:
            obj.text = text

        entities = MessagePacker.encodeEntities(msg.entities or [])
        if entities:
            obj.entities = entities

        media = msg.media
        if media:
            file = await self.downloadMedia(media)
            if file:
                obj.picture = {"file": file}

        if "text" not in obj and "picture" not in obj:
            return null

        obj.author = await self.encodeAuthor(msg)

        reply = await msg.get_reply_message()
        if reply:
            obj.reply = await self.encodeReply(reply)

        return obj

    def encodeEntities(entities):
        encEntities = []
        for entity in entities:
            entityType = MessagePacker.getEntityType(entity)
            if entityType:
                encEntities.append(
                    {
                        "type": entityType,
                        "offset": entity.offset,
                        "length": entity.length,
                    }
                )
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
        if t in [
            MessageEntityMention,
            MessageEntityTextUrl,
            MessageEntityMentionName,
            MessageEntityHashtag,
            MessageEntityCashtag,
            MessageEntityBotCommand,
        ]:
            return "bluetext"
        return null

    async def downloadMedia(self, inMedia, thumb=null):
        media = MessagePacker.getMedia(inMedia)
        if not media:
            return null
        mid = str(media.id)
        if thumb:
            mid += "." + str(thumb)
        if mid not in self.files:
            try:
                mime = media.mime_type
            except AttributeError:
                mime = "image/jpg"
            dl = await self.client.download_media(media, bytes, thumb=thumb)
            self.files[mid] = (str(len(self.files)), dl, mime)
        return self.files[mid][0]

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
        if not media or isinstance(media, ChatPhotoEmpty):
            return null
        mid = str(media.photo_id)
        if mid not in self.files:
            dl = await self.client.download_profile_photo(entity, bytes)
            self.files[mid] = (str(len(self.files)), dl, "image/jpg")
        return self.files[mid][0]

    async def encodeAuthor(self, msg):
        obj = dict()

        uid, name, picture, adminTitle = await self.getAuthor(msg)

        obj.id = uid
        obj.name = name
        if picture:
            obj.picture = {"file": picture}
        if adminTitle:
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
        if fwd:
            peer = fwd.from_id
            name = fwd.post_author or fwd.from_name

        t = type(peer)
        if t is int:
            uid = peer
        elif t is PeerUser:
            uid = peer.user_id
        elif t is PeerChannel:
            uid = peer.channel_id
        elif t is PeerChat:
            uid = peer.chat_id
        elif t is PeerBlocked:
            uid = peer.peer_id
        elif not peer:
            uid = int(hashlib.shake_256(name.encode("utf-8")).hexdigest(6), 16)

        if not name:
            entity = null
            try:
                entity = await self.client.get_entity(peer)
            except Exception:
                entity = await msg.get_chat()

            if isinstance(entity, User) and entity.deleted:
                name = "Deleted Account"
            else:
                name = utils.get_display_name(entity)

            if full:
                picture = await self.downloadProfilePicture(entity)

                if isinstance(chat, (PeerChannel, PeerChat)):
                    admins = await self.client.get_participants(
                        chat, filter=ChannelParticipantsAdmins
                    )
                    for admin in admins:
                        participant = admin.participant
                        if participant.user_id == uid:
                            try:
                                adminTitle = participant.rank
                            except AttributeError:
                                adminTitle = null
                            if not adminTitle:
                                if isinstance(participant, ChannelParticipantCreator):
                                    adminTitle = "owner"
                                else:
                                    adminTitle = "admin"
                            break

        return uid, name, picture, adminTitle

    async def encodeReply(self, reply):
        obj = dict()

        text = reply.message
        if text:
            obj.text = text
        else:
            media = reply.media
            if media:
                t = type(media)
                if t is MessageMediaPhoto:
                    obj.text = "📷 Photo"
                else:
                    obj.text = "💾 File"

        name = (await self.getAuthor(reply, full=false))[1]

        obj.author = name

        media = reply.media
        if media:
            file = await self.downloadMedia(media, -1)
            if file:
                obj.thumbnail = {"file": file}

        return obj


async def update(modules, message, url=MODULE_PATH):
    loader = next(filter(lambda x: "LoaderMod" == x.__class__.__name__, modules))
    try:
        if await loader.download_and_install(url, message):
            loader._db.set(
                __name__,
                "loaded_modules",
                list(set(loader._db.get(__name__, "loaded_modules", [])).union([url])),
            )
            return true
        else:
            return false
    except Exception:
        return false
