"""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.5.0
"""
import platform
import random
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from discord.ui import Button, View
from datetime import timezone

import psutil  # For CPU and memory usage
from datetime import datetime, timedelta 

from helpers import checks


class General(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot
        self.version = "5.5.0"  # Default version, replace with actual version
        self.first_start_time = datetime.utcnow().replace(tzinfo=timezone.utc)



    @commands.Cog.listener()
    async def on_ready(self):
          print(f"Logged in as {self.bot.user.name}")

    @commands.Cog.listener()
    async def on_button_click(self, interaction):
          # Handle button click here
          if interaction.component.label == "Say Hi":
              await interaction.respond(type=6)  # Acknowledge the button click
              await interaction.followup.send("Hi!")

  

    @commands.hybrid_command(
        name="help", description="List all commands the bot has loaded."
    )
    @checks.not_blacklisted()
    async def help(self, context: Context) -> None:
        prefix = self.bot.config["prefix"]
        embed = discord.Embed(
            title="Help", description="List of available commands:", color=0x9C84EF
        )

        for cog_name, cog in self.bot.cogs.items():
            if cog:
                commands = cog.get_commands()
                data = []
                for command in commands:
                    description = command.description.partition("\n")[0]
                    data.append(f"{prefix}{command.name} - {description}")
                help_text = "\n".join(data)
                embed.add_field(
                    name=cog_name.capitalize(), value=f"```{help_text}```", inline=False
                )

        await context.send(embed=embed)

    @commands.hybrid_command(
        name="botinfo",
        description="Get some useful (or not) information about the bot.",
        category="General"
    )
    @checks.not_blacklisted()
    async def botinfo(self, context: commands.Context) -> None:
        """
        Get some useful (or not) information about the bot.

        :param context: The hybrid command context.
        """
        # Calculate uptime
        uptime = datetime.utcnow().replace(tzinfo=timezone.utc) - self.first_start_time
        uptime_str = self.format_timedelta(uptime)

        # Get server and member counts
        servers_count = len(self.bot.guilds)
        members_count = sum(guild.member_count for guild in self.bot.guilds)

        # Create the embed
        embed = discord.Embed(
            title="Bot Information",
            description="An Advanced Growtopia Bot | [Support Server](https://discord.gg/TaDAdQCa) ",
            color=0xFFEF00,
        )
        embed.set_author(name="Droid-Pet:")
        embed.add_field(name="Bot Developers:", value="Lalushi and Boteto", inline=False)
        embed.add_field(name="Servers Count:", value=servers_count, inline=False)
        embed.add_field(name="Members:", value=members_count, inline=False)
        embed.add_field(name="Latest Restart:", value=self.format_datetime(self.first_start_time), inline=False)
        embed.add_field(name="Bot Uptime:", value=uptime_str, inline=False)
        embed.add_field(name="Version:", value=self.version, inline=False)
        embed.set_footer(text=f"Requested by {context.author} | {self.get_full_timestamp()}")

        # Send the embed and save the message ID
        message = await context.send(embed=embed)
        self.bot.botinfo_message_id = message.id

    def format_timedelta(self, duration):
        days, seconds = duration.days, duration.seconds
        years, days = days // 365, days % 365
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{years} years, {days} days, {hours} hours, {minutes} minutes, {seconds} seconds"

    def format_datetime(self, dt):
        # Format datetime to Discord-friendly string with auto time zone
        return f"<t:{int(dt.timestamp())}>"

    def get_full_timestamp(self):
        # Format current datetime with year, month, day, hour, minute, second
        return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

    @commands.hybrid_command(
        name="serverinfo",
        description="Get some useful (or not) information about the server.",
    )
    @checks.not_blacklisted()
    async def serverinfo(self, context: Context) -> None:
        """
        Get some useful (or not) information about the server.

        :param context: The hybrid command context.
        """
        roles = [role.name for role in context.guild.roles]
        if len(roles) > 50:
            roles = roles[:50]
            roles.append(f">>>> Displaying[50/{len(roles)}] Roles")
        roles = ", ".join(roles)

        embed = discord.Embed(
            title="**Server Name:**", description=f"{context.guild}", color=0x9C84EF
        )
        if context.guild.icon is not None:
            embed.set_thumbnail(url=context.guild.icon.url)
        embed.add_field(name="Server ID", value=context.guild.id)
        embed.add_field(name="Member Count", value=context.guild.member_count)
        embed.add_field(
            name="Text/Voice Channels", value=f"{len(context.guild.channels)}"
        )
        embed.add_field(name=f"Roles ({len(context.guild.roles)})", value=roles)
        embed.set_footer(text=f"Created at: {context.guild.created_at}")
        await context.send(embed=embed)
      
    @commands.hybrid_command(
                    name="ping",
                    description="Check if the bot is alive.",
                )
    @checks.not_blacklisted()
    async def ping(self, context: commands.Context) -> None:
                    """
                    Check if the bot is alive.

                    :param context: The hybrid command context.
                    """
                    embed = discord.Embed(
                        title="🏓 Pong!",
                        description=f"The bot latency is {round(self.bot.latency * 1000)}ms.",
                        color=0x9C84EF,
                    )

                    # Add a button to the message
                    button = Button(style=discord.ButtonStyle.primary, label="Say Hi")
                    view = View()
                    view.add_item(button)

                    # Send the embed with the button
                    message = await context.send(embed=embed, view=view)

                    # Wait for button click event
                    try:
                        interaction = await self.bot.wait_for("button_click", check=lambda i: i.component.label == "Say Hi" and i.message.id == message.id, timeout=30.0)
                        await interaction.respond(type=6)  # Acknowledge the button click

                        # Send a response when the button is clicked
                        await context.send("Hi!")
                    except Exception as e:
                        print(f"Button interaction failed: {e}")


    @commands.hybrid_command(
        name="invite",
        description="Get the invite link of the bot to be able to invite it.",
    )
    @checks.not_blacklisted()
    async def invite(self, context: Context) -> None:
        """
        Get the invite link of the bot to be able to invite it.

        :param context: The hybrid command context.
        """
        embed = discord.Embed(
            description=f"Invite me by clicking [here](https://discordapp.com/oauth2/authorize?&client_id={self.bot.config['application_id']}&scope=bot+applications.commands&permissions={self.bot.config['permissions']}).",
            color=0xD75BF4,
        )
        try:
            # To know what permissions to give to your bot, please see here: https://discordapi.com/permissions.html and remember to not give Administrator permissions.
            await context.author.send(embed=embed)
            await context.send("I sent you a private message!")
        except discord.Forbidden:
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="server",
        description="Get the invite link of the discord server of the bot for some support.",
    )
    @checks.not_blacklisted()
    async def server(self, context: Context) -> None:
        """
        Get the invite link of the discord server of the bot for some support.

        :param context: The hybrid command context.
        """
        embed = discord.Embed(
            description=f"Join the support server for the bot by clicking [here](https://discord.gg/UEmpX48D52).",
            color=0xD75BF4,
        )
        try:
            await context.author.send(embed=embed)
            await context.send("I sent you a private message!")
        except discord.Forbidden:
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="8ball",
        description="Ask any question to the bot.",
    )
    @checks.not_blacklisted()
    @app_commands.describe(question="The question you want to ask.")
    async def eight_ball(self, context: Context, *, question: str) -> None:
        """
        Ask any question to the bot.

        :param context: The hybrid command context.
        :param question: The question that should be asked by the user.
        """
        answers = [
            "It is certain.",
            "It is decidedly so.",
            "You may rely on it.",
            "Without a doubt.",
            "Yes - definitely.",
            "As I see, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again later.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
        ]
        embed = discord.Embed(
            title="**My Answer:**",
            description=f"{random.choice(answers)}",
            color=0x9C84EF,
        )
        embed.set_footer(text=f"The question was: {question}")
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="bitcoin",
        description="Get the current price of bitcoin.",
    )
    @checks.not_blacklisted()
    async def bitcoin(self, context: Context) -> None:
        """
        Get the current price of bitcoin.

        :param context: The hybrid command context.
        """
        # This will prevent your bot from stopping everything when doing a web request - see: https://discordpy.readthedocs.io/en/stable/faq.html#how-do-i-make-a-web-request
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.coindesk.com/v1/bpi/currentprice/BTC.json"
            ) as request:
                if request.status == 200:
                    data = await request.json(
                        content_type="application/javascript"
                    )  # For some reason the returned content is of type JavaScript
                    embed = discord.Embed(
                        title="Bitcoin price",
                        description=f"The current price is {data['bpi']['USD']['rate']} :dollar:",
                        color=0x9C84EF,
                    )
                else:
                    embed = discord.Embed(
                        title="Error!",
                        description="There is something wrong with the API, please try again later",
                        color=0xE02B2B,
                    )
                await context.send(embed=embed)


async def setup(bot):
    await bot.add_cog(General(bot))
