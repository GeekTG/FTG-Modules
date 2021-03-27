# -*- coding: utf-8 -*-

# Module author: @dekftgmodules, @ftgmodulesbyfl1yd

# requires: pydub numpy requests

import io
import math
import os
import requests

import numpy as np
from pydub import AudioSegment, effects
from telethon import types

from .. import loader, utils


@loader.tds
class AudioEditorMod(loader.Module):
    """Модуль для работы со звуком"""
    strings = {"name": "Audio Editor"}

    async def basscmd(self, message):
        """.bass [уровень bass'а 2-100 (Default 2)] <reply to audio>
        BassBoost"""
        args = utils.get_args_raw(message)
        if not args:
            lvl = 2
        else:
            if args.isdigit() and (1 < int(args) < 101):
                lvl = int(args)
            else:
                return await message.edit(f"[BassBoost] Укажи уровень от 2 до 100...")
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
        """.fv [уровень шакала 2-100 (Default 25)] <reply to audio>
        Шакалинг"""
        args = utils.get_args_raw(message)
        if not args:
            lvl = 25
        else:
            if args.isdigit() and (1 < int(args) < 101):
                lvl = int(args)
            else:
                return await message.edit(f"[Шакал] Укажи уровень от 2 до 100...")
        audio = await get_audio(message, "Шакал")
        if not audio:
            return
        out = audio.audio + lvl
        await go_out(message, audio, out, audio.pref, f"{audio.pref} {lvl}lvl")

    async def echoscmd(self, message):
        """.echos <reply to audio>
            Эхо эффект"""
        audio = await get_audio(message, "Эхо эффект")
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
            Увеличить громкость на 10dB"""
        audio = await get_audio(message, "+10dB")
        if not audio: return
        out = audio.audio + 10
        await go_out(message, audio, out, audio.pref, audio.pref)

    async def voldwcmd(self, message):
        """.voldw <reply to audio>
            Уменьшить громкость на 10dB"""
        audio = await get_audio(message, "-10dB")
        if not audio: return
        out = audio.audio - 10
        await go_out(message, audio, out, audio.pref, audio.pref)

    async def revscmd(self, message):
        """.revs <reply to audio>
            Развернуть аудио"""
        audio = await get_audio(message, "Reverse")
        if not audio: return
        out = audio.audio.reverse()
        await go_out(message, audio, out, audio.pref, audio.pref)

    async def repscmd(self, message):
        """.reps <reply to audio>
            Повторить аудио 2 раза подряд"""
        audio = await get_audio(message, "Повтор")
        if not audio: return
        out = audio.audio * 2
        await go_out(message, audio, out, audio.pref, audio.pref)

    async def slowscmd(self, message):
        """.slows <reply to audio>
            Замедлить аудио 0.5x"""
        audio = await get_audio(message, "Замедление")
        if not audio: return
        s2 = audio.audio._spawn(audio.audio.raw_data, overrides={
            "frame_rate": int(audio.audio.frame_rate * 0.5)})
        out = s2.set_frame_rate(audio.audio.frame_rate)
        await go_out(message, audio, out, audio.pref, audio.pref, audio.duration * 2)

    async def fastscmd(self, message):
        """.fasts <reply to audio>
        Ускорить аудио 1.5x"""
        audio = await get_audio(message, "Ускорение")
        if not audio: return
        s2 = audio.audio._spawn(audio.audio.raw_data, overrides={
            "frame_rate": int(audio.audio.frame_rate * 1.5)})
        out = s2.set_frame_rate(audio.audio.frame_rate)
        await go_out(message, audio, out, audio.pref, audio.pref,
                     round(audio.duration / 2))

    async def rightscmd(self, message):
        """.rights <reply to audio>
            Весь звук в правый канал"""
        audio = await get_audio(message, "Правый канал")
        if not audio: return
        out = effects.pan(audio.audio, +1.0)
        await go_out(message, audio, out, audio.pref, audio.pref)

    async def leftscmd(self, message):
        """.lefts <reply to audio>
            Весь звук в левый канал"""
        audio = await get_audio(message, "Левый канал")
        if not audio: return
        out = effects.pan(audio.audio, -1.0)
        await go_out(message, audio, out, audio.pref, audio.pref)

    async def normscmd(self, message):
        """.norms <reply to audio>
            Нормализовать звук (Из тихого - нормальный)"""
        audio = await get_audio(message, "Нормализация")
        if not audio: return
        out = effects.normalize(audio.audio)
        await go_out(message, audio, out, audio.pref, audio.pref)

    async def byrobertscmd(self, message):
        '''.byroberts <reply to audio>
            Добавить в конец аудио "Directed by Robert B Weide"'''
        audio = await get_audio(message, "Directed by...")
        if not audio: return
        out = audio.audio + AudioSegment.from_file(io.BytesIO(requests.get(
            "https://raw.githubusercontent.com/Daniel3k00/files-for-modules/master/directed.mp3").content)).apply_gain(
            +8)
        await go_out(message, audio, out, audio.pref, audio.pref)

    async def cutcmd(self, message):
        """Используй .cut <начало(сек):конец(сек)> <реплай на аудио/видео/гиф>."""
        args = utils.get_args_raw(message).split(':')
        reply = await message.get_reply_message()
        if not reply or not reply.media:
            return await message.edit('Нет реплая на медиа.')
        if reply.media:
            if args:
                if len(args) == 2:
                    try:
                        await message.edit('Скачиваем...')
                        smth = reply.file.ext
                        await message.client.download_media(reply.media,
                                                            f'uncutted{smth}')
                        if not args[0]:
                            await message.edit(
                                f'Обрезаем с 0 сек. по {args[1]} сек....')
                            os.system(
                                f'ffmpeg -i uncutted{smth} -ss 0 -to {args[1]} -c copy cutted{smth} -y')
                        elif not args[1]:
                            end = reply.media.document.attributes[0].duration
                            await message.edit(
                                f'Обрезаем с {args[0]} сек. по {end} сек....')
                            os.system(
                                f'ffmpeg -i uncutted{smth} -ss {args[0]} -to {end} -c copy cutted{smth} -y')
                        else:
                            await message.edit(
                                f'Обрезаем с {args[0]} сек. по {args[1]} сек....')
                            os.system(
                                f'ffmpeg -i uncutted{smth} -ss {args[0]} -to {args[1]} -c copy cutted{smth} -y')
                        await message.edit('Отправляем...')
                        await message.client.send_file(message.to_id,
                                                       f'cutted{smth}',
                                                       reply_to=reply.id)
                        os.system('rm -rf uncutted* cutted*')
                        await message.delete()
                    except:
                        await message.edit('Этот файл не поддерживается.')
                        os.system('rm -rf uncutted* cutted*')
                        return
                else:
                    return await message.edit('Неверно указаны аргументы.')
            else:
                return await message.edit('Нет аргументов')


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
        await message.edit(f"[{pref}] Скачиваю...")
        ae.audio = AudioSegment.from_file(
            io.BytesIO(await reply.download_media(bytes)))
        await message.edit(f"[{pref}] Работаю...")
        return ae
    else:
        await message.edit(f"[{pref}] reply to audio...")
        return None


async def go_out(message, audio, out, pref, title, fs=None):
    o = io.BytesIO()
    o.name = "audio." + ("ogg" if audio.voice else "mp3")
    if audio.voice: out.split_to_mono()
    await message.edit(f"[{pref}] Экспортирую...")
    out.export(o, format="ogg" if audio.voice else "mp3",
               bitrate="64k" if audio.voice else None,
               codec="libopus" if audio.voice else None)
    o.seek(0)
    await message.edit(f"[{pref}] Отправляю...")
    await message.client.send_file(message.to_id, o, reply_to=audio.reply.id,
                                   voice_note=audio.voice, attributes=[
            types.DocumentAttributeAudio(duration=fs if fs else audio.duration,
                                         title=title,
                                         performer="AudioEditor")] if not audio.voice else None)
    await message.delete()
