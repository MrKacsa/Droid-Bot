import discord
from discord.ext import commands
from discord.ext.commands import Context
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageFilter
from io import BytesIO
from datetime import datetime, timedelta
import re

class Template16(commands.Cog, name="template16"):
    def __init__(self, bot):
        self.bot = bot
        self.resize_methods = {
            "m1": (Image.NEAREST, 1),
            "m2": (Image.BOX, 2),
            "m3": (Image.BILINEAR, 3),
            "m4": (Image.HAMMING, 4),
            "m5": (Image.BICUBIC, 5),
            "m6": (Image.LANCZOS, 6),
            # Add more methods as needed
        }

    @commands.hybrid_command(
        name="sprite",
        description="Returns item sprite using a specified resize method.",
    )
    async def sprite(self, context: Context, item_name: str, method: str = "m1", size: int = 96):
        """
        Search the Growtopia Wiki for an item, resize its sprite, and return the enhanced image.

        :param context: The application command context.
        :param item_name: The name of the item to search for.
        :param method: The resize method to use (default is "m1").
        :param size: The desired size of the sprite (default is 96).
        """

        formatted_item_name = item_name.title().replace(" ", "_").replace("'", "%27").replace('%27S_', '%27s_')
        print(formatted_item_name)
        wiki_url = f"https://growtopia.fandom.com/wiki/{formatted_item_name}"

        # Fetch the details from the website
        response = requests.get(wiki_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            rarity_element = soup.find('span', {'class': 'mw-headline'})

            match = re.search(r'src="(.+?)"', str(rarity_element))
            if match:
                sprite_url = match.group(1)

                # Fetch the original sprite image
                original_sprite_response = requests.get(sprite_url)
                if original_sprite_response.status_code == 200:
                    original_sprite_image = Image.open(BytesIO(original_sprite_response.content))

                    # Check if the original sprite image has an alpha channel (transparency)
                    if original_sprite_image.mode == 'RGBA':
                        # Resize the sprite using RGBA mode to preserve transparency
                        resized_sprite_image = original_sprite_image.resize((size, size), resample=self.resize_methods[method][0])
                    else:
                        # Resize the sprite using the specified method for non-transparent images
                        resized_sprite_image = original_sprite_image.resize((size, size), resample=self.resize_methods[method][0])

                    # Add blur based on blur level
                    if self.resize_methods[method][1] > 1:
                        resized_sprite_image = resized_sprite_image.filter(ImageFilter.BLUR)

                    # Convert the image to RGBA mode if it's not already
                    resized_sprite_image = resized_sprite_image.convert('RGBA')

                    # Set the sprite's alpha channel to 255 (fully opaque) for non-transparent pixels
                    resized_sprite_image.putalpha(255)

                    sprite_bytes = BytesIO()
                    resized_sprite_image.save(sprite_bytes, format='PNG')

                    sprite_bytes.seek(0)

                    # Get user's profile picture URL
                    user_avatar_url = str(context.author.avatar.url) if context.author.avatar else str(context.author.default_avatar.url)
                    user_avatar_bytes = BytesIO(requests.get(user_avatar_url).content)

                    # Get current timestamp for the footer
                    timestamp = self.get_formatted_timestamp()

                    embed = discord.Embed(
                        title=f"{item_name.title()} Sprite",
                        description=f"`Sprite Size: {size} x {size}`\n`Blur  Level: {self.resize_methods[method][1]}`",
                        color=discord.Color.green(),
                    )

                    # Set sprite as image in the embed
                    embed.set_image(url=f"attachment://sprite.png")
                    # Set user's profile picture as footer
                    embed.set_footer(
                        text=f"Requested by {context.author.display_name} | at {timestamp}",
                        icon_url="attachment://user_avatar.png"
                    )

                    await context.send(
                        embed=embed,
                        files=[
                            discord.File(sprite_bytes, filename="sprite.png"),
                            discord.File(user_avatar_bytes, filename="user_avatar.png")
                        ]
                    )
                else:
                    await context.send(f"<:gmWhat:1143605764569706506> Cannot find anything called {item_name}.")
            else:
                await context.send(f"**Item name:** {item_name}\n**Description:** Sprite not found. If you believe that it is a mistake, Feel free to contact us via our [support server](https://discord.gg/vEY9hmYGkN).")
        else:
            await context.send(f"<:gmWhat:1143605764569706506> Cannot find anything called {item_name}.")

    def get_formatted_timestamp(self):
        # Get current timestamp
        current_time = datetime.utcnow()

        # Get yesterday's date and current date
        yesterday = (current_time - timedelta(days=1)).date()
        current_date = current_time.date()

        # Check if the request was made today, yesterday, or on a different date
        if yesterday == current_date:
            formatted_timestamp = "Yesterday at " + current_time.strftime('%I:%M %p ')
        elif yesterday < current_date:
            formatted_timestamp = "Today at " + current_time.strftime('%I:%M %p')
        else:
            formatted_timestamp = current_time.strftime('%Y-%m-%d %I:%M %p')

        return formatted_timestamp

async def setup(bot):
  await bot.add_cog(Template16(bot))
