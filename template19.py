import discord
from discord.ext import commands
from discord.ext.commands import Context
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageFilter
from io import BytesIO
import re
import json
import asyncio
from collections import Counter

class GrowtopiaGame(commands.Cog, name="growtopia_game"):
    def __init__(self, bot):
        self.bot = bot
        self.correct_guesses = []  # List to store correct guesses during a game
        self.resize_methods = {
            "m1": (Image.NEAREST, 1),
            # Add more methods as needed
        }
        self.leaderboard_size = 5
        self.leaderboard = Counter()

    def format_item_name(self, item_name):
        # Format the item name for fetching the sprite link
        return item_name.replace(" ", "_").replace("'", "%27").replace('%27S_', '%27s_')

    @commands.hybrid_command(
        name="start_game",
        description="Start a new Growtopia sprite guessing game!",
    )
    async def start_game(self, context: Context, item_name: str, timer: int = 60, leaderboard_size: int = 5, blur_level: int = 1):
        """
        Start a new game by generating a sprite for the given item, blurring it, and setting a timer.

        :param context: The application command context.
        :param item_name: The name of the item to generate the sprite for.
        :param timer: The time limit for guessing in seconds (default is 60 seconds).
        :param leaderboard_size: The number of players to display on the leaderboard (default is 5).
        :param blur_level: The blur level to apply to the sprite (1 to 6, default is 1).
        """
        # Reset the correct guesses and leaderboard
        self.correct_guesses = []
        self.leaderboard.clear()

        self.leaderboard_size = leaderboard_size
        formatted_item_name_for_guess = item_name.lower()  # Case-insensitive format for guessing
        formatted_item_name_for_sprite = self.format_item_name(item_name)

        # Generate sprite data for the game
        sprite_data = self.get_sprite_data_for_guess(formatted_item_name_for_sprite, blur_level=blur_level)

        if sprite_data:
            # Set correct guesses for the ongoing game
            self.correct_guesses = [formatted_item_name_for_guess]

            # Send an ephemeral message to the user
            await context.send(f"Command received! Starting a Growtopia sprite guessing game for `{item_name}`. Check the channel for the game details.", ephemeral=True)

            # Send the game details in an embed to the channel
            embed = discord.Embed(
                title="Growtopia Sprite Guessing Game",
                description=f"Guess the Growtopia sprite! Type your guess within the next {timer} seconds.",
                color=discord.Color.blurple(),
            )
            embed.set_thumbnail(url="attachment://blurred_sprite.png")

            # Send the blurred sprite for guessing to the channel
            game_message = await context.send(
                embed=embed,
                files=[discord.File(BytesIO(sprite_data), filename="blurred_sprite.png")]
            )

            # Start the timer
            await asyncio.sleep(timer)

            # Announce the end of the game
            await self.display_leaderboard_and_clear_sprite(context, item_name, sprite_data)

            # Reset correct guesses list
            self.correct_guesses = []

    @commands.hybrid_command(
        name="guess",
        description="Guess the Growtopia sprite for the given item!",
    )
    async def guess(self, context: Context, item_name: str):
        """
        Guess the Growtopia sprite for the given item.

        :param context: The application command context.
        :param item_name: The user's guess for the item.
        """
        # Check if a game is ongoing
        if not self.correct_guesses:
            await context.send("No game is currently in progress. Start a new game using `/start_game`.", ephemeral=True)
            return

        # Check if the user has already guessed correctly in the current game
        if context.author.name in self.leaderboard:
            await context.send("You have already guessed correctly in the current game. Wait for the next game to start.", ephemeral=True)
            return

        # Convert the user's guess to lowercase for case-insensitive comparison
        formatted_guess = item_name.lower()

        # Check if the user's guess is correct and update the leaderboard
        for correct_guess in self.correct_guesses:
            if formatted_guess == correct_guess:
                self.leaderboard[context.author.name] += 1
                position = self.leaderboard.most_common().index((context.author.name, self.leaderboard[context.author.name])) + 1
                await context.send(f"{context.author.mention}! You have guessed correctly!", ephemeral=True)
                await asyncio.sleep(1)  # Introduce a delay before sending the next message
                await context.channel.send(f"Someone has guessed correctly and is now in {ordinal(position)} place on the leaderboard.")
                return

        # If the user's guess is incorrect, notify them
        await context.channel.send("Wrong Guess.", ephemeral=True)

    def get_sprite_data_for_guess(self, formatted_item_name, blur_level):
        # Get the sprite data for the given item and apply blur
        sprite_data = self.get_sprite_data(formatted_item_name, method="m1", size=96, blur_level=blur_level)
        return sprite_data

    def get_sprite_data(self, formatted_item_name, method, size, blur_level):
        # Fetch the original sprite image
        wiki_url = f"https://growtopia.fandom.com/wiki/{formatted_item_name}"
        response = requests.get(wiki_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            rarity_element = soup.find('span', {'class': 'mw-headline'})

            match = re.search(r'src="(.+?)"', str(rarity_element))
            if match:
                original_sprite_response = requests.get(match.group(1))
                if original_sprite_response.status_code == 200:
                    original_sprite_image = Image.open(BytesIO(original_sprite_response.content))

                    # Convert to RGB mode if the image is in palette mode
                    if original_sprite_image.mode == "P":
                        original_sprite_image = original_sprite_image.convert("RGB")

                    # Resize the sprite using the specified method (always use m1)
                    resize_method, _ = self.resize_methods["m1"]
                    resized_sprite_image = original_sprite_image.resize((size, size), resample=resize_method)

                    # Add blur based on blur level
                    if blur_level > 1:
                        resized_sprite_image = resized_sprite_image.filter(ImageFilter.BLUR)

                    sprite_bytes = BytesIO()
                    resized_sprite_image.save(sprite_bytes, format='PNG')

                    sprite_bytes.seek(0)
                    return sprite_bytes.getvalue()

        return None

    async def display_leaderboard_and_clear_sprite(self, context: Context, item_name, sprite_data):
        # Display the top X players on the leaderboard
        leaderboard_text = f"The fastest people to guess were"

        for index, (player, score) in enumerate(self.leaderboard.most_common(self.leaderboard_size), 1):
            leaderboard_text += f"\n{index}. {player} (Score: {score})"

        # Create an embed with the leaderboard information
        leaderboard_embed = discord.Embed(
            title=f"Time's up! The correct answer was: {item_name}",
            description=leaderboard_text,
            color=discord.Color.blurple(),
        )

        # Set the leaderboard thumbnail as the clear item sprite
        leaderboard_embed.set_thumbnail(url="attachment://clear_item_sprite.png")

        # Send the leaderboard embed with the clear item sprite
        await context.send(embed=leaderboard_embed, files=[discord.File(BytesIO(sprite_data), filename="clear_item_sprite.png")])

        # Send the item sprite without blur and use guessbg.png as the background


def ordinal(n):
    suffix = 'th' if 11 <= n <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

async def setup(bot):
    await bot.add_cog(GrowtopiaGame(bot))
