from VJN_Command_Tools_2 import *

import time
import asyncio
import os

pricesCrepePath = 'D:\Personnal Backup\Document\Association\VJN\crepes disponibles pour le prochain event.txt'


#Variables--------------------------------------------------------------------------------------


BiereChan = None
TradiChan = None
CmdChan = None
paidCmdChan = None
validCmdChan = None
AssignmentChan = None

biereChanName = "pate-a-la-biere"
tradiChanName = "pate-traditionnelle"
CmdChanName = "commands"
paidCmdChanName = "paid-commands"
validCmdChanName = "valid-commands"
AssignmentChanName = "assignement-crepieres"


#Fonctions---------------------------------------------------------------------------------

def handleErr(e, errMsg):
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print("--------------------------------------------------------------------error")
        print("message d'erreur: %d\nline number: %d\nfile name: {%s}\n" %(e, line_number, filename))
        print(errMsg)
        print("--------------------------------------------------------------------error")


@bot.command()
async def order(ctx, *args):
    ctx.author.send(
     "```------------------------------\n"
        "     '$order' est obsolete    \n"
        "    rend toi sur le channel:  \n"
        "     '#aide-pour-commander'   \n"
        "  pour connaitre la procedure \n"
    )
    return

    try:
        await handleOrder(ctx.author, args, validCmdChan)

    except Exception as e:
        handleErr(e, f"commande envoyée: {args}")


@bot.event
async def on_raw_reaction_add(payload):
    print("------------------------------------------------------------on_raw_reaction_add Beg")
    adding = True
    if loadingPrice:
        return
    print("A")

    channel = await getChanFromId(payload.channel_id)
    msg = await getMsgFromChan(channel, payload.message_id)

    if channel == AssignmentChan:
        print("------------------------------------------------------------on_raw_reaction_add End")
        return
    print("B")
    
    print(f"msg.author.name: [{msg.author.name}]")
    if (await getAuthorFromId(payload.user_id)).name == "VJN - Command":
        print("------------------------------------------------------------on_raw_reaction_add End")
        return
    print("C")
        
    if not enableCmd:
        if channel == TradiChan or channel == BiereChan:
            await msg.remove_reaction(payload.emoji, await getAuthorFromId(payload.user_id))
        print("------------------------------------------------------------on_raw_reaction_add End")
        return

    try:
        print("D")

        #handle reaction from channel "pate-a-crepe chan"
        await handleSelectChan(payload, BiereChan, TradiChan, validCmdChan, paidCmdChan)
        print("E")
        #handle reaction from channel "valid-commands"
        await handleValidChan(payload, validCmdChan, paidCmdChan)
        #handle reaction from channel "paid-commands"
        await handlePaidChan(payload, paidCmdChan, AssignmentChan)

    except Exception as e:
        print("4")
        handleErr(e, f"curr message : {msg.content}")
    
    finally:
        adding = False

    print("------------------------------------------------------------on_raw_reaction_add End")


@bot.event
async def on_raw_reaction_remove(payload):
    print("------------------------------------------------------------on_raw_reaction_remove Beg")
    print(f"author name: {(await getAuthorFromId(payload.user_id)).name}")

    if not enableCmd:
        return

    channel = await getChanFromId(payload.channel_id)
    msg = await getMsgFromChan(channel, payload.message_id)
    
    if (await getAuthorFromId(payload.user_id)).name == "VJN - Command":
        return

    await handleRemoveReactionEvent(payload, paidCmdChan, AssignmentChan)
    
    print("------------------------------------------------------------on_raw_reaction_remove End")


@bot.command()
async def clear(ctx, *args):
    if ctx.author.name != "Livaï":
        return

    messages = await ctx.channel.history(limit = 10000).flatten()
    for message in messages:
        await message.delete()
    return   await message.delete()

"""
    messages = await validCmdChan.history(limit = 10000).flatten()
    for message in messages:
        await message.delete()

    messages = await paidCmdChan.history(limit = 10000).flatten()
    for message in messages:
        await message.delete()

    print("clear : done")
"""


@bot.command()
async def loadPrice(ctx, *args):
    if ctx.author.name != "Livaï":
        return

    try:
        loadingPrice = True
        await ctx.message.delete()
        
        priceChan = ctx.channel
        priceFile = open(pricesCrepePath, "r")
        lines = [line.strip("\n") for line in priceFile if line != "\n"]
        lenLines = len(lines)
        msgList = [None for i in range(lenLines)]

        i = 0
        for line in lines:
            msgList[i] = await priceChan.send(line)
            i += 1

        for msg in msgList:
            if msg.content.find("---") == -1:
                await msg.add_reaction(emojiMapper[1])
                await msg.add_reaction(emojiMapper[2])
                await msg.add_reaction(emojiMapper[3])
                await msg.add_reaction(emojiMapper[4])

    except Exception as e:
        handleErr(e, "Loading Price failed !")

    finally:
        priceFile.close()
        loadingPrice = False
        print("loadPrice : done")


@bot.command()
async def on(ctx, *args):
    await ctx.message.delete()
    if ctx.author.name != "Livaï":
        return

    global enableCmd
    enableCmd = True


@bot.command()
async def off(ctx, *args):
    await ctx.message.delete()
    if ctx.author.name != "Livaï":
        return

    global enableCmd
    enableCmd = False


#read all command(msg) sent in a channel and load each of them as a command in an excel file
@bot.command()
async def t1(ctx, *args):
    if ctx.author.name != "Livaï":
        return

    CmdChan = [x for x in bot.get_all_channels() if x.name == "commands"]

    msgs = await CmdChan.history(limit=10000).flatten()

    for msg in msgs:
        msgSplit = msg.content.split(' ')
        if len(msgSplit) > 1:
            (qte, ingrs, check, errMsg) = checkOrderCmd(msgSplit[1:])

            if check:
                currIngMapper = {}
                currIngMapper["client"] = msg.author
                currIngMapper["quantite"] = qte
                for ingr in ingrs:
                    currIngMapper[nameMapper[ingr]] = "X"
                append(currIngMapper, ignore_index=True)

    print("test1 : done")

@bot.command()
async def t2(ctx, *args):
    if ctx.author.name != "Livaï":
        return
    #emoji = "<:one:396521773144866826>"\U00000031
    #emoji = "<:one:0000000000000128578>"
    #emoji = "<:one:396521773144866826>"
    #emoji = discord.Emoji("\U0001F642");
    #emoji = discord.Emoji("uFE0F\u20E3");
    #emoji = discord.Emoji("\u0031\uFE0F");
    #emoji = discord.Emoji("\u0031\u20E3");
    await ctx.message.add_reaction("\U00000031\U0000fe0f\U000020e3")
    await ctx.message.remove_reaction("\U00000031\U0000fe0f\U000020e3", ctx.author)



@bot.event
async def on_ready():

    global BiereChan
    BiereChan = await getChanFromName(biereChanName)
    global TradiChan
    TradiChan = await getChanFromName(tradiChanName)
    global paidCmdChan
    paidCmdChan = await getChanFromName(paidCmdChanName)
    global validCmdChan
    validCmdChan = await getChanFromName(validCmdChanName)
    global CmdChan
    CmdChan = await getChanFromName(CmdChanName)
    global AssignmentChan
    AssignmentChan = await getChanFromName(AssignmentChanName)

    if not paidCmdChan or not validCmdChan or not BiereChan or not TradiChan or not AssignmentChan:
        sys.exit("paidCmdChan or validCmdChan or CmdChan or TradiChan or BiereChan or AssignmentChan don't exit !!!")
    print("ready !")


@bot.event
async def ServerInfo(ctx):
    server = ctx.guild
    numberOfTextChannel = server.test_channel
    #envoyer un message sur le salon courant
    await ctx.send("Hi!")


@bot.event
async def on_command_error(ctx, error):
    return


@bot.event
async def on_connect():
    print("co")
    return


@bot.event
async def on_disconnect():
    print("deco")
    #await deleteAssignMsg(AssignmentChan)
    return

try:
    bot.run(os.getenv('TOKEN'))
finally:
    allCmds.close()
    saveMapper()
    print("end")