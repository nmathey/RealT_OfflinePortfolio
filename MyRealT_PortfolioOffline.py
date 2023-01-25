import requests
import json
from json.decoder import JSONDecodeError
from pathlib import Path
from datetime import datetime

MyRealT_Portfolio_Path = Path('MyRealT_PortfolioOffline.json')
MyRealT_Portfolio_Tx_Path = Path('MyRealT_Portfolio_Tx.json')
MyRealT_API_Token = 'YOUR_OWN_REALT_API_TOKEN_KEY'

RealT_API_URI = 'https://api.realt.community/v1/token/'
MyRealT_API_Header = {
    'Accept': '*/*',
    'X_AUTH_REALT_TOKEN': MyRealT_API_Token
}


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

print("Updating offline portfolio as of today from Tx file")
for Tk_item in MyRealT_Portfolio_Tx.get('data'):
    Tk_Costs = 0.0
    Tk_Amounts = 0.0

    TokenInfo = requests.get(
        RealT_API_URI + str(Tk_item),
        headers=MyRealT_API_Header
    ).json()

    for Tx_item in MyRealT_Portfolio_Tx['data'][str(Tk_item)]['TokenTx']:
        if float(Tx_item) > float(LastSync):
            Tx_Cost = float(MyRealT_Portfolio_Tx['data'][str(Tk_item)]['TokenTx'][str(Tx_item)]['cost'])
            Tx_Amount = float(MyRealT_Portfolio_Tx['data'][str(Tk_item)]['TokenTx'][str(Tx_item)]['amount'])
            Tx_TPrice = float(MyRealT_Portfolio_Tx['data'][str(Tk_item)]['TokenTx'][str(Tx_item)]['tokenPrice'])
            Tk_Costs = Tk_Costs + (Tx_Cost * Tx_Amount)
            Tk_Amounts = Tk_Amounts + Tx_Amount

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

    my_dict = {
        MyRealT_Portfolio_Tx['data'][str(Tk_item)]['ContractAddress']: {
            'Fullname': MyRealT_Portfolio_Tx['data'][str(Tk_item)]['FullName'],
            'ContractAddress': MyRealT_Portfolio_Tx['data'][str(Tk_item)]['ContractAddress'],
            'CurrentBalance': Tk_Amounts,
            'CurrentTokenPrice': TokenInfo['tokenPrice'],
            'CurrentValue': Tk_Amounts * float(TokenInfo['tokenPrice']),
            'InvestValue': Tk_Costs,
            'Currency': TokenInfo['currency']
        }
    }
    MyRealT_Portfolio['data'].update(my_dict)

#ordonner les history puis les cumuler dans l'ordre chronologique
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
print(MyRealT_Portfolio['info']['valuation_history'])

for i in MyRealT_Portfolio['info']['investment_history']:
    if float(i) > float(LastSync):
        Invest_History_Acc = Invest_History_Acc + float(MyRealT_Portfolio['info']['investment_history'][i])
        MyRealT_Portfolio['info']['investment_history'][i] = Invest_History_Acc
print(MyRealT_Portfolio['info']['investment_history'])

for i in MyRealT_Portfolio['info']['amount_history']:
    if float(i) > float(LastSync):
        Amount_History_Acc = Amount_History_Acc + float(MyRealT_Portfolio['info']['amount_history'][i])
        MyRealT_Portfolio['info']['amount_history'][i] = Amount_History_Acc
print(MyRealT_Portfolio['info']['amount_history'])

MyRealT_Portfolio['info']['last_Tx']=list(MyRealT_Portfolio['info']['amount_history'].keys())[-1]

with open(MyRealT_Portfolio_Path, 'w') as outfile:
    json.dump(MyRealT_Portfolio, outfile, indent=4)
