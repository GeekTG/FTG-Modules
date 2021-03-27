# -*- coding: utf-8 -*-

# Module author: @dekftgmodules

# requires: pydub numpy requests

import io, math, os, requests, numpy as np, re
from pydub import AudioSegment, effects
from telethon import types
from .. import loader, utils


@loader.tds
class AudioEditorMod(loader.Module):
    """Модуль для работы со звуком"""
    strings = {"name": "Audio Editor"}

    async def basscmd(self, message):
        """.bass [level bass'а 2-100 (Default 2)] <reply to audio>
        BassBoost"""
        args = utils.get_args_raw(message)
        if not args:
            lvl = 2
        else:
            if args.isdigit() and (1 < int(args) < 101):
                lvl = int(args)
            else:
                return await message.edit(f"[BassBoost] Specify the level from 2 to 100...")
        audio = await get_audio(message, "BassBoost")
        if not audio: return
        sample_track = list(audio.audio.get_array_of_samples())
        est_mean = np.mean(sample_track)
        est_std = 3 * np.std(sample_track) / (math.sqrt(2))
        bass_factor = int(round((est_std - est_mean) * 0.005))
        attenuate_db = 0
        filtered = audio.audio.low_pass_filter(bass_factor)
        out = (audio.audio - attenuate_db).overlay(filtered + lvl)
        await go_out(message, audio, out, audio.pref, f"{audio.pref} {lvl}lvl")

    async def fvcmd(self, message):
        """.fv [level 2-100 (Default 25)] <reply to audio>
        Distort"""
        args = utils.get_args_raw(message)
        if not args:
            lvl = 25
        else:
            if args.isdigit() and (1 < int(args) < 101):
                lvl = int(args)
            else:
                return await message.edit(f"[Distort] Specify the level from 2 to 100...")
        audio = await get_audio(message, "Distort")
        if not audio:
            return
        out = audio.audio + lvl
        await go_out(message, audio, out, audio.pref, f"{audio.pref} {lvl}lvl")

    async def echoscmd(self, message):
        """.echos <reply to audio>
            Echo effect"""
        audio = await get_audio(message, "Echo")
        if not audio: return
        out = AudioSegment.empty()
        n = 200
        none = io.BytesIO()
        out += audio.audio + AudioSegment.from_file(none)
        for i in range(5):
            echo = audio.audio - 10
            out = out.overlay(audio.audio, n)
            n += 200
        await go_out(message, audio, out, audio.pref, audio.pref)

    async def volupcmd(self, message):
        """.volup <reply to audio>
            VolUp 10dB"""
        audio = await get_audio(message, "+10dB")
        if not audio: return
        out = audio.audio + 10
        await go_out(message, audio, out, audio.pref, audio.pref)

    async def voldwcmd(self, message):
        """.voldw <reply to audio>
            VolDw 10dB"""
        audio = await get_audio(message, "-10dB")
        if not audio: return
        out = audio.audio - 10
        await go_out(message, audio, out, audio.pref, audio.pref)

    async def revscmd(self, message):
        """.revs <reply to audio>
            Reverse audio"""
        audio = await get_audio(message, "Reverse")
        if not audio: return
        out = audio.audio.reverse()
        await go_out(message, audio, out, audio.pref, audio.pref)

    async def repscmd(self, message):
        """.reps <reply to audio>
            Repeat audio 2 times"""
        audio = await get_audio(message, "Repeat")
        if not audio: return
        out = audio.audio * 2
        await go_out(message, audio, out, audio.pref, audio.pref)

    async def slowscmd(self, message):
        """.slows <reply to audio>
            SlowDown 0.5x"""
        audio = await get_audio(message, "SlowDown")
        if not audio: return
        s2 = audio.audio._spawn(audio.audio.raw_data, overrides={
            "frame_rate": int(audio.audio.frame_rate * 0.5)})
        out = s2.set_frame_rate(audio.audio.frame_rate)
        await go_out(message, audio, out, audio.pref, audio.pref, audio.duration * 2)

    async def fastscmd(self, message):
        """.fasts <reply to audio>
        SpeedUp 1.5x"""
        audio = await get_audio(message, "SpeedUp")
        if not audio: return
        s2 = audio.audio._spawn(audio.audio.raw_data, overrides={
            "frame_rate": int(audio.audio.frame_rate * 1.5)})
        out = s2.set_frame_rate(audio.audio.frame_rate)
        await go_out(message, audio, out, audio.pref, audio.pref,
                     round(audio.duration / 2))

    async def rightscmd(self, message):
        """.rights <reply to audio>
            Push sound to right channel"""
        audio = await get_audio(message, "Right channel")
        if not audio: return
        out = effects.pan(audio.audio, +1.0)
        await go_out(message, audio, out, audio.pref, audio.pref)

    async def leftscmd(self, message):
        """.lefts <reply to audio>
            Push sound to left channel"""
        audio = await get_audio(message, "Left channel")
        if not audio: return
        out = effects.pan(audio.audio, -1.0)
        await go_out(message, audio, out, audio.pref, audio.pref)

    async def normscmd(self, message):
        """.norms <reply to audio>
            Normalize sound (from quiet to normal)"""
        audio = await get_audio(message, "Normalization")
        if not audio: return
        out = effects.normalize(audio.audio)
        await go_out(message, audio, out, audio.pref, audio.pref)

    async def byrobertscmd(self, message):
        '''.byroberts <reply to audio>
            Add at the end "Directed by Robert B Weide"'''
        audio = await get_audio(message, "Directed by...")
        if not audio: return
        out = audio.audio + AudioSegment.from_file(io.BytesIO(requests.get(
            "https://raw.githubusercontent.com/D4n13l3k00/files-for-modules/master/directed.mp3").content)).apply_gain(
            +8)
        await go_out(message, audio, out, audio.pref, audio.pref)

    async def cutscmd(self, message):
        """.cuts <start(ms):end(ms)> <reply to audio>
        Cut audio"""
        args = utils.get_args_raw(message)
        if not args: await message.edit("[Cut] Specify the time in the format start(ms):end(ms)")
        else:
            r = re.compile(r'^(\d+):(\d+)$')
            ee = r.match(args)
            if ee:
                start = int(ee.group(0))
                end   = int(ee.group(1))
            else: return await message.edit(f"[Cut] Specify the time in the format start(ms):end(ms)")
        audio = await get_audio(message, "Cut")
        if not audio: return
        out = audio.audio[start:end]
        await go_out(message, audio, out, audio.pref, audio.pref)
        


async def get_audio(message, pref):
    class audio_ae_class():
        audio = None
        duration = None
        voice = None
        pref = None
        reply = None

    reply = await message.get_reply_message()
    if reply and reply.file and reply.file.mime_type.split("/")[0] == "audio":
        ae = audio_ae_class()
        ae.pref = pref
        ae.reply = reply
        ae.voice = reply.document.attributes[0].voice
        ae.duration = reply.document.attributes[0].duration
        await message.edit(f"[{pref}] Downloading...")
        ae.audio = AudioSegment.from_file(
            io.BytesIO(await reply.download_media(bytes)))
        await message.edit(f"[{pref}] Working...")
        return ae
    else:
        await message.edit(f"[{pref}] reply to audio...")
        return None


async def go_out(message, audio, out, pref, title, fs=None):
    o = io.BytesIO()
    o.name = "audio." + ("ogg" if audio.voice else "mp3")
    if audio.voice: out.split_to_mono()
    await message.edit(f"[{pref}] Exporting...")
    out.export(o, format="ogg" if audio.voice else "mp3",
               bitrate="64k" if audio.voice else None,
               codec="libopus" if audio.voice else None)
    o.seek(0)
    await message.edit(f"[{pref}] Sending...")
    await message.client.send_file(message.to_id, o, reply_to=audio.reply.id,
                                   voice_note=audio.voice, attributes=[
            types.DocumentAttributeAudio(duration=fs if fs else audio.duration,
                                         title=title,
                                         performer="AudioEditor")] if not audio.voice else None)
    await message.delete()
