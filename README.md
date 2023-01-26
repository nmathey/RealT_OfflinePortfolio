
# RealT_OfflinePortfolio
Consolidate an offline version of your RealT properties portfolio

***This is a work in progress / sandbox personal development***
I'm not a dev so forgive the quick and dirty style ;)

## **Current limitations/requirements**

 * Gnosis network only
 * Need a RealT API key
 * If Token not found in RealT API, exiting without updating transactions JSON file
 * Need to manually update purchase/sell for each new transaction price once transactions JSON file generated/updated

## **Current usage**

***Step 1 - Syncing RealT Token transaction to/from your wallet - MyRealT_PortfolioOffline_TxUpdate.py***:
 1) Copy the file `secrets.py.example` to `secrets.py`
 2) In `secrets.py`, replace variables with your own Gnosis wallet address where your RealT Token are stored
 3) In `secrets.py`, replace your own RealT API Key via "MyRealT_API_Token" variable
 4) Run MyRealT_PortfolioOffline_TxUpdate.py and make a wish

***Output: MyRealT_Portfolio_Tx.json***
	 "Info" includes: 
 * last sync time with network
 * last transaction blockNumber synced

"data" includes for each property token linked to a transaction:
 - FullName
 - ShortName
 - Symbol
 - ContractAddress
 - CurrentTokenPrice
 - Currency
 - For each transaction: 
	 - amount
	 - cost: price you paid/sold *--> Need to be updated manually for now*
	 - tokenPrice
	 - currency
 

***Step 2 - Consolidating offline RealT portfolio based on transaction JSON file - MyRealT_PortfolioOffline.py***
1) Provide your own RealT API Key via "MyRealT_API_Token" variable
2) Run MyRealT_PortfolioOffline.py and cross your fingers

***Output: MyRealT_PortfolioOffline.json***
	 "Info" includes: 
 * last consolidation time
 * last transaction consolidated
 * investment history: cumulation of investments overtime (price you paid/sold)
 * valuation history: cumulation of portfolio valuation overtime (based on official token prices)
 * amount history: cumulation of owned token overtime

"data" includes for each property token own:
 - FullName
 - ContractAddress
 - CurrentBalance
 - CurrentTokenPrice
 - CurrentValue
 - InvestValue
 - Currency

Thanks to RealT Dev community especially those behind the API

For more information about RealT: https://realt.co/

If you want to signup, here is my referral link **https://realt.co/ref/nmathey/**

If you want to donate/support me, any ERC20 token transfer to the following Ethereum/Gnosis address will be appreciated: 0xEFf0d54e391C6097CdF24A3Fc450988Ebd9a91F7
