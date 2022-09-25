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

def PlotImpVolSurface(options):
	"""
	Plots the implied volatility surface for the options
		Parameters:
			options (list) : A list containing all the options objects
		Returns:

	"""

	vol_surface_df = GetVolSurfaceDF(options)
	print(vol_surface_df)
	x, y, z = CreateImpliedVolSurface(vol_surface_df)
	fig = plt.figure()
	ax1 = fig.add_subplot(1, 1, 1, projection = "3d")
	ax1.set_xlabel("Absolute Delta")
	ax1.set_ylabel("Days to Expiry")
	ax1.set_zlabel("Implied Volatility/%")
	ax1.plot_surface(x,y,z)
	plt.show()

def print_full(x):
    # pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    # pd.set_option('display.width', 2000)
    pd.set_option('display.float_format', '{:20,.2f}'.format)
    pd.set_option('display.max_colwidth', None)
    print(x)
    # pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')
    # pd.reset_option('display.width')
    pd.reset_option('display.float_format')
    pd.reset_option('display.max_colwidth')


option_contracts = derebit.GetOptions()

options_chain = optionschain.OptionsChain(option_contracts)
print_full(options_chain.options_chain_df)