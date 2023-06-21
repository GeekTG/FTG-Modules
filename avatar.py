# -*- coding: utf-8 -*-

# Module author: @ftgmodulesbyfl1yd, @dekftgmodules

import os

from telethon import functions
from telethon.errors.rpcerrorlist import UsernameOccupiedError
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest

from .. import loader, utils


class GetPPMod(loader.Module):
    strings = {"name": "Profile"}

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

    async def avacmd(self, message):
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
                for i in photos:
                    os.remove(i)
            else:
                try:
                    if u:
                        photo = await self.client.download_profile_photo(user.sender)
                    else:
                        photo = await self.client.download_profile_photo(
                            message.input_chat
                        )
                    await self.client.send_file(message.chat_id, photo)
                    os.remove(photo)
                except Exception:
                    await message.edit("<code>This user has no photos</code>")
                    return
        else:
            try:
                id = int(id)
                if id <= 0:
                    await message.edit("<code>ID number you entered is invalid</code>")
                    return
            except Exception:
                await message.edit("<code>ID number you entered is invalid</code>")
                return
            if int(id) <= (len(photos)):
                send_photos = await self.client.download_media(photos[id - 1])
                await self.client.send_file(message.chat_id, send_photos)
                os.remove(send_photos)
            else:
                await message.edit("<code>No photo found with that id</code>")
                return
        await message.delete()

    async def setavacmd(self, message):
        reply = await check_mediaa(message)
        if not reply:
            try:
                reply = await message.get_reply_message()
                if not reply:
                    return await message.edit("No reply to a media.")
                await message.edit("Downloading...")
                if reply.video:
                    await message.client.download_media(reply.media, "ava.mp4")
                    await message.edit("Converting...")
                    os.system("ffmpeg -i ava.mp4 -c copy -an gifavaa.mp4 -y")
                    os.system("ffmpeg -i gifavaa.mp4 -vf scale=360:360 gifava.mp4 -y")
                else:
                    await message.client.download_media(reply.media, "tgs.tgs")
                    await message.edit("Converting...")
                    os.system(
                        "lottie_convert.py tgs.tgs tgs.gif; mv tgs.gif gifava.mp4"
                    )
                await message.edit("Uploading avatar...")
                await message.client(
                    functions.photos.UploadProfilePhotoRequest(
                        video=await message.client.upload_file("gifava.mp4"),
                        video_start_ts=0.0,
                    )
                )
                await message.edit("Uploaded.")
                os.system("rm -rf ava.mp4 gifava.mp4 gifavaa.mp4 tgs*")
            except Exception:
                await message.edit("An unexpected error occurred")
                return os.system("rm -rf ava.mp4 gifava.mp4 gifavaa.mp4 tgs*")
        else:
            reply = await message.get_reply_message()
            media = reply.photo or reply.sticker if reply else None
            if not media:
                return await message.edit("No reply on photo/sticker")

            await message.edit("Downloading...")
            photo = await message.client.download_media(message=reply.photo)
            up = await message.client.upload_file(photo)
            await message.edit("Uploading avatar...")
            await message.client(functions.photos.UploadProfilePhotoRequest(up))
            await message.delete()
            os.remove(photo)

    async def delavacmd(self, message):
        ava = await message.client.get_profile_photos("me", limit=1)
        if len(ava) > 0:
            await message.edit("Deleting avatar...")
            await message.client(functions.photos.DeletePhotosRequest(ava))
            await message.edit("Current avatar was deleted.")
        else:
            await message.edit("No avatar found")

    async def delavascmd(self, message):
        ava = await message.client.get_profile_photos("me")
        if len(ava) > 0:
            await message.edit("Deleting avatars...")
            await message.client(
                functions.photos.DeletePhotosRequest(
                    await message.client.get_profile_photos("me")
                )
            )
            await message.edit("All avatars was deleted")
        else:
            await message.edit("No avatar found")

    async def setnamecmd(self, message):
        args = utils.get_args_raw(message).split("/")
        if len(args) == 1:
            firstname = args[0]
            lastname = " "
        elif len(args) == 2:
            firstname = args[0]
            lastname = args[1]
        await message.client(
            UpdateProfileRequest(first_name=firstname, last_name=lastname)
        )
        await message.edit("Name changed successfully!")

    async def setbiocmd(self, message):
        args = utils.get_args_raw(message)
        if not args:
            return await message.edit("No arguments.")
        await message.client(UpdateProfileRequest(about=args))
        await message.edit("Bio changed successfully!")

    async def setusercmd(self, message):
        args = utils.get_args_raw(message)
        if not args:
            return await message.edit("No args.")
        try:
            await message.client(UpdateUsernameRequest(args))
            await message.edit("Username changed successfully!")
        except UsernameOccupiedError:
            await message.edit("This username is already occupied!")


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
