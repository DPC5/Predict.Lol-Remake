
import discord 
from discord import app_commands
from discord.ext import commands
from lol_api import getPuuid, getAccountTag, getSummoner, getMastery, getStats, calcSR, extract_player_roles, getmatchDetails, calcPercent
# from predict import calcSR, calcPercent
from lol_api_idf import get_summoner_icon
import json
import datetime
import asyncio
import os
data_file = 'data.json'


TEST_GUILD = discord.Object(id=1349068689521115197)


with open('config.json', 'r') as file:
    config = json.load(file)
token = config.get('token')
RIOT_API = config.get('RIOT_API')

bot = commands.Bot(command_prefix="^", intents = discord.Intents.all())


with open(data_file, 'r') as f:
    data = json.load(f)


ver = data['version']
opgg_image_path = "opgg.png"


bot.remove_command('help')


@bot.event
async def on_ready():
    asyncio.create_task(update_activity())
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync(guild=TEST_GUILD)
        print(f"Synced {len(synced)} command(s) to test guild")
    except Exception as e:
        print(e)
    
    try:
        synced_global = await bot.tree.sync()
        print(f"Synced {len(synced_global)} global command(s)")
    except Exception as e:
        print(e)


async def update_activity():
    while True:
        predicts = data['predict']
        await bot.change_presence(activity=discord.Streaming(name="{} Predictions".format(predicts), url="https://www.twitch.tv/morememes_"))
        await asyncio.sleep(30)



@bot.tree.command(name="info", description="Get information about ChoBot", guild=TEST_GUILD)
async def info(interaction: discord.Interaction):
    embed = discord.Embed(title=" ", description=f"Version {ver} By Morememes")
    embed.set_author(name="ChoBot")
    embed.add_field(name="What does it do?", value="This bot was made as a test to see a couple things. First, if I could make a functioning bot. Second, can I make a program that has some connection to a game I play.", inline=False)
    embed.add_field(name="What is SR?", value="SR or Summoner Rating, is a number that gives an estimate to how much positive inpact a player has on their game. ", inline=False)
    embed.add_field(name="How is SR calculated?", value="SR is calculated right now by taking average stats over the past 10 games and comparing them with your rank. These stats include damage, tower damage, kda, and more. In a game SR will be dynamic, this means it will calculate whether the draft of that game makes you more impactful or makes the enemy more impactful. Expect SR around 125 to be high impact players im most of their games.", inline=False)
    embed.add_field(name="Why is somone's SR so high?", value="SR has two values, the main one being general SR this is what is displayed using ^lookup. This value is the impact that the player would have on an average game with ranging skill levels. The next SR is hidden, this will only be seen when ranks are close together. This SR will no longer apply bonuses based on rank, it will only apply bonuses based on LP. This is mainly prevelant in higher elo.", inline=False)
    embed.add_field(name="More?", value="If you have any suggestions please message me on discord. Also, keep in mind this is my first discord bot and first semi-public program, there will be bugs please be patient.", inline=False)
    
    await interaction.response.send_message(embed=embed)



#LOL API integration using my library

def fName(name: str):
    if "+" in name:
        name = name.split("+")
        tag = name[1]
        name = name[0]+" "+tag.split("#")[0]
        tag = tag.split("#")[1]
    else:
        split = name.split("#")
        name = split[0]
        tag = split[1]
    info = {
        "name": name,
        "tag": tag
    } 
    return info



@bot.tree.command(name="lookup", description="Look up a summoner's stats", guild=TEST_GUILD)
@app_commands.describe(name="The summoner name to look up")
async def lookup(interaction: discord.Interaction, name: str):
    print("Lookup command received!")
    channel = interaction.channel

    try:
        # Process name with + for spaces
        info = fName(name)
        name = info['name']
        tag = info['tag']
        
        if "+" in name:
            opurl = f"https://www.op.gg/summoners/na/{name.replace(' ','%20')}-{tag}"
        else:
            opurl = f"https://www.op.gg/summoners/na/{name}-{tag}"
            
        region = "americas"
        region2 = "na1"

        puuid = getPuuid(name, tag, region)
        
        file = discord.File(opgg_image_path, filename="opgg.png")
        account_tag = getAccountTag(puuid, region)
        summoner = getSummoner(puuid, region2)
        icon = get_summoner_icon(summoner['profileIconId'])
        level = summoner['summonerLevel']
        top_champ = getMastery(puuid, 1)[0]
        id = summoner['id']
        stats = getStats(id, region2)

        if stats['tier'] in {"UNRANKED", "MASTER", "GRANDMASTER", "CHALLENGER"}:
            rank = ""
        else:
            rank = stats['rank']

        rank = f"{stats['tier']} {rank} {stats['leaguePoints']} LP"
        wr = 0 if stats['losses'] == 0 else int(stats['wins']/(stats['wins']+stats['losses'])*100)
                    
        win_loss = f"{stats['wins']} | {stats['losses']} (%{wr} Win Rate)"
        sr = 0 if stats['tier'] == "UNRANKED" else calcSR(puuid)

        embed = discord.Embed(title=" ")
        embed.set_author(name=account_tag, url=opurl, icon_url="attachment://opgg.png")
        embed.set_thumbnail(url=icon)
        embed.add_field(name="Level", value=level, inline=True)
        embed.add_field(name="Rank", value=rank, inline=True)
        embed.add_field(name="Top Champion", value=top_champ, inline=True)
        embed.add_field(name="Win/Loss", value=win_loss, inline=True)
        embed.add_field(name="SR", value=sr, inline=True)
        
        await interaction.response.send_message(file=file, embed=embed)
        print("Lookup command sent!")
        
    except Exception as e:
        print(f"Error in lookup command: {e}")
        await interaction.response.send_message("An error occurred while processing your request.", ephemeral=True)

@bot.tree.command(name="predict", description="Predict the outcome of a match", guild=TEST_GUILD)
@app_commands.describe(match_id="The match ID to analyze")
@app_commands.checks.cooldown(1, 120, key=lambda i: (i.guild_id))
async def predict(interaction: discord.Interaction, match_id: str):
    print(f"predicting match: {match_id}")
    
    try:
        await interaction.response.defer()
        now = datetime.datetime.now().strftime("%I:%M %p")
        region = "americas"
        region2 = "na1"

        # Get match details
        match_details = getmatchDetails(match_id)
        if not match_details:
            await interaction.followup.send("Could not retrieve match details.", ephemeral=True)
            return

        players = extract_player_roles(match_details)
        if not players or len(players) != 10:
            await interaction.followup.send("Invalid number of players in match (expected 10).", ephemeral=True)
            return

        # Split into teams
        blueside = {}
        redside = {}
        for index, (name, data) in enumerate(players.items()):
            if index < 5:
                blueside[name] = {'puuid': data['puuid'], 'name': name}
            else:
                redside[name] = {'puuid': data['puuid'], 'name': name}

        roles = ['TOP', 'JUNGLE', 'MID', 'BOT', 'SUPPORT']
        bs = list(blueside.keys())
        rs = list(redside.keys())
        
        # Calculate SR for each player
        bsrT = 0
        rsrT = 0
        bsr = []
        rsr = []
        errors = []
        zero_sr_count = 0  # Track how many players have 0 SR
        
        for i in range(5):
            try:
                blue_puuid = blueside[bs[i]]['puuid']
                red_puuid = redside[rs[i]]['puuid']
                
                blue_sr = calcSR(blue_puuid) or 0  # Default to 0 if None
                red_sr = calcSR(red_puuid) or 0    # Default to 0 if None
                
                # Count players with 0 SR
                if blue_sr == 0:
                    zero_sr_count += 1
                if red_sr == 0:
                    zero_sr_count += 1
                    
                bsr.append(blue_sr)
                bsrT += blue_sr
                rsr.append(red_sr)
                rsrT += red_sr
            except Exception as e:
                print(f"Error calculating SR for player {i}: {e}")
                errors.append(f"Error calculating stats for {bs[i]} or {rs[i]}")
                continue

        if errors:
            await interaction.followup.send("\n".join(errors), ephemeral=True)
            return

        if bsrT == 0 or rsrT == 0:
            await interaction.followup.send("Could not calculate valid SR totals for both teams.", ephemeral=True)
            return

        # Create prediction
        prediction = calcPercent(bsrT, rsrT)
        if not prediction:
            await interaction.followup.send("Could not generate prediction.", ephemeral=True)
            return

        # Build description with warning if needed
        description = f"**Predicted Winner: {prediction.get('winner', 'Unknown')} " + \
                     f"({int(prediction.get('chance', 0))}% chance) " + \
                     f"Confidence: ({prediction.get('confidence', 'Unknown')})**"
        
        # Add warning if multiple players have 0 SR
        if zero_sr_count >= 2:
            description += "\n\n⚠️ **Note:** This prediction may be less reliable as " + \
                         f"{zero_sr_count} players have 0 SR (new or inactive players)."

        embed = discord.Embed(
            title=f"PREDICTION FOR MATCH: {match_id}", 
            description=description,
            color=0x0000ff
        )
        
        # Add team information
        for i in range(5):
            # Split summoner name into name and tag (assuming format "Name#Tag")
            blue_name_parts = bs[i].split('#')
            blue_name = blue_name_parts[0] if blue_name_parts else bs[i]
            blue_tag = blue_name_parts[1] if len(blue_name_parts) > 1 else ""
            
            red_name_parts = rs[i].split('#')
            red_name = red_name_parts[0] if red_name_parts else rs[i]
            red_tag = red_name_parts[1] if len(red_name_parts) > 1 else ""
            
            embed.add_field(
                name=f"{roles[i]} (Blue)", 
                value=f"{bs[i]}\nSR: {bsr[i] if i < len(bsr) else 'N/A'}", 
                inline=True
            )
            embed.add_field(
                name=f"{roles[i]} (Red)", 
                value=f"{rs[i]}\nSR: {rsr[i] if i < len(rsr) else 'N/A'}", 
                inline=True
            )
            embed.add_field(name="\u200b", value="\u200b", inline=True)  # Spacer

        # Create a view with buttons for each player
        view = discord.ui.View()
        
        # Add buttons for blue side players
        for i in range(5):
            name_parts = bs[i].split('#')
            name = name_parts[0] if name_parts else bs[i]
            tag = name_parts[1] if len(name_parts) > 1 else ""
            
            # Format the OP.GG URL
            opgg_url = f"https://www.op.gg/summoners/na/{name}-{tag}" if tag else f"https://www.op.gg/summoners/na/{name}"
            
            # Add button
            button = discord.ui.Button(
                label=f"{roles[i]}: {bs[i]}",
                url=opgg_url,
                style=discord.ButtonStyle.link,
                row=i
            )
            view.add_item(button)
            
        # Add buttons for red side players
        for i in range(5):
            name_parts = rs[i].split('#')
            name = name_parts[0] if name_parts else rs[i]
            tag = name_parts[1] if len(name_parts) > 1 else ""
            
            # Format the OP.GG URL
            opgg_url = f"https://www.op.gg/summoners/na/{name}-{tag}" if tag else f"https://www.op.gg/summoners/na/{name}"
            
            # Add button
            button = discord.ui.Button(
                label=f"{roles[i]}: {rs[i]}",
                url=opgg_url,
                style=discord.ButtonStyle.link,
                row=i
            )
            view.add_item(button)

        await interaction.followup.send(embed=embed, view=view)

    except Exception as e:
        print(f"Error in predict command: {str(e)}")
        await interaction.followup.send(
            "An error occurred while processing your request.", 
            ephemeral=True
        )

@predict.error
async def predict_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"This command is on cooldown. Try again in {error.retry_after:.1f} seconds.", 
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "An unexpected error occurred.", 
            ephemeral=True
        )
        raise error

bot.run(token)