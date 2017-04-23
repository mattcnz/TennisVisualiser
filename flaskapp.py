__author__ = 'mattmilliken'

from flask import Flask, render_template, request
from main import *
import requests
import traceback


app = Flask(__name__)


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

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/lander')
def lander():
    return render_template('lander.html')

@app.route('/stats', methods=['POST'])
def stats():

    name =  request.form['playerName']
    sex =  request.form['optradio']

    try:
        id = searchPlayer(name, sex)
    except:
        return "No Player With That Name"


    playerData, playerVital = getPlayerData(id)
    winStreak, lossStreak = getWinLossStreaks(playerData)
    print winStreak, lossStreak
    wins, losses = getWinLoss(playerData)

    if lossStreak == 0 and winStreak != 0:
        winPercentage = 1
        lossPercentage = 0
    else:
        winPercentage = float(winStreak) / (winStreak+lossStreak)
        winPercentage = int(winPercentage*100)
        lossPercentage = 1- winPercentage

    rankhistory, dateHistory = getGradeVsTime(playerData)

    return render_template('stats.html', rankhistory=rankhistory, dateHistory=dateHistory, wins=wins, losses=losses, winStreak=winStreak, lossStreak=lossStreak, id=id, name=name, winPercentage=winPercentage, lossPercentage=lossPercentage,playerVital=playerVital
                           )

if __name__ == '__main__':
  app.run()

