import discord
from discord.ext import commands
from io import BytesIO
import requests

class template9(commands.Cog, name="template9"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="xp-calculator",
        description="Calculate how much XP is needed to reach a goal level.",
    )
    async def xp_calculator(self, ctx, current_xp: int, current_level: int, goal_level: int, method: str = None, rarity: int = None, account_age: int = 0):
        xp_values = [
            100, 150, 300, 550, 900, 1350, 1900, 2550, 3300, 4150,
            5100, 6150, 7300, 8550, 9900, 11350, 12900, 14550, 16300, 18150,
            20100, 22150, 24300, 26550, 28900, 31350, 33900, 36550, 39300, 42150,
            45100, 48150, 51300, 54550, 57900, 61350, 64900, 68550, 72300, 76150,
            80100, 84150, 88300, 92550, 96900, 101350, 105900, 110550, 115300, 120150,
            125100, 130150, 135300, 140550, 145900, 151350, 156900, 162550, 168300, 174150,
            180100, 186150, 192300, 198550, 204900, 211350, 217900, 224550, 231300, 238150,
            245100, 252150, 259300, 266550, 273900, 281350, 288900, 296550, 304300, 312150,
            320100, 328150, 336300, 344550, 352900, 361350, 369900, 378550, 387300, 396150,
            405100, 414150, 423300, 432550, 441900, 451350, 460900, 470550, 480300, 490150,
            500100, 510150, 520300, 530550, 540900, 551350, 561900, 572550, 583300, 594150,
            605100, 616150, 627300, 638550, 649900, 661350, 672900, 684550, 696300, 708150,
            720100, 732150, 744300, 756550, 768900
        ]

        if current_level <= 0 or current_level > 125:
            await ctx.send("Your current level must be in the range [1-125].")
            return
        
        elif goal_level <= 0 or goal_level > 125:
            await ctx.send("Your goal level must be in the range [1-125].")
            return
        
        elif current_level > goal_level:
            await ctx.send("Your goal level must be lower than your current level.")
            return
        
        elif current_xp < 0 or current_xp > xp_values[current_level-1]:
            await ctx.send(f"Your current xp must be in the range of your current level xp requirement [0-{xp_values[current_level-1]}].")
            return
        
        level = current_level
    
        total_xp = 0
        while (level < goal_level):
            total_xp += 50 * (level ** 2 + 2)
            level += 1
            
        xp_needed = total_xp - current_xp

        method_xp = {
            "feeding": 10,
            "potion": 10000,
            "farming": 1 + rarity // 5 if rarity else 1,
            "surgery": 150,
            "star_voyage": 50,
            "fishing": 1,  # Replace with actual calculation based on weight of fish caught
            "wolfworld": 50,
            "challenge_of_fenrir": 1000,
            "harmonic_crystal": 20,
            "fire": 1,
            "geiger_item": 10,
            "compacting_clothing": 1,
            "carnival_game": 5,
            "ringmaster_quest_step": 100,
            "forging_item": 100,
            "sewing_item": 20,
            "consumable": 1,
            "harvesting_provider": 1,
            "cooking_food": 1,  # Replace with actual calculation based on food quality
            "catching_ghost": 1,
            "crimefighting_villain": 100,
            "crimefighting_mastermind": 200,
            "crimefighting_supervillain": 500,
            "crimefighting_holiday_villain": 500,
            "chemsynth": 100
            # Add more methods and XP values as needed
        }

        response_title = "<a:GrowboyTest:1088806331676381244> Level Calculator"
        response_content = (
            f"<:gtLevelUp:1058860630762864760> To level up from level {current_level} to level {goal_level}, "
            f"with your current level of {current_level} and {current_xp} XP, "
            f"you need to gain a total of {'{:,}'.format(xp_needed).replace(',', ' ')} XP."
        )

        embed = discord.Embed(title=response_title, description=response_content, color=0x008080)

        # Calculate activities needed
        if method:
            method_name = method.lower()
            if method_name in method_xp:
                method_xp_value = method_xp[method_name]
                activities_needed = xp_needed // method_xp_value
                embed.add_field(name=f"Activities To Complete", value=f"{method_name.replace('_', ' ')}: {activities_needed} times", inline=False)
            else:
                await ctx.send(f"Unknown method: {method_name}")
                return
        else:
            # Suggest all methods if none is set
            activities_to_complete = ""
            for method_name, method_xp_value in method_xp.items():
                activities_needed = xp_needed // method_xp_value
                activities_to_complete += f"{method_name.replace('_', ' ')}: {activities_needed} times\n"
            
            embed.add_field(name=f"Activities To Complete", value=activities_to_complete, inline=False)

        # Add footer with user avatar
        user_avatar_url = str(ctx.author.avatar.url) if ctx.author.avatar else str(ctx.author.default_avatar.url)
        user_avatar_bytes = BytesIO(requests.get(user_avatar_url).content)
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url="attachment://user_avatar.png")
        
        await ctx.send(embed=embed, file=discord.File(user_avatar_bytes, "user_avatar.png"))

# Rest of your code ...

# Add the cog to the bot so that it can load, unload, reload, and use its content.
async def setup(bot):
    await bot.add_cog(template9(bot))
