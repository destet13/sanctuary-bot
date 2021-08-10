from asyncio import sleep
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from glob import glob

from discord import Intents
from discord.errors import Forbidden
from discord.ext.commands import Bot as BotBase
from discord.ext.commands.errors import CommandNotFound, MissingRequiredArgument

from ..db import db

PREFIX = "/"
OWNER_IDS = ["156510645729099777", "612645749238530060"]
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]

class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f"{cog} ready!")
    
    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])

class Bot(BotBase):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.cogs_ready = Ready()
        self.guild = None
        self.scheduler = AsyncIOScheduler()

        db.autosave(self.scheduler)

        super().__init__(
            command_prefix=PREFIX, 
            owner_ids=OWNER_IDS, 
            intents=Intents.all(),
        )
    
    def setup(self):
        print("Loading COGS...")
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f"{cog} loaded")
        
        print("COGS loaded!")
    
    def run(self, version):
        self.VERSION = version

        self.setup()

        with open("./lib/bot/token", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()

        print(f"Running bot version {version}...")
        super().run(self.TOKEN, reconnect=True)

    async def on_connect(self):
        print("Bot up!!")
    
    async def on_disconnected(self):
        print("Bot is down!!")
    
    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Oopsy!! Something went wrong...")
        
        await self.stdout.send("An error ocurred..")
        raise

    async def on_command_error(self, ctx, exc):
        if isinstance(exc, CommandNotFound):
            await ctx.send("That command doesn't exist!!")
        elif isinstance(exc, MissingRequiredArgument):
            pass
        elif isinstance(exc.original, Forbidden):
            await ctx.send("Sadly i don't have permisson to execute that command!!")
        elif hasattr(exc, "original"):
            raise exc.original
        else:
            raise exc
    
    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(798394787032072252)
            self.stdout = self.get_channel(798394787032072255)
            self.scheduler.start()

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            # this should be the last think being made here
            self.ready = True
            await self.stdout.send("I am online and ready to go!!")
        else:
            print("Bot reconnected")
            
    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)

bot = Bot()