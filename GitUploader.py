# -*- coding: utf-8 -*-
#     GitHub File Uploader
#     Copyright (C) 2020 utya @unxho & wardsenz @azeronde

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.

#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
from .. import loader, utils
import logging
import base64
import os
import requests
import json
from requests.exceptions import MissingSchema, ChunkedEncodingError

logger = logging.getLogger(__name__)


def register(cb):
    cb(GitaddMod())


@loader.tds
class GitaddMod(loader.Module):
    """Загружает файлы на репозиторий GitHub"""

    strings = {
        "name": "GitUploader",
        "reply_to_file": "<b>Ответьте на файл</b>",
        "error_file": "Формат не поддерживается",
        "connection_error": "<i>Ошибка соединения</i>",
        "repo_error": "<i>Ошибка репозитория</i>",
        "token_error": "<i>Ошибка токена</i>",
        "exist_422": "<b>Не удалось загрузить файл. Возможная причина: файл с таким названием уже существует в репозитории.</b>",
        "cfg_token": "Токен GitHub",
        "token_not_found": "Токен не найден",
        "username_not_found": "Имя пользователя GitHub не указано",
        "repo_not_found": "Репозиторий не указан",
        "cfg_gh_user": "Имя пользователя на GitHub",
        "cfg_gh_repo": "Репозиторий, куда нужно загружать модули",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            "GH_TOKEN",
            "TOKEN",
            lambda m: self.strings("cfg_token", m),
            "GH_USERNAME",
            "USERNAME",
            lambda m: self.strings("cfg_gh_user", m),
            "GH_REPO",
            "REPOSITORY",
            lambda m: self.strings("cfg_gh_repo", m),
        )

    async def client_ready(self, client, db):
        self.client = client

    @loader.owner
    async def gitaddcmd(self, message):
        if self.config["GH_TOKEN"] == "TOKEN":
            await utils.answer(message, self.strings("token_not_found", message))
            return
        if self.config["GH_USERNAME"] == "USERNAME":
            await utils.answer(message, self.strings("username_not_found", message))
            return
        if self.config["GH_REPO"] == "REPOSITORY":
            await utils.answer(message, self.strings("repo_not_found", message))
            return
        reply = await message.get_reply_message()
        if not reply:
            await utils.answer(message, self.strings("reply_to_file", message))
            return
        media = reply.media
        if not media:
            await utils.answer(message, self.strings("reply_to_file", message))
            return
        try:
            fname = (reply.media.document.attributes[0]).file_name
        except AttributeError:
            await utils.answer(message, self.strings("error_file", message))
            return
        try:
            file = await message.client.download_file(media)
            encoded_string = base64.b64encode(file)
            stout = encoded_string.decode("utf-8")
            TOKEN = self.config["GH_TOKEN"]
            USERNAME = self.config["GH_USERNAME"]
            REPO = self.config["GH_REPO"]
            # url = f'{self.config["GH_REPO"]}{fname}'
            url = f"https://api.github.com/repos/{USERNAME}/{REPO}/contents/{fname}"
            head = {
                "Authorization": f"token {TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            }
            git_data = '{"message": "Upload file", "content":' + '"' + stout + '"' + "}"
            r = requests.put(url, headers=head, data=git_data)
            if int(r.status_code) == 201:
                uploaded_to = f"https://github.com/{USERNAME}/{REPO}"
                uploaded_to_raw = uploaded_to + f"/raw/master/{fname}"
                await utils.answer(
                    message,
                    f"Файл <code>{fname}</code> успешно загружен на <a href=\f'{uploaded_to}'>репозиторий!</a>\n\nПрямая ссылка: <code>{uploaded_to_raw}</code>",
                )
                return
            elif int(r.status_code) == 422:
                await utils.answer(message, self.strings("exist_422", message))
                return
            else:
                json_resp = json.loads(r.text)
                git_resp = json_resp["message"]
                await utils.answer(
                    message,
                    f"Произошла неизвестная ошибка! Ответ сервера:\n <code>{git_resp}</code>",
                )
                return
        except ConnectionError:
            await utils.answer(message, self.strings("connection_error", message))
            return
        except MissingSchema:
            await utils.answer(message, self.strings("repo_error", message))
            return
        except ChunkedEncodingError:
            await utils.answer(message, self.strings("token_error", message))
            return
