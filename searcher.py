# -*- coding: utf-8 -*-

# Module author: Official Repo, @GovnoCodules

# requires: search-engine-parser>=0.6.2

import io
import json

import requests
from search_engine_parser import GoogleSearch

from .. import loader, utils

@loader.tds
class SearchMod(loader.Module):
	"""Searcher module"""
	strings = {"name": "Search",
	           "search": "⚪⚪⚪\n⚪❓⚪\n⚪⚪⚪",
	           "no_reply": "<b>Reply to image or sticker!</b>",
	           "ya_result": '<a href="{}"><b>🔴⚪🔴|See</b>\n<b>⚪🔴⚪|Search</b>\n<b>⚪🔴⚪|Results</b></a>',
	           "error": '<b>Something went wrong...</b>',
	           "no_term": "<b>I can't Google nothing</b>",
	           "no_results": "<b>Could not find anything about</b> <code>{}</code> <b>on Google</b>",
	           "results": "<b>These came back from a Google search for</b> <code>{}</code>:\n\n",
	           "result": "<a href='{}'>{}</a>\n\n<code>{}</code>\n"
	           }

	@loader.owner
	async def yarscmd(self, message):
		""".yars <repy to image>"""
		reply = await message.get_reply_message()
		data = await check_media(message, reply)
		if not data:
			await utils.answer(message, self.strings("no_reply", message))
			return
		await utils.answer(message, self.strings("search", message))
		searchUrl = 'https://yandex.ru/images/search'
		files = {'upfile': ('blob', data, 'image/jpeg')}
		params = {'rpt': 'imageview', 'format': 'json',
		          'request': '{"blocks":[{"block":"b-page_type_search-by-image__link"}]}'}
		response = requests.post(searchUrl, params=params, files=files)
		if response.ok:
			query_string = json.loads(response.content)['blocks'][0]['params']['url']
			link = searchUrl + '?' + query_string
			text = self.strings("ya_result", message).format(link)
			await utils.answer(message, text)
		else:
			await utils.answer(message, self.strings("error", message))

	async def googlecmd(self, message):
		"""Shows Google search results."""
		text = utils.get_args_raw(message.message)
		if not text:
			text = (await message.get_reply_message()).message
		if not text:
			await utils.answer(message, self.strings("no_term", message))
			return
		gsearch = GoogleSearch()
		gresults = await gsearch.async_search(text, 1)
		if not gresults:
			await utils.answer(message, self.strings("no_results", message).format(text))
			return
		results = zip(gresults["titles"], gresults["links"], gresults["descriptions"])
		msg = "".join(
			self.strings("result").format(
				utils.escape_html(result[0]),
				utils.escape_html(result[1]),
				utils.escape_html(result[2]),
			) for result in results)
		await utils.answer(message, self.strings("results", message).format(utils.escape_html(text)) + msg)


async def check_media(message, reply):
	if not reply or not reply.media:
		return None
	if reply.photo:
		data = reply.photo
	elif reply.document:
		if reply.gif or reply.video or reply.audio or reply.voice:
			return None
		data = reply.media.document
	else:
		return None
	if not data or data is None:
		return None
	data = await message.client.download_file(data, bytes)
	return io.BytesIO(data)
