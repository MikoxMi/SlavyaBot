import discord

from googletrans import Translator
from cogs.utils.u_mongo import Mongo
from discord.ext import commands


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        """
        Instructions after authorization
        """
        print("=============================")
        print("Authorization successful!")
        print("To the following servers:")
        for s in self.bot.guilds:
            print(f'- {s.name} {s.id}')

        # Get all members to check
        for s in self.bot.guilds:
            for member in s.members:
                userID = member.id
                check = await Mongo.get_record('members', 'id', userID)
                server_record = await Mongo.get_record('server_settings', 'id', s.id)
                member_profile = await Mongo.get_record('member_profile', 'id', userID)

                if check is None:
                    shop_record = await Mongo.get_record_more('shop', 'category', 'Waifu')
                    
                    gifts = []
                    gifts_count = []
                    inv = []
                    i = 0

                    if shop_record is not None:
                        for i, a in enumerate(shop_record):
                            item = a['item']
                            gifts.insert(i, item)
                            gifts_count.insert(i, 0)
                    else:
                        pass

                    upg_member = {
                        "id": int(member.id),
                        "member_name": f"{member}",
                        "money": 0,
                        "bank": 0,
                        "rep": 0,
                        "waifu": "None",
                        "waifu_like": "None",
                        "waifu_gifts": gifts,
                        "waifu_gifts_count": gifts_count,
                        "summary_money": 0,
                        "inventory": inv,
                    }
                    await Mongo.record_insert('members', upg_member)
                if member_profile is None:
                    upg_profile = {
                        "id": int(member.id),
                        "member_name": f"{member}",
                        "title": "None",
                        "name_field_1": "None",
                        "name_field_2": "None",
                        "name_field_3": "None",
                        "field_1": "None",
                        "field_2": "None",
                        "field_3": "None",
                        "description": "None",
                        "image": "None"
                    }
                    await Mongo.record_insert('member_profile', upg_profile)
                if server_record is None:
                    upg_server = {
                        "id": int(s.id),
                        "prefix":"=",
                        "emoji_name": "None",
                        "translator": 'en'
                    }
                    await Mongo.record_insert('server_settings', upg_server)

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        React bot on all member message
        """

        #*Check if bot
        if message.author.bot:
            return
        
        userID = message.author.id
        member_record = await Mongo.get_record('members', 'id', userID)

        member = discord.utils.get(message.guild.members, id=userID)

        document = member_record["member_name"]
        if document != member:
            upg_name = {
                "member_name": f"{member}"
            }
            await Mongo.update_record('members', member_record, upg_name)
        else:
            pass

        #* Add money on member message
        if len(message.content) > 10:
            if ":" in message.content or "<@" in message.content:
                pass
            else:
                money_message = int(member_record['money']) + 3
                obwak = int(member_record['summary_money']) + 3
                upg_money = {
                    "money": money_message,
                    "summary_money": obwak
                }
                await Mongo.update_record('members', member_record, upg_money)

        #* Translate other language to Server_language 
        #* Standard: English
        record_server = await Mongo.get_record('server_settings', 'id', message.guild.id)
        prefix = record_server['prefix']

        first_message = message.content

        translator = Translator()
        t = translator.translate(first_message, dest=record_server['translator'])

        check_origin = t.origin.replace(' ', '')
        check_text = t.text.replace(' ', '')

        if check_origin != check_text and prefix not in first_message:
            await message.delete()
            author_content = f'{message.author.mention} say:\n```diff\n- {t.text}```'
            await message.channel.send(author_content)
        else:
            pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Event for member join 
        """

        member_record = await Mongo.get_record('members', 'id', member.id)
        member_profile = await Mongo.get_record('member_profile', 'id', member.id)
        shop_record = await Mongo.get_record_more('shop', 'category', 'Waifu')
            

        # Add all gifts
        gifts = []
        gifts_count = []
        inv = []
        if shop_record is not None:
            for i, doc in enumerate(shop_record):
                item = doc['item']
                gifts.insert(i, item)
                gifts_count.insert(i, 0)
        else:
            pass

        if member_record is None:
            upg_member = {
                "id": "%s" % (member.id),
                "member_name": "%s" % (member),
                "money": 0,
                "bank": 0,
                "rep": 0,
                "waifu": "None",
                "waifu_like": "None",
                "waifu_gifts": gifts,
                "waifu_gifts_count": gifts_count,
                "summary_money": 0,
                "inventory": inv,
            }
            await Mongo.record_insert('members', upg_member)

        if member_profile is None:
            upg_profile = {
                "id": int(member.id),
                "member_name": f"{member}",
                "title": "None",
                "name_field_1": "None",
                "name_field_2": "None",
                "name_field_3": "None",
                "field_1": "None",
                "field_2": "None",
                "field_3": "None",
                "description": "None",
                "image": "None"
            }
            await Mongo.record_insert('member_profile', upg_profile)

    @commands.Cog.listener()    
    async def on_member_remove(self, member):
        """
        Delete record User
        """
        await Mongo.delete_record('members', 'id', member.id)
        await Mongo.delete_record('members', 'id', member.id)


def setup(bot):
    bot.add_cog(Events(bot))