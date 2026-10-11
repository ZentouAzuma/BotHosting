import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import webserver

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event

async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to Hellzinc {member.name}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    
    hard_r_words = ["nigger"]
    soft_a_words = ["nigga"]
    
    content = message.content.lower()

    if any(word in content for word in hard_r_words):
        await message.delete()
        await message.channel.send(f"{message.author.mention} WOAH CHILL, THERE ARE KIDS HERE")
    elif any(word in content for word in soft_a_words):
        await message.delete()
        await message.channel.send(f"{message.author.mention} We're really using that word?")

    await bot.process_commands(message)

@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(titles="New Poll", description=question)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")

VALID_PVP_TYPES = ["Sword", "Axe", "UHC", "SMP", "DSMP", "Spear", "Mace", "DiaPot", "NethPot"]

RANK_THRESHOLDS = [
    (250, "LT5"),
    (500, "HT5"),
    (750, "LT4"),
    (1000, "HT4"),
    (1250, "LT3"),
    (1500, "HT3"),
    (1750, "LT2"),
    (2000, "HT2"),
    (2250, "LT1"),
    (2500, "HT1"),
]

def get_rank(elo):
    current_rank = RANK_THRESHOLDS[0][1]
    for threshold, rank_name in RANK_THRESHOLDS:
        if elo >= threshold:
            current_rank = rank_name
        else:
            break
    return current_rank

# --- Commands ---
@bot.command()
async def gg(ctx, player: discord.Member, pvp_type: str, opponent: discord.Member, score: str, previous_elo: int, new_elo: int):
    # Validate pvp_type against the allowed list (case-insensitive match)
    matched_type = None
    for t in VALID_PVP_TYPES:
        if t.lower() == pvp_type.lower():
            matched_type = t
            break

    if matched_type is None:
        await ctx.send(f"⚠️ '{pvp_type}' isn't a valid PVP type. Choose from: {', '.join(VALID_PVP_TYPES)}")
        return

    rank = get_rank(new_elo)
    if rank is None:
        await ctx.send(f"⚠️ {new_elo} elo is below the lowest rank (250). No role assigned.")
        return

    role_name = f"{matched_type} - {rank}"  # e.g. "Sword - HT3"

    message_text = (
        f"gg {player.mention} {matched_type}\n"
        f"Tester/Opponent {opponent.mention}\n"
        f"{score}\n\n"
        f"Previous elo:\n{previous_elo}\n"
        f"New elo: {new_elo}\n"
        f"Promoted to {rank}"
    )

    await ctx.send(message_text)

    type_prefix = f"{matched_type} - "
    rank_names = [r[1] for r in RANK_THRESHOLDS]
    roles_to_remove = [
        role for role in player.roles
        if role.name.startswith(type_prefix) and role.name.split(" - ", 1)[-1] in rank_names
    ]
    if roles_to_remove:
        await player.remove_roles(*roles_to_remove)


    print("Looking for role_name:", repr(role_name))
    for role in ctx.guild.roles:
        if matched_type.lower() in role.name.lower():
            print("Found similar server role:", repr(role.name))


    new_role = discord.utils.get(ctx.guild.roles, name=role_name)
    if new_role:
        await player.add_roles(new_role)
    else:
        await ctx.send(f"⚠️ Couldn't find a role named '{role_name}' — make sure it exists in this server.")

@bot.command()
async def listroles(ctx):
    names = [role.name for role in ctx.guild.roles]
    await ctx.send("\n".join(names))


# --- Run the bot ---
webserver.keep_alive()
bot.run(token, log_handler=handler, log_level=logging.DEBUG)