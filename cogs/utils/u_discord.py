import os
import re

import discord

from .u_mongo import Mongo


class DiscordUtils():

    @staticmethod
    async def get_emoji(ctx):
        """
        Get custom emoji from server
        """
        record_server = await Mongo.get_record('server_settings', 'id', ctx.message.guild.id)
        emoji = record_server['emoji_name']
        return emoji

    @staticmethod
    async def get_user(bot, ctx, arg, nick=None):
        """
        Get user from DB on nickname
        0 - members
        1 - member_profiles
        """

        if nick is None:
            userID = ctx.message.author.id
            flag = False
        elif "@" in nick:
            userID = re.findall('\\d+', nick)[0]
            userID = int(userID)
            flag = False
        else:
            #* Search with nickname
            record = await Mongo.get_record_option("members", 'member_name', nick)
            i = 0
            res = ''
            name_list = []
            for document in record:
                category = document['member_name']
                if category in res:
                    pass
                else:
                    name_list.insert(i, category)
                    shop_list = [f"[{i}] - {category}\n"]
                    for parameters in shop_list:
                        res += ''.join(parameters)
                    i += 1

            if i == 0:
                return await ctx.send("Member is not find")

            res = f"```Py\nSelect a number [0, 1, 2, ...]:\n{res}```"

            await ctx.send(res)

            message = await bot.wait_for('message')
            if message:
                name = message.content
                if not name.isdigit():
                    return await ctx.send("Please using only numbers")
                flag = True
            
        if flag is True:
            if arg == 0:
                record = await Mongo.get_record('members','member_name', name_list[int(name)])
                member = discord.utils.get(ctx.message.guild.members, id=record['id'])
            else:
                record = await Mongo.get_record('member_profile','member_name', name_list[int(name)])
                member = discord.utils.get(ctx.message.guild.members, id=record['id'])                
        else:
            if arg == 0:
                record = await Mongo.get_record("members", 'id', userID)
                member = discord.utils.get(ctx.message.guild.members, id=userID)
            else:
                record = await Mongo.get_record("member_profile", 'id', userID)
                member = discord.utils.get(ctx.message.guild.members, id=userID)                

        return record, member