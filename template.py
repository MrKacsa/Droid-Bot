import discord
from discord.ext import commands

class Template(commands.Cog, name="template"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="update",
        description="This command is used to send update embeds.",
    )
    @commands.check_any(commands.is_owner(), commands.has_role(1124567806147559583))  # Replace the ID with the actual role ID
    async def update(
        self,
        ctx: commands.Context,
        title: str,
        description: str,
        color_hex: str,
        url: str = None,
        image: str = None,
        footer: str = None,
        channel: discord.TextChannel = None
    ):
        """
        This command is used to send update embeds.

        :param ctx: The application command context.
        :param title: The title of the embed.
        :param description: The description of the embed.
        :param color_hex: The color in HEX format (e.g., "#FF0000" for red).
        :param url: (Optional) URL for the title.
        :param image: (Optional) Image URL to be added in the embed.
        :param footer: (Optional) Footer text for the embed.
        :param channel: (Optional) The target channel where the embed will be sent.
        """
        # Convert color_hex to a valid Color object
        color = discord.Color(int(color_hex.replace("#", ""), 16))

        # Call the create_embed function to create and send the embed
        await self.create_embed(ctx, title, description, color, url, image, footer, channel)

    @commands.hybrid_command(
        name="edit_update",
        description="This command is used to edit existing update embeds sent by the bot. (Press role required)",
    )
    @commands.has_role(1124567806147559583)  # Replace the ID with the actual role ID
    async def edit_update(
        self,
        ctx: commands.Context,
        message_id: discord.Message,
        title: str = None,
        description: str = None,
        color_hex: str = None,
        url: str = None,
        image: str = None,
        footer: str = None,
    ):
        """
        This command is used to edit existing update embeds sent by the bot.

        :param ctx: The application command context.
        :param message_id: The message containing the embed to be edited.
        :param title: (Optional) The new title of the embed.
        :param description: (Optional) The new description of the embed.
        :param color_hex: (Optional) The new color in HEX format for the embed.
        :param url: (Optional) The new URL for the title.
        :param image: (Optional) The new image URL to be added in the embed.
        :param footer: (Optional) The new footer text for the embed.
        """
        try:
            message = await message_id.channel.fetch_message(message_id.id)
        except discord.NotFound:
            return await ctx.send("Message not found.")
        except discord.Forbidden:
            return await ctx.send("I don't have permission to fetch messages.")
        except discord.HTTPException:
            return await ctx.send("Failed to fetch the message.")

        if message.author.id != self.bot.user.id or not message.embeds:
            return await ctx.send("The provided message is not a bot-sent embed.")

        embed = message.embeds[0]

        # Update the embed with the new values if provided
        if title:
            embed.title = title
        if description:
            embed.description = description
        if color_hex:
            color = discord.Color(int(color_hex.replace("#", ""), 16))
            embed.color = color
        if url:
            embed.url = url
        if image:
            embed.set_image(url=image)
        if footer:
            embed.set_footer(text=footer)

        try:
            await message.edit(embed=embed)
            await ctx.send("Embed edited successfully!")
        except discord.Forbidden:
            await ctx.send("I don't have permission to edit messages.")
        except discord.HTTPException:
            await ctx.send("Failed to edit the embed.")

    async def create_embed(
        self,
        ctx: commands.Context,
        title: str,
        description: str,
        color: discord.Color,
        url: str = None,
        image: str = None,
        footer: str = None,
        channel: discord.TextChannel = None
    ):
        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )
        if url:
            embed.url = url
        if image:
            embed.set_image(url=image)
        if footer:
            embed.set_footer(text=footer)

        # If a specific channel is provided, send the embed to that channel.
        # Otherwise, send it to the channel where the command was invoked.
        target_channel = channel or ctx.channel
        await target_channel.send(embed=embed)

# The rest of the code remains the same...

# And then we finally add the cog to the bot so that it can load, unload, reload, and use its content.
async def setup(bot):
    await bot.add_cog(Template(bot))
  