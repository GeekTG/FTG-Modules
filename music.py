# -*- coding: utf-8 -*-

# Module author: Official Repo, @dekftgmodules

# requires: lyricsgenius ShazamAPI

import io

import lyricsgenius
from ShazamAPI import Shazam

from .. import loader, utils


@loader.tds
class LyricsMod(loader.Module):
	"""Sings songs"""
	strings = {"name": "Lyrics",
	           "genius_api_token_doc": "The LyricsGenius API token from http://genius.com/api-clients",
	           "invalid_syntax": "<b>Please specify song and artist.</b>",
	           "song_not_found": "<b>Song not found</b>",
	           "missing_token": "<b>API Token missing</b>"}

	tag = "<b>[Shazam]</b> "

	def __init__(self):
		self.config = loader.ModuleConfig("GENIUS_API_TOKEN", None,
		                                  lambda message: self.strings("genius_api_token_doc", message))

	def config_complete(self):
		if self.config["GENIUS_API_TOKEN"]:
			self.genius = lyricsgenius.Genius(self.config["GENIUS_API_TOKEN"])
		else:
			self.genius = None

	@loader.unrestricted
	@loader.ratelimit
	async def lyricscmd(self, message):
		""".lyrics Song, Artist"""
		if self.genius is None:
			await utils.answer(message, self.strings("missing_token", message))
		args = utils.get_args_split_by(message, ",")
		if len(args) != 2:
			await utils.answer(message, self.strings("invalid_syntax", message))
			return
		try:
			song = await utils.run_sync(self.genius.search_song, args[0], args[1])
		except TypeError:
			# Song not found causes internal library error
			song = None
		if song is None:
			await utils.answer(message, self.strings("song_not_found", message))
			return
		await utils.answer(message, utils.escape_html(song.lyrics))

	async def shazamcmd(self, message):
		""".shazam <reply to audio> - распознать трек"""
		s = await get_audio_shazam(message)
		if not s: return
		try:
			shazam = Shazam(s.track.read())
			recog = shazam.recognizeSong()
			track = next(recog)[1]['track']
			await message.client.send_file(message.to_id, file=track['images']['background'],
			                               caption=self.tag + "Распознанный трек: " + track['share']['subject'],
			                               reply_to=s.reply.id)
			await message.delete()
		except:
			await message.edit(self.tag + "Не удалось распознать...")


async def get_audio_shazam(message):
	class rct():
		track = io.BytesIO()
		reply = None

	reply = await message.get_reply_message()
	if reply and reply.file and reply.file.mime_type.split("/")[0] == "audio":
		ae = rct()
		await utils.answer(message, "<b>Скачиваю...</b>")
		ae.track = io.BytesIO(await reply.download_media(bytes))
		ae.reply = reply
		await message.edit("<b>Распознаю...</b>")
		return ae
	else:
		await utils.answer(message, "<b>reply to audio...</b>")
		return None
