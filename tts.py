# requires: pydub requests gtts hachoir
import io
import os

import requests
from gtts import gTTS
from pydub import AudioSegment

from .. import loader, utils


def register(cb):
	cb(DttsMod())


class DttsMod(loader.Module):
	"""Text to speech module"""

	strings = {"name": 'DTTS',
	           "no_text": "I can't say nothing",
	           "tts_lang_cfg": "Set your language code for the TTS here."}

	def __init__(self):
		self.config = loader.ModuleConfig("TTS_LANG", "en", lambda m: self.strings("tts_lang_cfg", m))
		self.is_ffmpeg = os.system("ffmpeg -version") == 0

	async def say(self, message, speaker, text, file=".dtts.mp3"):
		reply = await message.get_reply_message()
		if not text:
			if not reply:
				return await utils.answer(message, self.strings['no_text'])
			text = reply.raw_text  # use text from reply
		if not text:
			return await utils.answer(message, self.strings['no_text'])
		if message.out:
			await message.delete()  # Delete message only one is user's
		data = {"text": text}
		if speaker:
			data.update({"speaker": speaker})

		# creating file in memory
		f = io.BytesIO(requests.get("https://station.aimylogic.com/generate", data=data).content)
		f.name = file

		if self.is_ffmpeg:
			f, duration = to_voice(f)
		else:
			duration = None

		await message.client.send_file(message.chat_id, f, voice_note=True, reply_to=reply, duration=duration)

	@loader.unrestricted
	@loader.ratelimit
	async def levitancmd(self, message):
		"""Convert text to speech with levitan voice"""
		await self.say(message, "levitan", utils.get_args_raw(message))

	@loader.unrestricted
	@loader.ratelimit
	async def oksanacmd(self, message):
		"""Convert text to speech with oksana voice"""
		await self.say(message, "oksana", utils.get_args_raw(message))

	@loader.unrestricted
	@loader.ratelimit
	async def yandexcmd(self, message):
		"""Convert text to speech with yandex voice"""
		await self.say(message, None, utils.get_args_raw(message))

	@loader.unrestricted
	@loader.ratelimit
	async def ttscmd(self, message):
		"""Convert text to speech with Google APIs"""
		reply = await message.get_reply_message()
		text = utils.get_args_raw(message.message)

		if not text:
			if message.is_reply:
				text = (await message.get_reply_message()).message
			else:
				return await utils.answer(message, self.strings("no_text", message))

		if message.out:
			await message.delete()

		tts = await utils.run_sync(gTTS, text, lang=self.config["TTS_LANG"])
		voice = io.BytesIO()
		await utils.run_sync(tts.write_to_fp, voice)
		voice.seek(0)
		voice.name = "voice.mp3"

		if self.is_ffmpeg:
			voice, duration = to_voice(voice)
		else:
			duration = None

		await message.client.send_file(message.chat_id, voice, voice_note=True, reply_to=reply, duration=duration)


def to_voice(item):
	"""Returns audio in opus format and it's duration"""
	item.seek(0)
	item = AudioSegment.from_file(item)
	m = io.BytesIO()
	m.name = "voice.ogg"
	item.split_to_mono()
	dur = len(item) / 1000
	item.export(m, format="ogg", bitrate="64k", codec="libopus")
	m.seek(0)
	return m, dur

# By @vreply @pernel_kanic @nim1love @db0mb3r and add @tshipenchko some geyporn
