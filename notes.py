# -*- coding: utf-8 -*-

import logging

from .. import loader, utils

logger = logging.getLogger("friendly-telegram.modules.notes")


@loader.tds
class NotesMod(loader.Module):
    """Stores global notes (aka snips)"""

    strings = {
        "name": "Notes",
        "what_note": "<b>What note should I show?</b>",
        "no_note": "<b>Note not found</b>",
        "save_what": "<b>And what to save?</b>",
        "what_name": "<b>And what will the note be called?</b>",
        "saved": "<b>Note saved as:</b> <code>{}</code>",
        "notes_header": "<b>Saved Notes:</b>\n\n",
        "notes_item": "<b>▷</b> <code>{}</code>",
        "delnote_args": "<b>And what note should I delete?</b>",
        "delnote_done": "<b>Note deleted!</b>",
        "delnotes_none": "<b>And there are no notes...</b>",
        "delnotes_done": "<b>ALL NOTES DELETED</b>",
        "notes_none": "<b>And there are no notes...</b>",
    }

    async def findnotecmd(self, message):
        """Gets the note specified"""
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, self.strings("what_note", message))
            return
        asset_id = self._db.get("friendly-telegram.modules.notes", "notes", {}).get(
            args[0], None
        )
        logger.debug(asset_id)
        asset = await self._db.fetch_asset(asset_id) if asset_id is not None else None
        if asset is None:
            self.del_note(args[0])
            await utils.answer(message, self.strings("no_note", message))
            return
        link = "https://t.me/c/{}/{}".format(asset.chat.id, asset.id)
        await message.edit(
            f'<b>Заметка</b> "<code>{args[0]}</code>" <a href="{link}">находится здесь.</a>'
        )

    async def notecmd(self, message):
        """Gets the note specified"""
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, self.strings("what_note", message))
            return
        asset_id = self._db.get("friendly-telegram.modules.notes", "notes", {}).get(
            args[0], None
        )
        logger.debug(asset_id)
        asset = await self._db.fetch_asset(asset_id) if asset_id is not None else None
        if asset is None:
            self.del_note(args[0])
            await utils.answer(message, self.strings("no_note", message))
            return
        if message.out:
            await message.delete()
        await message.client.send_message(
            message.chat_id,
            await self._db.fetch_asset(asset_id),
            reply_to=await message.get_reply_message(),
        )

    async def delallnotescmd(self, message):
        """Deletes all the saved notes"""
        if not self._db.get("friendly-telegram.modules.notes", "notes", {}):
            await utils.answer(message, self.strings("delnotes_none", message))
            return
        self._db.get("friendly-telegram.modules.notes", "notes", {}).clear()
        await utils.answer(message, self.strings("delnotes_done", message))

    async def savecmd(self, message):
        """Save a new note. Must be used in reply with one parameter (note name)"""
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, self.strings("what_name", message))
            return
        if message.is_reply:
            target = await message.get_reply_message()
        elif len(args) < 2:
            await utils.answer(message, self.strings("save_what", message))
            return
        else:
            message.entities = None
            message.message = args[1]
            target = message
            logger.debug(target.message)
        asset_id = await self._db.store_asset(target)
        self._db.set(
            "friendly-telegram.modules.notes",
            "notes",
            {
                **self._db.get("friendly-telegram.modules.notes", "notes", {}),
                args[0]: asset_id,
            },
        )
        await utils.answer(message, str(self.strings("saved", message)).format(args[0]))

    async def delnotecmd(self, message):
        """Deletes a note, specified by note name"""
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, self.strings("delnote_args", message))
        self.del_note(args[0])
        await utils.answer(message, self.strings("delnote_done", message))

    def del_note(self, note):
        old = self._db.get("friendly-telegram.modules.notes", "notes", {})
        try:
            del old[note]
        except KeyError:
            pass
        else:
            self._db.set("friendly-telegram.modules.notes", "notes", old)

    async def notescmd(self, message):
        """List the saved notes"""
        if not self._db.get("friendly-telegram.modules.notes", "notes", {}):
            await utils.answer(message, self.strings("notes_none", message))
            return
        await utils.answer(
            message,
            self.strings("notes_header", message)
            + "\n".join(
                self.strings("notes_item", message).format(key)
                for key in self._db.get("friendly-telegram.modules.notes", "notes", {})
            ),
        )

    async def client_ready(self, client, db):
        self._db = db
