import requests
import json
from json.decoder import JSONDecodeError
from pathlib import Path
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from bs4 import BeautifulSoup
from MySecrets import MyRealT_API_Token


MyRealT_Portfolio_Path = Path('MyRealT_PortfolioOffline.json')
MyRealT_Portfolio_Tx_Path = Path('MyRealT_Portfolio_Tx.json')

RealT_API_URI = 'https://api.realt.community/v1/token/'
MyRealT_API_Header = {
    'Accept': '*/*',
    'X_AUTH_REALT_TOKEN': MyRealT_API_Token
}

RealT_TokenHistory_URI = 'https://www.cryptalloc.com/realtsoon/index.php?MODL=HIST&house='

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
                "last_Tx": None,
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

LastSync = MyRealT_Portfolio['info']['last_sync']
MyRealT_Portfolio['info']['last_sync'] = str(datetime.timestamp(Now_Time))
MyTokenList_Gnosis_dict = {}
MyRealT_Portfolio_valuation = 0.0
MyRealT_Portfolio_invest = 0.0
MyRealT_Portfolio_New_Hist = {}

print("Updating offline portfolio as of today from Tx file, RealT API & Cryptalloc/realtsoon website")
for Tk_item in MyRealT_Portfolio_Tx.get('data'):
    Tk_Costs = 0.0
    Tk_Amounts = 0.0

    TokenInfo = requests.get(
        RealT_API_URI + str(Tk_item),
        headers=MyRealT_API_Header
    ).json()

    for Tx_item in MyRealT_Portfolio_Tx['data'][str(Tk_item)]['TokenTx']:
        if MyRealT_Portfolio_Tx['data'][str(Tk_item)]['TokenTx'][str(Tx_item)]['cost'] is not None:
            Tx_Cost = float(MyRealT_Portfolio_Tx['data'][str(Tk_item)]['TokenTx'][str(Tx_item)]['cost'])
            Tx_Amount = float(MyRealT_Portfolio_Tx['data'][str(Tk_item)]['TokenTx'][str(Tx_item)]['amount'])
            Tx_TPrice = float(MyRealT_Portfolio_Tx['data'][str(Tk_item)]['TokenTx'][str(Tx_item)]['tokenPrice'])
            Tk_Costs = Tk_Costs + (Tx_Cost * Tx_Amount)
            Tk_Amounts = Tk_Amounts + Tx_Amount

            if float(Tx_item) > float(LastSync):
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

   # Getting updates from https://www.cryptalloc.com/realtsoon/
    TokenHistInfo = requests.get(RealT_TokenHistory_URI + str(MyRealT_Portfolio_Tx['data'][str(Tk_item)]['ShortName'])).content
    currentRentedUnitsP = None
    currentNetRentP = None
    soup = BeautifulSoup(TokenHistInfo, "html.parser")
    net_rent_p = soup.find('td', string='net_rent_p')
    if net_rent_p.next_sibling.next_sibling is None:
        currentNetRentP = net_rent_p.next_sibling.string
    else:
        currentNetRentP = net_rent_p.next_sibling.next_sibling.string
    rented_units_p = soup.find('td', string='rented_units_p')
    if rented_units_p.next_sibling.next_sibling is None:
        currentRentedUnitsP = rented_units_p.next_sibling.string
    else:
        currentRentedUnitsP = rented_units_p.next_sibling.next_sibling.string

    #Generating updated Token position
    my_dict = {
        MyRealT_Portfolio_Tx['data'][str(Tk_item)]['ContractAddress']: {
            'Fullname': MyRealT_Portfolio_Tx['data'][str(Tk_item)]['FullName'],
            'Shortname': MyRealT_Portfolio_Tx['data'][str(Tk_item)]['ShortName'],
            'ContractAddress': MyRealT_Portfolio_Tx['data'][str(Tk_item)]['ContractAddress'],
            'CurrentBalance': Tk_Amounts,
            'CurrentTokenPrice': TokenInfo['tokenPrice'],
            'CurrentValue': Tk_Amounts * float(TokenInfo['tokenPrice']),
            'InvestValue': Tk_Costs,
            'CurrentRentedUnitsP': currentRentedUnitsP,
            'CurrentNetRentP': currentNetRentP,
            'Currency': TokenInfo['currency']
        }
    }
    MyRealT_Portfolio['data'].update(my_dict)

# Chronologically order histories and cumulating overtime
MyRealT_Portfolio['info']['valuation_history'] = {i: MyRealT_Portfolio['info']['valuation_history'][i] for i in sorted(MyRealT_Portfolio['info']['valuation_history'])}
MyRealT_Portfolio['info']['amount_history'] = {i: MyRealT_Portfolio['info']['amount_history'][i] for i in sorted(MyRealT_Portfolio['info']['valuation_history'])}
MyRealT_Portfolio['info']['investment_history'] = {i: MyRealT_Portfolio['info']['investment_history'][i] for i in sorted(MyRealT_Portfolio['info']['valuation_history'])}
if MyRealT_Portfolio['info']['last_Tx'] is None:
    Invest_History_Acc = 0.0
    Amount_History_Acc = 0.0
    Valuation_History_Acc = 0.0
else:
    Invest_History_Acc = float(list(MyRealT_Portfolio['info']['investment_history'].values())[-1])
    Amount_History_Acc = float(list(MyRealT_Portfolio['info']['amount_history'].values())[-1])
    Valuation_History_Acc = float(list(MyRealT_Portfolio['info']['valuation_history'].values())[-1])

for i in MyRealT_Portfolio['info']['valuation_history']:
    if float(i) > float(LastSync):
        Valuation_History_Acc = Valuation_History_Acc + float(MyRealT_Portfolio['info']['valuation_history'][i])
        MyRealT_Portfolio['info']['valuation_history'][i] = Valuation_History_Acc

for i in MyRealT_Portfolio['info']['investment_history']:
    if float(i) > float(LastSync):
        Invest_History_Acc = Invest_History_Acc + float(MyRealT_Portfolio['info']['investment_history'][i])
        MyRealT_Portfolio['info']['investment_history'][i] = Invest_History_Acc

for i in MyRealT_Portfolio['info']['amount_history']:
    if float(i) > float(LastSync):
        Amount_History_Acc = Amount_History_Acc + float(MyRealT_Portfolio['info']['amount_history'][i])
        MyRealT_Portfolio['info']['amount_history'][i] = Amount_History_Acc

# MyRealT_Portfolio['info']['last_Tx']=list(MyRealT_Portfolio['info']['amount_history'].keys())[-1]

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
fig.write_html('MyRealT_OfflinePortfolio.html', auto_open=True)

with open(MyRealT_Portfolio_Path, 'w') as outfile:
    json.dump(MyRealT_Portfolio, outfile, indent=4)
