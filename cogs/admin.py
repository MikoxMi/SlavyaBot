import discord

from .utils.u_mongo import Mongo
from discord.ext import commands
from discord.ext.commands import has_permissions

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(pass_context=True)
    @has_permissions(administrator=True)
    async def set_prefix(self, ctx, *, prefix='='):
        """
        Sets the prefix for the server
        -set_prefix <=, -, !>
        """

        record = await Mongo.get_record('server_settings', 'id', ctx.message.guild.id)
        upg = {
            "prefix": prefix
        }
        await Mongo.update_record('server_settings', record, upg)
        await ctx.send(f"Prefix is now: {prefix}")

    @commands.command(pass_context=True)
    @has_permissions(administrator=True)
    async def set_descriptor(self, ctx, descriptor='en'):
        """
        Set descriptor for translate other languages 
        -set_descriptor <en, ru>
        """
        
        record = await Mongo.get_record('server_settings', 'id', ctx.message.guild.id)

        upg = {
            "translator": descriptor
        }
        await Mongo.update_record('server_settings', record, upg)
        await ctx.send(f"Descriptor is now: {descriptor}")

    @commands.command(pass_context=True)
    @has_permissions(administrator=True)
    async def set_emoji(self, ctx, emoji):
        """
        Set emoji for money server
        -set_emoji <discord.Emoji>
        """

        server_id = ctx.message.guild.id
        record = await Mongo.get_record('server_settings', 'id', server_id)

        upg_emoji = {
            "emoji_name":emoji
        }
        await Mongo.update_record('server_settings', record, upg_emoji)

        await ctx.send(f"Money Emoji is now: {emoji}")


def setup(bot):
    bot.add_cog(Admin(bot))