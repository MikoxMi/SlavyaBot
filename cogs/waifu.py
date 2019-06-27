import discord
import asyncio
import re

from discord.ext import commands

from .utils.u_mongo import Mongo
from .utils.u_discord import DiscordUtils

class Waifu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    async def waifu(self, ctx):
        """
        Waifu subcommands

        -waifu profile <member>
        -waifu buy <member>
        -waifu gift <member>
        -waifu like <member>
        """

        if ctx.invoked_subcommand is None:
            msg = ctx.command.help
            em = discord.Embed(colour=ctx.message.author.colour)
            em.add_field(name="Command Helper", value=F"{msg}")
            await ctx.send(embed=em)
            return
    
    @waifu.command(pass_context=True)
    async def profile(self, ctx, member=None):
        """
        Get member waifu profile
        """

        record, member = await DiscordUtils.get_user(self.bot, ctx, 0, member)

        waifu = record['waifu']
        waifu_like = record['waifu_like']
        waifu_inventory = record['waifu_gifts']
        waifu_inventory_count = record['waifu_gifts_count']

        inventory = ''
        i = 0
        for items in waifu_inventory:
            record_shop = await Mongo.get_record('shop', 'item', items)
            if record_shop['emoji'] == "None":
                s = f"{items}: {waifu_inventory_count[i]}"
                inventory += ''.join(s) + '\n'
            else:
                name_emoji = record_shop['emoji']
                guild = discord.utils.get(self.bot.guilds, id=record_shop['emoji_id'])
                emoji = discord.utils.get(guild.emojis, name=name_emoji)
                s = f"{emoji}: {waifu_inventory_count[i]}"
                inventory += ''.join(s) + '\n'                
            i += 1

        if inventory == '':
            inventory = "None"

        em = discord.Embed(colour=member.colour)    
        em.set_author(name=member, icon_url=member.avatar_url)
        em.add_field(name="Waifu", value=f"{waifu}", inline=True)
        em.add_field(name="Like", value=f"{waifu_like}", inline=True)
        em.add_field(name='Inventory', value=inventory)

        await ctx.send(embed=em)

    @waifu.command(pass_context=True)
    async def like(self, ctx, member: discord.Member):
        """Putting in a profile of who you like

        -waifu like @member"""

        author = ctx.author

        if member.id == author:
            await self.bot.say("You can't love yourself. :(")
            return

        record = await Mongo.get_record('members', 'id', author.id)
        updates = {
            "waifu_like": F"{member.mention}"
        }
        await Mongo.update_record('members', record, updates)

        desc = F"{ctx.message.author.mention} wants to be with {member.mention} :heart:"
        em = discord.Embed(colour=ctx.message.author.colour, description=desc)
        em.set_author(name="Waifu system")
        await ctx.send(embed=em)

    @waifu.command(pass_context=True)
    async def marry(self, ctx, member=None):
        """
        Give invite of marry to user
        -waifu marry <member>
        """

        record, member = await DiscordUtils.get_user(self.bot, ctx, 0, member)

        record_buyer = await Mongo.get_record('members', 'id', ctx.author.id)

        if member.id == ctx.author.id:
            await ctx.send("You can't marry yourself.")
            return
        
        if record_buyer['waifu'] != "None":
            await ctx.send("```You're married```")
            return
        
        if record['waifu'] != "None":
            await ctx.send("This person is already married")
            return

        msg_help = await ctx.send('To accept this offer write !accept or !deny')
        
        msg = await self.bot.wait_for('message', check=lambda message: message.author == member)
        await ctx.send('!accept')
        if msg:
            if msg.content == '!accept':
                upg_waifu = {
                    "waifu": F"{ctx.author.mention}"
                }
                upg_member = {
                    "waifu": F"{member.mention}",
                }
                await Mongo.update_record('members', record, upg_waifu)
                await Mongo.update_record('members', record_buyer, upg_member)

                desc = F"{ctx.message.author.mention} now married to {member.mention}:heart:"
                e = discord.Embed(colour=ctx.message.author.colour, description=desc)
                e.set_author(name="Waifu system")
                await ctx.send(embed=e)
                await msg_help.delete()
                await msg.delete()
            else:
                await ctx.send(f'{member.mention} decline the offer')
                await msg_help.delete()
                await msg.delete()
                return

    @waifu.command(pass_context=True)
    async def declaim(self, ctx):
        """
        Break off relations
        -waifu declaim
        """

        record = await Mongo.get_record('members', 'id', ctx.message.author.id)

        waifu = record['waifu']
        id_m = re.findall('\\d+', waifu)[0]
        if waifu == "None":
            await ctx.send("You don't have waifu")
            return

        record_waifu = await Mongo.get_record('members', 'id', int(id_m))

        upg_member = {
            "waifu": "None"
        }

        upg_waifu = {
            "waifu": "None"
        }

        s = f'You throw away {waifu}'
        await ctx.send(s)

        await Mongo.update_record('members', record, upg_member)
        await Mongo.update_record('members', record_waifu, upg_waifu)

    @waifu.command(pass_context=True)
    async def gift(self, ctx, member:discord.Member, *, gift):
        """
        Gift for waifu
        waifu gift <member> <gift>
        """

        record_item = await Mongo.get_record('shop', 'item', gift)
        record_waifu = await Mongo.get_record('members', 'id', member.id)
        record_member = await Mongo.get_record('members', 'id', ctx.message.author.id)

        if record_item is None:
            await ctx.send("This item has not exist")
            return

        if record_item['category'] != "Waifu":
            await ctx.send("You can not give items that are not in the Waifu category")
            return

        if int(record_member['money']) < int(record_item['price']):
            await ctx.send("You do not have enough money for a gift")
            return

        if ctx.message.author.id == member.id:
            await ctx.send("You can not give gifts to yourself")
            return

        money_member = int(record_member['money']) - int(record_item['price'])

        #Add count to item
        i = 0
        inventory = record_waifu['waifu_gifts']
        for items in inventory:
            if gift == items:
                static_i = i
            i += 1
        
        waifu_count_gifts = record_waifu['waifu_gifts_count']
        inventory_count = int(waifu_count_gifts[static_i]) + 1
        waifu_count_gifts[static_i] = str(inventory_count)
        ###
    
        if record_item['emoji'] != "None":
           server = discord.utils.get(self.bot.guilds, id=record_item['emoji_id'])
           gift = discord.utils.get(server.emojis, name=record_item['emoji'])
        else:
            pass


        upg_member = {
            "money": int(money_member)
        }

        upg_waifu = {
            "waifu_gifts_count":waifu_count_gifts,
        }

        await Mongo.update_record('members', record_member, upg_member)
        await Mongo.update_record('members', record_waifu, upg_waifu)

        e = discord.Embed(colour=ctx.message.author.colour, description=F"{ctx.message.author.mention} gift {member.mention}: {gift}")
        if record_item['image'] == "None":
            pass
        else:
            e.set_image(url=record_item['image'])
        e.set_author(name="Waifu system:")
        await ctx.send(embed=e)




def setup(bot):
    bot.add_cog(Waifu(bot))
