##########################
# Skeleton of FTG module #
##########################

################################################
##     If you use third-party libraries,      ##
## you can specify from in a special comment, ##
##  and they will be installed automatically  ##
################################################
# requires: requests numpy

# Must be in any module
from .. import loader, utils
from telethon import types, TelegramClient

import asyncio
import logging

# If you want to use logging, leave it at that
logger = logging.getLogger(__name__)
# Usage:
#  logger.debug("Text")
#  logger.warning("Text")
#  logger.error("Text")
#  logger.log("Text")
#  logger.critical("Text") and etc...

# Module class must be must end in `Mod` and contains in args `loader.Module`
# Example: `MODULE_NAMEMod(loader.Module)`
@loader.tds
class YourMod(loader.Module):
    """Example module""" # Description for module | Translateable due to @loader.tds
    
    # Strings used in the module
    strings = {"name": "Module's name",
                "cfg_doc": "This is what is said, you can edit me with the configurator",
               "after_sleep": "We have finished sleeping!"}

    # If you want to use config, leave this `def` at that
    def __init__(self):
        self.config = loader.ModuleConfig("CONFIG_STRING", "hello", lambda m: self.strings("cfg_doc", m))
        # To get data from the configuration use: `self.config["CONFIG_STRING"]`
    
    # `client_ready` executing after loading module
    # It also adds support for working with the database (`self.db = db`) and TelegramClient (`self.client = client`)
    # Also for using client? you can just use: `message.client in command's functions`
    async def client_ready(self, client, db):
        self.client: TelegramClient = client # Telethon client
        
        self.db = db # Database of FTG
        # self.db.get("Key", "Value", `Any`)
        #  `Any` - The value that will be returned if the key is not found
        # self.db.set("Key", "Value")
    
    # To add a module command, create an asynchronous function that must end in cmd
    # .example == `examplecmd`
    @loader.unrestricted  # Security setting to change who can use the command (defaults to owner | sudo)
    async def examplecmd(self, message: types.Message):
        """Does something when you type .example (hence, named examplecmd)""" # Description for command
        
        logger.debug("We logged something!") # Example of logging in cmd
        
        # To get data from the configuration use: `self.config["CONFIG_STRING"]`
        message = await utils.answer(message, self.config["CONFIG_STRING"])
        
        await asyncio.sleep(5)  # Never use time.sleep
        
        # For using strings use: `self.strings("STRING", message)` or `self.strings("STRING", message).format(ur_data)`
        await utils.answer(message, self.strings("after_sleep", message))
        
        return # If you need to stop the function use `return`
