import numpy as np
import pandas as pd
import scipy.stats as stats
import datetime as dt

import matplotlib as mpl
import matplotlib.pyplot as plt

rel = ["Strike","Type","Mark","Implied Volatility","IV Value"]

def print_full(x):
	pd.set_option('display.max_rows', None)
	pd.set_option('display.max_columns', None)
	# pd.set_option('display.width', 2000)
	pd.set_option('display.float_format', '{:20,.2f}'.format)
	pd.set_option('display.max_colwidth', None)
	print(x)
	pd.reset_option('display.max_rows')
	pd.reset_option('display.max_columns')
	# pd.reset_option('display.width')
	pd.reset_option('display.float_format')
	pd.reset_option('display.max_colwidth')

class OptionsChain():
	"""
	Instances of this class are used to represent the options that are trading on an instrument
		Attributes:
			instrument (string) : The name of the instrument the implied volatility surface
			style (string) : The style of the options
			evaluation (datetime) : The date and time the options chain is being evaluated at
			options_chain_df (DataFrame) : DataFrame containing information about the all options contracts. 
											The index is the expiration date and here are the columns:
											Underlying Name (string)
											Underlying Price (float)
											Strike (float)
											Type (string)
											Bid (float)
											Ask (float)
											Mark (float)
											24H Vol (float)
											Open Interest (float)
											Time to Expiry (float) : The time to expiry in days
											Risk Free Rate (float)
											Forward Price (float)
											Log Simple Moneyness (float) : log(F/K)
											Implied Volatility (float)
											IV Value (float) : The theoretical value of the option assuming the implied volatility is correct
											Implied D1  (float) : The d_1 term in the BSM formula for the value of an option
											Implied D2 (float) : The d_2 term in the BSM formula for the value of an option											
			ivsurface (DataFrame) : DataFrame representing the implied volatility surface
		Methods:
			CalculateTimeToExpiry() : Creates/recalculates the Time to Expiry column
			CalculateRiskFreeRate() : Creates/recalculates the Risk Free Rate column
			CalculateForwardPrice() : Creates/recalculates the Forward Price column
			CalculateLogSimpleMoneyness() : Creates/recalculates the Log Simple Moneyness column
			CalculateImpliedD12() : Creates/recalculates the Implied D1 and Implied D2 columns
			CalculateIVValue() : Creates/recalculates the IV Value column
			CalculateImpliedVolatility() : Creates/recalculates the Implied Volatility column
			PlotImpliedVolatility() : Produces a 3D plot of the implied volatility of the options
	"""
	def __init__(self, options_chain_df):
		"""
		Constructor for the ImpliedVolatilitySurface class
			Parameters:
				options_chain_df (DataFrame) : DataFrame containing information about the all options contracts
				Expiration | Underlying Name | Underlying Price | Strike | Type | Bid | Ask | Mark | 24H Vol | Open Interest |
		"""
		self.style = "European"
		self.options_chain_df = options_chain_df
		self.evaluation = dt.datetime.now()
		self.CalculateTimeToExpiry()
		self.CalculateRiskFreeRate()
		self.CalculateForwardPrice()
		self.CalculateLogSimpleMoneyness()
		self.CalculateImpliedVolatility()
		writer = pd.ExcelWriter("chain.xlsx")
		self.options_chain_df.to_excel(writer,"Sheet 1")
		writer.save()

	def CalculateRiskFreeRate(self):
		"""
		Creates/recalculates the risk free rate column
		"""
		self.options_chain_df.loc[:,"Risk Free Rate"] = 0

	def CalculateTimeToExpiry(self):
		"""
		Creates/recalculates the time to expiry column
		"""
		expiration = self.options_chain_df.index
		days_to_expiry = (expiration - self.evaluation).days
		seconds_to_expiry = (expiration - self.evaluation).seconds
		self.options_chain_df.loc[:,"Time to Expiry"] = days_to_expiry/365.25 + seconds_to_expiry/(60*60*24*365.25)

	def CalculateForwardPrice(self):
		"""
		Creates/recalculates the Forward Price column
		"""
		S_0 = self.options_chain_df.loc[:,"Underlying Price"]
		r = self.options_chain_df.loc[:,"Risk Free Rate"]
		time_to_expiry = self.options_chain_df.loc[:,"Time to Expiry"]
		self.options_chain_df.loc[:,"Forward Price"] = S_0*np.exp(r*time_to_expiry)

	def CalculateLogSimpleMoneyness(self):
		"""
		Creates/recalculates the Log Simple Moneyness column log(Forward Price/Strike)
		"""
		F = self.options_chain_df.loc[:,"Forward Price"]
		K = self.options_chain_df.loc[:,"Strike"]
		self.options_chain_df.loc[:,"Log Simple Moneyness"] = np.log(K/F)

	def CalculateImpliedD12(self):
		"""
		Creates/recalculates the value in the D1 column for all the options
		"""
		S_0 = self.options_chain_df.loc[:,"Underlying Price"]
		K = self.options_chain_df.loc[:,"Strike"]
		r = self.options_chain_df.loc[:,"Risk Free Rate"]
		implied_vol = self.options_chain_df.loc[:,"Implied Volatility"]
		time_to_expiry = self.options_chain_df.loc[:,"Time to Expiry"]
		self.options_chain_df.loc[:,"Implied D1"] = (np.log(S_0/K) + (r + (implied_vol**2)/2)*time_to_expiry)/(implied_vol*np.sqrt(time_to_expiry))
		self.options_chain_df.loc[:,"Implied D2"] = self.options_chain_df.loc[:,"Implied D1"] - implied_vol*np.sqrt(time_to_expiry)

	def CalculateIVValue(self):
		"""
		Creates/recalculates the IV Value column
		"""
		S_0 = self.options_chain_df.loc[:,"Underlying Price"]
		K = self.options_chain_df.loc[:,"Strike"]
		r = self.options_chain_df.loc[:,"Risk Free Rate"]
		implied_vol = self.options_chain_df.loc[:,"Implied Volatility"]
		time_to_expiry = self.options_chain_df.loc[:,"Time to Expiry"]
		d_1 = self.options_chain_df.loc[:,"Implied D1"]
		d_2 = self.options_chain_df.loc[:,"Implied D2"]

		if self.style == "European":
			call_mask = self.options_chain_df.loc[:,"Type"] == "Call"
			self.options_chain_df.loc[:,"IV Value"] = np.where(call_mask, 
				BSMCallValue(S_0, K, r, time_to_expiry, d_1, d_2),
				BSMPutValue(S_0, K, r, time_to_expiry, d_1, d_2))

	def CalculateImpliedVolatility(self, it = 20):
		"""
		Creates/recalculates the Implied Volatility column
			it (int) : The number of iterations
		"""		
		# Create the columns needed to calculate implied volatility via bisection search
		bi_search_iv_columns = ["Max IV","Mid IV","Min IV"]
		starting_ivs = [2,1,0]
		for iv_column, starting_iv in zip(bi_search_iv_columns, starting_ivs):
			self.options_chain_df.loc[:,iv_column] = starting_iv
		bi_search_vals_columns = ["Max val","Mid val","Min val"]
		for val_column in bi_search_vals_columns:
			self.options_chain_df.loc[:,val_column] = None

		mark = self.options_chain_df.loc[:,"Mark"]
		for i in range(it):
			for iv_column, val_column in zip(bi_search_iv_columns, bi_search_vals_columns):
				self.options_chain_df.loc[:,"Implied Volatility"] = self.options_chain_df.loc[:,iv_column]
				self.CalculateImpliedD12()
				self.CalculateIVValue()
				self.options_chain_df.loc[:,val_column] = self.options_chain_df.loc[:,"IV Value"]

			max_iv = self.options_chain_df.loc[:,"Max IV"]
			mid_iv = self.options_chain_df.loc[:,"Mid IV"]
			min_iv = self.options_chain_df.loc[:,"Min IV"]
			max_value = self.options_chain_df.loc[:,"Max val"]
			mid_value = self.options_chain_df.loc[:,"Mid val"]
			min_value = self.options_chain_df.loc[:,"Min val"]
			# If the mark price is above the max price
			# Create a boolean Series that is true where the mark price is above the max value
			mark_above_max_mask = mark > max_value
			# Set the minimum implied volatility to the maximum implied volatility
			self.options_chain_df.loc[mark_above_max_mask,"Min IV"] = self.options_chain_df.loc[mark_above_max_mask,"Max IV"]
			# Double the maximum implied votility
			self.options_chain_df.loc[mark_above_max_mask,"Max IV"] *= 2

			# If the mark price is below the min price (min > mark)
			# Create a boolean Series that is true where the mark price is below the min price
			mark_below_min_mask = mark < min_value
			# Set the maximum implied volatility to the minimum implied volaitlity
			self.options_chain_df.loc[mark_below_min_mask,"Max IV"] = self.options_chain_df.loc[mark_below_min_mask,"Min IV"]
			# Half the minimum implied volatility 
			self.options_chain_df.loc[mark_below_min_mask,"Min val"] /= 2

			# If the mark price is between the maximum price and the mid price (max > mark > mid)
			# Create a boolean Series that is true where the mark price is between the max and mid price
			max_mark_mid_mask = (max_value > mark) & (mark > mid_value)
			# Set the minimum implied volatility to the mid
			self.options_chain_df.loc[max_mark_mid_mask,"Min IV"] = self.options_chain_df.loc[max_mark_mid_mask,"Mid IV"] 

			# If the mark price is between the minimum price and the mid price (mid > mark > min)
			# Create a boolean Series that is true where the mark price is between the mid and min price
			mid_mark_min_mask = (mid_value > mark) & (mark > min_value)
			# Set the maximum implied volatility to the mid 
			self.options_chain_df.loc[mid_mark_min_mask,"Max IV"] = self.options_chain_df.loc[mid_mark_min_mask,"Mid IV"] 

			# If the mark price is equal to the max price
			# Create a boolean Series that is true where the mark price is equal to the max price
			mark_equals_max = mark == max_value
			# Set the minimum implied volatility to the max implied volatility
			self.options_chain_df.loc[mark_equals_max,"Min IV"] = max_iv = self.options_chain_df.loc[mark_equals_max,"Max IV"] 

			# If the mark price is equal to the mid price
			mark_equals_mid = mark == mid_value
			self.options_chain_df.loc[mark_equals_mid,"Max IV"] = self.options_chain_df.loc[mark_equals_mid,"Mid IV"]
			self.options_chain_df.loc[mark_equals_mid,"Min IV"] = self.options_chain_df.loc[mark_equals_mid,"Mid IV"]

			# If the mark price is equal to the min price
			mark_equals_min = mark == min_value
			self.options_chain_df.loc[mark_equals_min,"Max IV"] = self.options_chain_df.loc[mark_equals_min,"Min IV"]

			self.options_chain_df.loc[:,"Mid IV"] = (self.options_chain_df.loc[:,"Max IV"] + self.options_chain_df.loc[:,"Min IV"])/2

		self.options_chain_df.loc[:,"Implied Volatility"] = self.options_chain_df.loc[:,"Mid IV"]

		self.options_chain_df.drop(columns = (bi_search_iv_columns + bi_search_vals_columns), inplace = True)

	def PlotImpliedVolatility(self) : 
		"""
		Produces a 3D plot of the implied volatility of the options
		"""
		x = self.options_chain_df.loc[:,"Log Simple Moneyness"]
		y = self.options_chain_df.loc[:,"Time to Expiry"]
		z = self.options_chain_df.loc[:,"Implied Volatility"]*100
		fig = plt.figure()
		ax1 = fig.add_subplot(1, 1, 1, projection = "3d")
		ax1.set_title("Implied Volatility")
		ax1.set_xlabel("Log Simple Moneyness")
		ax1.set_ylabel("Days to Expiry")
		ax1.set_zlabel("Implied Volatility/%")
		ax1.scatter(x,y,z)
		plt.show()


def BSMCallValue(S_0, K, r, t, d_1, d_2):
	"""
	Returns the theoretical value of a European call option according to the BSM model
		Parameters:
			S_0 (float) : The current price of the underlying
			K (float) : The strike of the option
			r (float) : The risk free interest rate
			t (float) : The time to expiry in dats
			d_1 (float) : The D1 term in the BSM call value formula
			d_2 (float) : The D2 term in the BSM call value formula
		Returns:
			bsm_call_value (float) : The theoretical value of the call option
	"""
	bsm_call_value = S_0*stats.norm.cdf(d_1, 0, 1) - K*np.exp(-r*t)*stats.norm.cdf(d_2, 0, 1)
	return bsm_call_value

def BSMPutValue(S_0, K, r, t, d_1, d_2):
	"""
	Returns the theoretical value of a European put option according to the BSM model
		Parameters:
			S_0 (float) : The current price of the underlying
			K (float) : The strike of the option
			r (float) : The risk free interest rate
			t (float) : The time to expiry in dats
			d_1 (float) : The D1 term in the BSM put value formula
			d_2 (float) : The D2 term in the BSM put value formula
		Returns:
			bsm_put_value (float) : The theoretical value of the put option
	"""
	bsm_put_value = K*np.exp(-r*t)*stats.norm.cdf(-d_2) - S_0*stats.norm.cdf(-d_1)
	return bsm_put_value




