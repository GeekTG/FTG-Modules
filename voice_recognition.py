# -*- coding: utf-8 -*-

# Module author: @dekftgmodules

# requires: pydub speechRecognition

from io import BytesIO

import speech_recognition as srec
from pydub import AudioSegment as auds

from .. import loader


@loader.tds
class VoiceRecognitionMod(loader.Module):
    """Распознавание речи через Google Recognition API"""

    strings = {"name": "VoiceRecognition", "pref": "<b>[VRC]</b> "}

    @loader.owner
    async def recvcmd(self, m):
        """.recv <reply to voice/audio> - распознать речь"""
        reply = await m.get_reply_message()
        if reply and reply.file.mime_type.split("/")[0] == "audio":
            await m.edit(self.strings["pref"] + "Downloading...")
            source = BytesIO(await reply.download_media(bytes))
            source.name = reply.file.name
            out = BytesIO()
            out.name = "recog.wav"
            await m.edit(self.strings["pref"] + "Converting...")
            auds.from_file(source).export(out, "wav")
            out.seek(0)
            await m.edit(self.strings["pref"] + "Processing...")
            recog = srec.Recognizer()
            sample_audio = srec.AudioFile(out)
            with sample_audio as audio_file:
                audio_content = recog.record(audio_file)
            await m.edit(
                self.strings["pref"]
                + recog.recognize_google(audio_content, language="ru-RU")
            )
        else:
            await m.edit(self.strings["pref"] + "reply to audio/voice...")
