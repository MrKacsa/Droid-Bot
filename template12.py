import discord
from discord.ext import commands
import datetime
import pytz
import requests

class template12(commands.Cog, name="template12"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="nextevents",
        description="Displays information about the upcoming growtopia events."
    )
    async def next_events(self, ctx):
        url = "https://gt.tommyhub.com/api/game/info"
        response = requests.get(url)
        data = response.json()

        eastern = pytz.timezone(data['time']['timezone'])
        current_time = datetime.datetime.now(tz=eastern)

        user = ctx.author  # Get the user who requested the command

        user_pfp = user.avatar.url if user.avatar else discord.Embed.Empty  # Get the user's avatar URL or use Empty if no custom avatar

        embed = discord.Embed(
            title="<:CrazyJim:1172589067687448758> Upcoming Events",
            color=discord.Color.from_rgb(50, 205, 50)  # Lime Green color
        )

        for event in data['event']:
            event_name = event['name']
            start_time = datetime.datetime.fromtimestamp(event['startTime'], tz=eastern)
            end_time = datetime.datetime.fromtimestamp(event['endTime'], tz=eastern)

            emoji = ""
            if "Daily Challenge" in event_name:
                emoji = "<:ChallengeBoard:1171880017786056864>"
            elif "Night of the Comet" in event_name:
                emoji = "<:CometDust:1171879785912336465>"
            elif "The Grand Tournament" in event_name:
                emoji = "<:MasterPeng:1171880496926576740>"

            if current_time < start_time:
                time_until_start = start_time - current_time
                start_days = time_until_start.days
                start_hours, start_remainder = divmod(time_until_start.seconds, 3600)
                start_minutes, _ = divmod(start_remainder, 60)

                embed.add_field(
                    name=f"{emoji} **{event_name} Event**",
                    value=f"Starts in: **{start_days} day{'s' if start_days != 1 else ''}**, "
                          f"**{start_hours} hour{'s' if start_hours != 1 else ''}**, and **{start_minutes} minute{'s' if start_minutes != 1 else ''}**.\n"
                          f"Ends in: <t:{int(end_time.timestamp())}:R>",
                    inline=False
                )
            else:
                time_elapsed = current_time - start_time
                elapsed_days = time_elapsed.days
                elapsed_hours, elapsed_remainder = divmod(time_elapsed.seconds, 3600)
                elapsed_minutes, _ = divmod(elapsed_remainder, 60)

                embed.add_field(
                    name=f"{emoji} **{event_name} Event**",
                    value=f"Already started: <t:{int(start_time.timestamp())}:R>\n"
                          f"Ends in: <t:{int(end_time.timestamp())}:R>",
                    inline=False
                )

        # Add "Requested By" and user's profile picture in the footer
        embed.set_footer(
            text=f"Requested By {user.name} | Today at {current_time.strftime('%I:%M %p')}",
            icon_url=user_pfp
        )

        await ctx.send(embed=embed)

# Add this cog to your bot
async def setup(bot):
    await bot.add_cog(template12(bot))
