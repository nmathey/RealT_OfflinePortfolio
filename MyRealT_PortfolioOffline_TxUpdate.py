import requests
import json
from json.decoder import JSONDecodeError
import re
from pathlib import Path
from datetime import datetime

MyRealT_Portfolio_Path = Path('MyRealT_Portfolio_Tx.json')
MyWallet_Gnosis_address = 'YOUR_OWN_REALT_PROPERTIESTOKEN_WALLET_ADDRESS'
MyRealT_API_Token = 'YOUR_OWN_REALT_API_TOKEN_KEY'

Gnosis_API_TokenTx_URI = 'https://blockscout.com/xdai/mainnet/api?module=account&action=tokentx&address='
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
                "last_sync": str(datetime.timestamp(Now_Time)),
                "last_blockNumber": None
            },
            "data": {}
        }

MyRealT_Portfolio['info']['last_sync'] = str(datetime.timestamp(Now_Time))
MyTokenList_Gnosis_Dict = {}

print("Checking if new token transaction with online wallet")
if MyRealT_Portfolio['info']['last_blockNumber'] is None:
    MyTokenTxList_Gnosis = json.loads(requests.get(Gnosis_API_TokenTx_URI + MyWallet_Gnosis_address + '&sort=asc').text)
else:
    MyTokenTxList_Gnosis = json.loads(requests.get(Gnosis_API_TokenTx_URI + MyWallet_Gnosis_address + '&sort=asc&start_block=' + str(int(MyRealT_Portfolio['info']['last_blockNumber'])+1)).text)

for item in MyTokenTxList_Gnosis.get('result'):
    if re.match(r'^RealToken', str(item.get('tokenName'))):
        MyRealT_Portfolio['info']['last_blockNumber'] = item.get('blockNumber')
        if item.get('contractAddress') not in MyRealT_Portfolio['data']:
            print("New token detected on online wallet: adding token to offline portfolio: " + item.get('contractAddress'))
            TokenInfoReq = requests.get(
                RealT_API_URI + str(item.get('contractAddress')),
                headers=MyRealT_API_Header
            )

            if TokenInfoReq.text == "[]":
                exit("Token not found in API")

            TokenInfo = TokenInfoReq.json()

            MyRealT_Portfolio['data'].update(
                {
                    item.get('contractAddress'): {
                        "FullName": TokenInfo['fullName'],
                        "ShortName": TokenInfo['shortName'],
                        'Symbol': item.get('tokenSymbol'),
                        'ContractAddress': item.get('contractAddress'),
                        'CurrentTokenPrice': TokenInfo['tokenPrice'],
                        'Currency': TokenInfo['currency'],
                        'TokenTx': {}
                    }
                }
            )
        print("Updating Token " + str(item.get('contractAddress') + "with new Tx - " + str(item.get('blockNumber'))))
        if str(item.get('to')) != MyWallet_Gnosis_address:
            MyRealT_Portfolio['data'][item.get('contractAddress')]['TokenTx'].update(
                {
                    item.get('timeStamp'):
                        {
                            'amount': -(float(item.get('value')) / pow(10, int(item.get('tokenDecimal')))),
                            'cost': None,
                            'tokenPrice': TokenInfo['tokenPrice'],
                            'currency': "USD"
                        }
                }
            )
        else:
            MyRealT_Portfolio['data'][item.get('contractAddress')]['TokenTx'].update(
                {
                    item.get('timeStamp'):
                        {
                            'amount': float(item.get('value')) / pow(10, int(item.get('tokenDecimal'))),
                            'cost': None,
                            'tokenPrice': TokenInfo['tokenPrice'],
                            'currency': "USD"
                        }
                }
            )
#print(MyRealT_Portfolio.get('data'))
with open(MyRealT_Portfolio_Path, 'w') as outfile:
    json.dump(MyRealT_Portfolio, outfile, indent=4)
