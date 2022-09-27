import derebit
import optionschain

import pprint
import datetime as dt

import pandas as pd
import numpy as np

def CreateImpliedVolSurface(implied_vol_surface_df):
	"""
	Creates the implied volatility surface using interpolation
		Parameters:
			implied_vol_surface_df (DataFrame) : DataFrame representing implied volatility surface
		Returns:
			delta (ndarray) : A 2D array of the deltas we plot for
			time_to_expiry (ndarray) : A 2D array of the time to expries we plot for
			interpolated_iv_surface (ndarray) : The interpolated implied volatility surface 
	"""
	delta1 = np.linspace(0,1,21)
	time_to_expiry1 = np.linspace(implied_vol_surface_df["Time to Expiry"].min(), implied_vol_surface_df["Time to Expiry"].max(), 21)

	delta, time_to_expiry = np.meshgrid(delta1, time_to_expiry1)

	print(delta)
	print(time_to_expiry)
	interpolated_iv_surface = scipy.interpolate.griddata( (implied_vol_surface_df["Absolute Delta"], implied_vol_surface_df["Time to Expiry"]),
		implied_vol_surface_df["Implied Volatility/%"],
		(delta, time_to_expiry),
		method = "linear"
		)
	return delta, time_to_expiry, interpolated_iv_surface


btc_option_contracts = derebit.GetOptions("BTC")

btc_options_chain = optionschain.OptionsChain(btc_option_contracts)
btc_options_chain.PlotImpliedVolatility()
# print_full(btc_options_chain.options_chain_df)


