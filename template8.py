import discord
from discord.ext import commands

class template8(commands.Cog, name="template8"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="clash-calculator",
        description="Calculate points needed for a Guild Clash event goal or pristine type.",
    )
    async def clash_calculator(self, ctx, points: int, anom_type: str, clash: str, goal_points: int = None):
        anom_type = anom_type.lower()
        clash = clash.lower()

        # Cancel calculation for incorrect arguments
        if not (anom_type in {'reliable', 'pristine', 'elegant'}):
            await ctx.send("Invalid pristine type. Please use 'reliable', 'pristine', or 'elegant'.")
            return
        
        # Predefined data for points calculation
        event_data = {
            "block bashers":      {'contri': 828000, 'reliable': 8, 'pristine': 50, 'elegant': 170},
            "block builders":     {'contri': 938200, 'reliable': 20, 'pristine': 80, 'elegant': 220},
            "fishing fanatics":   {'contri': 4690800, 'reliable': 3400, 'pristine': 15700, 'elegant': 42800},
            "harvest heroes":     {'contri': 938200, 'reliable': 20, 'pristine': 80, 'elegant': 220},
            "speedy splicers":    {'contri': 938200, 'reliable': 20, 'pristine': 80, 'elegant': 220},
            "surgery stars":      {'contri': 1655900, 'reliable': 1500, 'pristine': 6200, 'elegant': 20000},
            "cooking conquerors": {'contri': 1885000, 'reliable': 5500, 'pristine': 22000, 'elegant': 70000},
            "super startopians":  {'contri': 1655900, 'reliable': 2000, 'pristine': 7700, 'elegant': 24200}
        }

        if goal_points is None:
            points_needed = event_data[clash]['contri'] - points

        elif points > goal_points:
            await ctx.send("You can't have more points than your goal is.")
            return
        
        else:
            points_needed = goal_points - points

        actions_needed = points_needed / event_data[clash][anom_type]


        # Create and send a single embed with lime green color
        embed = discord.Embed(title="<a:GrowboyTest:1088806331676381244> Clash Calculator", color=0x00FF00)  # Lime Green
        embed.add_field(name="<:Information:1148005931267924138> Points", value=f"<:gtArrowRight:1057970795399352370> You need {points_needed} points to reach the goal for {clash}.")
        embed.add_field(name="<:Achievements:1053407111964541008> Actions", value=f"<:gtArrowRight:1057970795399352370> Number of actions needed using a(n) **{anom_type}** tool: {actions_needed:.2f}")
        

        await ctx.send(embed=embed)

# Rest of your code ...

# And then we finally add the cog to the bot so that it can load, unload, reload, and use its content.
async def setup(bot):
    await bot.add_cog(template8(bot))