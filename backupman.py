# Author @mishase
# Inspired by @tshipenchko

from .. import loader, utils
import io, sys, zlib

fname = "modules.bin"

enc = "utf-8"
d = [b"\xFD", b"\xFF"]

l = "friendly-telegram.modules.loader"

def register(cb):
	cb(BackupManMod())

class BackupManMod(loader.Module):
	"""BackupMan"""
	strings = {'name': 'BackupMan'}

	def __init__(self):
		self.name = self.strings['name']
	
	async def client_ready(self, client, db):
		self.db = db
		self.client = client

	async def backupcmd(self, message):
		modules = map(get_module, self.allmodules.modules)
		b = zlib.compress(d[1].join(map(lambda mod: d[0].join(map(lambda s: s if isinstance(s, bytes) else s.encode(enc), mod)), filter(lambda mod: None not in mod and mod[1] != "path", modules))))
		f = io.BytesIO(b)
		f.name = fname
		await message.client.send_file(message.to_id, f, caption=f"[BackupMan] Backup completed!")
		await message.delete()

	async def restorecmd(self, message):
		reply = await message.get_reply_message()
		if not reply or not reply.file or reply.file.name != fname:
			return await message.edit("Reply to file")
		await message.edit("[BackupMan] Downloading backup...")
		f = io.BytesIO()
		await reply.download_media(f)
		f.seek(0)
		b = zlib.decompress(f.read())
		modules = list(map(lambda e: list(map(lambda e: e.decode(enc), e.split(d[0]))), b.split(d[1])))
		loader = next(filter(lambda x: "LoaderMod" == x.__class__.__name__, self.allmodules.modules))
		await message.edit("[BackupMan] Loading backup...")
		for [name, mtype, data] in modules:
			if mtype == "link":
				if await loader.download_and_install(data):
					self.db.set(l, "loaded_modules", list(set(self.db.get(l, "loaded_modules", [])).union([data])))
			elif mtype == "text":
				await loader.load_module(data, None)
		await message.edit("[BackupMan] Restore completed!")

def get_module(module):
	name = module.name
	sysmod = sys.modules.get(module.__module__)
	origin = sysmod.__spec__.origin
	loader = sysmod.__loader__
	cname = type(loader).__name__
	r = [name, None, None]
	if cname == "SourceFileLoader":
		r[1] = "path"
		r[2] = loader.get_filename()
	elif cname == "StringLoader":
		if origin == "<string>":
			r[1] = "text"
			r[2] = loader.data
		else:
			r[1] = "link"
			r[2] = origin
	return r
