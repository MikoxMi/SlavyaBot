import discord

from .utils.u_mongo import Mongo
from .utils.u_discord import DiscordUtils

from discord.ext import commands

def is_owner(ctx):
    member = ctx.author.id
    l_owners = [282597309512941568]

    return member in l_owners

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(pass_context=True)
    @commands.check(is_owner)
    async def rld(self, ctx, extension_name : str):
        """
        Reload Module
        """
        self.bot.unload_extension(extension_name)
        await ctx.send("{} unloaded.".format(extension_name))
        try:
            self.bot.load_extension(extension_name)
        except (AttributeError, ImportError) as e:
            await ctx.send(f"```py\n{type(e).__name__}: {str(e)}\n```")
            return
        await ctx.send("{} loaded.".format(extension_name))

    @commands.command(pass_context=True)
    @commands.check(is_owner)
    async def unload(self, ctx, extension_name : str):
        """
        Unload Modules
        """
        self.bot.unload_extension(extension_name)
        await ctx.send("{} unloaded.".format(extension_name))

    @commands.command(pass_context=True)
    @commands.check(is_owner)
    async def logout(self, ctx):
        """
        Disable bot
        """
        await ctx.send("Disable bot")
        await self.bot.logout()

    @commands.command(pass_context=True)
    @commands.check(is_owner)
    async def add_money(self, ctx, member, money):
        """
        Add money to member
        add_money <@member> <money>
        """
        
        record, member = await DiscordUtils.get_user(self.bot, ctx, 0, member)

        money_member = record['money'] + int(money)
        upg = {
            "money": money_member
        }
        await Mongo.update_record('members', record, upg)
        
        await ctx.send(f"Owner bot give {member.mention} - {money} money")


def setup(bot):
    bot.add_cog(Owner(bot))