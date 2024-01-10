from discord.ext import commands
import json
import asyncio
import requests
import discord



class template13(commands.Cog, name="template13"):
    def __init__(self, bot):
        self.bot = bot
        self.db_channel_id = 1144242100788023306  

        # Load bot owners from config.json
        with open("config.json", "r") as config_file:
            config_data = json.load(config_file)
            self.owners = config_data["owners"]

        # Initialize an empty set to store permitted user IDs
        self.permitted_users = set()

    def _get_db_channel(self):
        return self.bot.get_channel(self.db_channel_id)

    async def _get_db_messages(self):
        db_channel = self._get_db_channel()
        messages = []
        async for message in db_channel.history(limit=None):
            try:
                content_json = json.loads(message.content)
                if "emoji_url" in content_json and "name" in content_json:  # Filter out incomplete messages
                    messages.append(content_json)
            except json.JSONDecodeError:
                pass
        return messages

    async def _add_db_message(self, content):
        db_channel = self._get_db_channel()
        content_json = json.dumps(content)
        await db_channel.send(content_json)

    def _has_permission(self, user_id):
        return user_id in self.owners

    @commands.hybrid_command(
        name="permit-growmoji-access",
        description="Allow a user to use /add-growmoji"
    )
    async def permit_growmoji_access(self, ctx, user: discord.User):
        if not self._has_permission(ctx.author.id):
            return await ctx.send("You do not have permission to use this command.")

        # Add the user's ID to the set of permitted users
        self.permitted_users.add(user.id)
        await ctx.send(f"{user.mention} has been granted access to use /add-growmoji.")


    @commands.hybrid_command(name="add-growmoji", description="Add a growmoji to the database.")
    async def add_growmoji(self, ctx, emoji: discord.Emoji, name: str, credits: str):
        # Check if the user is permitted
        if ctx.author.id not in self.permitted_users:
            return await ctx.send("You do not have permission to use this command.")

        emoji_info = {
            "emoji_url": str(emoji.url),  # Save the emoji URL
            "name": name,
            "author": str(ctx.author.id),
            "credits": credits,
            "sprite": str(emoji)
        }
        await self._add_db_message(emoji_info)

        # Send the emoji as a message and provide a clickable link to its external image
        message = await ctx.send(f"Growmoji '{emoji.name}' added to the database.\n"
                                 f"Sprite: {emoji}\n"
                                 f"External link: [Click Here]({emoji.url})")
        await message.add_reaction(emoji)

    @commands.hybrid_command(name="list-growmojis", description="List all growmojis in the database.")
    async def list_growmojis(self, ctx):
        allowed_channel = self._get_db_channel()
        if allowed_channel:
            messages = await self._get_db_messages()
            if messages:
                emojis_per_page = 9
                total_pages = (len(messages) + emojis_per_page - 1) // emojis_per_page
                current_page = 1

                while current_page <= total_pages:
                    embed = discord.Embed(title=f"List of Growmojis (Page {current_page}/{total_pages})", color=discord.Color.blue())
                    for i in range(current_page * emojis_per_page - emojis_per_page, current_page * emojis_per_page):
                        if i < len(messages):
                            emoji_info = messages[i]
                            emoji_url = emoji_info.get("emoji_url", None)
                            name = emoji_info.get("name", "Unknown")
                            author = emoji_info.get("author", "Unknown")
                            credits = emoji_info.get("credits", "Unknown")
                            sprite = emoji_info.get("sprite", "❓")

                            embed.add_field(
                                name=f"Growmoji {i + 1}",
                                value=f"Name: {name}\n"
                                      f"Sprite: {sprite}\n"
                                      f"Unavailable? [Click here.]({emoji_url})\nUploaded By: <@{author}>\nCredits: {credits}",
                                inline=False
                            )

                    message = await ctx.send(embed=embed)

                    if total_pages > 1:
                        await message.add_reaction("⬅️")
                        await message.add_reaction("➡️")

                    def check(reaction, user):
                        return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️"]

                    try:
                        reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                        if str(reaction.emoji) == "⬅️" and current_page > 1:
                            current_page -= 1
                            await message.delete()
                        elif str(reaction.emoji) == "➡️" and current_page < total_pages:
                            current_page += 1
                            await message.delete()
                    except asyncio.TimeoutError:
                        break

            else:
                await ctx.send("No growmojis found in the database.")
        else:
            await ctx.send("Database channel not found.")

    @commands.hybrid_command(name="fork-growmoji", description="Add a growmoji to your server emojis list.")
    async def fork_growmoji(self, ctx, emoji_url: str, name: str):
        try:
            response = requests.get(emoji_url)
            response.raise_for_status()
            emoji_data = response.content
        except requests.RequestException as e:
            return await ctx.send(f"Failed to fetch emoji data from the given URL. Error: {e}")

        try:
            await ctx.guild.create_custom_emoji(name=name, image=emoji_data, roles=[], reason=f"Added by {ctx.author}")
            await ctx.send(f"Growmoji {name} has been added to the server's emojis list!")
        except discord.HTTPException as e:
            await ctx.send(f"Failed to add growmoji to the server. Error: {e}")

async def setup(bot):
    with open("config.json", "r") as config_file:
        config_data = json.load(config_file)
        owners = config_data["owners"]
    await bot.add_cog(template13(bot))

# Assuming the rest of your bot setup 
