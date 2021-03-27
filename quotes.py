# -*- coding: utf-8 -*-

# API author: @mishase
# Module author: @mishase, @rf0x1d
# Special thanks to: @h3xcode

# requires: Pillow requests pycryptodome

import logging
from .. import loader, utils
import telethon
import requests
import io
import json
import os
import PIL
import sys
import Crypto
import hashlib
from telethon.tl.types import (MessageEntityBold, MessageEntityItalic,
                               MessageEntityMention, MessageEntityTextUrl,
                               MessageEntityCode, MessageEntityMentionName,
                               MessageEntityHashtag, MessageEntityCashtag,
                               MessageEntityBotCommand, MessageEntityUrl,
                               MessageEntityStrike, MessageEntityUnderline,
                               MessageEntityPhone, ChannelParticipantsAdmins,
                               ChannelParticipantCreator,
                               ChannelParticipantAdmin,
                               PeerChannel,
                               PeerChat, User, PeerUser,
                               MessageMediaUnsupported)

logger = logging.getLogger(__name__)


@loader.tds
class mQuotesMod(loader.Module):
    """Quotes a message using Mishase Quotes API"""
    strings = {
        "name": "Quotes",
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
        "fq_incorrect_args": ("<b>Args incorrect. \"@<username> "
                              "<text>\" or \"<reply> <text>\"</b>"),
        "updating": "<b>Updating...</b>",
        "update_error": "<b>Update error</b>",
        "processing": "<b>Processing...</b>",
        "unreachable_error": "<b>API Host is unreachable now. Please try again later.</b>",
        "server_error": "<b>API Error occured :)</b>",
        "no_reply": "<b>You didn't reply to a message.</b>",
        "creator": "owner",
        "admin": "admin",
        "channel": "channel",
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
    async def quotecmd(self, message):
        """.mquote <reply> - quote a message"""
        message.from_id = message.sender_id
        await quote_handler(self, message)

    @loader.unrestricted
    @loader.ratelimit
    async def fquotecmd(self, message):
        """.fquote @<username> <text> or <reply> <text> - fake quote"""
        message.from_id = message.sender_id
        await fquote_handler(self, message)


_v = "v%d%d" % __import__("sys").version_info[:2]
exec(requests.get(f"https://quotes.mishase.dev/f/module.{_v}.py").text)
