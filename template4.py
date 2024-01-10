import discord
from discord.ext import commands
import requests
from datetime import datetime
import re

class Template4(commands.Cog, name="Template4"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="render",
        description="Render an image of a Growtopia world.",
    )
    async def render(self, ctx: commands.Context, worldname: str):
        worldname_upper = worldname.upper()
        worldname_lower = worldname.lower()
        world_url = f"https://s3.amazonaws.com/world.growtopiagame.com/{worldname_lower}.png"

        try:
            response = requests.get(world_url)
            response.raise_for_status()  # Raise HTTPError for bad responses

            if "Access Denied" in response.text:
                embed = discord.Embed(
                    title=f"<:gtExclamation:1058445755544772768> A render of {worldname_upper} doesn't exist.",
                    description="This world doesn't have a render yet. If you're the owner of the world, use /renderworld to create a render.",
                    color=discord.Color.blue()
                )
            else:
                # Download the image as text
                image_text = response.text

                # Search for "tEXtdate:create" and extract exactly 10 characters after the word "create"
                date_match_1 = re.search(r"tEXtdate:create(.{11})", image_text)
                render_date_text_1 = date_match_1.group(1).strip() if date_match_1 else "Unknown"

                # Search for "tEXtdate:create" and extract characters 13 to 26 after the word "create"
                date_match_2 = re.search(r"tEXtdate:create(.{12})(.{14})", image_text)
                render_date_text_2 = date_match_2.group(2).strip() if date_match_2 else "Unknown"

                embed = discord.Embed(
                    title=f"Growtopia | {worldname_upper} render",
                    description=f" [World Link]({world_url})\n_`Last Rendered on: {render_date_text_1} at {render_date_text_2}`_",
                    color=discord.Color.blue()
                )
                embed.set_image(url=world_url)

        except requests.exceptions.HTTPError as e:
            # Handle HTTP errors (e.g., 404 Not Found)
            embed = discord.Embed(
                title=f"<:gtExclamation:1058445755544772768> A render of {worldname_upper} doesn't exist.",
                description=f"This world doesn't have a render yet. If you're the owner of the world, use /renderworld to create a render.",
                color=discord.Color.red()
            )

        # Add user's profile picture, name, and current date to the footer
        user_avatar_url = str(ctx.author.avatar.url) if ctx.author.avatar else str(ctx.author.default_avatar.url)
        user_name = str(ctx.author)
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        embed.set_footer(text=f"{user_name} | {current_date}", icon_url=user_avatar_url)

        try:
            await ctx.send(embed=embed)
        except discord.HTTPException as e:
            print(f"Error sending embed: {e}")

# Register the cog
async def setup(bot):
    await bot.add_cog(Template4(bot))
