import io, inspect 
from .. import loader, utils 
 
 
@loader.tds 
class ModulesLinkMod(loader.Module): 
    """Ссылка на модуль""" 
    strings = {'name': 'ModulesLink'} 
 
    async def mlcmd(self, message): 
        """Вывести ссылку на модуль""" 
        args = utils.get_args_raw(message) 
        if not args: 
            return await message.edit('Нет аргументов.') 
 
        await message.edit('Ищем...') 
 
        try: 
            f = ' '.join([x.strings["name"] for x in self.allmodules.modules if args.lower() == x.strings["name"].lower()]) 
            r = inspect.getmodule(next(filter(lambda x: args.lower() == x.strings["name"].lower(), self.allmodules.modules))) 
 
            link = str(r).split('(')[1].split(')')[0] 
            if "http" not in link: 
                text = f"Модуль {f}:" 
            else: 
                text = f"<a href=\"{link}\">Ссылка</a> на 🇺🇦{f}: <code>{link}</code>" 
 
            out = io.BytesIO(r.__loader__.data) 
            out.name = f + ".py" 
            out.seek(0) 
 
            await message.respond(text, file=out) 
            await message.delete() 
        except: 
            return await message.edit("Попробуй ввести имя модуля в кавычках")
