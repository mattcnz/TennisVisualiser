__author__ = 'mattmilliken'

from flask import Flask, render_template, request
from main import *
import requests
import traceback


app = Flask(__name__)


#Returns Results - Test Function
@app.route('/results/<ID>')
def test(ID):
    s = requests.session()
    r = s.get("http://tennis.org.nz/ResultsHistoryList.asp?pID=" + ID +"&gtID=2&CP=GradingList")

    r = s.get("http://tennis.org.nz/ResultsHistoryListPrint.asp")
    return r.content

#Counter - Test
@app.route('/countme/<input_str>')
def count_me(input_str):
    return input_str

#Handles Errors
@app.errorhandler(500)
def internal_error(exception):
    """Show traceback in the browser when running a flask app on a production server.
    By default, flask does not show any useful information when running on a production server.
    By adding this view, we output the Python traceback to the error 500 page.
    """
    trace = traceback.format_exc()
    return("<pre>" + trace + "</pre>"), 500

#-----------------------------------------------------------------#

@app.route('/work')
def main(jsondata=None):
    data = getWinLoss(14056)

    return render_template('d3test.html',jsondata=data)

@app.route('/workextend/<ID>')
def workextend(ID, content=None):

    data = getPlayerData(ID)
    return render_template('index2.html', content=data)

@app.route('/returnPlayerWinLoss/<ID>')
def winLoss(ID, graphData=None):
    graphData=getWinLoss(ID)
    return render_template('extend.html', graphData=graphData)


@app.route('/lander')
def lander():
    return render_template('lander.html')

@app.route('/testFormInput', methods=['POST'])
def testFormInput():

    name =  request.form['playerName']
    try:
        id = searchPlayer(name)
    except:
        return "no player with that name"


    playerData, playerVital = getPlayerData(id)
    winStreak, lossStreak = getWinLossStreaks(playerData)
    wins, losses = getWinLoss(playerData)

    winPercentage = float(winStreak) / (winStreak+lossStreak)
    lossPercentage = 1- winPercentage

    rankhistory, dateHistory = getGradeVsTime(playerData)

    return render_template('stats.html', rankhistory=rankhistory, dateHistory=dateHistory, wins=wins, losses=losses, winStreak=winStreak, lossStreak=lossStreak, id=id, name=name, winPercentage=winPercentage, lossPercentage=lossPercentage,playerVital=playerVital
                           )



if __name__ == '__main__':
  app.run()

