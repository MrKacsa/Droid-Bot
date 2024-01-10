from discord.ext import commands
from discord.ext.commands import Context
import discord

# Custom check to verify if the user has the required role
def has_required_role(ctx):
    required_role_id = 1138897156019847269
    return any(role.id == required_role_id for role in ctx.author.roles)

# Here we name the cog and create a new class for the cog.
class Template3(commands.Cog, name="template3"):
    def __init__(self, bot):
        self.bot = bot

    # Here you can just add your own commands, you'll always need to provide "self" as the first parameter.

    @commands.hybrid_command(
        name="addadmin",
        description="Assigns a specific role to a user by mentioning them.",
    )
    @commands.check(has_required_role)  # Custom check to allow users with the required role
    async def addadmin(self, context: Context, member: discord.Member):
        """
        Assigns a specific role to a user.

        :param context: The application command context.
        :param member: The member to assign the role to.
        """
        # Retrieve the role ID you want to assign to the user
        role_id = 1138897156019847269

        # Fetch the role object using the role ID
        role = context.guild.get_role(role_id)

        if role:
            # Assign the role to the member
            await member.add_roles(role)
            await context.send(f"<:gtFist:1057971347592056864> Role added to user {member.name}. Successfully <a:ML_CheckMark:992382091767582760>")
        else:
            await context.send("<:gtExclamation:1058445755544772768> Access Denied. Unauthorized")




    

async def setup(bot):
    await bot.add_cog(Template3(bot))
