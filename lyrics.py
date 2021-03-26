#    Friendly Telegram (telegram userbot)
#    Copyright (C) 2018-2019 The Authors

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

# requires: lyricsgenius

from .. import loader, utils

import logging
import lyricsgenius

logger = logging.getLogger(__name__)


@loader.tds
class LyricsMod(loader.Module):
    """Sings songs"""
    strings = {"name": "Lyrics",
               "genius_api_token_doc": "The LyricsGenius API token from http://genius.com/api-clients",
               "invalid_syntax": "<b>Please specify song and artist.</b>",
               "song_not_found": "<b>Song not found</b>",
               "missing_token": "<b>API Token missing</b>"}

    def __init__(self):
        self.config = loader.ModuleConfig("GENIUS_API_TOKEN", None, lambda m: self.strings("genius_api_token_doc", m))

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
            logger.debug(args)
            await utils.answer(message, self.strings("invalid_syntax", message))
            return
        logger.debug("getting song lyrics for " + args[0] + ", " + args[1])
        try:
            song = await utils.run_sync(self.genius.search_song, args[0], args[1])
        except TypeError:
            # Song not found causes internal library error
            song = None
        if song is None:
            await utils.answer(message, self.strings("song_not_found", message))
            return
        logger.debug(song)
        logger.debug(song.lyrics)
        await utils.answer(message, utils.escape_html(song.lyrics))
