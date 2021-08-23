from discord import Member, Embed
from discord.ext.commands import Cog, command
from discord.ext.commands.errors import MissingRequiredArgument

from ..db import db

class Epics(Cog):
    def __init__(self, bot):
        self.bot = bot


    async def get_epicIds(self, userId):
        epicIdRow = db.record("SELECT EpicId FROM users WHERE UserID = ?", userId)

        if epicIdRow:
            return epicIdRow[0].split(',')
    
    def verify_unique(self, epicIds, epic_ids):
        if epic_ids in epicIds:
            return False
        else:
            return True

    @command(name="addepic", aliases=["add"])
    async def add_epic(self, ctx, *, epic_ids):
        """This command links your discord user with your epic ids."""

        userId = ctx.author.id
        userName = ctx.author.name

        epicIds = await self.get_epicIds(userId)

        # If doesn't exists a epicId for this user insert a new one
        # If does exist then append the new epic to the list
        if not epicIds:
            db.execute("INSERT INTO users (UserId, UserName, EpicId) VALUES (?, ?, ?)", userId, userName, epic_ids)
        else:
            if self.verify_unique(epicIds, epic_ids):
                epicIds.append(epic_ids)

                epicsToAdd = ','.join(epicIds)
                
                db.execute("UPDATE users SET EpicId = ? WHERE UserID = ?", epicsToAdd, userId)

                await ctx.send(f"Added {epic_ids}")
            else:
                await ctx.send(f"{epic_ids} is already assigned to you!")

        await ctx.message.delete()

    @command(name="epicid", aliases=["showepicid", "giveepicid"])
    async def get_epicid(self, ctx, member: Member):
        """This command returns the epic ids for the given user."""
        
        userId = member.id

        epicIds = await self.get_epicIds(userId)

        embed = Embed(title=f"{member.display_name} Epic ids")
        embed.set_thumbnail(url=member.avatar_url)

        if epicIds:
            for id in epicIds:
                embed.add_field(name="** **", value=id, inline=False)
        else:
            embed.add_field(name="** **", value="This user didn't insert their epicId yet.", inline=False)

        await ctx.message.delete()
        await ctx.send(embed=embed)
         


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