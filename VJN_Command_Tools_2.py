import os
import re
import sys
import discord
import pandas as pd
from threading import Thread, Lock
from IPython.display import display
from discord.ext import commands as cmd

test = 2
enableCmd = False
loadingPrice = False
adding = False

#init and save--------------------------------------------------------------------------------------

bot = cmd.Bot(command_prefix = "$", descritption = "bot pour gérer les commandes")


csvBackupPath = 'D:\Personnal Backup\Document\Association\VJN\Bot Discord\Gestionnaire de Commandes de Crêpe Backup.csv'

allCmds = open(csvBackupPath, "a") if os.path.isfile(csvBackupPath) else open(csvBackupPath, "w")

validChanMsgBackupPath = 'D:\Personnal Backup\Document\Association\VJN\Bot Discord\Valid-Chan-Msg-Backup.csv'
paidChanMsgBackupPath = 'D:\Personnal Backup\Document\Association\VJN\Bot Discord\Paid-Chan-Msg-Backup.csv'
excelGestionPath = 'D:\Personnal Backup\Document\Association\VJN\Bot Discord\Gestionnaire de Commandes de Crêpe.xlsx'

columns = ["client", "sucre", "nutella", "raclette", "reblochon", "emmental", "jambon", "poulet", "confiture_fraise", "confiture_abricot", "oignon", "champignon"]

ingrSucre = ["nutella", "confiture_fraise", "confiture_abricot", "sucre", "beurre", "n", "cf", "ca", "s", "be"]

ingrSale = ["jambon", "poulet", "emmental", "raclette", "reblochon", "oignon", "oeuf", "champignon", "j", "p", "e", "ra", "re", "oi", "oe", "c"]

ingrNeutre = ["traditionnelle", "biere", "t", "bi"]

QteLimit = 4
nbOfCrepiere = 10
nbIngredientMax = 10

ingrAll = []
ingrAll.extend(ingrNeutre);
ingrAll.extend(ingrSucre);
ingrAll.extend(ingrSale);

pattern = re.compile(f"^[1-9] ((({')|('.join(ingrAll)})) )*(({')|('.join(ingrAll)}))$")

if len(sys.argv) > 1:
    if sys.argv[1] == "del":
        if os.path.isfile(validChanMsgBackupPath):
            os.remove(validChanMsgBackupPath)
        if os.path.isfile(paidChanMsgBackupPath):
            os.remove(paidChanMsgBackupPath)


ingrPrice = pd.read_excel(excelGestionPath, sheet_name='Prix des Produits')
if (ingrPrice.empty):
    sys.exit("ingrPrice is empty !!!")


def initMapper():
    validMapper = {}
    paidMapper = {}
    print("------------------------------------------------initMapper")
    if (os.path.isfile(validChanMsgBackupPath) and os.path.getsize(validChanMsgBackupPath) > 0):
        validFrame = pd.read_csv(validChanMsgBackupPath)
        display(validFrame)

        for i in range(0, len(validFrame.index)):
            currMsgId = int(validFrame.at[i, "message-id"])
            currAuthorId = int(validFrame.at[i, "author-id"])
            quantity = int(validFrame.at[i, "quantity"])
            ingredients = validFrame.at[i, "ingredients"]

            validMapper[currMsgId] = (currAuthorId, quantity, ingredients)

    if (os.path.isfile(paidChanMsgBackupPath) and os.path.getsize(paidChanMsgBackupPath) > 0):
        paidFrame = pd.read_csv(paidChanMsgBackupPath)

        for i in range(0, len(paidFrame.index)):
            currMsgId = int(paidFrame.at[i, "message-id"])
            currAuthorId = int(paidFrame.at[i, "author-id"])

            paidMapper[currMsgId] = currAuthorId

    print("------------------------------------------------initMapper")
    return (validMapper, paidMapper)

(validCmdMapper, paidCmdMapper) = initMapper()

def saveMapper():
    validBackup = open(validChanMsgBackupPath, "w")
    paidBackup = open(paidChanMsgBackupPath, "w")

    validBackup.write("message-id,author-id,quantity,ingredients\n")
    for msgId, tup in validCmdMapper.items():
        validBackup.write(f"{msgId},{tup[0]},{tup[1]},{tup[2]}\n")

    paidBackup.write("message-id,author-id\n")
    for msgId, author in paidCmdMapper.items():
        paidBackup.write(f"{msgId},{author}\n")

    validBackup.close()
    paidBackup.close()


def getEmojiFromName(name):
    return discord.utils.get(bot.emojis, name = name)

#Variables--------------------------------------------------------------------------------------


mutexMsg = Lock()
mutexCmdMapper = Lock()

mutextSys = Lock()

paidAssignMapper = {}

emojiMapper = {
    "\U00000031\U0000fe0f\U000020e3" : 1,
    "\U00000032\U0000fe0f\U000020e3" : 2,
    "\U00000033\U0000fe0f\U000020e3" : 3,
    "\U00000034\U0000fe0f\U000020e3" : 4,
    "\U00000035\U0000fe0f\U000020e3" : 5,
    "\U00000036\U0000fe0f\U000020e3" : 6,
    "\U00000037\U0000fe0f\U000020e3" : 7,
    "\U00000038\U0000fe0f\U000020e3" : 8,
    "\U00000039\U0000fe0f\U000020e3" : 9,
    1 : "\U00000031\U0000fe0f\U000020e3",
    2 : "\U00000032\U0000fe0f\U000020e3",
    3 : "\U00000033\U0000fe0f\U000020e3",
    4 : "\U00000034\U0000fe0f\U000020e3",
    5 : "\U00000035\U0000fe0f\U000020e3",
    6 : "\U00000036\U0000fe0f\U000020e3",
    7 : "\U00000037\U0000fe0f\U000020e3",
    8 : "\U00000038\U0000fe0f\U000020e3",
    9 : "\U00000039\U0000fe0f\U000020e3"
}

nameMapper = {
    "t" : "traditionnelle",
    "bi" : "biere",
    "n" : "nutella",
    "cf" : "confiture_fraise",
    "ca" : "confiture_abricot",
    "s" : "sucre",
    "be" : "beurre",
    "j" : "jambon",
    "p" : "poulet",
    "e" : "emmental",
    "ra" : "raclette",
    "re" : "reblochon",
    "oi" : "oignon",
    "oe" : "oeuf",
    "c" :"champignon", 
    "traditionnelle" : "traditionnelle",
    "biere" : "biere",
    "nutella" : "nutella",
    "confiture_fraise" : "confiture_fraise",
    "confiture_abricot" : "confiture_abricot",
    "sucre" : "sucre",
    "beurre" : "beurre",
    "jambon" : "jambon",
    "poulet" : "poulet",
    "emmental" : "emmental",
    "raclette" : "raclette",
    "reblochon" : "reblochon",
    "oignon" : "oignon",
    "oeuf" : "oeuf",
    "champignon" :"champignon"
}

nameMapperInv = {
    "t" : "t",
    "bi" : "bi",
    "n" : "n",
    "cf" : "cf",
    "ca" : "ca",
    "s" : "s",
    "be" : "be",
    "j" : "j",
    "p" : "p",
    "e" : "e",
    "ra" : "ra",
    "re" : "re",
    "oi" : "oi",
    "oe" : "oe",
    "c" :"c",
    "traditionnelle" : "t",
    "biere" : "bi",
    "nutella" : "n",
    "confiture_fraise" : "cf",
    "confiture_abricot" : "ca",
    "sucre" : "s",
    "beurre" : "be",
    "jambon" : "j",
    "poulet" : "p",
    "emmental" : "e",
    "raclette" : "ra",
    "reblochon" : "re",
    "oignon" : "oi",
    "oeuf" : "oe",
    "champignon" :"c"
}

#Fonctions---------------------------------------------------------------------------------

def align(max, str):
    strSize = len(str)
    if strSize >= max:
        return str
    return str + f" {(max - strSize) * ' '}"

def alignCenter(maxSize, centerSize):
    if centerSize >= maxSize:
        return ""
    return int(((maxSize - centerSize) / 2)) * "-"
    
async def getMsgFromChan(chan, msgId):
    return discord.utils.get(await chan.history(limit=10000).flatten(), id=msgId)
    
async def getAuthorFromId(userId):
    return await bot.fetch_user(userId)
    
async def getChanFromId(chanId):
    chan = [x for x in bot.get_all_channels() if x.id == chanId]
    if chan == []:
        return None
    return chan[0]

async def getChanFromName(chanName):
    chan = [x for x in bot.get_all_channels() if x.name == chanName]
    if chan == []:
        return None
    return chan[0]
    
def batterIsPresent(ingredients):
    count = 0
    for ingr in ingredients:
        if ingr in ingrNeutre:
            count += 1
    
    return count == 1


async def userOrderCmdFailed(author, ingredientsList, errMsg):
    await author.send(f"message d'erreur: {errMsg}\n\ncommande envoyée: {ingredientsList}")


async def removeReaction(msg, emoji, author):

    await msg.remove_reaction(emoji, author)

        

    
    
def checkOrderCmd(args):

    #manque d'argument
    if (len(args) < 2):
        return (None, 0, False, "Il manque des arguments à votre commande")
        
    #vérifier que la commande n'a pas une longueur excessive
    if (len(args) > nbIngredientMax + 1): #"+1" pour comptabiliser la quantité
        return (None, 0, False, "votre commande a une longueur excessive !")

    #apply lowercase to all args element
    ingredients = [ingr.lower() for ingr in args]

    #vérifier que la commande respecte la syntax de commande
    if (not pattern.match(' '.join(ingredients))):
        return (None, 0, False, "vérifier que votre commande respecte le channel syntax-de-commande")

    #vérifier si une pate à crepe est présente dans la liste d'ingredients
    if not batterIsPresent(ingredients):
        return (None, 0, False, "Vous avez pas selectionné de type de pâte à crepe.")

    #vérifier qu'il n'y ai pas de doublon
    if (len(ingredients) != len(set(ingredients))):
        return (None, 0, False, "votre commande contient des doublons")
    
    #vérifier les melange douteux
    if (set(ingrSucre) & set(ingredients) and set(ingrSale) & set(ingredients)):
        return (None, 0, False, "Les melange que tu as fais sont douteux (melange sucré - salé interdit !")
    
    #to abreviation
    ingredientsAbr = []
    for ingr in ingredients[1:]:
        ingredientsAbr.append(nameMapperInv[ingr.lower()])

    return (int(ingredients[0]), ingredientsAbr, True, "Success")



def calculeCmdPrice(qte, ingredientsList, ingrPrice):
    prices = 0
    for ingr in ingredientsList:
        realName = nameMapper[ingr]
        priceLine = ingrPrice.loc[0]
        if (priceLine.empty):
            return (False, 0, "impossible de récupérer le prix des ingrédients")
        price = priceLine.at[realName]
        prices += price

    return (True, round(float(prices) * float(qte), 2), "Success")
    
    
async def sendCmdPriceToUser(author, qte, ingredientsList, cmdPrice):
    ingrs = ' '.join(ingredientsList) 
    centrage = 30

    await author.send("```------------------------------\n"
                     f"---- Recap de ta commande ----\n"
                     f"{alignCenter(centrage, len(ingrs))} {ingrs} {alignCenter(centrage, len(ingrs) + 2)}\n"
                     f"{alignCenter(centrage, 9)} {qte} crepes {alignCenter(centrage, 9)}\n"
                     f"{alignCenter(centrage, len(str(cmdPrice)) + 8)} {cmdPrice} euros {alignCenter(centrage, len(str(cmdPrice)) + 8)}\n"
                      "------------------------------\n"
                      "-- Viens payer à la caisse ---\n"
                      "------------------------------\n"
                     f"-- Carte à partir de 1 euro --```")


async def sendCmdToValidChannel(author, qte, ingredientsList, cmdPrice, validCmdChan):
    name = str(author)
    ingrs = ' '.join([nameMapper[ingr] for ingr in ingredientsList])

    key = f"```[{align(13, name)}] [{qte} crepes] [{align(13, ingrs)}] [{cmdPrice} euros]```"

    msg = await validCmdChan.send(f"{key}")

    validCmdMapper[msg.id] = (author.id, qte, ingrs)
    
    print("EE")
    

async def handleOrder(author, args, validCmdChan):
    print("AA")
    (qte, ingredientsList, check, errMsg) = checkOrderCmd(args)
    if (not check):
        await userOrderCmdFailed(author, args, errMsg)
    else:
        print("BB")
        (check, cmdPrice, errMsg) = calculeCmdPrice(qte, ingredientsList, ingrPrice)
        if (not check):
            print (f"message d'erreur: {errMsg}\n\ncommande envoyée: {ingredientsList}\n--------------------------------------------------------")
        else:
            print("CC")
            await sendCmdPriceToUser(author, qte, ingredientsList, cmdPrice)
            print("DD")
            await sendCmdToValidChannel(author, qte, ingredientsList, cmdPrice, validCmdChan)
            print("FF")


def rebuildArgsFromSelectChan(SelectMsg, currChan, TradiChan, qte):

    if 'uniquement' in SelectMsg:
        return [str(qte), 't' if currChan == TradiChan else 'bi']

    args = [x.strip('`') for x in SelectMsg.split(' ') if x != '']

    if currChan == TradiChan:
        args.insert(0, 't')
    else:
        args.insert(0, 'bi')
    args.insert(0, f"{qte}")
    args = args[:len(args) - 2]
    return args
    
    
async def handleSelectChan(payload, BiereChan, TradiChan, validCmdChan, paidCmdChan):
    print("1")

    currChan = await getChanFromId(payload.channel_id)
    msg = await getMsgFromChan(currChan, payload.message_id)


    print("2")
    if msg.content.find("---") != -1 or (currChan != TradiChan and currChan != BiereChan):
        return
    print("3")
        
    author = await getAuthorFromId(payload.user_id)

    print("4")
    if not payload.emoji.name in emojiMapper:
        await removeReaction(msg, payload.emoji, author)

    elif emojiMapper[payload.emoji.name] <= QteLimit:
        print("5")
        qte = emojiMapper[payload.emoji.name]

        await removeReaction(msg, payload.emoji, author)

        print("5.1")
        args = rebuildArgsFromSelectChan(msg.content, currChan, TradiChan, qte)
        print("5.2")
        await handleOrder(author, args, validCmdChan)
        print("5.3")

    print("6")



async def deleteMsg(msg):
    await msg.delete()


def addCurrentCmdToBackupCmd(curAuthor, ingrs):

    currIngMapper = set("quantite")
    ingrsList = ingrs.split(' ')

    for ingr in ingrsList:
        currIngMapper.add(nameMapper[ingr])
    
    newLine = f"{curAuthor}"
    for colName in columns:
        if colName in currIngMapper:
            newLine + ",1"
        else:
            newLine += ","
    
    allCmds.write(f"{newLine}\n")


async def handleValidChan(payload, validCmdChan, paidCmdChan):
    print("------------------------------------------------------------handleValidChan")
    key = payload.message_id
    if (key in validCmdMapper):

        (curAuthorId, qte, ingrs) = validCmdMapper[key]
        curAuthor = await getAuthorFromId(curAuthorId)
            
        validMsg = await getMsgFromChan(validCmdChan, key)

        if payload.emoji.name == "ticketverte":
            ingrs = ' '.join([nameMapperInv[ingr] for ingr in ingrs.split(' ')])
            toSend = f"```[{align(25, str(curAuthor))}] [{ingrs}]```"

            for i in range(qte):
                paidMsg = await paidCmdChan.send(toSend)
                paidCmdMapper[paidMsg.id] = curAuthor.id
                addCurrentCmdToBackupCmd(curAuthor, ingrs)

            validCmdMapper.pop(key)
            await deleteMsg(validMsg)

        elif payload.emoji.name == "croixrouge":
            validCmdMapper.pop(key)
            await deleteMsg(validMsg)

    print("------------------------------------------------------------handleValidChan")



#-----------------------------------------------------------------------------------------------------------------PAID NAMESPACE

def printAssignChan(id):
    """
    print("------------------------------------------------------------printAssignChan Beg")
    
    print(id)
    print(f"len(paidAssignMapper.items()) : {len(paidAssignMapper.items())}")
    for item in paidAssignMapper.items():
        print(f"{type(item[0])}")
        print(f"{type(item[1])}")
        print(f"len(item[1][0].reactions) : {len(item[1][0].reactions)}")
        print(f"len(item[1][1].reactions) : {len(item[1][1].reactions)}")
        print(f"item[1][0].content : {item[1][0].content}")
        print(f"item[1][1].content : {item[1][1].content}")
        print(f"key: {item[0]}, val: ({item[1][0].reactions[0].emoji}, {item[1][1].reactions[0].emoji})")

    print("------------------------------------------------------------printAssignChan End")
    """


async def deleteAssignMsg(AssignmentChan):
    msgs = await AssignmentChan.history(limit=10000).flatten()
    for msg in msgs:
        await delete(msg)
    paidAssignMapper.clear()


async def createAssignMsg(emoji, paidMsg, AssignmentChan):
    print("------------------------------------------------------------createAssignMsg Beg")
    toSend = paidMsg.content.split('[')[2].strip('`').strip(']')
    toSend = ' '.join([nameMapper[ingr] for ingr in toSend.split(' ')])

    paidAssignMapper[emoji.name] = paidMsg

    assignMsg = await AssignmentChan.send(toSend)

    await assignMsg.add_reaction(emoji)
    print("------------------------------------------------------------createAssignMsg End")

async def removeAssignMsg(emojiName, author, AssignmentChan):
    print("------------------------------------------------------------removeAssignMsg Beg")
    print(f"emojiName: {emojiName}")
    printAssignChan("")
    
    paidMsg = paidAssignMapper[emojiName]
    print(f"removeAssignMsg: {paidMsg.content}, {emojiName}; {author}")
    await removeReaction(paidMsg, emojiName, author)
    nLastMsg = AssignmentChan.history(limit=nbOfCrepiere)
    assignMsg = await nLastMsg.find(lambda x: x.reactions[0].emoji == emojiName)
    print(f"assignMsg: {assignMsg.content}")

    await assignMsg.delete()

    print("AAA")
    paidAssignMapper.pop(emojiName)
    print("BBB")

    print("------------------------------------------------------------removeAssignMsg End")
    
async def handleStopEmoji(paidMsg, stopEmoji, paidChanManager, AssignmentChan):
    if len(paidMsg.reactions) > 1:
        numberEmoji = [x.emoji for x in paidMsg.reactions if x.emoji != stopEmoji][0]
        if numberEmoji.name in paidAssignMapper:
            await removeAssignMsg(numberEmoji.name, paidChanManager, AssignmentChan)

    await deleteMsg(paidMsg)


async def removePrevAssign(paidMsg, numberEmojiName, paidChanManager, AssignmentChan):
    prevNumberEmojiName = [x.emoji for x in paidMsg.reactions if x.emoji != numberEmojiName][0]
    print(f"prevNumberEmojiName: {prevNumberEmojiName}")
    await removeAssignMsg(prevNumberEmojiName, paidChanManager, AssignmentChan)


async def handleNumberEmoji(numberEmoji, paidMsg, AssignmentChan, paidChanManager):

    print("------------------------------------------------------------handleNumberEmoji Beg")
    printAssignChan("------> 0")
    if numberEmoji.name in paidAssignMapper:
        print ("enter   -->   handleNumberEmoji   -->   if payload.emoji.name in emojiMapper:")
        
        if len(paidMsg.reactions) > 1:
            print ("enter   -->   1) handleNumberEmoji   -->   if len(paidMsg.reactions) > 1:")
            await removePrevAssign(paidMsg, numberEmoji.name, paidChanManager, AssignmentChan)
            printAssignChan("------> 2")

        await removeAssignMsg(numberEmoji.name, paidChanManager, AssignmentChan)
        printAssignChan("------> 3")
    else:
        if len(paidMsg.reactions) > 1:
            print ("enter   -->   2) handleNumberEmoji   -->   if len(paidMsg.reactions) > 1:")
            await removePrevAssign(paidMsg, numberEmoji.name, paidChanManager, AssignmentChan)
            printAssignChan("------> 4")

    await createAssignMsg(numberEmoji, paidMsg, AssignmentChan)
    print("------------------------------------------------------------handleNumberEmoji End")


async def handleRemoveReactionEvent(payload, paidCmdChan, AssignmentChan):
    if not payload.message_id in paidCmdMapper:
        #le message courant n'est pas en lien avec la vente de crepe
        return

    if not payload.emoji.name in emojiMapper:
        #seul la suppression des emoji "numero" nous interesse
        return
    
    paidChanManager = await getAuthorFromId(payload.user_id)

    await removeAssignMsg(payload.emoji.name, paidChanManager, AssignmentChan)


async def handlePaidChan(payload, paidCmdChan, AssignmentChan):
    print("------------------------------------------------------------handlePaidChan Beg")

    if not payload.message_id in paidCmdMapper:
        return
        
    key = payload.message_id
    paidMsg = await getMsgFromChan(paidCmdChan, key)
    authorId = paidCmdMapper[key]
    author = await getAuthorFromId(authorId)
    paidChanManager = await getAuthorFromId(payload.user_id)

    if payload.emoji.name in emojiMapper:
        print ("enter   -->   handlePaidChan   -->   if payload.emoji.name in emojiMapper:")
        await handleNumberEmoji(payload.emoji, paidMsg, AssignmentChan, paidChanManager)

    elif payload.emoji.name == "croixrouge":
        await handleStopEmoji(paidMsg, payload.emoji, paidChanManager,AssignmentChan)

    elif payload.emoji.name == "ticketverte":

        await author.send("```------------------------------\n"
                          "--> Ta Commande Est Prete <---\n"
                          "------------------------------\n```")
        paidCmdMapper.pop(key)
        await handleStopEmoji(paidMsg, payload.emoji, paidChanManager, AssignmentChan)

    else:
        print("remove reaction machinal")
        await removeReaction(paidMsg, payload.emoji, paidChanManager)

    print("------------------------------------------------------------handlePaidChan End")