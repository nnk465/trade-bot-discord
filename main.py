import requests
import json
import discord
import time

url = 'https://www.binance.com/fr/futures-activity/leaderboard?type=myProfile&encryptedUid=08F22AF1161739C74509F9F38F188A8D'
uneid = '3F45CB93EAF1326BC467A938E172122D'

# creation bot discord
defIntents = discord.Intents.default()
defIntents.members = True
client = discord.Client(intents=defIntents)
token = 'MTAyOTc4MzU2ODM4NzQyMDI0NA.GKGQQK.kfivCHOFvKhYODvtOXe6k4FBpJppf3QDkBHp2Q'


def send_message(message):
    general_channel = client.get_channel(610807410952634372)
    general_channel.send(str(message))


def get_price(sym):
    u = 'https://www.binance.com/fapi/v1/ticker/24hr?symbol=' + sym + 'BUSD'
    response = requests.get(u)
    code = json.loads(response.text)
    return code.get('lastPrice')


def get_position(uid):
    r = requests.post('https://www.binance.com/bapi/futures/v1/public/future/leaderboard/getOtherPosition',
                      json=dict(encryptedUid=uid, tradeType="PERPETUAL"))
    json_requests = json.loads(r.text)
    return json_requests


def get_name(uid):
    r = requests.post('https://www.binance.com/bapi/futures/v2/public/future/leaderboard/getOtherLeaderboardBaseInfo',
                      json=dict(encryptedUid=uid, tradeType="PERPETUAL"))
    json_requests = json.loads(r.text)
    return json_requests['data']['nickName']


def get_hour(hour):
    return str(hour[0]) + '/' + str(hour[1]) + '/' + str(hour[2]) + ' ' + str(int(hour[3] + 2)) + ':' + str(
        hour[4]) + ':' + str(hour[5])


var = {'otherPositionRetList': [
    {'symbol': 'NEARBUSD', 'entryPrice': 4.443979, 'markPrice': 3.50664535, 'pnl': -4874.13498, 'roe': -5.34604191,
     'updateTime': [2022, 10, 4, 4, 2, 54, 591000000], 'amount': 5200.0, 'updateTimeStamp': 1664856174591,
     'yellow': False, 'tradeBefore': False},
    {'symbol': 'BNBBUSD', 'entryPrice': 283.7040796001, 'markPrice': 277.51123572, 'pnl': 619.284388, 'roe': 0.44631302,
     'updateTime': [2022, 10, 7, 2, 52, 33, 667000000], 'amount': -100.0, 'updateTimeStamp': 1665111153667,
     'yellow': False, 'tradeBefore': False},
    {'symbol': 'BTCBUSD', 'entryPrice': 20140.0, 'markPrice': 19416.3, 'pnl': -2171.1, 'roe': -0.93182017,
     'updateTime': [2022, 10, 6, 13, 1, 38, 235000000], 'amount': 3.0, 'updateTimeStamp': 1665061298235,
     'yellow': False, 'tradeBefore': False}], 'updateTime': [2022, 10, 4, 4, 2, 54, 591000000],
    'updateTimeStamp': 1664856174591}


@client.event
async def on_ready():
    print('ok')
    sendPosition(uneid)


def sendPosition(eid):
    general_channel = client.get_channel(610807410952634372)
    code = get_position(eid)['data']
    dateList = []
    newDateList = []
    name = get_name(eid)
    for m in range(5):
        newCode = get_position(eid)['data']

        # repérer si il y a de nouveaux trades
        for i in range(len(newCode['otherPositionRetList'])):
            newDateList.append(newCode['otherPositionRetList'][i]['updateTime'])

        # si il n'y a rien de nouveau détécté
        if newDateList == dateList:
            pass
        # si il y'a du nouveau
        else:
            # repérer si il y'a un nouveau trade
            for date in newDateList:
                if not date in dateList:
                    emplacement = newDateList.index(date)
                    newTrade = newCode['otherPositionRetList'][emplacement]
                    await general_channel.send(
                        f" {name} a tradé {newTrade['amount']} {newTrade['symbol']} pour {int(newTrade['amount'] * int(newTrade['entryPrice']))}$"
                        f"\n prix d'entré: {newTrade['entryPrice']}$"
                        f"\n date/heure: {get_hour(newTrade['updateTime'])}")
            # repérer si il n'y a pas eu une cloture de trade
            for date in dateList:
                if not date in newDateList:
                    emplacement = dateList.index(date)
                    oldTrade = code['otherPositionRetList'][emplacement]
                    await general_channel.send(
                        f"{name} vient de cloturer: {oldTrade['amount']} {oldTrade['symbol']}"
                        f"\n{round(oldTrade['entryPrice'] * oldTrade['amount'])} --> {round(oldTrade['entryPrice'] * oldTrade['amount'] + oldTrade['pnl'])}({oldTrade['roe']}%)"
                        f"\ndate et heure: {time.strftime('%x'), time.strftime('%H'), ':', time.strftime('%M')}")
                    if oldTrade['pnl'] > 0:
                        await general_channel.send(f"benef de {oldTrade['pnl']}")
                    else:
                        await general_channel.send(f"perte de {oldTrade['pnl']}")

        dateList = newDateList
        newDateList = []


client.run(token)
