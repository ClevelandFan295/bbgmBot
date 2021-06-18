import discord
from discord.ext import commands
import json
import urllib.request
import csv
import math
import os
import time
import asyncio
from difflib import SequenceMatcher


client = commands.Bot(command_prefix='')

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=str(len(client.guilds)) + ' servers'))
    # remove the hashtags to leave a server
    # to_leave = client.get_guild(server ID to leave)
    # await to_leave.leave()
    servers = client.guilds
    print('Servers connected to:')
    for server in servers:
        print(server.name + ' | ID: ' + str(server.id))
        
prefix = '-'
nonExportCommands = ['help', 'load', 'test']
playerCommands = ['stats', 'bio', 'ratings', 'adv', 'proghistory', 'awards', 'compare', 'splits']
teamCommands = ['roster', 'picks', 'pyramid', 'sos']
leagueCommands = ['fa', 'pr', 'draft', 'matchups', 'matchup', 'leaders', 'ps', 'deaths']
totalCommands = nonExportCommands + playerCommands + teamCommands + leagueCommands + automationCommands
adminUsers = [625806545610997762]


@client.event
async def on_message(message):
    if message.content.startswith(prefix):
        messageArgs = str(message.content).split(' ')
        command = messageArgs[0].replace(prefix, '')
        command = str.lower(command)
        argOne = ""
        try: argOne = messageArgs[1]
        except: pass
        messageContentRaw = str(message.content).replace((messageArgs[0] + ' '), '')
        messageContentRaw = messageContentRaw.split(',')
        messageContent = messageContentRaw[0]
        messageContentComma = ""
        try: messageContentComma = messageContentRaw[1]
        except: pass

        if command in totalCommands:
            print(message.author.name, 'in', message.guild.name, ': ', message.content)

        if command in nonExportCommands:
            if command == 'load':
                if (message.author.guild_permissions.manage_roles or message.author.id in adminUsers):
                    exportCheck = argOne.startswith('https://')
                    if exportCheck == True:
                        await message.channel.send('Loading export...')
                        urllib.request.urlretrieve(argOne, f'{message.guild.id}.json')
                        await message.channel.send("Loaded!")
                    if exportCheck == False:
                        await message.channel.send("That doesn't look like a valid URL.")
                else:
                    await message.channel.send("You don't have permissions to load exports. Users with the 'manage roles' command can.")

            if command == 'help':
                embed = discord.Embed(
                        title='bbgmBot',
                        description=f'Currently in {len(client.guilds)} servers, bbgmBot pulls information from Basketball GM and Zen GM Hockey exports.',
                        color=0xE7AA00)
                embed.set_footer(text="Made by ClevelandFan#6181")
                # embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/829211052708855859/843262932179877928/55u7s4.jpg')
                embed.add_field(name="**Player Commands**",value="""
                • **-stats**
                • **-ratings**
                • **-bio**
                • **-adv** (advanced stats)
                • **-proghistory**
                • **-awards**
                • **-compare** (compares a draft prospects ceiling to a player)
                """, inline=False)
                embed.add_field(name="**Team Commands**",value="""
                • **-roster** (can show both contracts and stats)
                • **-picks**
                • **-pyramid** (projected record based on TR, and SOS)
                """, inline=False)
                embed.add_field(name="**League Commands**",value="""
                • **-fa**
                • **-draft** (not functional yet)
                """, inline=True)
                embed.add_field(name="**Other**",value="""
                • **-load** (server mods only, loads an export file)
                • **-help**
                """, inline=True)
                await message.channel.send(embed=embed)
            
        
        if command in playerCommands:
            with open(f'{message.guild.id}.json', 'r', encoding='utf-8-sig') as file:
                    export = json.load(file)
                    export['meta']['phaseText'] = 'Undefined phase'
                    players = export['players']
                    teams = export['teams']
                    settings = export['gameAttributes']
                    if 'sst' in players[0]['ratings'][0]:
                        sport = 'hockey'
                    if 'drb' in players[0]['ratings'][0]:
                        sport = 'basketball'
                    #meta stuff
                    season = settings['season']
                    games = ""
                    try: games = export['games']
                    except: pass
            commandPlayerRaw = messageContent.replace("0", "").replace("1", "").replace("2", "").replace("3", "").replace("4", "").replace("5", "").replace("6", "").replace("7", "").replace("8", "").replace("9", "")
            commandSeason = "".join(filter(str.isdigit, messageContent))
            commandPlayerRaw = str.lower(commandPlayerRaw)
            commandPlayer = commandPlayerRaw.replace(' ', '')
            commandPlayerRaw = commandPlayerRaw.split(' ')
            bestMatch = 0
            bestOvr = 0
            for p in players:
                playerName = p['firstName'] + p['lastName']
                match = SequenceMatcher(a=commandPlayer, b=playerName)
                match = float(match.ratio())
                match = match + (p['ratings'][-1]['ovr'] / 500)
                if str.lower(p['firstName']) in commandPlayerRaw or str.lower(p['lastName']) in commandPlayerRaw:
                    match = match + 1
                if match > bestMatch:
                    bestMatch = match
                    winningPid = p['pid']
                    bestOvr = p['ratings'][-1]['ovr']
                if match == bestMatch:
                    if p['ratings'][-1]['ovr'] > bestOvr:
                        bestMatch = match
                        winningPid = p['pid']
                        bestOvr = p['ratings'][-1]['ovr']
            for p in players:
                if p['pid'] == winningPid:
                    playerName = p['firstName'] + ' ' + p['lastName']
                    playerPos = p['ratings'][-1]['pos']
                    playerRating = str(p['ratings'][-1]['ovr']) + '/' + str(p['ratings'][-1]['pot'])
                    playerHOvr = p['ratings'][-1]['ovr']
                    playerHPot = p['ratings'][-1]['pot']
                    playerAge = str(season - p['born']['year'])
                    jerseyNumber = '00'
                    try: jerseyNumber = str(p['stats'][-1]['jerseyNumber'])
                    except: pass
                    playerTid = p['tid']
                    if commandSeason == "":
                        scrubVar = 1
                    else:
                        ratings = p['ratings']
                        for r in ratings:
                            if str(r['season']) == str(commandSeason):
                                playerPos = r['pos']
                                playerRating = str(r['ovr']) + '/' + str(r['pot'])
                                playerHOvr = r['ovr']
                                playerHPot = r['pot']
                                playerAge = str(int(commandSeason) - p['born']['year'])
                        stats = p['stats']
                        playerTid = -1
                        for s in stats:
                            if str(s['season']) == str(commandSeason):
                                playerTid = s['tid']
                                try: jerseyNumber = s['jerseyNumber']
                                except: pass
                        if int(commandSeason) <= p['draft']['year']:
                            playerTid = -2
                    if playerTid == -3:
                        playerTeam = 'Retired'
                        image = p['imgURL']
                        embedColor = 0x000000
                        playoffResult = "None"
                        onTeam = False
                    if playerTid == -2:
                        playerTeam = str(p['draft']['year']) + ' Draft Prospect'
                        image = p['imgURL']
                        embedColor = 0x000000
                        playoffResult = "None"
                        onTeam = False
                    if playerTid == -1:
                        playerTeam = 'Free Agent'
                        image = p['imgURL']
                        embedColor = 0x000000
                        playoffResult = "None"
                        onTeam = False
                    if playerTid > -1:
                        onTeam = True
                        for t in teams:
                            if t['tid'] == playerTid:
                                playerTeam = t['region'] + ' ' + t['name'] + ' (' + str(t['seasons'][-1]['won']) + '-' + str(t['seasons'][-1]['lost'])
                                if t['seasons'][-1]['otl'] > 0:
                                    playerTeam = playerTeam + '-' + str(t['seasons'][-1]['otl']) + ')'
                                else:
                                    playerTeam = playerTeam + ')'
                                image = t['seasons'][-1]['imgURL']
                                teamColor = int(t['colors'][0].replace("#", ""),16)
                                embedColor = int(hex(teamColor), 0)
                                playoffRoundsWon = t['seasons'][-1]['playoffRoundsWon']
                                if commandSeason == "":
                                    scrubVar = 1
                                else:
                                    seasons = t['seasons']
                                    for s in seasons:
                                        if str(s['season']) == str(commandSeason):
                                            playerTeam = s['region'] + ' ' + s['name'] + ' (' + str(s['won']) + '-' + str(s['lost'])
                                            teamOtl = 0
                                            try: teamOtl = s['otl']
                                            except: pass
                                            if teamOtl > 0:
                                                playerTeam = playerTeam + '-' + str(teamOtl) + ')'
                                            else:
                                                playerTeam = playerTeam + ')'
                                            image = s['imgURL']
                                            teamColor = int(s['colors'][0].replace("#", ""),16)
                                            embedColor = int(hex(teamColor), 0)
                                            playoffRoundsWon = s['playoffRoundsWon']
                    if playerTid > -1:
                        playoffSettings = settings['numGamesPlayoffSeries']
                        try: playoffRounds = len(playoffSettings[-1]['value'])
                        except: playoffRounds = len(playoffSettings)
                        if commandSeason == "":
                            scrubVar = 1
                        else:
                            commandSeason = int(commandSeason)
                            for ps in playoffSettings:
                                if ps['start'] == None:
                                    ps['start'] = 1900
                                if ps['start'] <= commandSeason:
                                    try: playoffRounds = len(ps['value'])
                                    except: playoffRounds - len(ps)
                        if playoffRoundsWon == -1:
                            playoffResult = 'Missed playoffs'
                        if playoffRoundsWon == 0:
                            playoffResult = 'Made 1st round'
                        if playoffRoundsWon == 1:
                            playoffResult = 'Made 2nd round'
                        if playoffRoundsWon == 2:
                            playoffResult = 'Made 3rd round'
                        if playoffRoundsWon == 3:
                            playoffResult = 'Made 4th round'
                        if playoffRoundsWon == playoffRounds:
                            playoffResult = 'League champions'
                        if playoffRoundsWon == (playoffRounds - 1):
                            playoffResult = 'Made finals'
                        if playoffRoundsWon == (playoffRounds - 2):
                            playoffResult = 'Made semifinals'

                    if commandSeason == "":
                        contractMoney = p['contract']['amount'] / 1000
                        bottomHeader = 'Contract: $' + str(contractMoney) + 'M / ' + str(p['contract']['exp'])
                        if playerTid == -1:
                            bottomHeader = bottomHeader.replace('Contract:', 'Request:')
                        if playerTid < -1:
                            bottomHeader = '---'
                        injury = p['injury']['type']
                        if injury == 'Healthy':
                            gamesOut = ''
                        else:
                            gamesOut = ' (out ' + str(p['injury']['gamesRemaining']) + ' more games)'
                        bottomText = injury + gamesOut
                    else:
                        commandSeason = int(commandSeason)
                        bottomHeader = 'Playoff result: ' + playoffResult
                        bottomText = "---"
            urlCheck = image.startswith('/img/')
            if urlCheck == True:
                image = image.replace('/img/', 'http://play.basketball-gm.com/img/')
            regularEmbed = discord.Embed(
                        title=playerName,
                        description=f'{playerPos}, {playerRating}, {playerAge} years | #{jerseyNumber}, {playerTeam}',
                        color=embedColor)
            regularEmbed.set_thumbnail(url=image)
            secondEmbed = False
            if command == 'stats':
                for p in players:
                    if p['pid'] == winningPid:
                        if commandSeason == "":
                            statSeason = season
                            try: statSeason = p['stats'][-1]['season']
                            except: pass
                        else:
                            statSeason = int(commandSeason)
                        async def find_stats(playoff):
                            if sport == 'basketball':
                                totalPts = 0
                                totalReb = 0
                                totalAst = 0
                                totalBlk = 0
                                totalStl = 0
                                totalTov = 0
                                totalPer = 0
                                totalMins = 0
                                totalFg = 0
                                totalFga = 0
                                totalTp = 0
                                totalTpa = 0
                                totalFt = 0
                                totalFta = 0
                                totalGames = 0
                                statTeams = []
                            if sport == 'hockey':
                                totalPts = 0
                                totalGl = 0
                                totalAst = 0
                                totalPm = 0
                                totalGames = 0
                                totalShots = 0
                                totalOps = 0
                                totalDps = 0
                                totalFcfW = 0
                                totalFcf = 0
                                totalPpToi = 0
                                totalToi = 0
                                totalBlk = 0
                                totalHit = 0
                                totalTk = 0
                                totalGa = 0
                                totalSv = 0
                                totalGps = 0
                                totalSo = 0
                                statTeams = []
                            stats = p['stats']
                            for s in stats:
                                if s['season'] == statSeason and s['playoffs'] == playoff:
                                    if sport == 'basketball':
                                        totalPts += s['pts']
                                        totalReb += s['drb']
                                        totalReb += s['orb']
                                        totalAst += s['ast']
                                        totalBlk += s['blk']
                                        totalStl += s['stl']
                                        totalTov += s['tov']
                                        totalPer += (s['per']*s['gp'])
                                        totalMins += s['min']
                                        totalFg += s['fg']
                                        totalFga += s['fga']
                                        totalTp += s['tp']
                                        totalTpa += s['tpa']
                                        totalFt += s['ft']
                                        totalFta += s['fta']
                                        totalGames += s['gp']
                                        if s['gp'] > 0:
                                            statTid = s['tid']
                                            for t in teams:
                                                if t['tid'] == statTid:
                                                    seasons = t['seasons']
                                                    for ts in seasons:
                                                        if ts['season'] == statSeason:
                                                            statTeams.append(ts['abbrev'])
                                    if sport == 'hockey':
                                        totalGl += s['evG'] + s['ppG'] + s['shG']
                                        totalAst += s['evA'] + s['ppA'] + s['shA']
                                        totalPts += s['evG'] + s['ppG'] + s['shG'] + s['evA'] + s['ppA'] + s['shA']
                                        totalToi += s['min']
                                        totalPpToi += s['ppMin']
                                        totalPm += s['pm']
                                        totalShots += s['s']
                                        totalOps += s['ops']
                                        totalDps += s['dps']
                                        totalFcf += s['fol'] + s['fow']
                                        totalFcfW += s['fow']
                                        totalBlk += s['blk']
                                        totalHit += s['hit']
                                        totalTk += s['tk']
                                        totalGa += s['ga']
                                        totalSv += s['sv']
                                        totalGps += s['gps']
                                        totalSo += s['so']
                                        totalGames += s['gp']
                                        if s['gp'] > 0:
                                            statTid = s['tid']
                                            for t in teams:
                                                if t['tid'] == statTid:
                                                    seasons = t['seasons']
                                                    for ts in seasons:
                                                        if ts['season'] == statSeason:
                                                            statTeams.append(ts['abbrev'])
                                        
                            if totalGames == 0:
                                basicStatline = "*No stats available.*"
                                effStatline = "*No stats available.*"
                                statTeamText = '(' + '/'.join(statTeams) + ')'
                                if statTeamText == '()':
                                    statTeamText = ''
                                embedHeader = str(statSeason) + ' Stats ' + statTeamText
                                if playoff == False:
                                    regularEmbed.add_field(name=embedHeader,value=basicStatline, inline=False)
                                    regularEmbed.add_field(name='Efficiency',value=effStatline, inline=False)
                                if playoff == True:
                                    secondaryEmbed.add_field(name=embedHeader,value=basicStatline, inline=False)
                                    secondaryEmbed.add_field(name='Efficiency',value=effStatline, inline=False)
                                    secondaryEmbed.add_field(name=bottomHeader,value=bottomText, inline=False)
                                    secondaryEmbed.set_footer(text="Click the ⬅️  arrow to see regular season stats | Made by ClevelandFan#6181")
                                    secondaryEmbed.set_thumbnail(url=image)
                            else:
                                if sport == 'basketball':
                                    averagePts = round(totalPts / totalGames, 1)
                                    averageReb = round(totalReb / totalGames, 1)
                                    averageAst = round(totalAst / totalGames, 1)
                                    averageBlk = round(totalBlk / totalGames, 1)
                                    averageStl = round(totalStl / totalGames, 1)
                                    averageTov = round(totalTov / totalGames, 1)
                                    averagePer = round(totalPer / totalGames, 1)
                                    averageMins = round(totalMins / totalGames, 1)
                                    averageFg = round(totalFg / (totalFga + 0.00000000000000000000001)*100, 1)
                                    averageTp = round(totalTp / (totalTpa + 0.00000000000000000000001)*100, 1)
                                    averageFt = round(totalFt / (totalFta + 0.00000000000000000000001)*100, 1)
                                    basicStatline = f'{str(averagePts)} pts, {str(averageReb)} reb, {str(averageAst)} ast, {str(averageBlk)} blk, {str(averageStl)} stl, {str(averageTov)} tov'
                                    effStatline = f'{str(totalGames)} GP, {str(averageMins)} MPG, {str(averagePer)} PER, {str(averageFg)}% FG, {str(averageTp)}% 3P, {str(averageFt)}% FT'
                                    statTeamText = '(' + '/'.join(statTeams) + ')'
                                    if playoff == False:
                                        embedHeader = str(statSeason) + ' Stats ' + statTeamText
                                        regularEmbed.add_field(name=embedHeader,value=basicStatline, inline=False)
                                        regularEmbed.add_field(name='Efficiency',value=effStatline, inline=False)
                                    if playoff == True:
                                        embedHeader = str(statSeason) + ' Stats ' + statTeamText
                                        secondaryEmbed.add_field(name=embedHeader,value=basicStatline, inline=False)
                                        secondaryEmbed.add_field(name='Efficiency',value=effStatline, inline=False)
                                        secondaryEmbed.add_field(name=bottomHeader,value=bottomText, inline=False)
                                        secondaryEmbed.set_footer(text="Click the ⬅️  arrow to see regular season stats | Made by ClevelandFan#6181")
                                        secondaryEmbed.set_thumbnail(url=image)
                                if sport == 'hockey':
                                    averageToi = round(totalToi / totalGames, 1)
                                    averagePpToi = round(totalPpToi / totalGames, 1)
                                    fcfStat = f'{str(round((totalFcfW / (totalFcf + 0.0000000000000000001))*100, 1))}% FCF ({str(totalFcfW)}/{str(totalFcf)})'
                                    averageSP = round((totalGl / (totalShots + 0.0000000000000000001))*100, 1)
                                    psStat = f'{str(round(totalOps + totalDps, 1))} PS ({str(round(totalOps, 1))} OPS, {str(round(totalDps, 1))} DPS)'
                                    svPc = round(totalSv / (totalSv + totalGa + 0.000000000000000000001), 3)
                                    svPc = str(svPc).replace('0.', '.')
                                    statTeamText = '(' + '/'.join(statTeams) + ')'
                                    if totalPm > 0:
                                        totalPm = '+' + str(totalPm)
                                    if playerPos == 'W':
                                        basicStatline = f'{totalPts} pts, {totalGl} G, {totalAst} A, {str(totalPm)} +/-, {psStat}'
                                        effStatline = f'{averageToi} average TOI ({averagePpToi} PP TOI), {str(averageSP)} S%'
                                        if playoff == False:
                                            embedHeader = str(statSeason) + ' Stats ' + statTeamText
                                            regularEmbed.add_field(name=embedHeader,value=basicStatline, inline=False)
                                            regularEmbed.add_field(name='Efficiency',value=effStatline, inline=False)
                                        if playoff == True:
                                            embedHeader = str(statSeason) + ' Stats ' + statTeamText
                                            secondaryEmbed.add_field(name=embedHeader,value=basicStatline, inline=False)
                                            secondaryEmbed.add_field(name='Efficiency',value=effStatline, inline=False)
                                            secondaryEmbed.add_field(name=bottomHeader,value=bottomText, inline=False)
                                            secondaryEmbed.set_footer(text="Click the ⬅️  arrow to see regular season stats | Made by ClevelandFan#6181")
                                            secondaryEmbed.set_thumbnail(url=image)
                                    if playerPos == 'C':
                                        basicStatline = f'{totalPts} pts, {totalGl} G, {totalAst} A, {str(totalPm)} +/-, {psStat}'
                                        effStatline = f'{averageToi} average TOI ({averagePpToi} PP TOI), {fcfStat}'
                                        if playoff == False:
                                            embedHeader = str(statSeason) + ' Stats ' + statTeamText
                                            regularEmbed.add_field(name=embedHeader,value=basicStatline, inline=False)
                                            regularEmbed.add_field(name='Efficiency',value=effStatline, inline=False)
                                        if playoff == True:
                                            embedHeader = str(statSeason) + ' Stats ' + statTeamText
                                            secondaryEmbed.add_field(name=embedHeader,value=basicStatline, inline=False)
                                            secondaryEmbed.add_field(name='Efficiency',value=effStatline, inline=False)
                                            secondaryEmbed.add_field(name=bottomHeader,value=bottomText, inline=False)
                                            secondaryEmbed.set_footer(text="Click the ⬅️  arrow to see regular season stats | Made by ClevelandFan#6181")
                                            secondaryEmbed.set_thumbnail(url=image)
                                    if playerPos == 'D':
                                        basicStatline = f'{totalPts} pts, {totalGl} G, {totalAst} A, {str(totalPm)} +/-, {psStat}'
                                        effStatline = f'{averageToi} average TOI ({averagePpToi} PP TOI), {str(totalBlk)} BLK, {str(totalHit)} HIT, {str(totalTk)} TK'
                                        if playoff == False:
                                            embedHeader = str(statSeason) + ' Stats ' + statTeamText
                                            regularEmbed.add_field(name=embedHeader,value=basicStatline, inline=False)
                                            regularEmbed.add_field(name='Defense/Efficiency',value=effStatline, inline=False)
                                        if playoff == True:
                                            embedHeader = str(statSeason) + ' Stats ' + statTeamText
                                            secondaryEmbed.add_field(name=embedHeader,value=basicStatline, inline=False)
                                            secondaryEmbed.add_field(name='Defense/Efficiency',value=effStatline, inline=False)
                                            secondaryEmbed.add_field(name=bottomHeader,value=bottomText, inline=False)
                                            secondaryEmbed.set_footer(text="Click the ⬅️  arrow to see regular season stats | Made by ClevelandFan#6181")
                                            secondaryEmbed.set_thumbnail(url=image)
                                    if playerPos == 'G':
                                        basicStatline = f'{totalGames} GP, {totalGa} goals allowed, {svPc} SV%, {round(totalGps, 1)} GPS'
                                        if playoff == False:
                                            embedHeader = str(statSeason) + ' Stats ' + statTeamText
                                            regularEmbed.add_field(name=embedHeader,value=basicStatline, inline=False)
                                        if playoff == True:
                                            embedHeader = str(statSeason) + ' Stats ' + statTeamText
                                            secondaryEmbed.add_field(name=embedHeader,value=basicStatline, inline=False)
                                            secondaryEmbed.add_field(name=bottomHeader,value=bottomText, inline=False)
                                            secondaryEmbed.set_footer(text="Click the ⬅️  arrow to see regular season stats | Made by ClevelandFan#6181")
                                            secondaryEmbed.set_thumbnail(url=image)


                                            


                        await find_stats(False)
                        secondaryEmbed = discord.Embed(
                                    title=playerName + ' Playoff Stats',
                                    description=f'{playerPos}, {playerRating}, {playerAge} years | #{jerseyNumber}, {playerTeam}',
                                    color=embedColor)
                        await find_stats(True)
                        secondEmbed = True
            if command == 'bio':
                for p in players:
                    if p['pid'] == winningPid:
                        stats = p['stats']
                        ratings = p['ratings']
                        #get jersey numbers
                        jerseyNumbers = []
                        for s in stats:
                            try: jerseyNumbers.append(s['jerseyNumber'])
                            except: pass
                        jerseyNumbers = list(dict.fromkeys(jerseyNumbers))
                        #get exp
                        expList = []
                        playoffYears = 0
                        for s in stats:
                            if s['gp'] > 0:
                                expList.append(s['season'])
                        expList = list(dict.fromkeys(expList))
                        expYears = len(expList)
                        for s in stats:
                            if s['playoffs'] == True:
                                playoffYears += 1
                        #get career stats
                        if sport == 'basketball':
                            totalPts = 0
                            totalReb = 0
                            totalAst = 0
                            totalPer = 0
                            totalGames = 0
                            for s in stats:
                                if s['playoffs'] == False:
                                    totalPts += s['pts']
                                    totalReb += s['orb'] + s['drb']
                                    totalAst += s['ast']
                                    totalPer += (s['per']*s['gp'])
                                    totalGames += s['gp']
                            if totalGames == 0:
                                careerStatline = '*No stats.*'
                            else:
                                averagePts = round(totalPts / totalGames, 1)
                                averageReb = round(totalReb / totalGames, 1)
                                averageAst = round(totalAst / totalGames, 1)
                                averagePer = round(totalPer / totalGames, 1)
                                careerStatline = f'{averagePts} pts, {averageReb} reb, {averageAst} ast, {averagePer} PER'
                        if sport == 'hockey':
                            totalGoals = 0
                            totalAst = 0
                            totalPts = 0
                            for s in stats:
                                totalGoals += s['evG'] + s['ppG'] + s['shG']
                                totalAst += s['evA'] + s['ppA'] + s['shA']
                                totalPts += s['evG'] + s['ppG'] + s['shG'] + s['evA'] + s['ppA'] + s['shA']
                            careerStatline = f'{totalPts} pts, {totalGoals} G, {totalAst} A'
                        #get physical/personal info
                        playerInches = divmod(p['hgt'], 12)
                        playerHeight = str(playerInches[0]) + "'" + str(playerInches[1]) + '"'
                        playerWeight = str(p['weight']) + 'lbs'
                        playerAgeText = str(playerAge) + ' (born ' + str(p['born']['year']) + ')'
                        playerCountry = p['born']['loc']
                        playerCollege = p['college']
                        if playerCollege == '':
                            playerCollege = 'None'
                        moodTraits = ' '.join(p['moodTraits'])
                        #get draft info
                        if p['draft']['tid'] == -1:
                            #for undrafted players, simple version
                            draftPick = 'Undrafted (' + str(p['draft']['year']) + ')'
                            draftRating = str(p['draft']['ovr']) + '/' + str(p['draft']['pot']) + ' at draft'
                            draftSection = draftPick + '\n' + draftRating
                        else:
                            draftPick = str(p['draft']['year']) + ' Round ' + str(p['draft']['round']) + ', Pick ' + str(p['draft']['pick'])
                            draftedTid = p['draft']['tid']
                            draftedYear = p['draft']['year']
                            for t in teams:
                                if t['tid'] == draftedTid:
                                    foundSeason = 0
                                    seasons = t['seasons']
                                    for s in seasons:
                                        if s['season'] == draftedYear:
                                            foundSeason = 1
                                            draftedTeam = s['region'] + ' ' + s['name']
                                    if foundSeason == 0:
                                        draftedTeam = t['seasons'][0]['region'] + ' ' + t['seasons'][0]['name']
                            draftRating = str(p['draft']['ovr']) + '/' + str(p['draft']['pot']) + ' at draft'
                            draftSection = draftPick + '\n' + draftedTeam + '\n' + draftRating
                        #set up the bio on the embed now
                        finalNumbers = ""
                        for j in jerseyNumbers:
                            finalNumbers = finalNumbers + str(j) + ' '
                        if finalNumbers == "":
                            finalNumbers = 'None'
                        expText = str(expYears) + ' years, ' + str(playoffYears) + ' playoff appearances'
                        if expText == '0 years, 0 playoff appearances':
                            expText = 'None'
                        leagueEmbed = '**Jersey Numbers:** ' + finalNumbers + '\n' + '**Experience:** ' + expText + '\n' + '**Career stats:** ' + careerStatline
                        regularEmbed.add_field(name='League',value=leagueEmbed, inline=False)
                        physicalEmbed = '**Height:** ' + playerHeight + '\n' + '**Weight:** ' + playerWeight + '\n' + '**Age:** ' + playerAgeText
                        regularEmbed.add_field(name='Physical',value=physicalEmbed, inline=True)
                        personalEmbed = '**Country:** ' + playerCountry + '\n' + '**College:** ' + playerCollege + '\n' + '**Mood Traits:** ' + moodTraits
                        regularEmbed.add_field(name='Personal',value=personalEmbed, inline=True)
                        regularEmbed.add_field(name='Draft',value=draftSection, inline=True)

            if command == 'ratings':
                for p in players:
                    if p['pid'] == winningPid:
                        if commandSeason == "":
                            commandSeason = p['ratings'][-1]['season']
                        else:
                            commandSeason = int(commandSeason)
                        ratings = p['ratings']
                        for r in ratings:
                            if r['season'] == commandSeason:
                                if sport == 'basketball':
                                    physicalBlock = '**Height:** ' + str(r['hgt']) + '\n' + '**Strength:** ' + str(r['stre']) + '\n' + '**Speed:** ' + str(r['spd']) + '\n' + '**Jumping:** ' + str(r['jmp']) + '\n' + '**Endurance:** ' + str(r['endu'])
                                    scoringBlock = '**Inside:** ' + str(r['ins']) + '\n' + '**Dunks/Layups:** ' + str(r['dnk']) + '\n' + '**Free Throws:** ' + str(r['ft']) + '\n' + '**Two Pointers:** ' + str(r['fg']) + '\n' + '**Three Pointers:** ' + str(r['tp'])
                                    skillBlock = '**Offensive IQ:** ' + str(r['oiq']) + '\n' + '**Defensive IQ:** ' + str(r['diq']) + '\n' + '**Dribbling:** ' + str(r['drb']) + '\n' + '**Passing:** ' + str(r['pss']) + '\n' + '**Rebounding:** ' + str(r['reb'])
                                    playerSkills = ""
                                    playerSkills = ' '.join(r['skills'])
                                    if playerSkills == "":
                                        playerSkills = 'None'
                                    regularEmbed.add_field(name='Physical',value=physicalBlock, inline=True)
                                    regularEmbed.add_field(name='Scoring',value=scoringBlock, inline=True)
                                    regularEmbed.add_field(name='Skill',value=skillBlock, inline=True)
                                    regularEmbed.add_field(name='Skills: ' + playerSkills,value='---')
                                if sport == 'hockey':
                                    physicalBlock = '**Height:** ' + str(r['hgt']) + '\n' + '**Strength:** ' + str(r['stre']) + '\n' + '**Speed:** ' + str(r['spd']) + '\n' + '**Endurance:** ' + str(r['endu'])
                                    offenseBlock = '**Offensive IQ:** ' + str(r['oiq']) + '\n' + '**Passing:** ' + str(r['pss']) + '\n' + '**Wristshot:** ' + str(r['wst']) + '\n' + '**Slapshot:** ' + str(r['sst']) + '\n' + '**Stickhandling:** ' + str(r['stk'])
                                    defenseBlock = '**Defensive IQ:** ' + str(r['diq']) + '\n' + '**Checking:** ' + str(r['chk']) + '\n' + '**Blocking:** ' + str(r['blk']) + '\n' + '**Faceoffs:** ' + str(r['fcf']) + '\n' + '**Goalkeeping:** ' + str(r['glk'])
                                    playerSkills = ""
                                    playerSkills = ' '.join(r['skills'])
                                    if playerSkills == "":
                                        playerSkills = 'None'
                                    regularEmbed.add_field(name='Physical',value=physicalBlock, inline=True)
                                    regularEmbed.add_field(name='Scoring',value=offenseBlock, inline=True)
                                    regularEmbed.add_field(name='Defense',value=defenseBlock, inline=True)
                                    regularEmbed.add_field(name='Skills: ' + playerSkills,value='---')
            if command == 'proghistory':
                for p in players:
                    if p['pid'] == winningPid:
                        #get the "drafted moment"
                        if p['draft']['tid'] == -1:
                            draftedMoment = playerName + ' went undrafted in the ' + str(p['draft']['year']) + ' draft.'
                        else:
                            draftedTid = p['draft']['tid']
                            for t in teams:
                                if t['tid'] == draftedTid:
                                    foundSeason = 0
                                    seasons = t['seasons']
                                    for s in seasons:
                                        if s['season'] == p['draft']['year']:
                                            foundSeason = 1
                                            draftedTeam = s['region'] + ' ' + s['name']
                                    if foundSeason == 0:
                                        draftedTeam = t['seasons'][0]['region'] + ' ' + t['seasons'][0]['name']
                            draftedRound = str(p['draft']['round'])
                            if p['draft']['round'] == 1:
                                draftedRound = '1st'
                            if p['draft']['round'] == 2:
                                draftedRound = '2nd'
                            if p['draft']['round'] == 3:
                                draftedRound = '3rd'
                            if p['draft']['round'] == 4:
                                draftedRound = '4th'
                            draftedMoment = str(p['draft']['year']) + ' - ' + playerName + ' was selected #' + str(p['draft']['pick']) + ' in the ' + draftedRound + ' round, by the ' + draftedTeam + '.'
                        #get the actual prog history
                        progHistory = draftedMoment + '\n'
                        ratings = p['ratings']
                        for r in ratings:
                            ratingAge = r['season'] - p['born']['year']
                            skills = ""
                            skills = ' '.join(r['skills'])
                            progHistory = progHistory + str(r['season']) + ' - ' + r['pos'] + ' ' + playerName + ' - ' + str(ratingAge) + ' yo ' + str(r['ovr']) + '/' + str(r['pot']) + ' ' + skills + '\n'
                        regularEmbed.add_field(name='Prog History', value=progHistory)

            if command == 'adv':
                if sport == 'basketball':
                    for p in players:
                        if p['pid'] == winningPid:
                            if commandSeason == "":
                                statSeason = season
                                try: statSeason = p['stats'][-1]['season']
                                except: pass
                            else:
                                statSeason = int(commandSeason)
                            async def find_stats(playoff):
                                totalGames = 0
                                totalMins = 0
                                totalPer = 0
                                totalEwa = 0
                                totalOws = 0
                                totalDws = 0
                                totalObpm = 0
                                totalDbpm = 0
                                totalVorp = 0
                                totalOrtg = 0
                                totalDrtg = 0
                                totalUsg = 0
                                totalTs = 0
                                totalAtRimA = 0.000000000000000001
                                totalAtRimM = 0
                                totalLowPostA = 0.000000000000000001
                                totalLowPostM = 0
                                totalMidRangeA = 0.000000000000000001
                                totalMidRangeM = 0
                                totalTpa = 0.000000000000000001
                                totalTp = 0
                                statTeams = []
                                stats = p['stats']
                                for s in stats:
                                    if s['season'] == statSeason and s['playoffs'] == playoff:
                                        totalGames += s['gp']
                                        totalMins += s['min']
                                        totalPer += (s['per']*s['gp'])
                                        totalEwa += s['ewa']
                                        totalOws += s['ows']
                                        totalDws += s['dws']
                                        totalObpm += s['obpm']*s['gp']
                                        totalDbpm += s['dbpm']*(s['gp'])
                                        totalVorp += s['vorp']
                                        totalOrtg += s['ortg']*s['gp']
                                        totalDrtg += s['drtg']*s['gp']
                                        totalUsg += s['usgp']*s['gp']
                                        totalAtRimA += s['fgaAtRim']
                                        totalAtRimM += s['fgAtRim']
                                        totalLowPostA += s['fgaLowPost']
                                        totalLowPostM += s['fgLowPost']
                                        totalMidRangeA += s['fgaMidRange']
                                        totalMidRangeM += s['fgMidRange']
                                        totalTpa += s['tpa']
                                        totalTp += s['tp']
                                        totalTs += ((s['pts'] /(2 * (s['fga'] + 0.44 * (s['fta'] + 0.000000000000000001)))) *100) * s['gp']
                                        if s['gp'] > 0:
                                            statTid = s['tid']
                                            for t in teams:
                                                if t['tid'] == statTid:
                                                    seasons = t['seasons']
                                                    for ts in seasons:
                                                        if ts['season'] == statSeason:
                                                            statTeams.append(ts['abbrev'])
                                            
                                if totalGames == 0:
                                    basicStatline = "*No stats available.*"
                                    effStatline = "*No stats available.*"
                                    statTeamText = '(' + '/'.join(statTeams) + ')'
                                    if statTeamText == '()':
                                        statTeamText = ''
                                    embedHeader = str(statSeason) + ' Stats ' + statTeamText
                                    if playoff == False:
                                        regularEmbed.add_field(name=embedHeader,value=basicStatline, inline=False)
                                        regularEmbed.add_field(name='Efficiency',value=effStatline, inline=False)
                                    if playoff == True:
                                        secondaryEmbed.add_field(name=embedHeader,value=basicStatline, inline=False)
                                        secondaryEmbed.add_field(name='Efficiency',value=effStatline, inline=False)
                                        secondaryEmbed.add_field(name=bottomHeader,value=bottomText, inline=False)
                                        secondaryEmbed.set_footer(text="Click the ⬅️  arrow to see regular season stats | Made by ClevelandFan#6181")
                                        secondaryEmbed.set_thumbnail(url=image)
                                else:
                                    averageMins = round(totalMins / totalGames, 1)
                                    averagePer = round(totalPer / totalGames, 1)
                                    endEwa = round(totalEwa, 1)
                                    endOws = round(totalOws, 1)
                                    endDws = round(totalDws, 1)
                                    endWs = round((totalOws + totalDws), 1)
                                    averageObpm = round(totalObpm / totalGames, 1)
                                    averageDbpm = round(totalDbpm / totalGames, 1)
                                    averageBpm = round((totalObpm + totalDbpm) / totalGames, 1)
                                    endVorp = round(totalVorp, 1)
                                    averageOrtg = round(totalOrtg / totalGames, 1)
                                    averageDrtg = round(totalDrtg / totalGames, 1)
                                    averageUsg = round(totalUsg / totalGames, 1)
                                    averageTs = round(totalTs / totalGames, 1)
                                    lowPostFinal = round((totalLowPostM / totalLowPostA)*100, 1)
                                    atRimFinal = round((totalAtRimM / totalAtRimA)*100, 1)
                                    midRangeFinal = round((totalMidRangeM / totalMidRangeA)*100, 1)
                                    tpFinal = round((totalTp / totalTpa)*100, 1)
                                    ws48 = round(endWs / totalMins * 48, 3)
                                    ws48 = str(ws48).replace('0.', '.')
                                    basicStatline = f'{totalGames} GP, {averageMins} MPG, {averagePer} PER, {endEwa} EWA, {averageBpm} BPM ({averageObpm} OBPM, {averageDbpm} DBPM), {endVorp} VORP'
                                    effStatline = f'{endWs} WS ({endOws} OWS, {endDws} DWS), {ws48} WS/48min, {averageOrtg} ORTg, {averageDrtg} DRTg, {averageUsg} USG%'
                                    shootingStatline = f'{atRimFinal}% at-rim, {lowPostFinal}% low post, {midRangeFinal}% mid-range, {tpFinal}% 3P, {averageTs}% TS'
                                    statTeamText = '(' + '/'.join(statTeams) + ')'
                                    if playoff == False:
                                        embedHeader = str(statSeason) + ' Stats ' + statTeamText + ' - Basic'
                                        regularEmbed.add_field(name=embedHeader,value=basicStatline, inline=False)
                                        regularEmbed.add_field(name='Team',value=effStatline, inline=False)
                                        regularEmbed.add_field(name='Shooting', value=shootingStatline)
                                    if playoff == True:
                                        embedHeader = str(statSeason) + ' Stats ' + statTeamText
                                        secondaryEmbed.add_field(name=embedHeader,value=basicStatline, inline=False)
                                        secondaryEmbed.add_field(name='Efficiency',value=effStatline, inline=False)
                                        secondaryEmbed.add_field(name=bottomHeader,value=bottomText, inline=False)
                                        secondaryEmbed.set_footer(text="Click the ⬅️  arrow to see regular season stats | Made by ClevelandFan#6181")
                                        secondaryEmbed.set_thumbnail(url=image)

                                                


                            await find_stats(False)
                            secondaryEmbed = discord.Embed(
                                        title=playerName + ' Playoff Stats',
                                        description=f'{playerPos}, {playerRating}, {playerAge} years | #{jerseyNumber}, {playerTeam}',
                                        color=embedColor)
                            await find_stats(True)
                            secondEmbed = True

                else:
                    regularEmbed.add_field(name='Error', value='*Advanced stats are not yet available for hockey or football.')
            if command == 'awards':
                for p in players:
                    if p['pid'] == winningPid:
                        awards = p['awards']
                        finalAwards = ""
                        totalAwards = []
                        for a in awards:
                            totalAwards.append(a['type'])
                        totalAwards = list(dict.fromkeys(totalAwards))
                        for t in totalAwards:
                            numAward = 0
                            awardSeasons = []
                            for a in awards:
                                if a['type'] == t:
                                    numAward += 1
                                    awardSeasons.append(str(a['season']))
                            awardYears = ', '.join(awardSeasons)
                            awardYears = '(' + awardYears + ')'
                            awardYears = awardYears.replace(', )', ')')
                            finalAwards = finalAwards + f'{numAward}x {t} {awardYears}' + '\n'
                        if finalAwards == "":
                            finalAwards = 'No awards!'
                        regularEmbed.add_field(name='Awards', value=finalAwards)
            if command == 'compare':
                if int(playerAge) > 23:
                    regularEmbed.add_field(name='Error', value='Comparisons are only available for players under 24.')
                else:
                    for p in players:
                        if p['pid'] == winningPid:
                            if sport == 'basketball':
                                r = p['ratings'][0]
                                hgt = r['hgt']
                                stre = r['stre']
                                spd = r['spd']
                                jmp = r['jmp']
                                endu = r['endu']
                                ins = r['ins']
                                dnk = r['dnk']
                                ft = r['ft']
                                fg = r['fg']
                                tp = r['tp']
                                oiq = r['oiq']
                                diq = r['diq']
                                drb = r['drb']
                                pss = r['pss']
                                reb = r['reb']
                            if sport == 'hockey':
                                r = p['ratings'][0]
                                hgt = r['hgt']
                                stre = r['stre']
                                spd = r['spd']
                                endu = r['endu']
                                pss = r['pss']
                                wst = r['wst']
                                sst = r['sst']
                                stk = r['stk']
                                oiq = r['oiq']
                                chk = r['chk']
                                blk = r['blk']
                                fcf = r['fcf']
                                diq = r['diq']
                                glk = r['glk']
                    #now we're gonna search ALL players for the best match
                    winningDiff = 1000000
                    for p in players:
                        #ensure the player peaked at 55 ovr at minimum and is over 23, AND is better than our winningPlayer AND (just keep adding) does not match winningPid
                        playerRatings = p['ratings']
                        approved = 0
                        for pr in playerRatings:
                            if pr['ovr'] > 54 and pr['ovr'] > playerHOvr and pr['ovr'] > (playerHPot*0.90):
                                approved = 1
                        scanAge = season - p['born']['year']
                        if approved < 1 or scanAge < 24 or p['pid'] == winningPid:
                            continue
                        else:
                            r = p['ratings'][0]
                            if sport == 'basketball':
                                hgtDff = abs(r['hgt'] - hgt)*4
                                streDff = abs(r['stre'] - stre)
                                spdDff = abs(r['spd'] - spd)*2
                                jmpDff = abs(r['jmp'] - jmp)*2
                                enduDff = abs(r['endu'] - endu)
                                insDff = abs(r['ins'] - ins)*1.5
                                dnkDff = abs(r['dnk'] - dnk)
                                ftDff = abs(r['ft'] - ft)
                                fgDff = abs(r['fg'] - fg)
                                tpDff = abs(r['tp'] - tp)*1.5
                                oiqDff = abs(r['oiq'] - oiq)
                                diqDff = abs(r['diq'] - diq)
                                drbDff = abs(r['drb'] - drb)
                                pssDff = abs(r['pss'] - pss)*1.5
                                rebDff = abs(r['reb'] - reb)
                                totalDiff = hgtDff + streDff + spdDff + jmpDff + enduDff + insDff + dnkDff + ftDff + fgDff + tpDff + oiqDff + diqDff + drbDff + pssDff + rebDff
                                if totalDiff < winningDiff:
                                    winningDiff = totalDiff
                                    comparePid = p['pid']
                            if sport == 'hockey':
                                hgtDff = abs(r['hgt'] - hgt)
                                streDff = abs(r['stre'] - stre)
                                spdDff = abs(r['spd'] - spd)
                                enduDff = abs(r['endu'] - endu)
                                pssDff = abs(r['pss'] - pss)
                                wstDff = abs(r['wst'] - wst)
                                sstDff = abs(r['sst'] - sst)
                                stkDff = abs(r['stk'] - stk)
                                oiqDff = abs(r['oiq'] - oiq)
                                chkDff = abs(r['chk'] - chk)
                                blkDff = abs(r['blk'] - blk)
                                diqDff = abs(r['diq'] - diq)
                                fcfDff = abs(r['fcf'] - fcf)
                                glkDff = abs(r['glk'] - glk)
                                if playerPos == 'G':
                                    totalDiff = hgtDff + glkDff
                                else:
                                    totalDiff = hgtDff + streDff + spdDff + enduDff + pssDff + wstDff + sstDff + stkDff + oiqDff + chkDff + blkDff + diqDff + fcfDff
                                if totalDiff < winningDiff:
                                    winningDiff = totalDiff
                                    comparePid = p['pid']
                    #we have the comparison, finishing touches now...
                    for p in players:
                        if p['pid'] == comparePid:
                            compareisonName = p['firstName'] + ' ' + p['lastName']
                            ratings = p['ratings']
                            peakOvr = 0
                            peakSeason = 0
                            peakPot = 0
                            ratingsSeen = 0
                            for r in ratings:
                                ratingsSeen += 1
                                #purpose of this is just to taint it towards a younger version of the player, since they're more likely to match the DP
                                if r['ovr'] > (peakOvr + (0.33*ratingsSeen)):
                                    peakOvr = r['ovr']
                                    peakPot = r['pot']
                                    peakSeason = r['season']
                                    peakPos = r['pos']
                            #simple stat-pulling code, based off the bio career stats thing but only scanning for peakSeason
                            stats = p['stats']
                            if sport == 'basketball':
                                totalPts = 0
                                totalReb = 0
                                totalAst = 0
                                totalPer = 0
                                totalGames = 0
                                for s in stats:
                                    if s['playoffs'] == False and s['season'] == peakSeason:
                                        totalPts += s['pts']
                                        totalReb += s['orb'] + s['drb']
                                        totalAst += s['ast']
                                        totalPer += (s['per']*s['gp'])
                                        totalGames += s['gp']
                                if totalGames == 0:
                                    careerStatline = '*No stats.*'
                                else:
                                    averagePts = round(totalPts / totalGames, 1)
                                    averageReb = round(totalReb / totalGames, 1)
                                    averageAst = round(totalAst / totalGames, 1)
                                    averagePer = round(totalPer / totalGames, 1)
                                    compStatline = f'{peakSeason}: {averagePts} pts, {averageReb} reb, {averageAst} ast, {averagePer} PER'
                            if sport == 'hockey':
                                totalGoals = 0
                                totalAst = 0
                                totalPts = 0
                                for s in stats:
                                    if s['playoffs'] == False and s['season'] == peakSeason:
                                        totalGoals += s['evG'] + s['ppG'] + s['shG']
                                        totalAst += s['evA'] + s['ppA'] + s['shA']
                                        totalPts += s['evG'] + s['ppG'] + s['shG'] + s['evA'] + s['ppA'] + s['shA']
                                compStatline = f'{peakSeason}: {totalPts} pts, {totalGoals} G, {totalAst} A'
                            regularEmbed.add_field(name=f'**Comparison:** {peakSeason} {compareisonName} ({peakOvr}/{peakPot})', value=compStatline)

            if command == 'splits':
                if sport == 'basketball':
                    messageContentComma = messageContentComma.replace(' ', '')
                    if messageContentComma == "":
                        regularEmbed.add_field(name='Error', value='No split information provided, (add the usages here)')
                    else:
                        splitsType = str.lower(messageContentComma.replace("0", "").replace("1", "").replace("2", "").replace("3", "").replace("4", "").replace("5", "").replace("6", "").replace("7", "").replace("8", "").replace("9", ""))
                        splitsLength = int("".join(filter(str.isdigit, messageContentComma)))
                        if games == "":
                            regularEmbed.add_field(name='Error', value='No box scores found in this export.')
                        else:
                            gameList = []
                            for g in games:
                                gameTeams = g['teams']
                                for gt in gameTeams:
                                    gamePlayers = gt['players']
                                    for gp in gamePlayers:
                                        if gp['pid'] == winningPid and gp['min'] > 0:
                                            rebounds = gp['orb'] + gp['drb']
                                            gameList.append("{} {} {} {} {} {} {} {} {} {} {} {} {}".format(gp['pts'], rebounds, gp['ast'], gp['blk'], gp['stl'], gp['tov'], gp['fg'], gp['tp'], gp['ft'], gp['min'], gp['fga'], gp['tpa'], gp['fta']))
                            splitsText = ""
                            if splitsType == 'f':
                                splitsText = 'First '
                                gameList = gameList[:splitsLength]
                            else:
                                if splitsType == 'l':
                                    splitsText = 'Last '
                                    splitsLength = -splitsLength
                                    gameList = gameList[splitsLength:]
                                else:
                                    regularEmbed.add_field(name='Error', value='Please use L or F after the comma to indicate first or last X games.', inline=False)
                            totalPts = 0
                            totalReb = 0
                            totalAst = 0
                            totalBlk = 0
                            totalStl = 0
                            totalTov = 0
                            totalFg = 0
                            totalFga = 0.0000000000000000001
                            totalTpa = 0.0000000000000000001
                            totalTp = 0
                            totalFta = 0.000000000000000001
                            totalFt = 0
                            totalMins = 0
                            gamesPlayed = 0
                            for y in gameList:
                                x = y.split()
                                gamesPlayed += 1
                                totalPts += float(x[0])
                                totalReb += float(x[1])
                                totalAst += float(x[2])
                                totalBlk += float(x[3])
                                totalStl += float(x[4])
                                totalTov += float(x[5])
                                totalFg += float(x[6])
                                totalTp += float(x[7])
                                totalFt += float(x[8])
                                totalMins += float(x[9])
                                totalFga += float(x[10])
                                totalTpa += float(x[11])
                                totalFta += float(x[12])
                            ptsGame = round(totalPts / gamesPlayed, 1)
                            rebGame = round(totalReb / gamesPlayed, 1)
                            astGame = round(totalAst / gamesPlayed, 1)
                            blkGame = round(totalBlk / gamesPlayed, 1)
                            stlGame = round(totalStl / gamesPlayed, 1)
                            tovGame = round(totalTov / gamesPlayed, 1)
                            fgAvg = round(totalFg / (totalFga + 0.001)*100, 1)
                            tpAvg = round(totalTp / (totalTpa + 0.001)*100, 1)
                            ftAvg = round(totalFt / (totalFta + 0.001)*100, 1)
                            minAvg = round(totalMins / gamesPlayed, 1)
                            finalSplitline = f'{str(ptsGame)} pts, {str(rebGame)} reb, {str(astGame)} ast, {str(blkGame)} blk, {str(stlGame)} stl, {str(tovGame)} tov, {str(fgAvg)} FG%, {str(tpAvg)} 3PT%, {str(ftAvg)} FT%, {str(minAvg)} MPG'
                            regularEmbed.add_field(name=f'{splitsText}{len(gameList)} Games', value=finalSplitline)
                        
                                                                        


                else:
                    regularEmbed.add_field(name='Error', value='Splits is not yet supported for hockey.')                                                             



 






            #Send the final embed, set up the arrow switcher if there's two embeds
            regularEmbed.add_field(name=bottomHeader,value=bottomText, inline=False)
            if secondEmbed == True:
                regularEmbed.set_footer(text="Click the ➡️  arrow to see playoff stats | Made by ClevelandFan#6181")
            else:
                regularEmbed.set_footer(text="Made by ClevelandFan#6181")
            botEmbed = await message.channel.send(embed=regularEmbed)
            if secondEmbed == True:
                await botEmbed.add_reaction('⬅️')
                await botEmbed.add_reaction('➡️')
                for i in range(10):
                    def check(reaction, user):
                        return reaction.message == botEmbed and user == message.author and str(reaction.emoji) == '➡️'
                    try:
                        reaction, user = await client.wait_for('reaction_add', timeout=120.0, check=check)
                    except asyncio.TimeoutError:
                        scrubVar = 1
                    else:
                        await botEmbed.edit(content='', embed=secondaryEmbed)
                        await botEmbed.remove_reaction('➡️', message.author)
                    def check(reaction, user):
                        return reaction.message == botEmbed and user == message.author and str(reaction.emoji) == '⬅️'
                    try:
                        reaction, user = await client.wait_for('reaction_add', timeout=120.0, check=check)
                    except asyncio.TimeoutError:
                        scrubVar = 1
                    else:
                        await botEmbed.edit(content='', embed=regularEmbed)
                        await botEmbed.remove_reaction('⬅️', message.author)
            #cooldown to prevent overloads


        if command in teamCommands:
            with open(f'{message.guild.id}.json', 'r', encoding='utf-8-sig') as file:
                    export = json.load(file)
                    export['meta']['phaseText'] = 'Undefined phase'
                    players = export['players']
                    teams = export['teams']
                    settings = export['gameAttributes']
                    games = ""
                    try: games = export['games']
                    except: pass
                    schedule = ""
                    try: schedule = export['schedule']
                    except: pass
                    if 'sst' in players[0]['ratings'][0]:
                        sport = 'hockey'
                    if 'drb' in players[0]['ratings'][0]:
                        sport = 'basketball'
                    #meta stuff
                    season = settings['season']
                    phaseText = export['meta']['phaseText'].split(' ')
                    phase = phaseText[1]
                    picks = export['draftPicks']
            commandTeam = messageContent.replace("0", "").replace("1", "").replace("2", "").replace("3", "").replace("4", "").replace("5", "").replace("6", "").replace("7", "").replace("8", "").replace("9", "")
            commandSeason = "".join(filter(str.isdigit, messageContent))
            commandTeam = str.lower(commandTeam)
            commandTeam = commandTeam.replace(' ', '')
            teamFound = 0
            for t in teams:
                if str.lower(t['abbrev']) == commandTeam or str.lower(t['region']) == commandTeam or str.lower(t['name']) == commandTeam:
                    winningTid = t['tid']
                    teamFound = 1
            if teamFound == 0:
                bestMatch = 0
                for t in teams:
                    teamName = t['region'] + ' ' + t['name']
                    teamName = str.lower(teamName)
                    match = SequenceMatcher(a=commandTeam, b=teamName)
                    if float(match.ratio()) > bestMatch:
                        bestMatch = float(match.ratio())
                        winningTid = t['tid']
            for t in teams:
                if t['tid'] == winningTid:
                    teamName = t['region'] + ' ' + t['name']
                    teamAbbrev = t['abbrev']
                    ls = t['seasons'][-1]
                    teamRecord = str(season) + ' record: ' + str(ls['won']) + '-' + str(ls['lost'])
                    playoffRoundsWon = ls['playoffRoundsWon']
                    playoffRounds = len(settings['numGamesPlayoffSeries'][-1]['value'])
                    teamColor = int(t['colors'][0].replace("#", ""),16)
                    embedColor = int(hex(teamColor), 0)
                    image = t['imgURL']
                    if playoffRoundsWon == -1:
                        playoffResult = 'missed playoffs'
                    if playoffRoundsWon == 0:
                        playoffResult = 'made 1st round'
                    if playoffRoundsWon == 1:
                        playoffResult = 'made 2nd round'
                    if playoffRoundsWon == 2:
                        playoffResult = 'made 3rd round'
                    if playoffRoundsWon == 3:
                        playoffResult = 'made 4th round'
                    if playoffRoundsWon == playoffRounds:
                        playoffResult = '**league champions**'
                    if playoffRoundsWon == (playoffRounds - 1):
                        playoffResult = 'made finals'
                    if playoffRoundsWon == (playoffRounds - 2):
                        playoffResult = 'made semifinals'
                    if commandSeason == "":
                        scrubVar = 1
                    else:
                        commandSeason = int(commandSeason)
                        seasons = t['seasons']
                        for s in seasons:
                            if s['season'] == commandSeason:
                                teamName = s['region'] + ' ' + s['name']
                                teamRecord = str(s['season']) + ' record: ' + str(s['won']) + '-' + str(s['lost'])
                                teamAbbrev = s['abbrev']
                                playoffSettings = settings['numGamesPlayoffSeries']
                                image = s['imgURL']
                                for ps in playoffSettings:
                                    if ps['start'] == None:
                                        ps['start'] = 1900
                                    if ps['start'] <= commandSeason:
                                        playoffRounds = len(ps['value'])
                                playoffRoundsWon = s['playoffRoundsWon']
                                if playoffRoundsWon == -1:
                                    playoffResult = 'missed playoffs'
                                if playoffRoundsWon == 0:
                                    playoffResult = 'made 1st round'
                                if playoffRoundsWon == 1:
                                    playoffResult = 'made 2nd round'
                                if playoffRoundsWon == 2:
                                    playoffResult = 'made 3rd round'
                                if playoffRoundsWon == 3:
                                    playoffResult = 'made 4th round'
                                if playoffRoundsWon == playoffRounds:
                                    playoffResult = '**league champions**'
                                if playoffRoundsWon == (playoffRounds - 1):
                                    playoffResult = 'made finals'
                                if playoffRoundsWon == (playoffRounds - 2):
                                    playoffResult = 'made semifinals'
                                teamColor = int(t['colors'][0].replace("#", ""),16)
                                embedColor = int(hex(teamColor), 0)
            if image.startswith('/img/'):
                image = ""
            regularEmbed = discord.Embed(
                        title=teamName,
                        description=f'{teamRecord}, {playoffResult}',
                        color=embedColor)
            regularEmbed.set_thumbnail(url=image)
            secondEmbed = False


            #time for the actual commands
            if command == 'roster':
                infoSeason = season
                #first part is collecting the players. We need two different methods, one if user asked for current roster and one if they asked for historic
                if commandSeason == "":
                    #get everyone with said tid
                    teamRoster = []
                    for p in players:
                        if p['tid'] == winningTid:
                            rosterOrder = 100
                            try: rosterOrder = p['rosterOrder']
                            except: pass
                            teamRoster.append("{} {} {}".format(p['pid'], rosterOrder, season))
                    teamRoster.sort(key=lambda l: int(l.split(' ')[1]), reverse=False)
                else:
                    commandSeason = int(commandSeason)
                    teamRoster = []
                    #find players who's final stat TID from that season matches
                    for p in players:
                        finalTid = None
                        stats = p['stats']
                        for s in stats:
                            if s['season'] == commandSeason:
                                finalTid = s['tid']
                        if finalTid == winningTid:
                            ratings = p['ratings']
                            for r in ratings:
                                if r['season'] == commandSeason:
                                    playerOvr = r['ovr']
                            teamRoster.append("{} {} {}".format(p['pid'], playerOvr, commandSeason))
                    teamRoster.sort(key=lambda l: int(l.split(' ')[1]), reverse=True)
                #list grabbed, now to put it into the final roster output... gonna set it to just top 15 first
                teamRoster = teamRoster[:13]
                contractRoster = ""
                statRoster = ""
                ratings = [0,0,0,0,0,0,0,0,0,0]
                for tr in teamRoster:
                    x = tr.split(' ')
                    pid = x[0]
                    infoSeason = x[2]
                    for p in players:
                        if p['pid'] == int(pid):
                            playerName = p['firstName'] + ' ' + p['lastName']
                            playerAge = int(infoSeason) - p['born']['year']
                            playerContract = '$' + str(p['contract']['amount'] / 1000) + 'M/' + str(p['contract']['exp'])
                            playerRatings = p['ratings']
                            for r in playerRatings:
                                if r['season'] == int(infoSeason):
                                    playerPos = r['pos']
                                    playerRating = str(r['ovr']) + '/' + str(r['pot'])
                                    ratings.append(r['ovr'])
                            #once again using a stat finder ripped off from -bio and -compare
                            stats = p['stats']
                            if sport == 'basketball':
                                totalPts = 0
                                totalReb = 0
                                totalAst = 0
                                totalPer = 0
                                totalGames = 0
                                for s in stats:
                                    if s['playoffs'] == False and s['season'] == int(infoSeason):
                                        totalPts += s['pts']
                                        totalReb += s['orb'] + s['drb']
                                        totalAst += s['ast']
                                        totalPer += (s['per']*s['gp'])
                                        totalGames += s['gp']
                                if totalGames == 0:
                                    statline = '*No stats.*'
                                else:
                                    averagePts = round(totalPts / totalGames, 1)
                                    averageReb = round(totalReb / totalGames, 1)
                                    averageAst = round(totalAst / totalGames, 1)
                                    averagePer = round(totalPer / totalGames, 1)
                                    statline = f'``{averagePts} pts, {averageReb} reb, {averageAst} ast, {averagePer} PER``'
                            if sport == 'hockey':
                                totalGoals = 0
                                totalAst = 0
                                totalPts = 0
                                for s in stats:
                                    if s['playoffs'] == False and s['season'] == int(infoSeason):
                                        totalGoals += s['evG'] + s['ppG'] + s['shG']
                                        totalAst += s['evA'] + s['ppA'] + s['shA']
                                        totalPts += s['evG'] + s['ppG'] + s['shG'] + s['evA'] + s['ppA'] + s['shA']
                                statline = f'``{totalPts} pts, {totalGoals} G, {totalAst} A``'
                            contractRoster = contractRoster + f'{playerPos} **{playerName}** {playerAge} yo {playerRating} | {playerContract}' + '\n'     
                            statRoster = statRoster + f'{playerPos} **{playerName}** {playerAge} yo {playerRating} | {statline}' + '\n'   
                #calculate team rating
                ratings.sort(reverse=True)
                if len(ratings) > 9:
                    teamRatingSpread = -124.13 + 0.4417 * math.exp(-0.1905 * 0) * ratings[0] + 0.4417 * math.exp(-0.1905 * 1) * ratings[1] + 0.4417 * math.exp(-0.1905 * 2) * ratings[2] + 0.4417 * math.exp(-0.1905 * 3) * ratings[3] + 0.4417 * math.exp(-0.1905 * 4) * ratings[4] + 0.4417 * math.exp(-0.1905 * 5) * ratings[5] + 0.4417 * math.exp(-0.1905 * 6) * ratings[6] + 0.4417 * math.exp(-0.1905 * 7) * ratings[7] + 0.4417 * math.exp(-0.1905 * 8) * ratings[8] + 0.4417 * math.exp(-0.1905 * 9) * ratings[9] + 0.4417 * math.exp(-0.1905 * 10)
                    teamRating = (teamRatingSpread * 50)/20 + 50
                    teamRating = str(round(teamRating)) + '/100'
                else:
                    teamRating = 'Can not calculate'
                #rosters created, now we'll decide how to handle the embed based on historic or not
                secondaryEmbed = discord.Embed(
                            title=teamName + ' (Stats)',
                            description=f'{teamRecord}, {playoffResult}',
                            color=embedColor)
                if commandSeason == "":
                    #calculate payroll
                    teamPayroll = 0
                    for p in players:
                        if p['tid'] == winningTid:
                            teamPayroll += p['contract']['amount']
                    releasedPlayers = ""
                    try: releasedPlayers = export['releasedPlayers']
                    except: pass
                    if releasedPlayers == "":
                        scrubVar = 1
                    else:
                        for x in releasedPlayers:
                            if x['tid'] == winningTid:
                                teamPayroll += x['contract']['amount']
                    salaryCap = settings['salaryCap'] / 1000
                    salaryCap = f'Salary cap: ${salaryCap}M'
                    teamPayroll = f'Payroll: ${teamPayroll / 1000}M'
                    regularEmbed.add_field(name=teamAbbrev + ' ' + str(infoSeason) + ' Roster (TR: ' + teamRating + ')', value=contractRoster, inline=False)
                    regularEmbed.add_field(name=teamPayroll, value=salaryCap, inline=False)
                    secondaryEmbed.add_field(name=teamAbbrev + ' ' + str(infoSeason) + ' Roster (TR: ' + teamRating + ')', value=statRoster)
                    secondaryEmbed.set_footer(text="Click the ⬅️  arrow to see contracts | Made by ClevelandFan#6181")   
                    secondEmbed = True
                else:
                    regularEmbed.add_field   (name=teamAbbrev + ' ' + str(infoSeason) + ' Roster (TR: ' + teamRating + ')', value=statRoster)  
                    secondEmbed = False

            if command == 'picks':
                #short and simple
                teamPicks = ""
                for p in picks:
                    if p['tid'] == winningTid:
                        pickOg = p['originalTid']
                        for t in teams:
                            if t['tid'] == pickOg:
                                pickTeam = t['abbrev']
                        pickSeason = p['season']
                        pickRound = p['round']
                        pick = f'{pickSeason} {pickRound} round pick ({pickTeam})'
                        pick = pick.replace('1 round', '1st round').replace('2 round', '2nd round').replace('3 round', '3rd round').replace('4 round', '4th round')
                        if pickRound == 1:
                            pick = '**' + pick + '**'
                        teamPicks = teamPicks + pick + '\n'
                regularEmbed.add_field(name=teamAbbrev + ' Picks', value=teamPicks)

            if command == 'pyramid' or command == 'sos':
                #first to calculate average TR of the league for pryamid win
                totalTr = 0
                for t in teams:
                    #two things in this loop: first part is calculating TR for every team
                    ratings = [0,0,0,0,0,0,0,0,0,0]
                    numPlayers = 0
                    for p in players:
                        if p['tid'] == t['tid']:
                            ratings.append(p['ratings'][-1]['ovr'])
                            numPlayers += 1
                    ratings.sort(reverse=True)
                    teamRatingSpread = -124.13 + 0.4417 * math.exp(-0.1905 * 0) * ratings[0] + 0.4417 * math.exp(-0.1905 * 1) * ratings[1] + 0.4417 * math.exp(-0.1905 * 2) * ratings[2] + 0.4417 * math.exp(-0.1905 * 3) * ratings[3] + 0.4417 * math.exp(-0.1905 * 4) * ratings[4] + 0.4417 * math.exp(-0.1905 * 5) * ratings[5] + 0.4417 * math.exp(-0.1905 * 6) * ratings[6] + 0.4417 * math.exp(-0.1905 * 7) * ratings[7] + 0.4417 * math.exp(-0.1905 * 8) * ratings[8] + 0.4417 * math.exp(-0.1905 * 9) * ratings[9]
                    teamRating = (teamRatingSpread * 50)/20 + 50
                    if teamRating < 0:
                        teamRating = 0
                    totalTr += teamRating
                    #now we check if it's the team in question, grab info if so
                    if t['tid'] == winningTid:
                        teamTr = teamRating
                        gamesWon = t['seasons'][-1]['won']
                        gamesLost = t['seasons'][-1]['lost']
                #divide team TR by the average TR
                x = teamTr / (totalTr / len(teams))
                #find wack divide number (credit: Grim Reaper)
                divNum = ((2/3) * x) + 7/6
                #pyramid win%
                predictedWp = x / divNum

                #obsolete code (moved to after SOS calculation)
                # pyramidWins = predictedWp * (settings['numGames'] - (gamesWon + gamesLost))
                # predictedLoses = (settings['numGames'] - (gamesWon + gamesLost)) - pyramidWins

                #calculate SOS... this will be used in a few places
                opponentWins = 0
                opponentLoses = 0
                if schedule == "":
                    sosText = "No schedule found in this export."
                    sos = 0.5
                else:
                    for g in schedule:
                        if g['homeTid'] == winningTid:
                            for t in teams:
                                if t['tid'] == g['awayTid']:
                                    opponentWins += t['seasons'][-1]['won']
                                    opponentLoses += t['seasons'][-1]['lost']
                        if g['awayTid'] == winningTid:
                            for t in teams:
                                if t['tid'] == g['homeTid']:
                                    opponentWins += t['seasons'][-1]['won']
                                    opponentLoses += t['seasons'][-1]['lost']
                    sos = round(opponentWins / (opponentWins + opponentLoses), 3)
                    sosText = str(sos).replace('0.', '.')
                
                pyramidSos = (0 - sos) + 1.5
                predictedWp = predictedWp*pyramidSos
                pyramidWin = round(predictedWp * (settings['numGames'] - (gamesWon + gamesLost)), 1)
                pyramidWins = pyramidWin + gamesWon
                pyramidLoses = round((settings['numGames'] - (gamesWon + gamesLost)) - pyramidWin, 1)
                pyramidLoses = pyramidLoses + gamesLost
                #if they used depricated -sos command, add a field for that
                if command == 'sos':
                    regularEmbed.add_field(name='-sos has moved', value='-pyramid and -sos have been merged into one command, now just -pyramid. -sos will still redirect you here temporarily.', inline=False)
                regularEmbed.add_field(name=teamAbbrev + ' Projected Record: ' + str(pyramidWins) + '-' + str(pyramidLoses), value='Team SOS: ' + str(sosText) + '\n' + 'Pyramid win% (does not factor played games): ' + str(round(predictedWp, 3)).replace('0.', '.'), inline=False)
                secondaryEmbed = discord.Embed(
                            title=teamName + ' (Stats)',
                            description=f'{teamRecord}, {playoffResult}',
                            color=embedColor)
                secondaryEmbed.add_field(name='How Pyramid Wins Work', value="*The pyramid projected record factors in games already played (it only does 'projections' for games remaining on the schedule, and adds them to current record), team rating, and strength of schedule. It does not factor injuries, stats, or team makeup (so consider differing from the pyramid record to tell a story about roster construction). The way it works is it compares a team rating to the league average team rating (a team with exactly the average would have a .500 pyramid win %, not accounting for schedule) and then applying a boost for a weak schedule and vice versa.*")
                secondaryEmbed.set_footer(text="Click the ⬅️  arrow to go pack to the pyramid wins projection | Made by ClevelandFan#6181")   
                secondEmbed = True

            #send the embed and set up second embed
            if secondEmbed == True:
                if command == 'roster':
                    regularEmbed.set_footer(text="Click the ➡️  arrow to see stats | Made by ClevelandFan#6181")
                if command == 'pyramid':
                    regularEmbed.set_footer(text='Click the ➡️  arrow to see how pyramid wins work | Made by ClevelandFan#6181')
            else:
                regularEmbed.set_footer(text="Made by ClevelandFan#6181")
            #send the actual embed
            botEmbed = await message.channel.send(embed=regularEmbed)
            if secondEmbed == True:
                await botEmbed.add_reaction('⬅️')
                await botEmbed.add_reaction('➡️')
                for i in range(10):
                    def check(reaction, user):
                        return reaction.message == botEmbed and user == message.author and str(reaction.emoji) == '➡️'
                    try:
                        reaction, user = await client.wait_for('reaction_add', timeout=120.0, check=check)
                    except asyncio.TimeoutError:
                        scrubVar = 1
                    else:
                        await botEmbed.edit(content='', embed=secondaryEmbed)
                        await botEmbed.remove_reaction('➡️', message.author)
                    def check(reaction, user):
                        return reaction.message == botEmbed and user == message.author and str(reaction.emoji) == '⬅️'
                    try:
                        reaction, user = await client.wait_for('reaction_add', timeout=120.0, check=check)
                    except asyncio.TimeoutError:
                        scrubVar = 1
                    else:
                        await botEmbed.edit(content='', embed=regularEmbed)
                        await botEmbed.remove_reaction('⬅️', message.author)
            #cooldown to prevent overloads
        
        if command in leagueCommands:
            with open(f'{message.guild.id}.json', 'r', encoding='utf-8-sig') as file:
                    export = json.load(file)
                    export['meta']['phaseText'] = 'Undefined phase'
                    players = export['players']
                    teams = export['teams']
                    settings = export['gameAttributes']
                    games = ""
                    try: games = export['games']
                    except: pass
                    schedule = ""
                    try: schedule = export['schedule']
                    except: pass
                    if 'sst' in players[0]['ratings'][0]:
                        sport = 'hockey'
                    if 'drb' in players[0]['ratings'][0]:
                        sport = 'basketball'
                    #meta stuff
                    season = settings['season']
                    phaseText = export['meta']['phaseText']
                    phase = phaseText.split(' ')[1]
                    picks = export['draftPicks']
            
            number = "".join(filter(str.isdigit, messageContent))

            regularEmbed = discord.Embed(
                    title=message.guild.name,
                    description=str(phaseText),
                    color=0x000000)
            secondEmbed = False


            if command == 'fa':
                if number == "":
                    number = 10
                else:
                    number = int(number)
                    if number > 25:
                        number = 25
                        regularEmbed.add_field(name='Error',value="You can only view up to 25 free agents due to discord character restrictions. Here's the top 25.", inline=False)
                freeAgents = []
                for p in players:
                    if p['tid'] == -1:
                        freeAgents.append("{} {} {}".format(p['pid'], p['ratings'][-1]['ovr'], p['ratings'][-1]['pot']))
                freeAgents.sort(key=lambda l: int(l.split(' ')[1]), reverse=True)
                freeAgents = freeAgents[:number]
                #create standard embed
                freeAgentsContent = ""
                for f in freeAgents:
                    x = f.split(' ')
                    for p in players:
                        if p['pid'] == int(x[0]):
                            pos = p['ratings'][-1]['pos']
                            name = p['firstName'] + ' ' + p['lastName']
                            rating = str(p['ratings'][-1]['ovr']) + '/' + str(p['ratings'][-1]['pot'])
                            age = str(season - p['born']['year'])
                            skills = ""
                            try: skills = ' '.join(p['ratings'][-1]['skills'])
                            except: pass
                    freeAgentsContent = freeAgentsContent + f'{pos} **{name}** - {age} yo {rating}'
                    if skills == "":
                        freeAgentsContent += '\n'
                    else:
                        freeAgentsContent += ' | ' + str(skills) + '\n'
                regularEmbed.add_field(name='Free Agents', value=freeAgentsContent)
                
                #now we create the POT embed
                freeAgents.sort(key=lambda l: int(l.split(' ')[2]), reverse=True)
                freeAgentsContent = ""
                for f in freeAgents:
                    x = f.split(' ')
                    for p in players:
                        if p['pid'] == int(x[0]):
                            pos = p['ratings'][-1]['pos']
                            name = p['firstName'] + ' ' + p['lastName']
                            rating = str(p['ratings'][-1]['ovr']) + '/' + str(p['ratings'][-1]['pot'])
                            age = str(season - p['born']['year'])
                            skills = ""
                            try: skills = ' '.join(p['ratings'][-1]['skills'])
                            except: pass
                    freeAgentsContent = freeAgentsContent + f'{pos} **{name}** - {age} yo {rating}'
                    if skills == "":
                        freeAgentsContent += '\n'
                    else:
                        freeAgentsContent += ' | ' + str(skills) + '\n'
                secondaryEmbed = discord.Embed(
                    title=message.guild.name,
                    description=str(phaseText),
                    color=0x000000)
                secondaryEmbed.add_field(name='Free Agents (POT)', value=freeAgentsContent)
                secondaryEmbed.set_footer(text='Click the ⬅️  arrow to sort by OVR | Made by ClevelandFan#6181')
                secondEmbed = True
        
            if command == 'deaths':
                deathList = []
                deathListSecond = []
                deathText = ">>> "
                totalDeaths = 0
                for p in players:
                    if 'diedYear' in p:
                        if totalDeaths < 20:
                            deathList.append("{} {}".format(p['pid'], p['diedYear']))
                            totalDeaths += 1
                        else:
                            deathListSecond.append("{} {}".format(p['pid'], p['diedYear']))
                            secondEmbed = True
                deathList.sort(key=lambda l: int(l.split()[1]), reverse=True)
                for d in deathList:
                    x = d.split(' ')
                    for p in players:
                        if p['pid'] == int(x[0]):
                            playerName = p['firstName'] + ' ' + p['lastName']
                            diedAge = p['diedYear'] - p['born']['year']
                    deathText = deathText + playerName + ' - Died ' + str(x[1]) + ' (age ' + str(diedAge) + ')' + '\n'
                regularEmbed.add_field(name='Deaths', value=deathText)
                if secondEmbed == True:
                    secondaryEmbed = discord.Embed(
                        title=message.guild.name,
                        description=str(phaseText),
                        color=0x000000)
                    deathSecondText = ""
                    deathListSecond.sort(key=lambda l: int(l.split()[1]), reverse=True)
                    for d in deathListSecond:
                        x = d.split(' ')
                        for p in players:
                            if p['pid'] == int(x[0]):
                                playerName = p['firstName'] + ' ' + p['lastName']
                                diedAge = p['diedYear'] - p['born']['year']
                        deathSecondText = deathSecondText + playerName + ' - Died ' + str(x[1]) + ' (age ' + str(diedAge) + ')' + '\n'
                    
                    secondaryEmbed.add_field(name='Deaths (continued)', value=deathSecondText)
                    secondaryEmbed.set_footer(text='Made by ClevelandFan#6181')
                    secondEmbed = True


            #send the embed and set up second embed
            if secondEmbed == True:
                if command == 'fa':
                    regularEmbed.set_footer(text="Click the ➡️  arrow to sort by POT | Made by ClevelandFan#6181")

            else:
                regularEmbed.set_footer(text="Made by ClevelandFan#6181")
            #send the actual embed
            botEmbed = await message.channel.send(embed=regularEmbed)
            if secondEmbed == True:
                await botEmbed.add_reaction('⬅️')
                await botEmbed.add_reaction('➡️')
                for i in range(10):
                    def check(reaction, user):
                        return reaction.message == botEmbed and user == message.author and str(reaction.emoji) == '➡️'
                    try:
                        reaction, user = await client.wait_for('reaction_add', timeout=120.0, check=check)
                    except asyncio.TimeoutError:
                        scrubVar = 1
                    else:
                        await botEmbed.edit(content='', embed=secondaryEmbed)
                        await botEmbed.remove_reaction('➡️', message.author)
                    def check(reaction, user):
                        return reaction.message == botEmbed and user == message.author and str(reaction.emoji) == '⬅️'
                    try:
                        reaction, user = await client.wait_for('reaction_add', timeout=120.0, check=check)
                    except asyncio.TimeoutError:
                        scrubVar = 1
                    else:
                        await botEmbed.edit(content='', embed=regularEmbed)
                        await botEmbed.remove_reaction('⬅️', message.author)

                

   



client.run("your_token")
