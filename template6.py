import discord
import re
from discord.ext import commands
from discord.ext.commands import Context
import requests
from bs4 import BeautifulSoup

from helpers import checks

class Template6(commands.Cog, name="template6"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="item-info",
        description="Search for a Growtopia item info.",
    )
    @checks.not_blacklisted()
    async def gtwiki(self, context: Context, item_name: str):
        formatted_item_name = item_name.title().replace(" ", "_").replace("'", "%27").replace('%27S_', '%27s_')
        wiki_url = f"https://growtopia.fandom.com/wiki/{formatted_item_name}"

        # Fetch the details from the website
        response = requests.get(wiki_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract information from the website as needed and send it back to Discord
            # Find the div element with class "card-text" and extract its text
            description_element = soup.find("div", class_="card-text")
            table = soup.find('table', {'class': 'card-field'})
            rarity_element = soup.find('span', {'class': 'mw-headline'})
            rarity_match = re.search(r'Rarity:_([0-9]+)', str(rarity_element))

            if description_element:
                description_text = description_element.get_text(strip=True)
                embed = discord.Embed(
                    title=f"Growtopia Wiki search for {item_name.title()}",
                    color=discord.Color.green(),
                )
                embed.add_field(
                    name=f"Item Name",
                    value=item_name.title(),
                    inline=False
                )
                if rarity_match:
                    embed.add_field(
                        name=f"Rarity",
                        value=rarity_match.group(1),
                        inline=False
                    )
                embed.add_field(
                    name=f"Information",
                    value=description_text,
                    inline=False
                )

                if table:
                    # Now you can proceed to extract data from the 'table' variable
                    # You can iterate through rows and cells as shown in the previous example
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        headers = row.find_all('th')

                        # Iterate through headers and cells
                        for header, cell in zip(headers, cells):
                            header_text = header.text.strip()
                            cell_text = cell.text.strip()

                            # Remove the part related to images and sprites
                            cell_text = cell_text.replace('<img src="', '')

                            embed.add_field(name=header_text, value=cell_text.replace('HitsRestores', 'Hits\nRestores'), inline=False)

                    # Send the embed without images
                    await context.send(embed=embed)
            else:
                await context.send(f"**Item Name:** `{item_name}` \n**Description:** Not found on the Wiki.", ephemeral=True)
        else:
            await context.send(f"`{item_name}` doesnt exist.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Template6(bot))
