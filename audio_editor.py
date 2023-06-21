# .------.------.------.------.------.------.------.------.------.------.
# |D.--. |4.--. |N.--. |1.--. |3.--. |L.--. |3.--. |K.--. |0.--. |0.--. |
# | :/\: | :/\: | :(): | :/\: | :(): | :/\: | :(): | :/\: | :/\: | :/\: |
# | (__) | :\/: | ()() | (__) | ()() | (__) | ()() | :\/: | :\/: | :\/: |
# | '--'D| '--'4| '--'N| '--'1| '--'3| '--'L| '--'3| '--'K| '--'0| '--'0|
# `------`------`------`------`------`------`------`------`------`------'
#
#                     Copyright 2022 t.me/D4n13l3k00
#           Licensed under the Creative Commons CC BY-NC-ND 4.0
#
#                    Full license text can be found at:
#       https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode
#
#                           Human-friendly one:
#            https://creativecommons.org/licenses/by-nc-nd/4.0

# meta developer: @D4n13l3k00


# requires: pydub numpy requests

import io
import math
import re

import aiohttp
import numpy as np
from pydub import AudioSegment, effects
from telethon import types

from .. import loader, utils


@loader.tds
class AudioEditorMod(loader.Module):
    """Module for working with sound"""

    strings = {
        "name": "AudioEditor",
        "downloading": "<b>[{}]</b> Downloading...",
        "working": "<b>[{}]</b> Working...",
        "exporting": "<b>[{}]</b> Exporting...",
        "set_value": "<b>[{}]</b> Specify the level from {} to {}...",
        "reply": "<b>[{}]</b> reply to audio...",
        "set_fmt": "<b>[{}]</b> Specify the format of output audio...",
        "set_time": "<b>[{}]</b> Specify the time in the format start(ms):end(ms)",
    }

    @loader.owner
    async def basscmd(self, m):
        """.bass [level bass'а 2-100 (Default 2)] <reply to audio>
        BassBoost"""
        args = utils.get_args_raw(m)
        if not args:
            lvl = 2.0
        elif re.match(r"^\d+(\.\d+)?$", args) and (1.0 < float(args) < 100.1):
            lvl = float(args)
        else:
            return await utils.answer(
                m, self.strings("set_value", m).format("BassBoost", 2.0, 100.0)
            )
        audio = await self.get_audio(m, "BassBoost")
        if not audio:
            return
        sample_track = list(audio.audio.get_array_of_samples())
        out = (audio.audio - 0).overlay(
            audio.audio.low_pass_filter(
                int(
                    round(
                        (
                            3 * np.std(sample_track) / (math.sqrt(2))
                            - np.mean(sample_track)
                        )
                        * 0.005
                    )
                )
            )
            + lvl
        )
        await self.send_audio(m, audio, out, audio.pref, f"{audio.pref} {lvl}lvl")

    @loader.owner
    async def fvcmd(self, m):
        """.fv [level 2-100 (Default 25)] <reply to audio>
        Distort"""
        args = utils.get_args_raw(m)
        if not args:
            lvl = 25.0
        elif re.match(r"^\d+(\.\d+)?$", args) and (1.0 < float(args) < 100.1):
            lvl = float(args)
        else:
            return await utils.answer(
                m, self.strings("set_value", m).format("Distort", 2.0, 100.0)
            )
        audio = await self.get_audio(m, "Distort")
        if not audio:
            return
        out = audio.audio + lvl
        await self.send_audio(m, audio, out, audio.pref, f"{audio.pref} {lvl}lvl")

    @loader.owner
    async def echoscmd(self, m):
        """.echos <reply to audio>
        Echo effect"""
        audio = await self.get_audio(m, "Echo")
        if not audio:
            return
        out = AudioSegment.empty()
        n = 200
        none = io.BytesIO()
        out += audio.audio + AudioSegment.from_file(none)
        for _ in range(5):
            audio.audio - 10
            out = out.overlay(audio.audio, n)
            n += 200
        await self.send_audio(audio.message, audio, out, audio.pref, audio.pref)

    @loader.owner
    async def volupcmd(self, m):
        """.volup <reply to audio>
        VolUp 10dB"""
        audio = await self.get_audio(m, "+10dB")
        if not audio:
            return
        out = audio.audio + 10
        await self.send_audio(audio.message, audio, out, audio.pref, audio.pref)

    @loader.owner
    async def voldwcmd(self, m):
        """.voldw <reply to audio>
        VolDw 10dB"""
        audio = await self.get_audio(m, "-10dB")
        if not audio:
            return
        out = audio.audio - 10
        await self.send_audio(audio.message, audio, out, audio.pref, audio.pref)

    @loader.owner
    async def revscmd(self, m):
        """.revs <reply to audio>
        Reverse audio"""
        audio = await self.get_audio(m, "Reverse")
        if not audio:
            return
        out = audio.audio.reverse()
        await self.send_audio(audio.message, audio, out, audio.pref, audio.pref)

    @loader.owner
    async def repscmd(self, m):
        """.reps <reply to audio>
        Repeat audio 2 times"""
        audio = await self.get_audio(m, "Repeat")
        if not audio:
            return
        out = audio.audio * 2
        await self.send_audio(audio.message, audio, out, audio.pref, audio.pref)

    @loader.owner
    async def slowscmd(self, m):
        """.slows <reply to audio>
        SlowDown 0.5x"""
        audio = await self.get_audio(m, "SlowDown")
        if not audio:
            return
        s2 = audio.audio._spawn(
            audio.audio.raw_data,
            overrides={"frame_rate": int(audio.audio.frame_rate * 0.5)},
        )
        out = s2.set_frame_rate(audio.audio.frame_rate)
        await self.send_audio(
            audio.message, audio, out, audio.pref, audio.pref, audio.duration * 2
        )

    @loader.owner
    async def fastscmd(self, m):
        """.fasts <reply to audio>
        SpeedUp 1.5x"""
        audio = await self.get_audio(m, "SpeedUp")
        if not audio:
            return
        s2 = audio.audio._spawn(
            audio.audio.raw_data,
            overrides={"frame_rate": int(audio.audio.frame_rate * 1.5)},
        )
        out = s2.set_frame_rate(audio.audio.frame_rate)
        await self.send_audio(
            audio.message,
            audio,
            out,
            audio.pref,
            audio.pref,
            round(audio.duration / 2),
        )

    @loader.owner
    async def rightscmd(self, m):
        """.rights <reply to audio>
        Push sound to right channel"""
        audio = await self.get_audio(m, "Right channel")
        if not audio:
            return
        out = effects.pan(audio.audio, +1.0)
        await self.send_audio(audio.message, audio, out, audio.pref, audio.pref)

    @loader.owner
    async def leftscmd(self, m):
        """.lefts <reply to audio>
        Push sound to left channel"""
        audio = await self.get_audio(m, "Left channel")
        if not audio:
            return
        out = effects.pan(audio.audio, -1.0)
        await self.send_audio(audio.message, audio, out, audio.pref, audio.pref)

    @loader.owner
    async def normscmd(self, m):
        """.norms <reply to audio>
        Normalize sound (from quiet to normal)"""
        audio = await self.get_audio(m, "Normalization")
        if not audio:
            return
        out = effects.normalize(audio.audio)
        await self.send_audio(audio.message, audio, out, audio.pref, audio.pref)

    @loader.owner
    async def tovscmd(self, m):
        """.tovs <reply to audio>
        Convert to voice message"""
        utils.get_args_raw(m)
        audio = await self.get_audio(m, "Voice")
        if not audio:
            return
        audio.voice = True
        await self.send_audio(audio.message, audio, audio.audio, audio.pref, audio.pref)

    @loader.owner
    async def convscmd(self, m):
        """.convs <reply to audio> [audio_format (ex. `mp3`)]
        Convert audio to some format"""
        f = utils.get_args(m)
        if not f:
            return await utils.answer(m, self.strings("set_fmt", m).format("Converter"))
        audio = await self.get_audio(m, "Converter")
        if not audio:
            return
        await self.send_audio(
            audio.message,
            audio,
            audio.audio,
            audio.pref,
            f"Converted to {f[0].lower()}",
            fmt=f[0].lower(),
        )

    @loader.owner
    async def byrobertscmd(self, m):
        '''.byroberts <reply to audio>
        Add at the end "Directed by Robert B Weide"'''
        audio = await self.get_audio(m, "Directed by...")
        if not audio:
            return
        async with aiohttp.ClientSession() as s, s.get(
            "https://raw.githubusercontent.com/D4n13l3k00/files-for-modules/master/directed.mp3"
        ) as r:
            out = audio.audio + AudioSegment.from_file(
                io.BytesIO(await r.read())
            ).apply_gain(+8)
        await self.send_audio(audio.message, audio, out, audio.pref, audio.pref)

    @loader.owner
    async def cutscmd(self, m):
        """.cuts <start(ms):end(ms)> <reply to audio>
        Cut audio"""
        args = utils.get_args_raw(m)
        if not args:
            return await utils.answer(m, self.strings("set_time", m).format("Cut"))
        r = re.compile(r"^(?P<start>\d+){0,1}:(?P<end>\d+){0,1}$")
        ee = r.match(args)
        if not ee:
            return await utils.answer(m, self.strings("set_time", m).format("Cut"))
        start = int(ee["start"]) if ee["start"] else 0
        end = int(ee["end"]) if ee["end"] else 0
        audio = await self.get_audio(m, "Cut")
        if not audio:
            return
        out = audio.audio[start : end or len(audio.audio) - 1]
        await self.send_audio(audio.message, audio, out, audio.pref, audio.pref)

    class AudioEditorClass:
        audio = None
        message = None
        duration = None
        voice = None
        pref = None
        reply = None

    async def get_audio(self, m, pref):
        r = await m.get_reply_message()
        if r and r.file and r.file.mime_type.split("/")[0] in ["audio", "video"]:
            ae = self.AudioEditorClass()
            ae.pref = pref
            ae.reply = r
            ae.voice = (
                r.document.attributes[0].voice
                if r.file.mime_type.split("/")[0] == "audio"
                else False
            )
            ae.duration = r.document.attributes[0].duration
            ae.message = await utils.answer(
                m, self.strings("downloading", m).format(pref)
            )
            ae.audio = AudioSegment.from_file(io.BytesIO(await r.download_media(bytes)))
            ae.message = await utils.answer(
                ae.message, self.strings("working", m).format(pref)
            )
            return ae
        await utils.answer(m, self.strings("reply", m).format(pref))
        return None

    async def send_audio(self, message, audio, out, pref, title, fs=None, fmt="mp3"):
        out_file = io.BytesIO()
        out_file.name = "audio." + ("ogg" if audio.voice else "mp3")
        if audio.voice:
            out.split_to_mono()
        message = await utils.answer(message, self.strings("exporting").format(pref))
        out.export(
            out_file,
            format="ogg" if audio.voice else fmt,
            bitrate="64k" if audio.voice else None,
            codec="libopus" if audio.voice else None,
        )
        out_file.seek(0)
        await utils.answer(
            message,
            out_file,
            reply_to=audio.reply.id,
            voice_note=audio.voice,
            attributes=None
            if audio.voice
            else [
                types.DocumentAttributeAudio(
                    duration=fs or audio.duration,
                    title=title,
                    performer="AudioEditor",
                )
            ],
        )
