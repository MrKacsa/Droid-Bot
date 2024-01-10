import discord
from discord.ext import commands
from discord.ext.commands import Context
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re

class Template20(commands.Cog, name="template20"):
    def __init__(self, bot):
        self.bot = bot

    def build_embed(self, context, title, description, buffs, drops, harvesting_time):
        # Create embed
        embed = discord.Embed(color=discord.Color.green())
        embed.title = title
        embed.description = description

        # Display buffs, drops, and harvesting time sections
        embed.add_field(name="<:Misses_Droid:1192517100888141946> Buffs", value=buffs, inline=False)
        embed.add_field(name="<:Tractor_Droid:1192515057851039744> Drops", value=drops, inline=False)
        embed.add_field(name="<:wall_clock:1192222861876805782> Estimated Harvesting Time", value=harvesting_time, inline=False)

        # Add footer
        timestamp = datetime.now().strftime("%d %H:%M:%S")
        user_pfp_url = str(context.author.avatar) if context.author.avatar else str(context.author.default_avatar)
        embed.set_footer(text=f"Requested by {context.author.display_name} | at {timestamp}", icon_url=user_pfp_url)

        return embed

    @commands.hybrid_command(
        name="harvest",
        description="Calculate the average block drops, seed drop chance, gem drops.",
        usage="<item_count> <item_name> <harvester_buff> <dcs_buff>",
    )
    async def harvest(self, context: Context, item_count: int, item_name: str, harvester_buff: bool = False, dcs_buff: bool = False):
        formatted_item_name = item_name.replace(" ", "_").title()  # Convert to Title Case with underscores
        wiki_url = f"https://growtopia.fandom.com/wiki/{formatted_item_name}"

        # Fetch the details from the website
        response = requests.get(wiki_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Check if the item is in the "Farmables" category
            farmable_category = soup.find('li', {'class': 'category normal', 'data-name': 'Farmables'})

            if farmable_category:
                base_blocks = 3.75
                base_seed_chance = 0.33
                farmability = "Farmable"
            else:
                base_blocks = 2.5
                base_seed_chance = 0.25
                farmability = "Unfarmable"

            # Apply buffs based on user input
            active_buffs = []
            if harvester_buff:
                base_blocks += 0.375  # 10% more blocks
                active_buffs.append("<:Harvester:1192529921839468634> Harvester")
            if dcs_buff:
                base_blocks += 0.075  # 2% more blocks
                active_buffs.append("<:DCS:1192529429088456715> Dreamcatcher Staff")

            # Format the buffs for display
            buffs_display = "\n".join(active_buffs) if active_buffs else "No bonuses active"

            # Get rarity information from the wiki
            rarity_element = soup.find('small', text=re.compile(r'Rarity: (\d+)'))
            if rarity_element:
                rarity = int(re.search(r'Rarity: (\d+)', rarity_element.text).group(1))

                # Calculate seed drop chance based on rarity
                seed_chance = self.calculate_seed_chance(rarity)
                # Calculate average seed drops per X trees
                average_seeds = seed_chance * item_count

                # Retrieve gem drop information
                gem_drop_info = soup.find('th', string=re.compile(r"Default Gems Drop")).find_next('td')
                gem_drop_match = re.search(r'(\d+)\s*-\s*(\d+)', gem_drop_info.text)
                if gem_drop_match:
                    min_gem_drop = int(gem_drop_match.group(1))
                    max_gem_drop = int(gem_drop_match.group(2))
                else:
                    min_gem_drop = max_gem_drop = 0

                # Calculate average gem drop
                average_gem_drop = (min_gem_drop + max_gem_drop) / 2
                gem_drops = average_gem_drop * item_count

            else:
                rarity = None
                seed_chance = None
                average_seeds = None
                average_gem_drop = None
                gem_drops = None
                farmability = "Unknown"

            # Calculate average block drops per tree
            average_blocks = base_blocks * item_count

            # Calculate estimated harvesting time
            harvesting_time = f"<a:GtDotAnimated:1186706594969428078> Using any tractor: {item_count * 0.25:,.0f} sec\n<a:GtDotAnimated:1186706594969428078> By hand: {item_count * 0.435:,.0f} sec\n<a:GtDotAnimated:1186706594969428078> By Hand and Speedy: {item_count * 0.375:,.0f} sec\n<a:GtDotAnimated:1186706594969428078> With tractor and Speedy: {item_count *0.24528:,.0f}"

            # Build the embed using the helper function
            title = f"Drops from harvesting {item_count} {item_name} Tree"
            description = f"({farmability}, rarity {rarity})"
            buffs = buffs_display
            drops = f"<a:GtDotAnimated:1186706594969428078> Gem drops: {gem_drops:,.0f}\n<a:GtDotAnimated:1186706594969428078> Block drops: {average_blocks:,.0f}\n<a:GtDotAnimated:1186706594969428078> Seed Drops: {average_seeds:,.0f}"

            embed = self.build_embed(context, title, description, buffs, drops, harvesting_time)

            await context.send(embed=embed)

        else:
            await context.send(f"An item {item_name} is not found.", ephemeral=True)

    def calculate_seed_chance(self, rarity):
        # Define the rarity ranges and corresponding drop rates
        rarity_ranges = [
            (1, 3), (4, 7), (8, 11), (12, 15), (16, 19), (20, 23), (24, 27),
            (28, 31), (32, 35), (36, 39), (40, 47), (48, 55), (56, 71), (72, 91),
            (92, 123), (124, 127), (128, 179), (194, 241), (242, 363)
        ]

        drop_rates = [0.33, 0.25, 0.2, 0.16, 0.14, 0.12, 0.11, 0.1, 0.09, 0.08,
                      0.07, 0.06, 0.05, 0.04, 0.03, None, 0.02, 0.01, None, 0.01]

        # Find the corresponding drop rate for the given rarity
        for (lower, upper), rate in zip(rarity_ranges, drop_rates):
            if lower <= rarity <= upper:
                return rate

        # Default case if rarity is not in the defined ranges
        return None


async def setup(bot):
    await bot.add_cog(Template20(bot))
