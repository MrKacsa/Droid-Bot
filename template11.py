import datetime
import discord
from discord.ext import commands
import requests

class GrowtopiaStatusCog(commands.Cog, name="growtopia_status"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="growtopia_status", description="Get Growtopia server status.")
    async def growtopia_status(self, ctx: commands.Context):
        try:
            status = self.get_server_status()
            embed = self.create_status_embed(status)
            await ctx.send(embed=embed)
        except requests.exceptions.RequestException as error:
            await ctx.send(f"Error: {error}")

    def get_server_status(self):
        growtopia_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-5)))  # America/New_York timezone

        try:
            res = requests.get("https://www.growtopiagame.com/detail").json()
            player_count = int(res["online_user"])
            wotd_url = res["world_day_images"]["full_size"]
            wotd_name = wotd_url[wotd_url.rfind("/") + 1:wotd_url.rfind(".")].upper()

            return {
                "date": growtopia_time.strftime("%b %d"),
                "time": growtopia_time.strftime("%I:%M:%S"),
                "player_count": player_count,
                "wotd_name": wotd_name,
                "wotd_url": wotd_url,
            }

        except requests.exceptions.RequestException as error:
            raise error

    def create_status_embed(self, status):
        embed = discord.Embed(
            title="Growtopia Server Status",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="Date", value=status["date"], inline=True)
        embed.add_field(name="Time", value=status["time"], inline=True)
        embed.add_field(name="Player Count", value=status["player_count"], inline=False)
        embed.add_field(name="WOTD Name", value=status["wotd_name"], inline=True)
        embed.set_image(url=status["wotd_url"])
        return embed

async def setup(bot):
    await bot.add_cog(GrowtopiaStatusCog(bot))
