## install discord.py
## py -3 -m pip install -U discord.py

## install requests
## py -3 -m pip install -U requests

## install qbittorrent-api
## py -3 -m pip install -U qbittorrent-api

import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
import requests

import qbittorrentapi

def filterBy(TorrentInfo,filterType):
    if TorrentInfo[1]==filterType or filterType=="all":
        return True
    else:
        return False

def filterList(FullList,filterType):
    FilteredList=[]
    for i in range(len(FullList)):
        if filterBy(FullList[i],filterType):
            FilteredList.append(FullList[i])
    SortedList=[]
    for i in range(len(FilteredList)):
        if FilteredList[i][2]!="100%":
            SortedList.append(FilteredList[i])
    SortedList.sort(key=lambda x:float(x[2][:-1]),reverse=True)
    for i in range(len(FilteredList)):
        if FilteredList[i][2]=="100%":
            SortedList.append(FilteredList[i])
    return SortedList

def renameStates(FullList):
    completedList=["uploading","pausedUP","checkingUP","stalledUP","forcedUP"]
    downloadingList=["downloading"]
    missingList=["missingFiles"]
    stalledList=["stalledDL"]
    metaList=["metaDL"]
    queuedList=["queuedDL"]
    pausedList=["pausedDL"]
    for i in range(len(FullList)):
        if FullList[i][3] in completedList:
            FullList[i][3]=StatusList[0]
        elif FullList[i][3] in downloadingList:
            FullList[i][3]=StatusList[1]
        elif FullList[i][3] in missingList:
            FullList[i][3]=StatusList[2]
        elif FullList[i][3] in stalledList:
            FullList[i][3]=StatusList[3]
        elif FullList[i][3] in metaList:
            FullList[i][3]=StatusList[4]
        elif FullList[i][3] in queuedList:
            FullList[i][3]=StatusList[5]
        elif FullList[i][3] in pausedList:
            FullList[i][3]=StatusList[6]
        else:
            FullList[i][3]=StatusList[7]
    return FullList

def findCompleted(FullList):
    CompletedList=[]
    for i in range(len(FullList)):
        if FullList[i][3]==StatusList[0]: #Completed
            CompletedList.append(FullList[i])
    return CompletedList

def findDownloading(FullList):
    DownloadingList=[]
    for i in range(len(FullList)):
        if FullList[i][3]==StatusList[1]: #Downloading
            DownloadingList.append(FullList[i])
        elif FullList[i][3]==StatusList[3]: #Stalled
            DownloadingList.append(FullList[i])
        elif FullList[i][3]==StatusList[4]: #DownloadingMeta
            DownloadingList.append(FullList[i])
        elif FullList[i][3]==StatusList[5]: #Queued
            DownloadingList.append(FullList[i])
        elif FullList[i][3]==StatusList[6]: #Paused
            DownloadingList.append(FullList[i])
    return DownloadingList

def convertToDiscord(InfoList):
    if not InfoList:
        return NothingDownloading
    maxCharsDiscord=1700
    FinalList=[]
    indexRange=[2,3,4,0]
    for i in range(len(InfoList)):
        FinalList.append([])
        for j in range(len(indexRange)):
            if InfoList[i][indexRange[j]]!="inf":
                FinalList[i].append(InfoList[i][indexRange[j]])
    StringListTwo=convertToString(FinalList)
    StringList=convertToString(FinalList)
    currentLength=len(StringList)
    currentMsg=[]
    while currentLength>0:
        maxLength=StringList[0:maxCharsDiscord].count('\n')
        numChars=findNth(StringList,'\n',maxLength)
        if(StringList[numChars+1:-1].count('\n'))==0:
            currentMsg.append(StringList[:])
        else:
            currentMsg.append(StringList[0:numChars])
        StringList=StringList[numChars+1:-1]
        currentLength=currentLength-maxCharsDiscord
    return currentMsg 

def findNth(String,Substring,Occurence):
    val = -1
    for i in range(0, Occurence):
        val = String.find(Substring, val + 1)
    return val

def convertToString(nonStrList):
    StringList=str(nonStrList)
    if StringList.find(ListSeparator)==-1:
        StringList=StringList.replace("'], ['","\n\n")
        StringList=StringList.replace("']]","")
        StringList=StringList.replace("[['","")
        StringList=StringList.replace("', '",ListSeparator)
    else:
        StringList=StringList.replace("', '","\n\n")
        StringList=StringList.replace("']","")
        StringList=StringList.replace("['","")
    return StringList

def printMessages(DiscordLists):
    if DiscordLists!=NothingDownloading:
        for i in range(len(DiscordLists)):
            print(convertToString(DiscordLists[i]))
            print("------------------------------------------------")
    else:
        print(NothingDownloading)
        print("------------------------------------------------")

StatusList = ["Completed","Downloading","Files missing","Stalled","Attempting to start","Queued","Paused","Unknown status"]
ListSeparator = "   |   "
NothingDownloading = "Nothing is downloading! Why not request something?"
DownloadingStatus = "downloading"
CompleteStatus = "completed"

#############################
## ENTER YOUR DETAILS HERE ##
#############################

botChannel = "tower" ## ID CHANNEL OF THE CHANNEL FOR THE BOT TO LISTEN TO ##
tvCategory = "tv-sonarr" ## CATEGORY IN QBIT FOR TV SHOWS ##
movieCategory = "radarr" ## CATEGORY IN QBIT FOR MOVIES ##
host='192.168.1.129'
print("------------------------------------------------")

print("Connecting to qBitTorrent at {}...",host)

print("------------------------------------------------")
qbt_client = qbittorrentapi.Client(host, port=6880, username='admin', password='rawtal0972') ## QBIT WEB LOGIN DETAILS ##

TOKEN = "OTU5MTIyMTYxNDAwOTYzMTIy.YkXSHg.OTBxzA4hwUJnzvJqmL5zDcCvFu0" ## DISCORD BOT SECRET ##

#############################
#############################
#############################

# the Client will automatically acquire/maintain a logged in state in line with any request.
# therefore, this is not necessary; however, you may want to test the provided login credentials.
try:
    qbt_client.auth_log_in()
except qbittorrentapi.LoginFailed as e:
    print(e)

def updateTorrentList():
    counter = 0
    TorrentList=[]
    for torrent in qbt_client.torrents_info():
        TempList=[]
        TempList.append(torrent.name)
        TempList.append(torrent.category)
        TempList.append(str(round(torrent.progress*100,2))+"%")
        TempList.append(torrent.state)
        TempList.append(convertTime(torrent.eta))
        TorrentList.append(TempList)
        counter=counter+1
    return TorrentList

def convertTime(seconds):
    intervals = (
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('minutes', 60),
    ('seconds', 1),)
    if seconds!=8640000:
        result = []
        for name, count in intervals:
            value = seconds // count
            if value:
                seconds -= value * count
                if value == 1:
                    name = name.rstrip('s')
                result.append("{} {}".format(value, name))
        return 'ETA: '+', '.join(result[:])
    else:
        return "inf"

def updateAll(category,status="all"):
    TorrentList=updateTorrentList()
    FilteredList = filterList(TorrentList,category)
    FinalList=renameStates(FilteredList)
    if status==DownloadingStatus:
        FinalList=findDownloading(FinalList)
    elif status==CompleteStatus:
        FinalList=findCompleted(FinalList)
    DiscordList=convertToDiscord(FinalList)
    return DiscordList
    
print("------------------------------------------------")

print("Connecting to Discord...")

print("------------------------------------------------")

client = discord.Client()
prefix = "$"
bot=commands.Bot(command_prefix=prefix)
slash = SlashCommand(bot,sync_commands=True)

# @bot.event
# async def on_ready():
#     print('We have logged in as {0.user}'.format(bot))
#     print("------------------------------------------------")

# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return
#     await bot.process_commands(message)

# @bot.command(
#         help = "Use this to see the status of what's currently downloading."+"\n"+"If you want to get fancy, you can search for movies/tv shows specifically by type $status movies or $status tv."+"\n"+"You can also see what's completed by doing $status completed, or $status all to see everything."+"\n"+"Finally, you can combine these (like $status tv completed) to only see completed tv shows."+"\n"+"(tip: you can see everything by typing $status all)",
#         brief = "Use this to see what's currently downloading"
#     )

# @slash.slash(
#     name = "hello",
#     description = "hey"
# )
# async def _hello(ctx:SlashContext):
#     await ctx.send("World")
# ## BOT VERSION ##


@slash.slash(
    name = "qBitCheck",
    description = "Check status for downloads",
    # guild_ids = [958801660451377274],
    options = [
        create_option(
            name = "status",
            description = "status",
            required = True,
            option_type = 3,
            choices = [
                create_choice(
                    name = "all",
                    value = "all"
                ),
                create_choice(
                    name = "completed",
                    value = "completed"
                )
            ]
        ),
        create_option(
            name = "category",
            description = "category",
            required = False,
            option_type = 3,
            choices = [
                create_choice(
                    name = "movies",
                    value = "movies"
                ),
                create_choice(
                    name = "tv",
                    value = "tv"
                ),               
            ]         
            
        )
    ]
)
async def status(ctx:SlashContext, status:str , category:str = "all"):
    print("Checking " + status + "Downloads from " + category + " category")
    if "all" == status:
        updateStatus="all"
    elif "completed" == status:
        updateStatus=CompleteStatus
    else:
        updateStatus=DownloadingStatus
    # if "movies" in category:
    #     Category=movieCategory
    # elif "tv" in category:
    #     Category=tvCategory
    # else:
    #     Category="all"

    match category:
        case "movies":
            Category=movieCategory
        case "tv":
            Category=tvCategory
        case "all":
            Category="all"

    DiscordList=updateAll(Category,updateStatus)
    if DiscordList!=NothingDownloading:
        for i in range(len(DiscordList)):
                await ctx.send(DiscordList[i])
    else:
        await ctx.send(NothingDownloading)


@slash.slash(
    name = "pauseAll",
    description = "Pause all torrents"
)
async def pauseAll(ctx:SlashContext):
    print("Pausing all torrents")
    qbt_client.torrents.pause.all()
    await ctx.send("Paused all torrents")

@slash.slash(
    name = "resumeAll",
    description = "Pause all torrents"
)
async def resumeAll(ctx:SlashContext):
    print("Resuming all torrents")
    qbt_client.torrents.resume.all()
    await ctx.send("Resumed all torrents")

bot.run(TOKEN)
