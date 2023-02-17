import requests
import json
from json.decoder import JSONDecodeError
from pathlib import Path
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


MyRealT_Portfolio_Path = Path('MyRealT_PortfolioOffline.json')
MyRealT_Portfolio_Tx_Path = Path('MyRealT_Portfolio_Tx.json')
RealT_OfflineTokenList_Path = Path('RealT_OfflineTokenList.json')

Now_Time = datetime.today()
print(datetime.timestamp(Now_Time))

MyRealT_Portfolio_Path.touch(exist_ok=True)
with open(MyRealT_Portfolio_Path) as json_file:
    try:
        MyRealT_Portfolio = json.load(json_file)
    except JSONDecodeError:
        MyRealT_Portfolio = {
            "info": {
                "last_sync": str(0),
                "last_Tx": str(0),
                "investment_history": {},
                "valuation_history": {},
                "amount_history": {}
            },
            "data": {}
        }

with open(MyRealT_Portfolio_Tx_Path) as json_file:
    try:
        MyRealT_Portfolio_Tx = json.load(json_file)
    except JSONDecodeError:
        print("Problem with portfolio Tx file!")

RealT_OfflineTokenList_Path.touch(exist_ok=True)
with open(RealT_OfflineTokenList_Path) as json_file:
    try:
        RealT_OfflineTokenList = json.load(json_file)
    except JSONDecodeError:
        print("Problem with RealT Offline Token List file!")

LastTxSync = MyRealT_Portfolio['info']['last_Tx']
MyRealT_Portfolio['info']['last_sync'] = str(datetime.timestamp(Now_Time))
MyTokenList_Gnosis_dict = {}
MyRealT_Portfolio_valuation = 0.0
MyRealT_Portfolio_invest = 0.0
MyRealT_Portfolio_New_Hist = {}

print("Updating offline portfolio as of today from Tx file")
for Tk_item in MyRealT_Portfolio_Tx.get('data'):
    Tk_Costs = 0.0
    Tk_Amounts = 0.0

    TokenInfo = RealT_OfflineTokenList['data'].get(str(Tk_item))

    for Tx_item in MyRealT_Portfolio_Tx['data'][str(Tk_item)]['TokenTx']:
        if MyRealT_Portfolio_Tx['data'][str(Tk_item)]['TokenTx'][str(Tx_item)]['cost'] is not None:
            Tx_Cost = float(MyRealT_Portfolio_Tx['data'][str(Tk_item)]['TokenTx'][str(Tx_item)]['cost'])
            Tx_Amount = float(MyRealT_Portfolio_Tx['data'][str(Tk_item)]['TokenTx'][str(Tx_item)]['amount'])
            Tx_TPrice = float(MyRealT_Portfolio_Tx['data'][str(Tk_item)]['TokenTx'][str(Tx_item)]['tokenPrice'])
            Tk_Costs = Tk_Costs + (Tx_Cost * Tx_Amount)
            Tk_Amounts = Tk_Amounts + Tx_Amount

            if float(Tx_item) > float(LastTxSync):
                if str(Tx_item) in MyRealT_Portfolio['info']['investment_history']:
                    print("Updating invest history")
                    New_Hist_Invest = float(MyRealT_Portfolio['info']['investment_history'][str(Tx_item)]) + (Tx_Cost * Tx_Amount)
                    print(float(MyRealT_Portfolio['info']['investment_history'][str(Tx_item)]) + (Tx_Cost * Tx_Amount))
                else:
                    print("New invest history")
                    New_Hist_Invest = (Tx_Cost * Tx_Amount)
                MyRealT_Portfolio['info']['investment_history'].update({str(Tx_item): New_Hist_Invest})

                if str(Tx_item) in MyRealT_Portfolio['info']['amount_history']:
                    New_Hist_Amount = float(MyRealT_Portfolio['info']['amount_history'][str(Tx_item)]) + Tx_Amount
                else:
                    New_Hist_Amount = Tx_Amount
                MyRealT_Portfolio['info']['amount_history'].update({str(Tx_item): New_Hist_Amount})

                if str(Tx_item) in MyRealT_Portfolio['info']['valuation_history']:
                    New_Hist_Valuation = float(MyRealT_Portfolio['info']['valuation_history'][str(Tx_item)]) + (Tx_Amount * Tx_TPrice)
                else:
                    New_Hist_Valuation = (Tx_Amount * Tx_TPrice)
                MyRealT_Portfolio['info']['valuation_history'].update({str(Tx_item): New_Hist_Valuation})
        else:
            exit("At least one transaction cost is missing")


    #Generating updated Token position
    print(str(Tk_item))
    my_dict = {
        str(Tk_item): {
            'Fullname': MyRealT_Portfolio_Tx['data'][str(Tk_item)]['FullName'],
            'Shortname': MyRealT_Portfolio_Tx['data'][str(Tk_item)]['ShortName'],
            'ContractAddress': str(Tk_item),
            'CurrentBalance': Tk_Amounts,
            'CurrentTokenPrice': TokenInfo['tokenPrice'],
            'CurrentValue': Tk_Amounts * float(TokenInfo['tokenPrice']),
            'InvestValue': Tk_Costs,
            'CurrentRentedUnitsP': TokenInfo['rentedPercentage'],
            'CurrentNetRentP': TokenInfo['annualPercentageYield'],
            'netRentMonth': Tk_Amounts * TokenInfo['netRentMonthPerToken'],
            'Currency': TokenInfo['currency'],
            'RentStartDate': TokenInfo['rentStartDate'],
            'marketplaceLink': TokenInfo['marketplaceLink'],
            'imageLink': TokenInfo['imageLink']
        }
    }
    MyRealT_Portfolio['data'].update(my_dict)

# Chronologically order histories and cumulating overtime
MyRealT_Portfolio['info']['valuation_history'] = {i: MyRealT_Portfolio['info']['valuation_history'][i] for i in sorted(MyRealT_Portfolio['info']['valuation_history'])}
MyRealT_Portfolio['info']['amount_history'] = {i: MyRealT_Portfolio['info']['amount_history'][i] for i in sorted(MyRealT_Portfolio['info']['valuation_history'])}
MyRealT_Portfolio['info']['investment_history'] = {i: MyRealT_Portfolio['info']['investment_history'][i] for i in sorted(MyRealT_Portfolio['info']['valuation_history'])}

Invest_History_Acc = 0.0
Amount_History_Acc = 0.0
Valuation_History_Acc = 0.0

if MyRealT_Portfolio['info']['last_Tx'] is not None:
    # Get last accumulated histories values to update with new ones
    Invest_History_Acc = float(list(MyRealT_Portfolio['info']['investment_history'].values())[-2])
    Amount_History_Acc = float(list(MyRealT_Portfolio['info']['amount_history'].values())[-2])
    Valuation_History_Acc = float(list(MyRealT_Portfolio['info']['valuation_history'].values())[-2])

for i in MyRealT_Portfolio['info']['valuation_history']:
    if float(i) > float(LastTxSync):
        Valuation_History_Acc = Valuation_History_Acc + float(MyRealT_Portfolio['info']['valuation_history'][i])
        MyRealT_Portfolio['info']['valuation_history'][i] = Valuation_History_Acc

for i in MyRealT_Portfolio['info']['investment_history']:
    if float(i) > float(LastTxSync):
        Invest_History_Acc = Invest_History_Acc + float(MyRealT_Portfolio['info']['investment_history'][i])
        MyRealT_Portfolio['info']['investment_history'][i] = Invest_History_Acc

for i in MyRealT_Portfolio['info']['amount_history']:
    if float(i) > float(LastTxSync):
        Amount_History_Acc = Amount_History_Acc + float(MyRealT_Portfolio['info']['amount_history'][i])
        MyRealT_Portfolio['info']['amount_history'][i] = Amount_History_Acc

MyRealT_Portfolio['info']['last_Tx'] = list(MyRealT_Portfolio['info']['amount_history'].keys())[-1]

# Graphing histories overtime
df = pd.DataFrame()
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(
    go.Scatter(
        x=[datetime.fromtimestamp(int(ts)).date() for ts in list(MyRealT_Portfolio['info']['amount_history'].keys())],
        y=list(MyRealT_Portfolio['info']['amount_history'].values()),
        name="# of token"
    ),
    secondary_y=True,
)
fig.add_trace(
    go.Scatter(
        x=[datetime.fromtimestamp(int(ts)).date() for ts in list(MyRealT_Portfolio['info']['investment_history'].keys())],
        y=list(MyRealT_Portfolio['info']['investment_history'].values()),
        name="Invested"
    ),
    secondary_y=False,
)
fig.add_trace(
    go.Scatter(
        x=[datetime.fromtimestamp(int(ts)).date() for ts in list(MyRealT_Portfolio['info']['valuation_history'].keys())],
        y=list(MyRealT_Portfolio['info']['valuation_history'].values()),
        name="Valuation"
    ),
    secondary_y=False,
)
fig.update_layout(
    title_text="MyRealt portfolio evolution"
)
fig.update_xaxes(title_text="Date")
fig.update_yaxes(title_text="Value", secondary_y=False)
fig.update_yaxes(title_text="Tk amount", secondary_y=True)
# fig.show()
fig.write_html('MyRealT_OfflinePortfolio.html')

with open(MyRealT_Portfolio_Path, 'w') as outfile:
    json.dump(MyRealT_Portfolio, outfile, indent=4)
