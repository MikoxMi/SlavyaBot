import os
import asyncio
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

from .utils.u_mongo import Mongo
from .utils.u_discord import DiscordUtils


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(pass_context=True)
    async def shop(self, ctx, category=None, page=None):
        """Check categories in shop
        
        -shop <category> <page>"""

        emoji_money = await DiscordUtils.get_emoji(ctx)
        record = await Mongo.get_record_sort('shop', 'price', 1)
        if category is None:
            res = ''
            name = []
            num_cat = []

            index = 0
            for document in record:
                category = document['category']
                if category in res:
                    pass
                else:
                    name.insert(index, category)
                    num_cat.insert(index, index)
                    shop_list = [f"[{index}] - {category}\n"]
                    for parameters in shop_list:
                        res += ''.join(parameters)
                    index += 1
            
            res_new = f"```Py\nSelect number category [0, 1, 2, ...]:\n{res}```"
            await ctx.send(res_new)


            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            if msg:
                _id = msg.content
                if int(_id) not in num_cat:
                    await ctx.send("Incorect write category ID")
                    return

                if not _id.isdigit():
                    await ctx.send("Use only numbers")
                    return
            category = name[int(_id)]
        else:
            pass    

        if page is None:
            page = 1
            std_min = 0
            std_max = 5
        else:
            std_max = 5
            std_max *= int(page)
            std_min = std_max - 5

        res_item_z = ''
        k = 0
        record_items = await Mongo.get_record_sort('shop', 'price', 1)

        for document in record_items:
            if category == document['category']:
                k += 1
                if k > std_min and k < std_max:
                    desc = ''
                    item_name = document['item']
                    price = document['price']
                    description = document['description']
                    emoji_decor = document['emoji']
                    income = document['income']
                    for description_list in description:
                        desc += ''.join(description_list)
                    if emoji_decor == "None":   
                        item_list = [f"{item_name} - {price}{emoji_money}\nIncome:{income}\n{desc}\n\n"]
                    else:
                        emoji_id = document['emoji_id']
                        server = discord.utils.get(self.bot.guilds, id=emoji_id)
                        emoji_get = discord.utils.get(server.emojis, name=emoji_decor)
                        item_list = [f"{emoji_get} {item_name} - {price} {emoji_money}\nIncome:{income}\n{desc}\n\n"]
                    for item_list_add in item_list:
                        res_item_z += ''.join(item_list_add)
                else:
                    pass

        pages = (k // 5) + 1
        if int(page) > pages:
            await ctx.send('Incorect page')
            return

        res_item = f"{res_item_z}"
        em = discord.Embed(colour=ctx.message.author.colour)
        em.add_field(name=f"**Category: {category}**\nBuy item: ```-buy <item>```", value=F"**{res_item}**")
        em.set_footer(text=F"Page: {page}/{pages}")
        msg = await ctx.send(embed=em)


    @commands.command(pass_context=True)
    async def buy(self, ctx, *, item):
        """
        Buy item
        -buy <item>
        """
        userID = ctx.message.author.id
        record_check = await Mongo.get_record_sort('shop', 'price', 1)

        for document in record_check:
            doc = document['item']
            if doc == item:
                status = True
            else:
                pass

        if not status:
            await ctx.send("This item has not found")
            return

        money_record = await Mongo.get_record('members', 'id', userID)
        shop_record = await Mongo.get_record('shop', 'item', item)

        category = shop_record['category']

        if category == "Waifu":
            await ctx.send("This item can only be gifted to waifu:\n`-waifu gift @member gift`")
            return

        if category == "Undefined":
            await ctx.send("This item is inactive and cannot be purchased.")
            return

        money = money_record['money']
        
        price = shop_record['price']
        item_z = shop_record['item']
        role_check = shop_record['role']
        emoji = shop_record['emoji']
        image = shop_record['image']
        income = shop_record['income']


        if int(money) < int(price):
            await ctx.send("You don't enough money")
            return

        #* Buying
        if role_check == "True":
            role = discord.utils.get(ctx.guild.roles, name = item_z)
            networth = int(money) - int(price)
            upg = {
                "money":networth
            }
            await ctx.author.add_roles(role)
            await Mongo.update_record('members', money_record, upg)

            if emoji == "None":
                desc = F"{ctx.message.author.mention} successful purchase of an item: **{item_z}**\nIncome:{income}\nIf the role has not been issued, contact your server admin"
                e = discord.Embed(colour=ctx.message.author.colour, description=desc)
            else:
                emoji_id = shop_record['emoji_id']
                server = discord.utils.get(self.bot.guilds, id=emoji_id)
                emoji_get = discord.utils.get(server.emojis, name=emoji)
                desc = F"{ctx.message.author.mention} successful purchase of an item: **{item_z}{emoji_get}**\nIncome:{income}\nIf the role has not been issued, contact your server admin"
                e = discord.Embed(colour=ctx.message.author.colour, description=desc)
            e.set_author(name="Shop system:")
            if image == "None":
                pass
            else:
                e.set_image(url=image)
            await ctx.send(embed=e)
        else:
            networth = int(money) - int(price)
            upg = {
                "money":networth
            }
            await Mongo.update_record('members', money_record, upg)

            if emoji == "None":
                desc = F"{ctx.message.author.mention} successful purchase of an item: **{item_z}**\nIncome:{income}\nThis item has not a role"
                e = discord.Embed(colour=ctx.message.author.colour, description=desc)
            else:
                emoji_id = shop_record['emoji_id']
                server = discord.utils.get(self.bot.guilds, id=emoji_id)
                emoji_get = discord.utils.get(server.emojis, name=emoji)
                desc = F"{ctx.message.author.mention} successful purchase of an item: **{item_z}{emoji}**\nIncome:{income}\nThis item has not a role"
                e = discord.Embed(colour=ctx.message.author.colour, description=desc)
            e.set_author(name="Shop system:")
            if image == "None":
                pass
            else:
                e.set_image(url=image)
            await ctx.send(embed=e)


        if category == "Items":
            inv = money_record['inventory']
            inv.insert(0, item_z)
            
            upg_inv = {
                "inventory":inv
            }
            await Mongo.update_record('members', money_record, upg_inv)


    
    @commands.command(pass_context=True)
    @has_permissions(administrator=True)
    async def add_item(self, ctx, *, item):
        """
        Add item [Administrator]
        -add_item <name>
        """
        record = await Mongo.get_record('shop', 'item', item)

        if record is None: 
            upg = {
    		    "category":"Undefined",
    		    "item":item,
			    "price":"None",
                "description":"None",
                "role":"None",
                "income":"None",
                "emoji":"None",
                "emoji_id":"None",
                "image":"None"
			}
            await Mongo.record_insert('shop', upg)
            await ctx.send("Item has been add to shop!")
        else:
            await ctx.send("This item has exist")



    @commands.command(pass_context=True, aliases=['del'])
    @has_permissions(administrator=True)
    async def delete(self, ctx, *, item):
        """
        Delete item from shop [Administrator]
        -[del, delete] <item_name>
        """

        record = Mongo.get_record('shop', 'item', item)

        if record is None:
            return await ctx.send("There is no such item.")
        
        await ctx.send(f"Delete item: {item} :ballot_box_with_check:")

        if record['category'] == "Waifu":
            record_member = await Mongo.get_record('members', 'id', ctx.message.author.id)
            inventory = record_member['waifu_gifts']
            inventory_count = record_member['waifu_gifts_count']
            for i, count in enumerate(inventory):
                if count == item:
                    del inventory[i]
                    del inventory_count[i]

            upg = {
                "waifu_gifts":inventory,
                "waifu_gifts_count":inventory_count
            }
            await Mongo.update_all('members', upg)

        if record['category'] == "Items":
            record_member = await Mongo.get_record('members', 'id', ctx.message.author.id)
            inventory = record_member['inventory']
            for i, count in enumerate(inventory):
                if count == item:
                    del inventory[i]

            upg = {
                "inventory": inventory
            }
            await Mongo.update_all('members', upg)
        
        if record['role'] == 'True':
            role = discord.utils.get(ctx.message.author.guild.roles, name=record['item'])
            await ctx.guild.delete_role(role)

        await Mongo.delete_record('shop', 'item', item)

    @commands.group(pass_context=True)
    @has_permissions(administrator=True)
    async def edit(self, ctx):
        """Edit item in shop [Administrator]
        
        "item_name" - Item name in shop

        Commands:
        -edit - Show sub_commands

        -edit view <name> - Information about item

        -edit category <item_name> <category> - Change item category

        -edit all_category <category> <new_category> - Change category for all items in <category>

        -edit name <item_name> <new_name> - Change name item

        -edit price <item_name> <price> - Change price item

        -edit description <item_name> <description> - Change description item

        -edit role <item_name> <True|False> - Change to give this item Role

        -edit income <item_name> <Number|None> - Change will Incom give this item

        -edit emoji <item_name> <emoji_name> - Change Emoji this item

        -edit image <item_name> <url_img> - Add image and the conclusion after buying
        """

        if ctx.invoked_subcommand is None:
            msg = ctx.command.help
            em = discord.Embed(colour=ctx.message.author.colour)
            em.add_field(name="Command Helper", value=F"{msg}")
            await ctx.send(embed=em)
            return
        
    @edit.command(pass_context=True)
    @has_permissions(administrator=True)
    async def view(self, ctx, *, name=None):
        """
        Information about item [Administrator]
        -edit view <name>
        """

        record = await Mongo.get_record('shop', 'item', name)
        if record is None:
            await ctx.send("This item does not exist to create an item use:\n`shop add_item <name>`")
        e = discord.Embed(colour=ctx.message.author.colour, description="Change item:\nTo change the subject, use Subcomandante typing: `edit`")
        e.add_field(name="Category:", value=record['category'], inline=False)
        e.add_field(name="Name:", value=record['item'], inline=False)
        e.add_field(name="Price:", value=record['price'], inline=False)
        e.add_field(name="Description:", value=record['description'], inline=False)
        e.add_field(name="Role:", value=record['role'], inline=False)
        e.add_field(name="Emoji:", value=record['emoji'], inline=False)
        e.add_field(name="Income:", value=record['income'], inline=False)
        if record['image'] == "None":
            e.add_field(name="Image on purchase:", value=record['image'], inline=False)
        else:
            e.set_image(url=record['image'])
        await ctx.send(embed=e)
        return


    @edit.command(pass_context=True)
    @has_permissions(administrator=True)
    async def category(self, ctx, name, *, category):
        """
        Change item category [Administrator]
        -edit category <name_item> <category>
        """

        record = await Mongo.get_record('shop', 'item', name)
        if record is None:
            return await ctx.send("This item does not exist to create it:\n`shop add_item name`")

        updates = {
            "category":category
        }
        await Mongo.update_record('shop', record, updates)
        await ctx.send(F"Item {name} has been updated. Assigned category: {category}")

        if category == "Waifu":
            record_waifu = await Mongo.get_record('members', 'id', ctx.message.author.id)
            waifu_gifts = record_waifu['waifu_gifts']
            waifu_gifts_count = record_waifu['waifu_gifts_count']
            index = len(waifu_gifts)
            waifu_gifts.insert(index, name)
            waifu_gifts_count.insert(index, 0)
            upg = {
                "waifu_gifts":waifu_gifts,
                "waifu_gifts_count":waifu_gifts_count
            }
            await Mongo.update_all('members', upg)

    @edit.command(pass_context=True)
    @has_permissions(administrator=True)
    async def all_category(self, ctx, category, *, new_category):
        """
        Change all items category [Administrator]
        -edit category <category> <new_category>
        """
        check = await Mongo.get_record('shop', 'category', category)
        if check is None:
            await ctx.send("Category is not found")
            return

        record = await Mongo.get_record_find('shop')
        for doc in record:
            if doc['category'] == category:
                upg = {
                    "category":new_category
                }
                await Mongo.update_record('shop', doc, upg)
        await ctx.send(F"All items in category change from the `{category}` to the `{new_category}``")
    
    @edit.command(pass_context=True)
    @has_permissions(administrator=True)
    async def name(self, ctx, name, *, new_name):
        """
        Change item name [Administrator]
        -edit name <name> <new_item_name>
        """
        record = await Mongo.get_record('shop', 'item', name)

        if record is None:
            return await ctx.send("This item does not exist to create it:\n`-shop add_item name`")

        if record['role'] == "None":
            pass
        else:
            role = discord.utils.get(ctx.guild.roles, name=name)
            await role.edit(name=new_name)

        record_member = await Mongo.get_record_find('members')
        for doc in record_member:
            inv = doc['inventory']
            if name in inv:
                inv.remove(name)
                inv.insert(0, new_name)
                upg_member = {
                    "inventory": inv
                }
                await Mongo.update_record('members', doc, upg_member)
            else:
                pass

        updates = {
            "item":new_name
        }
        await Mongo.update_record('shop', record, updates)
        await ctx.send(F"Item {name} has been updated:\nChange name on: {new_name}")
    
    @edit.command(pass_context=True)
    @has_permissions(administrator=True)
    async def price(self, ctx, name, price):
        """
        Change price item [Administrator]
        -edit price "item_name" <price>
        """
        record = await Mongo.get_record('shop', 'item', name)
        if record is None:
            await ctx.send("This item does not exist to create it:\n`-shop add_item name`")

        if not price.isdigit():
            await ctx.send("Use only numbers")
            return

        if len(price) > 9:
            await ctx.send("Too much amount to change, no more than 9 characters")
            return

        upg = {
            "price":int(price)
        }
        await Mongo.update_record('shop', record, upg)
        await ctx.send(F"Item {name} has been updated. New price: {price}")

    @edit.command(pass_context=True)
    @has_permissions(administrator=True)
    async def description(self, ctx, name, *, description):
        """
        Change item description
        -edit description <item_name> <description>
        """

        record = await Mongo.get_record('shop', 'item', name)
        if record is None:
            await ctx.send("This item does not exist to create it:\n`-shop add_item name`")
            return

        upg = {
            "description":description
        }
        await Mongo.update_record('shop', record, upg)
        await ctx.send(F"Description item: {name} has been updated")

    @edit.command(pass_context=True)
    @has_permissions(administrator=True)
    async def role(self, ctx, name, check):
        """
        Change item This Role or Not
        -edit role <name> <True|False>
        """

        record = await Mongo.get_record('shop', 'item', name)
        if record is None:
            await ctx.send("This item does not exist to create it:\n`-shop add_item name`")
            return
        
        if record['category'] == "Waifu":
            await ctx.send("You cannot change the role for this item because it belongs to waifu_shop")
            return
        
        if check == record['role']:
            await ctx.send("This value is already written")
            return
        

        if check == "True":
            role = discord.utils.get(ctx.message.author.guild.roles, name=name)
            if role is None:
                await ctx.send("This role does not exist, do you want to create it? `Y` or `N`")

                message = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

                if message.content == "Y":
                    await ctx.guild.create_role(name=name, permissions=discord.Permissions(permissions=0))
                    await ctx.send(F"Role has been created\nNow {name} will be issued upon purchase")
                    upg = {
                        "role":"True"
                    }
                    await Mongo.update_record('shop', record, upg)
                    return
                elif message.content == "N":
                    await ctx.send("Role has not create")
                    return
                else:
                    await ctx.send("Role has not create")
                    return
            else:
                upg = {
                    "role":"True"
                }
                await Mongo.update_record('shop', record, upg)
                await ctx.send(F"Now {name} will be issued upon purchase")
        elif check == "False":
            updates = {
                "role":"False"
            }
            role = discord.utils.get(ctx.message.guild.roles, name=name)
            if role is None:
                pass
            else:
                await ctx.guild.delete_role(role)
                await ctx.send("Role has been deleted")

            await Mongo.update_record('shop', record, updates)
            await ctx.send(F"Role {name} not will be issued")
        else:
            return await ctx.send("Incorect values, enter `True` | `False`")
            
    
    @edit.command(pass_context=True)
    @has_permissions(administrator=True)
    async def income(self, ctx, name, income):
        """
        Change Income
        -edit income <name> <Number|None>
        """
        record = await Mongo.get_record('shop', 'item', name)
        
        if record is None:
            await ctx.send("This item does not exist to create it:\n`-shop add_item name`")
            return

        if record['category'] == "Waifu":
            await ctx.send("You cannot change Income for this subject, as it belongs waifu_shop")

        if income == "None":
            upg = {
                "income":income
            }
            await Mongo.update_record('shop', record, upg)
            await ctx.send(F"Item {name} has been updated: Change Income to: {income}")
            return


        if not income.isdigit():
            await ctx.send("Use only numbers")
            return

        if len(income) > 9:
            await ctx.send("Too much amount to change, no more than 9 characters")
            return

        upg = {
            "income":income
        }
        await Mongo.update_record('shop', record, upg)
        await ctx.send(F"Item {name} has been updated: Change Income to: {income}")
    
    @edit.command(pass_context=True)
    @has_permissions(administrator=True)
    async def emoji(self, ctx, name, emoji):
        """
        Change emoji for item
        -edit emoji <name> <emoji_name>
        """
        
        record = await Mongo.get_record('shop', 'item', name)
        if record is None:
            await ctx.send("This item does not exist to create it:\n`-shop add_item name`")
            return
        
        await ctx.send("Where do you want to use emoji from?\nBot server: `Y`. This server: `N`")
        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if msg.content == "Y":
            server = discord.utils.get(self.bot.guilds, id=282597833536831491)
            emoji_d = discord.utils.get(server.emojis, name=emoji)
            if emoji_d is None:
                return await ctx.send("Emoji has not exist")
            updates = {
                "emoji":emoji,
                "emoji_id":server.id
            }
            await Mongo.update_record('shop', record, updates)
            await ctx.send(F"Emoji for item: {name} updated: {emoji_d}")
            return

        elif msg.content == "N":
            emoji_d = discord.utils.get(ctx.guild.emojis, name=emoji)
            if emoji_d is None:
                return await ctx.send("Emoji has not exist")
            updates = {
                "emoji":emoji,
                "emoji_id":ctx.message.guild.id
            }
            await Mongo.update_record('shop', record, updates)
            await ctx.send(F"Emoji for item: {name} updated: {emoji_d}")
            return
        else:
            await ctx.send(F"{ctx.message.author.mention} action rejected")
            return

    @edit.command(pass_context=True)
    @has_permissions(administrator=True)
    async def image(self, ctx, name, url):
        """
        Changing the image when buying
        -edit image <name> <url>
        """
        record = await Mongo.get_record('shop', 'item', name)
        if record is None:
            await ctx.send("This item does not exist to create it:\n`-shop add_item name`")
            return
        
        updates = {
            "image":url
        }
        await Mongo.update_record('shop', record, updates)
        await ctx.send(F"Image has been add to:{name}")

        
def setup(bot):
	bot.add_cog(Shop(bot))	
