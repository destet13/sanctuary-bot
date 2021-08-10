from discord.errors import HTTPException
from discord.ext.commands import Cog, command
from discord.ext.commands.errors import MissingRequiredArgument

from ..db import db

class Epics(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="addepic", aliases=["add"])
    async def add_epic(self, ctx, *, epic_ids):
        """This command links your discord user with your epic ids."""

        userId = ctx.author.id
        userName = ctx.author.name

        epicIdRow = db.record("SELECT EpicId FROM users WHERE UserID = ?", userId)

        # If doesn't exists a epicId for this user insert a new one
        # If does exist then append the new epic to the list
        if not epicIdRow:
            db.execute("INSERT INTO users (UserId, UserName, EpicId) VALUES (?, ?, ?)", userId, userName, epic_ids)
        else:
            epicIds = list(epicIdRow)
            epicIds.append(epic_ids)

            epicsToAdd = ','.join(epicIds)
            
            db.execute("UPDATE users SET EpicId = ? WHERE UserID = ?", epicsToAdd, userId)

        await ctx.message.delete()
        await ctx.send(f"Added {epic_ids}")

    @add_epic.error
    async def add_epic_error(self, ctx, exc):
        if isinstance(exc, MissingRequiredArgument):
            print(f"ERROR: {exc}")
            await ctx.send("Please send the id/ids required | /add [EPIC_ID] | separeted by commas")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("epics")
    

def setup(bot):
    bot.add_cog(Epics(bot))