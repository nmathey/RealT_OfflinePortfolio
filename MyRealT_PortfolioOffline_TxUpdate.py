import requests
import json
from json.decoder import JSONDecodeError
import re
from pathlib import Path
from datetime import datetime, timedelta

from MySecrets import MyRealT_API_Token, MyWallet_Gnosis_address

MyRealT_Portfolio_Tx_Path = Path('MyRealT_Portfolio_Tx.json')
RealT_OfflineTokenList_Path = Path('RealT_OfflineTokenList.json')

Gnosis_API_TokenTx_URI = 'https://blockscout.com/xdai/mainnet/api?module=account&action=tokentx&address='
RealT_API_TokenList_URI = 'https://api.realt.community/v1/token'

MyRealT_API_Header = {
    'Accept': '*/*',
    'X-AUTH-REALT-TOKEN': MyRealT_API_Token
}


Now_Time = datetime.today()
print(datetime.timestamp(Now_Time))


RealT_OfflineTokenList_Path.touch(exist_ok=True)
with open(RealT_OfflineTokenList_Path) as json_file:
    try:
        RealT_OfflineTokenList = json.load(json_file)
    except JSONDecodeError:
        RealT_OfflineTokenList = {
            "info": {
                "last_sync": str(datetime.timestamp(Now_Time - timedelta(weeks=1)))
            },
            "data": {}
        }

# Update offlineTokenList if more than 1 week old
if float(RealT_OfflineTokenList["info"]["last_sync"]) < datetime.timestamp(Now_Time - timedelta(weeks=1)):
    TokenListReq = requests.get(
                RealT_API_TokenList_URI,
                headers=MyRealT_API_Header
            )

    TokenList = TokenListReq.json()
    for item in TokenList:
        RealT_OfflineTokenList['data'].update(
            {
                item.get('uuid').lower(): {
                    'fullName': item.get('fullName'),
                    'shortName': item.get('shortName'),
                    'xDaiContract': item.get('xDaiContract').lower(),
                    'gnosisContract': item.get('gnosisContract').lower(),
                    'tokenPrice': item.get('tokenPrice'),
                    'netRentMonthPerToken': item.get('netRentMonthPerToken'),
                    'currency': item.get('currency'),
                    'annualPercentageYield': item.get('annualPercentageYield'),
                    'marketplaceLink': item.get('marketplaceLink'),
                    'imageLink': item.get('imageLink')[0],
                    'rentStartDate': item.get('rentStartDate'),
                    'rentedPercentage': float(item.get('rentedUnits'))/float(item.get('totalUnits'))
                }
            }
        )

    RealT_OfflineTokenList['info']['last_sync'] = str(datetime.timestamp(Now_Time))

MyRealT_Portfolio_Tx_Path.touch(exist_ok=True)
with open(MyRealT_Portfolio_Tx_Path) as json_file:
    try:
        MyRealT_Portfolio_Tx = json.load(json_file)
    except JSONDecodeError:
        MyRealT_Portfolio_Tx = {
            "info": {
                "last_sync": str(datetime.timestamp(Now_Time)),
                "last_blockNumber": None
            },
            "data": {}
        }

MyRealT_Portfolio_Tx['info']['last_sync'] = str(datetime.timestamp(Now_Time))
MyTokenList_Gnosis_Dict = {}

print("Checking if new token transaction with online wallet")
if MyRealT_Portfolio_Tx['info']['last_blockNumber'] is None:
    MyTokenTxList_Gnosis = json.loads(requests.get(Gnosis_API_TokenTx_URI + MyWallet_Gnosis_address + '&sort=asc').text)
else:
    MyTokenTxList_Gnosis = json.loads(requests.get(Gnosis_API_TokenTx_URI + MyWallet_Gnosis_address + '&sort=asc&start_block=' + str(int(MyRealT_Portfolio_Tx['info']['last_blockNumber'])+1)).text)

previous_token_contract = None
for item in MyTokenTxList_Gnosis.get('result'):
    TokenInfo = RealT_OfflineTokenList['data'].get(str(item.get('contractAddress')))
    if re.match(r'^REALTOKEN', str(item.get('tokenSymbol'))) or re.match(r'^armmREALTOKEN',str(item.get('tokenSymbol'))):
        if item.get('contractAddress') not in MyRealT_Portfolio_Tx['data'] and not re.match(r'^armmREALTOKEN',str(item.get('tokenSymbol'))):
            if item.get('contractAddress') not in RealT_OfflineTokenList['data']:
                print(item.get('contractAddress'))
                print(RealT_OfflineTokenList['data'].keys())
                print(RealT_OfflineTokenList['data'].get('0x2fb7eeeece8498af2bf5b00ea29ca03005c35956'))
                exit("Token not found in API try again in few days")

            MyRealT_Portfolio_Tx['data'].update(
                {
                    item.get('contractAddress'): {
                        "FullName": TokenInfo['fullName'],
                        "ShortName": TokenInfo['shortName'],
                        'ContractAddress': TokenInfo['gnosisContract'],
                        'CurrentTokenPrice': TokenInfo['tokenPrice'],
                        'Currency': TokenInfo['currency'],
                        'TokenTx': {}
                    }
                }
            )
        print("Updating Token " + str(item.get('contractAddress') + "with new Tx - " + str(item.get('blockNumber'))))
        if str(item.get('to')) != MyWallet_Gnosis_address:
            MyRealT_Portfolio_Tx['data'][item.get('contractAddress')]['TokenTx'].update(
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
            if MyRealT_Portfolio_Tx['info']['last_blockNumber'] == item.get('blockNumber') and re.match(r'^armmREALTOKEN', str(item.get('tokenSymbol'))):
                #deleting last tokentx wich looks RMM related
                del MyRealT_Portfolio_Tx['data'][previous_token_contract]['TokenTx'][item.get('timeStamp')]
            else:
                MyRealT_Portfolio_Tx['data'][item.get('contractAddress')]['TokenTx'].update(
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
        MyRealT_Portfolio_Tx['info']['last_blockNumber'] = item.get('blockNumber')
        previous_token_contract = item.get('contractAddress')
#print(MyRealT_Portfolio.get('data'))
with open(MyRealT_Portfolio_Tx_Path, 'w') as outfile:
    json.dump(MyRealT_Portfolio_Tx, outfile, indent=4)

with open(RealT_OfflineTokenList_Path, 'w') as outfile:
    json.dump(RealT_OfflineTokenList, outfile, indent=4)