import asyncio
import logging
import os
import platform
import shutil
import sys

import telethon

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class InfoMod(loader.Module):
	"""Provides system information about the computer hosting this bot"""
	strings = {"name": "System Info",
	           "info_title": "<b>System Info</b>",
	           "kernel": "<b>Kernel:</b> <code>{}</code>",
	           "arch": "<b>Arch:</b> <code>{}</code>",
	           "os": "<b>OS:</b> <code>{}</code>",
	           "heroku": "FTG Installed on <b>Heroku</b>",
	           "distro": "<b>Linux Distribution:</b> <code>{}</code>",
	           "android_sdk": "<b>Android SDK:</b> <code>{}</code>",
	           "android_ver": "<b>Android Version:</b> <code>{}</code>",
	           "android_patch": "<b>Android Security Patch:</b> <code>{}</code>",
	           "unknown_distro": "<b>Could not determine Linux distribution.</b>",
	           "python_version": "<b>Python version:</b> <code>{}</code>",
	           "telethon_version": "<b>Telethon version:</b> <code>{}</code>",
	           "git_version": "<b>Git version:</b> <code>{}</code>",
	           "ftg_type": "<b>FTG Type:</b> <code>{}</code>"}

	async def infocmd(self, message):
		"""Shows system information"""
		ftg_type = "PC/Server"
		reply = self.strings("info_title", message)
		reply += "\n" + self.strings("kernel", message).format(utils.escape_html(platform.release()))
		reply += "\n" + self.strings("arch", message).format(utils.escape_html(platform.architecture()[0]))
		reply += "\n" + self.strings("os", message).format(utils.escape_html(platform.system()))

		if platform.system() == "Linux":
			done = False
			try:
				a = open("/etc/os-release").readlines()
				b = {line.split("=")[0]: line.split("=")[1].strip().strip("\"") for line in a}
				reply += "\n" + self.strings("distro", message).format(utils.escape_html(b["PRETTY_NAME"]))
				done = True
			except FileNotFoundError:
				ftg_type = "Android (Termux)"
				getprop = shutil.which("getprop")
				if getprop is not None:
					sdk = await asyncio.create_subprocess_exec(getprop, "ro.build.version.sdk",
					                                           stdout=asyncio.subprocess.PIPE)
					ver = await asyncio.create_subprocess_exec(getprop, "ro.build.version.release",
					                                           stdout=asyncio.subprocess.PIPE)
					sec = await asyncio.create_subprocess_exec(getprop, "ro.build.version.security_patch",
					                                           stdout=asyncio.subprocess.PIPE)
					sdks, unused = await sdk.communicate()
					vers, unused = await ver.communicate()
					secs, unused = await sec.communicate()
					if sdk.returncode == 0 and ver.returncode == 0 and sec.returncode == 0:
						reply += "\n" + self.strings("android_sdk", message).format(sdks.decode("utf-8").strip())
						reply += "\n" + self.strings("android_ver", message).format(vers.decode("utf-8").strip())
						reply += "\n" + self.strings("android_patch", message).format(secs.decode("utf-8").strip())
						done = True
			if not done:
				reply += "\n" + self.strings("unknown_distro", message)
		reply += "\n" + self.strings("python_version", message).format(utils.escape_html(sys.version))
		reply += "\n" + self.strings("telethon_version", message).format(utils.escape_html(telethon.__version__))
		if 'DYNO' in os.environ:
			ftg_type = "Heroku"
		else:
			reply += "\n" + self.strings("git_version", message).format(
				os.popen(f"cd {utils.get_base_dir()[:-17]} && git show -s --format=\"%h %cd\"").read()[:-7])
		if 'LAVHOST' in os.environ:
			reply += "\n" + "<b>FTG Type:</b> " + f"<code>lavHost {os.getenv('LAVHOST')}</code> (@lavHost)"
		else:
			reply += "\n" + self.strings("ftg_type", message).format(ftg_type)
		await utils.answer(message, reply)
