"""
.------.------.------.------.------.------.------.------.------.------.
|D.--. |4.--. |N.--. |1.--. |3.--. |L.--. |3.--. |K.--. |0.--. |0.--. |
| :/\: | :/\: | :(): | :/\: | :(): | :/\: | :(): | :/\: | :/\: | :/\: |
| (__) | :\/: | ()() | (__) | ()() | (__) | ()() | :\/: | :\/: | :\/: |
| '--'D| '--'4| '--'N| '--'1| '--'3| '--'L| '--'3| '--'K| '--'0| '--'0|
`------`------`------`------`------`------`------`------`------`------'

                    Copyright 2022 t.me/D4n13l3k00                     
          Licensed under the Creative Commons CC BY-NC-ND 4.0          
  
                   Full license text can be found at:                  
      https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode      
    
                          Human-friendly one:                          
           https://creativecommons.org/licenses/by-nc-nd/4.0           
"""
# meta developer: @D4n13l3k00


# requires: moviepy requests

import os
import random as rnd
import re
import string

import requests
from moviepy.editor import *
from telethon import types

from .. import loader, utils


@loader.tds
class VideoEditorMod(loader.Module):
    "Module for working with video"

    strings = {
        "name": "VideoEditor",
        "downloading": "<b>[{}]</b> Downloading...",
        "working": "<b>[{}]</b> Working...",
        "exporting": "<b>[{}]</b> Exporting...",
        "set_value": "<b>[{}]</b> Specify the level from {} to {}...",
        "reply": "<b>[{}]</b> reply to video/gif...",
        "set_time": "<b>[{}]</b> Specify the time in the format start(ms):end(ms)",
        "set_link": "<b>[{}]</b> Enter link...",
    }

    @loader.owner
    async def xflipvcmd(self, m: types.Message):
        """.xflipv <reply_to_video> - Flip video by X"""
        vid = await get_video(self, m, "XFlip")
        if not vid:
            return
        out = vid.video.fx(vfx.mirror_x)
        await go_out(self, vid.message, vid, out, vid.pref)

    @loader.owner
    async def yflipvcmd(self, m: types.Message):
        """.yflipv <reply_to_video> - Flip video by Y"""
        vid = await get_video(self, m, "YFlip")
        if not vid:
            return
        out = vid.video.fx(vfx.mirror_y)
        await go_out(self, vid.message, vid, out, vid.pref)

    @loader.owner
    async def bwvcmd(self, m: types.Message):
        """.bwv <reply_to_video> - BlackWhite"""
        vid = await get_video(self, m, "BlackWhite")
        if not vid:
            return
        out = vid.video.fx(vfx.blackwhite)
        await go_out(self, vid.message, vid, out, vid.pref)

    @loader.owner
    async def revvcmd(self, m: types.Message):
        """.revv <reply_to_video> - Reverse video"""
        vid = await get_video(self, m, "Reverse")
        if not vid:
            return
        out = vid.video.fx(vfx.time_mirror)
        await go_out(self, vid.message, vid, out, vid.pref)

    @loader.owner
    async def paintvcmd(self, m: types.Message):
        """.paintv <reply_to_video> - Paint effect"""
        vid = await get_video(self, m, "Paint")
        if not vid:
            return
        out = vid.video.fx(vfx.painting)
        await go_out(self, vid.message, vid, out, vid.pref)

    @loader.owner
    async def invertvcmd(self, m: types.Message):
        """.invertv <reply_to_video> - Invert colors"""
        vid = await get_video(self, m, "Invert")
        if not vid:
            return
        out = vid.video.fx(vfx.invert_colors)
        await go_out(self, vid.message, vid, out, vid.pref)

    @loader.owner
    async def rmsvcmd(self, m: types.Message):
        """.rmsv <reply_to_video> - Remove sound (to gif without compression)"""
        vid = await get_video(self, m, "NoAudio")
        if not vid:
            return
        out = vid.video.without_audio()
        await go_out(self, vid.message, vid, out, vid.pref)

    @loader.owner
    async def cutvcmd(self, m: types.Message):
        """.cutv <int [Default 30]> <reply_to_video> - Cut video"""
        args = utils.get_args_raw(m)
        if not args:
            return await utils.answer(m, self.strings("set_time", m).format("Cut"))
        r = re.compile(r"^(?P<start>\d+){0,1}:(?P<end>-?\d+){0,1}$")
        ee = r.match(args)
        if not ee:
            return await utils.answer(m, self.strings("set_time", m).format("Cut"))
        start = int(ee.group("start")) if ee.group("start") else 0
        end = int(ee.group("end")) if ee.group("end") else None
        vid = await get_video(self, m, "Cut")
        if not vid:
            return
        out = vid.video.subclip(start, end)
        await go_out(self, vid.message, vid, out, vid.pref)

    @loader.owner
    async def audvcmd(self, m: types.Message):
        """.audv <link> <reply_to_video> - Add audio to video"""
        args = utils.get_args_raw(m)
        if not args:
            return await utils.answer(m, self.strings("set_link", m).format("Audio"))
        r = re.compile(
            r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"
        )
        ee = r.match(args)
        if not ee:
            return await utils.answer(m, self.strings("set_link", m).format("Audio"))
        vid = await get_video(self, m, "Audio")
        if not vid:
            return
        a = requests.get(args)
        nm = "".join(rnd.sample(string.ascii_letters, 24)) + ".mp3"
        if a.status_code == 200:
            open(nm, "wb").write(a.content)
        else:
            return
        out = vid.video
        out.audio = CompositeAudioClip([AudioFileClip(nm)])
        await go_out(self, vid.message, vid, out, vid.pref)
        try:
            os.remove(nm)
        except:
            pass

    @loader.owner
    async def fpsvcmd(self, m: types.Message):
        """.fpsv <int [Default 30]> <reply_to_video> - Change fps"""
        args = utils.get_args_raw(m)
        if not args:
            fps = 30
        elif re.match(r"^\d+$", args) and (0 < int(args) < 241):
            fps = int(args)
        else:
            return await utils.answer(
                m, self.strings("set_value", m).format("FPS", 1, 240)
            )
        vid = await get_video(self, m, "FPS")
        if not vid:
            return
        out = vid.video.set_fps(fps)
        await go_out(self, vid.message, vid, out, vid.pref)

    @loader.owner
    async def marginvcmd(self, m: types.Message):
        """.marginv <int [Default 5]> <reply_to_video> - Add marging"""
        args = utils.get_args_raw(m)
        if not args:
            margin = 5
        elif re.match(r"^\d+$", args) and (0 < int(args) < 101):
            margin = int(args)
        else:
            return await utils.answer(
                m, self.strings("set_value", m).format("Scale", 1, 100)
            )
        vid = await get_video(self, m, "Margin")
        if not vid:
            return
        out = vid.video.fx(vfx.margin, margin)
        await go_out(self, vid.message, vid, out, vid.pref)

    @loader.owner
    async def speedvcmd(self, m: types.Message):
        """.speedv <float [Default 1.5]> <reply_to_video> - Speed"""
        args = utils.get_args_raw(m)
        if not args:
            speed = 1.5
        elif re.match(r"^\d+(\.\d+)?$", args) and (0.009 < float(args) < 10.1):
            speed = float(args)
        else:
            return await utils.answer(
                m, self.strings("set_value", m).format("Speed", 0.01, 10.0)
            )
        vid = await get_video(self, m, "Speed")
        if not vid:
            return
        out = vid.video.fx(vfx.speedx, speed)
        await go_out(self, vid.message, vid, out, vid.pref)

    @loader.owner
    async def contrastvcmd(self, m: types.Message):
        """.contrastv <float [Default 1.5]> <reply_to_video> - Contrast"""
        args = utils.get_args_raw(m)
        if not args:
            contrast = 1.5
        elif re.match(r"^\d+(\.\d+)?$", args) and (0.009 < float(args) < 100.1):
            contrast = float(args)
        else:
            return await utils.answer(
                m, self.strings("set_value", m).format("Contrast", 0.01, 100.0)
            )
        vid = await get_video(self, m, "Contrast")
        if not vid:
            return
        out = vid.video.fx(vfx.lum_contrast, contrast=contrast)
        await go_out(self, vid.message, vid, out, vid.pref)

    @loader.owner
    async def lumvcmd(self, m: types.Message):
        """.lumv <float [Default 25]> <reply_to_video> - Lum"""
        args = utils.get_args_raw(m)
        if not args:
            lum = 25
        elif re.match(r"^\d+(\.\d+)?$", args) and (0.009 < float(args) < 100.1):
            lum = float(args)
        else:
            return await utils.answer(
                m, self.strings("set_value", m).format("Lum", 0.01, 100.0)
            )
        vid = await get_video(self, m, "Lum")
        if not vid:
            return
        out = vid.video.fx(vfx.lum_contrast, lum=lum)
        await go_out(self, vid.message, vid, out, vid.pref)

    @loader.owner
    async def scalevcmd(self, m: types.Message):
        """.scalev <float [Default 0.75]> <reply_to_video> - Scale("Resize") video"""
        args = utils.get_args_raw(m)
        if not args:
            scale = 0.75
        elif re.match(r"^\d+(\.\d+)?$", args) and (0.009 < float(args) < 100.1):
            scale = float(args)
        else:
            return await utils.answer(
                m, self.strings("set_value", m).format("Scale", 0.01, 100.0)
            )
        vid = await get_video(self, m, "Scale")
        if not vid:
            return
        out = vid.video.resize(scale)
        await go_out(self, vid.message, vid, out, vid.pref)


class VideoEditorClass:
    video: VideoFileClip = None
    message = None
    pref: str = None
    reply = None


async def get_video(self, m, pref: str):
    r = await m.get_reply_message()
    if r and r.file and r.file.mime_type.split("/")[0] in ["video"]:
        vid = VideoEditorClass()
        vid.pref = pref
        vid.reply = r
        vid.message = await utils.answer(m, self.strings("downloading", m).format(pref))
        vid.video = VideoFileClip(await r.download_media())
        return vid
    await utils.answer(m, self.strings("reply", m).format(pref))


async def go_out(self, m, vid: VideoEditorClass, out: VideoFileClip, pref):
    m = await utils.answer(m, self.strings("exporting", m).format(pref))
    filename = "".join(rnd.sample(string.ascii_letters, 24)) + ".mp4"
    out.write_videofile(filename)
    await utils.answer(
        m, open(filename, "rb"), reply_to=vid.reply.id, supports_streaming=True
    )
    try:
        os.remove(filename)
    except:
        pass
    try:
        os.remove(vid.video.filename)
    except:
        pass
