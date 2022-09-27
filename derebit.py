"""
This program is for getting a DataFrame containing information on all the options contracts for a
specific cryptocurrency on the Derebit crypto options exchange
"""

import pandas as pd
import numpy as np
import datetime as dt

import asyncio
import websockets
import json
import nest_asyncio
nest_asyncio.apply()

# API request functions
async def CallAPI(msg):
    async with websockets.connect('wss://test.deribit.com/ws/api/v2') as websocket:
        await websocket.send(msg)
        while websocket.open:
            response = await websocket.recv()
            return response

def AsnycLoop(api, message):
    return asyncio.get_event_loop().run_until_complete(api(message))

def GetResult(msg):
	"""
	This function returns the results of our API request
		Parameters:
			msg (dictionary) : The requrest message
		Returns
			results (DataFrame) : A DataFrame containing the results of the request 
	"""
	resp = AsnycLoop(CallAPI, json.dumps(msg))
	print(pd.read_json(resp))
	print(pd.read_json(resp).columns)
	df = pd.read_json(resp).loc[:,"result"]
	results = pd.DataFrame((list(df.values)))
	return results

def GetIndexPrice(currency = "BTC"):
	"""
	Returns the current price of the index for a cryptocurrency
		Parameters:
			currency (string) : The cryptocurrency you want the index for
		Returns:
			current_price (float) : The current price of the index
	"""
	# Mapping from currencies to indexes
	curreny_index_map = {"BTC":"btc_usd",
						"ETH":"etc_usd",
						"SOL":"sol_usd" }
	# Get the name of the index
	index_name = curreny_index_map[currency]
	# The request message to get the current index price
	index_msg = { "jsonrpc": "2.0",
				 "method": "public/get_index_price",
				 "id": 42,
				 "params": {"index_name": index_name}
				}
	current_price = GetResult(index_msg).iloc[1,0]
	return current_price

def GetRawOptionsDF(currency = "BTC"):
	"""
	Returns a DataFrame with all the data on the options contracts currently trading on
	a certain cryptocurrency
		Parameters:
			currency (string) : The cryptocurrency you want data for
		Returns:
			raw_data (DataFrame) : A DataFrame with all the data on the derivative contracts for the cryptocurrency
	"""
	derivatives_msg = {
		    "jsonrpc": "2.0",
		    "id": 833,
		    "method": "public/get_book_summary_by_currency",
		    "params": { "currency": currency,
		    "kind":"option"}
		  }
	# Create a list of the data that is relevant
	relevant_data = [
	"instrument_name",
	"underlying_index",
	"underlying_price",
	"bid_price",
	"ask_price",
	"mark_price",
	"volume",
	"open_interest",
	]
	raw_data = GetResult(derivatives_msg)
	return raw_data

def GetRelevantOptionsDF(currency = "BTC"):
	"""
	Returns a DataFrame with all the data on the options contracts currently trading on a cryptocurrecy
	so that into only includes relevant columns
		Parameters:
			currency (string) : The cryptocurrency you want data for
		Returns:
			data (DataFrame) : A DataFrame with all the relevant data on the options conctrats for the cryptocurrency
	"""
	# Get the raw data from the API request
	raw_data = GetRawOptionsDF(currency)
	# Create a list of the data that is relevant
	relevant_data = [
	"instrument_name",
	"underlying_index",
	"underlying_price",
	"bid_price",
	"ask_price",
	"mark_price",
	"volume",
	"open_interest"
	]
	data = raw_data.loc[:,relevant_data]
	return data

def RenameOptionsDF(data):
	"""
	Renames the columns DataFrame with the relevant information on the options for a crypto
		Parameters:
			data (DataFrame) : A DataFrame with all the relevant data on the options conctrats for the cryptocurrency
	"""
	column_map = {"underlying_index":"Underlying Name",
	"underlying_price":"Underlying Price",
	"bid_price":"Bid",
	"ask_price":"Ask",
	"mark_price":"Mark",
	"volume":"24H Vol",
	"open_interest":"Open Interest"
	}
	data.rename(columns = column_map, inplace = True)

# Functions to transform the raw data into the correct format
def CallOrPut(contract_name_series):
	"""
	This function returns a Series which contains the type of the option
		Parameters:
			contract_name_series (Series) : A Series containing the names of the options contracts
		Return:
			otype_series (Series) : A Series containing the type of the option ("Call"/"Put")
	"""
	call_mask = contract_name_series.str.endswith("-C")
	otype_series = np.where(call_mask, "Call","Put")
	return otype_series

def Strike(contract_name_series):
	"""
	This function returns a Series which contains the strike of the option
		Parameters:
			contract_name_series (Series) : A Series containing the names of the options contracts
		Return:
			strike_series (Series) : A Series containing the strikes of the option
	"""
	info_series = contract_name_series.str.split('-')
	strike_series = info_series.str[2]
	return strike_series.astype(np.int64)

def ExpiryDatetime(contract_name_series):
	"""
	This function returns a Series which contains the expriy datetime of the option
		Parameters:
			contract_name_series (Series) : A Series containing the names of the options contracts
		Return:
			expiry_dt_series (Series) : A Series containing the expiry dates of the of the option as datetime objects
	"""
	# Get a Series with the information about the options contract
	info_series = contract_name_series.str.split('-')
	# Get a Series of DataTime objects representing the expiry datees
	expiry_dt_series = pd.to_datetime(info_series.str[1])
	# Derebit options expiry at 08:00 UTC
	expiry_dt_series += dt.timedelta(seconds = 60*60*8)
	return expiry_dt_series

def SortOptionsDF(data):
	"""
	Sorts the columns of the DataFrame containing the data on the options
		Parameters:
			data (DataFrame) : A DataFrame with all the data on the derivative contracts for the cryptocurrency
		Returns:
			option_contracts (DataFrame) : A DataFrame containing all the information about
			the option contracts on an instrument (in the correct format for use in the IV surface class)
	"""
	option_contracts = data.reindex(columns = ["Expiration","Underlying Name",
	"Underlying Price",
	"Strike",
	"Type",
	"Bid",
	"Ask",
	"Mark",
	"24H Vol",
	"Open Interest"])
	option_contracts.sort_values(by = ["Expiration","Type","Strike"], inplace = True)
	option_contracts.set_index(["Expiration"], inplace = True)
	return option_contracts

def TransformOptionsDF(data, currency = "BTC"):
	"""
	Transforms the DataFrame containing the relevant data on all the options into the correct
	format to pass into the implied volatility surface constructor
		Parameters:
			data (DataFrame) : A DataFrame with all the data on the derivative contracts for the cryptocurrency
			currency (string) : The cryptocurrency you want data for
		Returns:
			option_contracts (DataFrame) : A DataFrame containing all the information about
			the option contracts on an instrument (in the correct format for use in the IV surface class)
	"""
	# First rename the columns of the DataFrame
	RenameOptionsDF(data)

	# Multiply the prices by the price of the index to get the bid,ask and mark in USD
	index_price = GetIndexPrice(currency)
	data.loc[:,["Bid","Ask","Mark"]] *= index_price

	# Create a column with the type of the option (call or put)
	data.loc[:,"Type"] = CallOrPut(data.loc[:,"instrument_name"])
	# Create a column with the strike of the option
	data.loc[:,"Strike"] = Strike(data.loc[:,"instrument_name"])
	# Create a column with the expiry of the option as a datetime object
	data.loc[:,"Expiration"] = ExpiryDatetime(data.loc[:,"instrument_name"])
	
	data.drop(columns = ["instrument_name"], inplace = True)
	option_contracts = SortOptionsDF(data)
	return option_contracts

def GetOptions(currency = "BTC"):
	"""
		currency (string) : The cryptocurrency you want data for
	"""
	data = GetRelevantOptionsDF(currency)
	option_contracts = TransformOptionsDF(data, currency)
	return option_contracts
