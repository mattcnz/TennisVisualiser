__author__ = 'mattmilliken'

from bs4 import BeautifulSoup
import json
import re
import unicodedata
from flask import jsonify

import requests

def searchPlayer(name, sex):
    """Takes a string and searches for a player of that name.
    """

    payload = {

    "fPlayerSurname" : "NoNameEntered",
    "fSex":"M",
    "fGradingType":"2",
    "fGradeCd":"",
    "frd":"",
    "fClub":"",
    "fAgegroup":"",
    "fAgegroupDate":"15+Aug+2016",
    "MyStuff":"TopDog+Top+Dog+Yardstick",
    "MySubmitAction":"Search",
    "CallingPage":"GradingList.asp",
    "GradingListIsSubmitted":"No",
    }

    payload['fSex'] = sex

    #Get the surname (NZTennis uses this to search, no firstname)
    surname = name.split()[1]
    firstname = name.split()[0]

    #Add it to the request payload
    payload['fPlayerSurname']=surname

    #Make the request and use bs4 to clean up the response
    s = requests.session()
    r = s.post("http://tennis.org.nz/GradingList.asp", payload)
    soup = BeautifulSoup(r.content)


    #Search through the list of names with that surname and return the playerCode for that firstname,lastname combo.
    namesList = soup.find_all("a")[18:-3]
    namesList = namesList[1:]
    for name in namesList:
        i = name.text.split(',')
        if firstname.upper() in i[1].upper():

            playerCode = str(name).split('pID=')
            pc = "".join(_ for _ in playerCode[1] if _ in ".1234567890")
            pc = pc[:-1]
            #playerCode =  playerCode[1][:-49]
            #playerCode =re.sub("[^0-9]", "", playerCode)

    return int(pc)


def getPlayerData(id):
    """Takes the ID code from getPlayerID and get's info about their games etc"""

    s = requests.session()
    r = s.get("http://tennis.org.nz/ResultsHistoryList.asp?pID="+str(id)+"&gtID=2&CP=GradingList")
    r = s.get("http://tennis.org.nz/ResultsHistoryListPrint.asp")

    soup = BeautifulSoup(r.content, 'html.parser')

    soup = soup.find_all('tr')

    #Parses player data from html
    player_data = []

    for i in soup[:]:
        toadd = []
        for indiv in i.find_all('td'):
            toadd.append(indiv.text)
        player_data.append(toadd)
    s.close()

    #Get vital info - Player Code, Region, Club and Rank

    playerInfo = unicodedata.normalize('NFKD', player_data[0][0]).encode('ascii','ignore').split()
    print playerInfo
    playerCode = playerInfo[2][1:].replace(',', '')
    playerRegion = playerInfo[3].replace(',', '')
    playerClub = playerInfo[4].replace(',', '')
    playerCurRank = playerInfo[13]
    player_data = player_data[4:]

    playerVital = [playerCode, playerRegion, playerClub, playerCurRank]


    #player_data is a list. This add's everything to a nice dictionary, mydict.
    #Each entry in the dict has date, round, rank etc.
    mydict = {}
    count= 0

    for entry in player_data:

        if len(entry)==8:
            toadd = {}
            toadd["date"]=entry[0],
            toadd["round"]=entry[1],
            toadd["comp"]=entry[2],
            toadd["rank"]=entry[3],
            toadd["opponent"]=entry[4],
            toadd["opp_rank"]=entry[5],
            toadd["result"]=entry[6],
            toadd["score"]=entry[7],

            mydict[count]=toadd
            count+=1

    playerDataFinal = json.dumps(mydict)
    return playerDataFinal, playerVital


def getWinLoss(playerData):
    """Get's the W-L record for the player. Takes the playerDataFinal dict object.
       Counts the wins and losses, and returns both integers.
    """
    data = json.loads(playerData)

    wLDict = { "win" : 0,
               "lost": 0}

    for key in data:
        if str("Won") in str(data[key]['result']):
            wLDict['win'] +=1

        if str("Lost") in str(data[key]['result']):
            wLDict['lost'] +=1

    wLDict["win"] = str(wLDict["win"])
    wLDict["lost"] = str(wLDict["lost"])

    wLDict=dict(wLDict)

    return wLDict["win"], wLDict["lost"]


def getWinLossStreaks(playerData):
    """Get's the players best win streak and worst losing streak"""



    playerDataDict = json.loads(playerData)

    #Check if they've ever lost/won

    for i in range(1,len(playerDataDict)):
        if str('Won') in str(playerDataDict[str(i)]['result']):
            hasWon=True
        if str('Lost') in str(playerDataDict[str(i)]['result']):
            hasLost=True


    count=0
    highest=0
    for i in range(1,len(playerDataDict)):
        if str('Won') in str(playerDataDict[str(i)]['result']):
            count+=1
            print count
        else:
            if count > highest: highest = count
            count=0

    count=0
    loss_streak=0
    #Count loss streak
    for i in range(1,len(playerDataDict)):
        if str('Lost') in str(playerDataDict[str(i)]['result']):
            count+=1
        else:
            if count > loss_streak: loss_streak = count
            count=0
    return highest, loss_streak


def hasNumbers(stringToCheck):
    return any(char.isdigit() for char in stringToCheck)

def getGradeVsTime(playerData):
    playerDataDict = json.loads(playerData);


    rankHistory = []
    dateHistory=[]

    for i in range(1,len(playerDataDict)):
        rank = str(playerDataDict[str(i)]['rank'])

        result = re.search('-(.*)-', rank)

        if result != None:
            rankHistory.append(int(result.group((1))))
            dateHistory.append(str(playerDataDict[str(i)]['date']))


        if '-' not in rank and hasNumbers(rank):


            rankHistory.append(int((rank)[-6:-2]))
            dateHistory.append(str(playerDataDict[str(i)]['date']))

    dateHistoryFinal = []
    for t in dateHistory:
        dateHistoryFinal.append(t[3:-2])
    rankHistory.reverse()
    dateHistoryFinal.reverse()

    return rankHistory, dateHistoryFinal





