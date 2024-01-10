import discord
from discord.ext import commands
from discord.ext.commands import Context
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime


class Template18(commands.Cog, name="template18"):
  def __init__(self, bot):
    self.bot = bot

  @commands.hybrid_command(
    name="breaking",
    description="Calculate the drop rates for breaking blocks in Growtopia.",
    usage="<item_count> <item_name>",
  )
  async def betawiki(self,
                     context: Context,
                     item_count: int,
                     item_name: str,
                     luck_mode: bool = False,
                     blue_ances_lvl: int = 0,
                     has_buddys_block_head: bool = False,
                     arroz_con_pollo: bool = False,
                     emerald_lock: bool = False):
    formatted_item_name = item_name.title().replace(" ", "_").replace(
      "'", "%27").replace('%27S_', '%27s_')
    wiki_url = f"https://growtopia.fandom.com/wiki/{formatted_item_name}"

    # Fetch the details from the website
    response = requests.get(wiki_url)
    if response.status_code == 200:
      soup = BeautifulSoup(response.text, "html.parser")

      # Extract information from the website as needed and send it back to Discord
      rarity_element = soup.find('span', {'class': 'mw-headline'})
      rarity_match = re.search(r'Rarity:_([0-9]+)', str(rarity_element))
      farmable_category = soup.find('li', {
        'class': 'category normal',
        'data-name': ['Farmables', 'Farmable']
      })

      if rarity_match:
        rarity = int(rarity_match.group(1))
        gem_drop, block_drop, seed_drop = self.calculate_drops(
          rarity, item_count, blue_ances_lvl, luck_mode, has_buddys_block_head,
          arroz_con_pollo, emerald_lock, formatted_item_name)

        # Extract item hit information
        item_hit = self.extract_item_hit(soup)

        total_gem_drop, total_block_drop, total_seed_drop = self.calculate_total_drops(
          rarity, item_count, luck_mode, blue_ances_lvl, has_buddys_block_head,
          arroz_con_pollo, emerald_lock, formatted_item_name)
        xp_earned = (1 + int(rarity / 5)) * item_count
        time_taken = 0.2625 * (int(item_hit) * item_count) if item_hit else 0

        # Create embed
        embed = discord.Embed(color=discord.Color.green(), )
        embed.title = f"Drops from breaking {item_count:,} {item_name}."
        rarity_description = "Farmable" if farmable_category else "Non-farmable"
        embed.description = f"({rarity_description}, rarity {rarity})"

        # Display bonuses
        bonuses = []
        if blue_ances_lvl > 0:
          bonuses.append(
            f"<:correct:1058861496018411582> Ancestral Tesseract of Dimensions *(+{(blue_ances_lvl+4)}% block drop)*"
          )
        if luck_mode:
          bonuses.append(
            "<:correct:1058861496018411582> Lucky! Mod *(10% of extra drops)*")
        if has_buddys_block_head:
          bonuses.append(
            "<:correct:1058861496018411582> Buddy's Block Head *(+2% block drop)*"
          )
        if arroz_con_pollo:
          bonuses.append(
            "<:correct:1058861496018411582> Arroz Con Pollo *(10% of extra gem drop)*"
          )
        if emerald_lock:
          bonuses.append(
            "<:correct:1058861496018411582> Emerald Lock *(10% of extra gem drop)*"
          )

        if bonuses:
          embed.add_field(name="Bonuses",
                          value="\n".join(bonuses),
                          inline=False)
        else:
          embed.add_field(name="Bonuses",
                          value="*No bonuses active*",
                          inline=False)

          # Add thumbnail to the embed
          thumbnail_url = "https://media.discordapp.net/attachments/1162636034174107698/1186523522298814525/droidflip.png?ex=65a60424&is=65938f24&hm=54fe797ee253417128a7a178&"  # Replace with the URL of your thumbnail
          embed.set_thumbnail(url=thumbnail_url)


        # Display drops
        embed.add_field(
          name="Drops",
          value=
          f"<a:GtDotAnimated:1186706594969428078>**Gem drops:** {total_gem_drop:,.2f}\n"
          f"<a:GtDotAnimated:1186706594969428078>**Block drops:** {total_block_drop:,.2f}\n"

          f"<a:GtDotAnimated:1186706594969428078>**Seed drops:** {total_seed_drop:,.2f}\n"
          f"<a:GtDotAnimated:1186706594969428078>**XP Earned:** {xp_earned:,.2f}",
          inline=False)

        # Add item hit information to the embed
        if item_hit:
          #If it takes more than a day
          if time_taken / 86400 > 1:
            embed.add_field(
              name=
              "<:wall_clock:1192222861876805782> Estimated Breaking Time",
            value=
            f"<:fist:1192268526971519156> Over a day. ({time_taken/3600:,.1f} Hours) _(without pickaxe)_",
            inline=False)
          #If it takes less than a full day, but more than an hour

          elif time_taken / 3600 > 1:
            embed.add_field(
              name=
              "<:wall_clock:1192222861876805782> Estimated Breaking Time",
              value=
              f"<:fist:1192268526971519156> {time_taken/3600:,.1f} Hours _(without pickaxe)_",
              inline=False)
          #if it takes less than an hour but more than a minute



          elif time_taken / 60 > 1:
            embed.add_field(
              name=
              "<:wall_clock:1192222861876805782> Estimated Breaking Time",
              value=
              f"<:fist:1192268526971519156> {time_taken/60:,.1f} Minutes _(without pickaxe)_",
              inline=False)
          #If it takes less than a minute
          else:
            embed.add_field(
              name=
              "<:wall_clock:1192222861876805782> Estimated Breaking Time",
              value=
              f"<:fist:1192268526971519156> {time_taken:,.3f} Seconds _(without pickaxe)_",
              inline=False)
        else:
          embed.add_field(
            name="System Error Occured",
            value=
            "[Please make sure to inform our staffs via our support server.](https://discord.gg/Dgat7rmQ7E)",
            inline=False)

        # Add footer
        timestamp = datetime.now().strftime("%d %H:%M:%S")
        user_pfp_url = str(
          context.author.avatar) if context.author.avatar else str(
            context.author.default_avatar)
        embed.set_footer(
          text=f"Requested by {context.author.display_name} | at {timestamp}",
          icon_url=user_pfp_url)

        await context.send(embed=embed)
      else:
        await context.send(
          f"**Item Name:** {item_name}\n**Rarity:** Not found on the Wiki.",
          ephemeral=True)
    else:
      await context.send(f"An item {item_name} is not found.", ephemeral=True)

  def calculate_drops(self, rarity, item_count, blue_ances_lvl, luck_mod,
                      has_buddys_block_head, arroz_con_pollo, emerald_lock,
                      item_name):
    # Handle special case for "Mystery Block"
    if "mystery_block" in item_name.lower():
      return 25, 0, 0

    base_gem_bonus = 0
    base_block_bonus = 0

    if "bountiful" in item_name.lower():
      # If the item name contains "bountiful", skip base gem calculations and set base gem drop to 0
      return 0, 1 / 12, 1 / 4  # base gem drop is set to 0, block drop is unaffected, and seed drop is unaffected

    if blue_ances_lvl > 0:
      # Ancestral Tesseract of Dimensions selected, calculate the level bonus
      level_bonus = 0.05 + (blue_ances_lvl - 1) * 0.01
      base_block_bonus += level_bonus

    if has_buddys_block_head:
      # Buddy's Block Head bonus
      base_block_bonus += 0.02

    # Total block drop rate calculation
    total_block_drop_rate = 1 / 12 + base_block_bonus

    gem_drop = self.calculate_gem_drop(rarity, base_gem_bonus)
    seed_drop_rate = 1 / 4  # 1 block in 4 blocks drops 1 seed

    # Return gem drops, block drops, and seed drops without multiplying by item_count
    return gem_drop, total_block_drop_rate, seed_drop_rate

  def calculate_total_drops(self, rarity, item_count, luck_mod, blue_ances_lvl,
                            has_buddys_block_head, arroz_con_pollo,
                            emerald_lock, formatted_item_name):
    gem_drop_rate, block_drop_rate, seed_drop_rate = self.calculate_drops(
      rarity, item_count, blue_ances_lvl, luck_mod, has_buddys_block_head,
      arroz_con_pollo, emerald_lock, formatted_item_name)

    total_gem_drop = gem_drop_rate * item_count
    total_block_drop = block_drop_rate * item_count
    total_seed_drop = seed_drop_rate * item_count

    if luck_mod:
      # Calculate the number of lucky gems (+10% to trigger 0-5x drop)
      # Therefore we use 2.5 (median of 0-5) as an average return
      total_gem_drop = total_gem_drop * 1.25

      # Calculate the number of lucky blocks (10% of item count)
      lucky_blocks = int(item_count * 0.1)
      total_block_drop += lucky_blocks

    if arroz_con_pollo:
      # Arroz Con Pollo bonus for gems (10% of item blocks)
      total_gem_drop += 0.1 * item_count

    if emerald_lock:
      # Emerald Lock bonus for gems (10% of item blocks)
      total_gem_drop += 0.1 * item_count

    return total_gem_drop, total_block_drop, total_seed_drop

  def calculate_gem_drop(self, rarity, base_gem_bonus):
    base_gem_drop = 0
    if 0 <= rarity <= 30:
      base_gem_drop = 0.053872119 * rarity - 4.98141e-5
    else:
      base_gem_drop = 0.0808082133 * rarity - 3.54996498e-5

    return base_gem_drop + base_gem_bonus

  def extract_item_hit(self, soup):

    table = soup.find('table', {'class': 'card-field'})
    if table:
      rows = table.find_all('tr')
      for row in rows:
        headers = row.find_all('th')
        cells = row.find_all('td')
        for header, cell in zip(headers, cells):
          header_text = header.text.strip().lower()
          cell_text = cell.text.strip()
          if 'hardness' in header_text:
            hits_match = re.search(r'([0-9]+)\s*Hits', cell_text)
            if hits_match:
              return hits_match.group(1)
    return None


async def setup(bot):
  await bot.add_cog(Template18(bot))
