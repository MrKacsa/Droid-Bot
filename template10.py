import discord
from discord.ext import commands
import asyncio
import sqlite3
import datetime
import typing
import re
import json

class template10(commands.Cog, name="template10"):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect("wotd.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS wotd (name TEXT, builder TEXT, date TEXT, image_url TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS admins (user_id INTEGER PRIMARY KEY)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS members (user_id INTEGER PRIMARY KEY)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS wotd_channels (channel_id INTEGER PRIMARY KEY)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS submitting_channels (channel_id INTEGER PRIMARY KEY)")
        self.conn.commit()

    def cog_unload(self):
        self.conn.close()

    def is_admin(self, user_id):
        self.cursor.execute("SELECT user_id FROM admins WHERE user_id = ?", (user_id,))
        admin_result = self.cursor.fetchone()
        return admin_result is not None

#add method 


    async def add_wotd(self, ctx, entry_format):
          match = re.match(r"\[([^]]+)] (.+) by (.+)", entry_format)
          if not match:
              await ctx.send("Invalid format. Please use the format [xx/xx/xxxx] WORLDNAME by BUILDER.")
              return

          wotd_date, wotd_name, builder_name = match.groups()
          wotd_name_lower = wotd_name.lower()

          if builder_name.lower() == "unknown?":
              builder_name = "Unknown Builder"
          else:
              builder_name = builder_name.strip()  # Remove leading/trailing spaces

          # Check if the WOTD entry already exists in the database
          self.cursor.execute("SELECT * FROM wotd WHERE name = ? AND date = ?", (wotd_name_lower, wotd_date))
          existing_entry = self.cursor.fetchone()

          if existing_entry:
              # WOTD entry already exists, send an alert in the same channel
              alert_message = f"WOTD entry '{wotd_name}' on {wotd_date} by {builder_name} already exists in the database."
              alert_message += "\nReact with ❌ to ignore this alert and proceed with adding it again."

              alert_msg = await ctx.send(alert_message)
              await alert_msg.add_reaction("❌")

              def check_reaction(reaction, user):
                  return (
                      reaction.message.id == alert_msg.id
                      and user == ctx.author
                      and str(reaction.emoji) == "❌"
                  )

              try:
                  reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=check_reaction)
              except asyncio.TimeoutError:
                  await ctx.send("WOTD entry not added. User did not react to the alert.")
                  return

          # Continue with adding the WOTD entry
          image_url = f"https://s3.amazonaws.com/world.growtopiagame.com/{wotd_name_lower}.png"
          current_date = wotd_date if wotd_date.lower() != "unknown?" else datetime.datetime.now().strftime("%d/%m/%Y")

          embed = discord.Embed(
              title=f"{wotd_name.upper()} WOTD Information",
              description=f"By {builder_name}\nDate: {current_date}",
              color=discord.Color.blue()
          )
          embed.set_image(url=image_url)
          embed.set_author(name=f"{wotd_name} [World Link]", url=image_url)

          if wotd_date.lower() == "unknown":
              embed.set_footer(text="Unknown Date WOTD")

          await ctx.send(embed=embed)

          # Add the WOTD entry to the database
          self.cursor.execute("INSERT INTO wotd VALUES (?, ?, ?, ?)", (wotd_name_lower, builder_name, current_date, image_url))
          self.conn.commit()
          await ctx.send(f"{wotd_name} has been uploaded to the WOTD database.")


#edit method
    async def edit_wotd(self, ctx, old_input, new_input):
          match_old = re.match(r"\[([^]]+)] (.+) by (.+)", old_input)
          match_new = re.match(r"\[([^]]+)] (.+) by (.+)", new_input)

          if not match_old or not match_new:
              await ctx.send("Invalid format. Please use the format [xx/xx/xxxx] WORLDNAME by BUILDER.")
              return

          old_date, old_name, old_builder = match_old.groups()
          new_date, new_name, new_builder = match_new.groups()

          # Check if the old WOTD entry exists in the database
          self.cursor.execute("SELECT * FROM wotd WHERE name = ? AND date = ?", (old_name.lower(), old_date))
          existing_entry = self.cursor.fetchone()

          if not existing_entry:
              await ctx.send(f"No WOTD entry found for '{old_name}' on {old_date}.")
              return

          # Check if the new WOTD entry already exists in the database
          self.cursor.execute("SELECT * FROM wotd WHERE name = ? AND date = ?", (new_name.lower(), new_date))
          new_entry = self.cursor.fetchone()

          if new_entry:
              # WOTD entry already exists, send an alert in the same channel
              alert_message = f"WOTD entry '{new_name}' on {new_date} by {new_builder} already exists in the database."
              alert_message += "\nReact with ❌ to ignore this alert and proceed with editing it again."

              alert_msg = await ctx.send(alert_message)
              await alert_msg.add_reaction("❌")

              def check_reaction(reaction, user):
                  return (
                      reaction.message.id == alert_msg.id
                      and user == ctx.author
                      and str(reaction.emoji) == "❌"
                  )

              try:
                  reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=check_reaction)
              except asyncio.TimeoutError:
                  await ctx.send("WOTD entry not edited. User did not react to the alert.")
                  return

          # Continue with editing the WOTD entry
          new_image_url = f"https://s3.amazonaws.com/world.growtopiagame.com/{new_name.lower()}.png"
          new_current_date = new_date if new_date.lower() != "unknown?" else datetime.datetime.now().strftime("%d/%m/%Y")

          # Update the WOTD entry in the database
          self.cursor.execute(
              "UPDATE wotd SET name = ?, builder = ?, date = ?, image_url = ? WHERE name = ? AND date = ?",
              (new_name.lower(), new_builder, new_current_date, new_image_url, old_name.lower(), old_date)
          )
          self.conn.commit()

          # Send an embed with the edited information
          embed = discord.Embed(
              title=f"{new_name.upper()} WOTD Information (Edited)",
              description=f"By {new_builder}\nDate: {new_current_date}",
              color=discord.Color.blue()
          )
          embed.set_image(url=new_image_url)
          embed.set_author(name=f"{new_name} [World Link]", url=new_image_url)

          if new_date.lower() == "unknown":
              embed.set_footer(text="Unknown Date WOTD")

          await ctx.send(embed=embed)
          await ctx.send(f"WOTD entry for '{old_name}' on {old_date} has been edited to '{new_name}' on {new_date}.")

    async def delete_wotd(self, ctx, entry_format):
          match = re.match(r"\[([^]]+)] (.+) by (.+)", entry_format)
          if not match:
              await ctx.send("Invalid format. Please use the format [xx/xx/xxxx] WORLDNAME by BUILDER.")
              return

          wotd_date, wotd_name, builder_name = match.groups()

          # Check if the WOTD entry exists in the database
          self.cursor.execute("SELECT * FROM wotd WHERE name = ? AND date = ?", (wotd_name.lower(), wotd_date))
          existing_entry = self.cursor.fetchone()

          if not existing_entry:
              await ctx.send(f"No WOTD entry found for '{wotd_name}' on {wotd_date}.")
              return

          # If there are multiple entries with the same name and date, ask the user which one to delete
          self.cursor.execute("SELECT * FROM wotd WHERE name = ? AND date = ?", (wotd_name.lower(), wotd_date))
          multiple_entries = self.cursor.fetchall()

          if len(multiple_entries) > 1:
              entry_options = "\n".join([f"Option {i + 1}: {entry[1]} by {entry[2]}" for i, entry in enumerate(multiple_entries)])
              await ctx.send(f"Multiple WOTD entries found for '{wotd_name}' on {wotd_date}:\n{entry_options}\nType the option number to delete.")

              def check_option(m):
                  return (
                      m.author == ctx.author
                      and m.channel == ctx.channel
                      and m.content.isdigit()
                      and 1 <= int(m.content) <= len(multiple_entries)
                  )

              try:
                  response = await self.bot.wait_for("message", timeout=60.0, check=check_option)
              except asyncio.TimeoutError:
                  await ctx.send("Timeout. Deletion canceled.")
                  return

              selected_option = int(response.content) - 1
              selected_entry = multiple_entries[selected_option]
          else:
              selected_entry = existing_entry

          # Continue with deleting the selected WOTD entry
          self.cursor.execute("DELETE FROM wotd WHERE name = ? AND date = ?", (selected_entry[0], selected_entry[2]))
          self.conn.commit()

          # Send a confirmation message
          await ctx.send(f"WOTD entry for '{selected_entry[1]}' on {selected_entry[2]} has been deleted.")




    @commands.hybrid_command(
        name="wotd-editor",
        description="Edit, upload, or delete a WOTD entry in the database.",
    )
    async def wotd_editor(self, ctx, operation=None):
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        if operation is None:
            await ctx.send("Do you want to edit, upload, or delete a WOTD entry? (Type 'edit', 'upload', or 'delete')")

            try:
                response = await self.bot.wait_for("message", timeout=90.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Timeout. All changes are discarded.")
                return

            operation = response.content.lower()

        if operation == "edit":
            await ctx.send("What's the old input you'd like to edit?")
            try:
                response = await self.bot.wait_for("message", timeout=90.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Timeout. All changes are discarded.")
                return

            old_input = response.content

            await ctx.send("What's the new input?")
            try:
                response = await self.bot.wait_for("message", timeout=90.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Timeout. All changes are discarded.")
                return

            new_input = response.content

            await self.edit_wotd(ctx, old_input, new_input)

        elif operation == "upload":
            await ctx.send("Input the WOTD entry in the following format: [xx/xx/xxxx] WORLDNAME by BUILDER")

            try:
                response = await self.bot.wait_for("message", timeout=90.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Timeout. All changes are discarded.")
                return

            entry_format = response.content

            await self.add_wotd(ctx, entry_format)

        elif operation == "delete":
            await ctx.send("Enter the full WOTD entry (including date) you want to delete in the format [DD/MM/YYYY] WORLDNAME by BUILDER:")

            try:
                response = await self.bot.wait_for("message", timeout=90.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Timeout. Deletion canceled.")
                return

            entry_format = response.content
            await self.delete_wotd(ctx, entry_format)

        else:
            await ctx.send("Invalid choice. Use 'edit', 'upload', or 'delete'.")







# wotd search command in here


    def get_wotd_embed(self, name, builder, date, image_url, results):
          embed = discord.Embed(
              title=f"{name.upper()} WOTD Information",
              description=f"By {builder}\nDate: {date}",
              color=discord.Color.blue()
          )
          embed.set_image(url=image_url)
          embed.set_footer(text=f"Results ({len(results)})")

          return embed


    @commands.hybrid_command(
          name="wotd",
          description="Search for information about the World of the Day.",
      )
    async def wotd_search(self, ctx, date_query: str = None, world_query: str = None, builder_query: str = None):
          date_query_lower = date_query.lower() if date_query else None
          builder_query_lower = builder_query.lower() if builder_query else None

          sql_query = "SELECT * FROM wotd WHERE 1=1"
          query_params = []

          if date_query_lower:
              if date_query_lower == "unknown":
                  # If date_query is set to "unknown", filter by only unknown dates
                  sql_query += " AND date = 'Unknown'"
              else:
                  sql_query += " AND date = ?"
                  query_params.append(date_query_lower)
          if world_query:
              sql_query += " AND LOWER(name) = ?"
              query_params.append(world_query.lower())
          if builder_query_lower and (builder_query_lower == "unknown" or builder_query_lower == "?"):
              # If builder_query is set to "unknown" or "?", filter by only unknown builders
              sql_query += " AND LOWER(builder) = 'unknown builder'"
          elif builder_query_lower:
              sql_query += " AND LOWER(builder) = ?"
              query_params.append(builder_query_lower)

          if not (date_query_lower or world_query or builder_query_lower):
              # If no search parameters are provided, show the current date's WOTD
              current_date = datetime.datetime.now().strftime("%d/%m/%Y").lower()
              sql_query += " AND date = ?"
              query_params.append(current_date)

          self.cursor.execute(sql_query, tuple(query_params))
          results = self.cursor.fetchall()

          if results:
              embeds = []
              for result in results:
                  name, builder, date, image_url = result
                  embed = self.get_wotd_embed(name, builder, date, image_url, results)
                  embeds.append(embed)

              paginator = Paginator(ctx, embeds)
              await paginator.start()
          else:
              await ctx.send("No matching WOTD announcements found.")


# staff command in here

    @commands.hybrid_command(
        name="add-wotd-staff",
        description="Add a user or role as a WOTD staff member.",
    )
    async def add_wotd_staff(self, ctx, option: str, entity: typing.Union[discord.Role, discord.Member]):
        if self.is_admin(ctx.author.id):
            if option.lower() == "admin":
                await self.add_wotd_admin(ctx, entity)
            elif option.lower() == "teammember":
                await self.add_wotd_teammember(ctx, entity)
            else:
                await ctx.send("Invalid option. Use 'admin' or 'teammember'.")
        else:
            await ctx.send("Only admins can add staff members.")

    async def add_wotd_admin(self, ctx, user_or_role):
        # Add the user or role to the admins table in the database
        if isinstance(user_or_role, discord.Member):
            user_id = user_or_role.id
            self.cursor.execute("INSERT INTO admins (user_id) VALUES (?)", (user_id,))
            self.conn.commit()
            await ctx.send(f"{user_or_role.mention} has been added as a WOTD admin.")
        else:
            await ctx.send("Invalid user option. Please provide a valid user.")

    async def add_wotd_teammember(self, ctx, user_or_role):
        # Add the user or role to the teammembers table in the database
        if isinstance(user_or_role, discord.Member):
            user_id = user_or_role.id
            self.cursor.execute("INSERT INTO teammembers (user_id) VALUES (?)", (user_id,))
            self.conn.commit()
            await ctx.send(f"{user_or_role.mention} has been added as a WOTD team member.")
        else:
            await ctx.send("Invalid user option. Please provide a valid user.")





    @commands.hybrid_command(
        name="wotd-leaderboard",
        description="Show the WOTD leaderboard.",
    )
    async def wotd_leaderboard(self, ctx, option: str = "builders", year: int = None):
        if option == "builders":
            query = """
                SELECT LOWER(builder), MAX(builder) as latest_name, COUNT(*) as count
                FROM wotd
                {}
                GROUP BY LOWER(builder)
                HAVING count >= 1
                ORDER BY count DESC
            """
            if year is None:
                self.cursor.execute(query.format(""))  # No additional condition for all years
            else:
                self.cursor.execute(query.format("WHERE date LIKE ?", f"%/{year}%"), (f"%/{year}%",))

        elif option == "worlds":
            query = """
                SELECT LOWER(name), MAX(name) as latest_name, COUNT(*) as count
                FROM wotd
                {}
                GROUP BY LOWER(name)
                HAVING count >= 1
                ORDER BY count DESC
            """
            if year is None:
                self.cursor.execute(query.format(""))  # No additional condition for all years
            else:
                self.cursor.execute(query.format("WHERE date LIKE ?", f"%/{year}%"), (f"%/{year}%",))

        else:
            await ctx.send("Invalid option. Use 'builders' or 'worlds'.")
            return

        results = self.cursor.fetchall()

        if results:
            if year is None:
                title = "All Time WOTD Leaderboard"
            else:
                title = f"{year} WOTD Leaderboard"

            embeds = []
            per_page = 10
            total_pages = (len(results) + per_page - 1) // per_page

            for page_num in range(total_pages):
                embed = discord.Embed(title=title, color=discord.Color.gold())
                start_idx = page_num * per_page
                end_idx = min(start_idx + per_page, len(results))

                for index, result in enumerate(results[start_idx:end_idx], start=start_idx):
                    leaderboard_entry = result[0]
                    if option == "builders":
                        embed.add_field(name=f"{index + 1}. {result[1]}", value=f"WOTD Count: {result[2]}", inline=False)
                    elif option == "worlds":
                        embed.add_field(name=f"{index + 1}. {result[1]}", value=f"Trophy Count: {result[2]}", inline=False)

                embed.set_footer(text=f"Page {page_num + 1}/{total_pages}")
                embeds.append(embed)

            paginator = Paginator(ctx, embeds)
            await paginator.start()

        else:
            await ctx.send("No data available for the leaderboard.")


#pg

class Paginator:
  def __init__(self, ctx, embeds):
      self.ctx = ctx
      self.embeds = embeds
      self.current_page = 0

  async def start(self):
      self.message = await self.ctx.send(embed=self.embeds[self.current_page])
      await self.message.add_reaction("⏪")  # New emoji for jumping to the first page
      await self.message.add_reaction("⬅️")
      await self.message.add_reaction("➡️")
      await self.message.add_reaction("⏩")  # New emoji for jumping to the last page
      await self.message.add_reaction("❌")

      while True:
          try:
              reaction, user = await self.ctx.bot.wait_for(
                  "reaction_add",
                  timeout=900,  # 15 minutes
                  check=lambda reaction, user: reaction.message == self.message and user == self.ctx.author
              )

              if reaction.emoji == "➡️":
                  self.current_page = (self.current_page + 1) % len(self.embeds)
              elif reaction.emoji == "⬅️":
                  self.current_page = (self.current_page - 1) % len(self.embeds)
              elif reaction.emoji == "⏪":  # Jump to the first page
                  self.current_page = 0
              elif reaction.emoji == "⏩":  # Jump to the last page
                  self.current_page = len(self.embeds) - 1
              else:
                  await self.message.edit(embed=self.get_closed_embed())
                  await self.message.clear_reactions()
                  return

              await self.message.edit(embed=self.embeds[self.current_page])
              await self.message.remove_reaction(reaction, user)

          except asyncio.TimeoutError:
              await self.message.edit(embed=self.get_closed_embed())
              await self.message.clear_reactions()
              break
          except Exception as e:
              print(e)  # Handle other exceptions

  def get_closed_embed(self):
      return discord.Embed(
          title="Embed Closed",
          description="This embed has been closed due to inactivity. If you believe that it was a mistake, please contact us via our [support server](https://discord.gg/UEmpX48D52).",
          color=discord.Color.red()
      )


async def setup(bot):
    await bot.add_cog(template10(bot))