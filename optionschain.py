"""
TODO:
- Calculate the risk free rate on options properly. Derebit is easy since they all have a risk free rate of 0
- Add a forward price column
- Calculate the implied volatility bid and ask and be able to plot the bid, ask and mark implied
volatility surface
- Repeat with binance options
"""
import numpy as np
import pandas as pd
import scipy.stats as stats
import datetime as dt

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
			CreateIVSurface() : Creates the implied volatility surface from the options chain DataFrame
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
		self.options_chain_df.loc[:,"Time to Expiry"] = time_to_expiry = days_to_expiry/365.25 + seconds_to_expiry/(60*60*24*365.25)

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
		Creates/recalculates the Log Simple Moneyness column
		"""
		F = self.options_chain_df.loc[:,"Forward Price"]
		K = self.options_chain_df.loc[:,"Strike"]
		self.options_chain_df.loc[:,"Log Simple Moneyness"] = np.log(F/K)

	def CalculateImpliedD12(self):
		"""
		Creates/recalculates the values in the D1 column for all the options
		"""
		S_0 = self.options_chain_df.loc[:,"Underlying Price"]
		K = self.options_chain_df.loc[:,"Strike"]
		r = self.options_chain_df.loc[:,"Risk Free Rate"]
		implied_vol = self.options_chain_df.loc[:,"Implied Volatility"]
		time_to_expiry = self.options_chain_df.loc[:,"Time to Expiry"]
		self.options_chain_df.loc[:,"Implied D1"] = (np.log(S_0/K) + (r + (implied_vol**2)/2)*time_to_expiry)/(implied_vol*np.sqrt(time_to_expiry))
		self.options_chain_df.loc[:,"Implied D2"] = (np.log(S_0/K) + (r - (implied_vol**2)/2)*time_to_expiry)/(implied_vol*np.sqrt(time_to_expiry))

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

	def CalculateImpliedVolatility(self, it = 10):
		"""
		Creates/recalculates the Implied Volatility column
			it (int) : The number of iterations
		"""
		max_implied_vol = pd.Series(1, index = self.options_chain_df.index)
		min_implied_vol =pd.Series(0.05, index = self.options_chain_df.index)

		for i in range(it):
			# Calculate the maximum price of the option
			self.options_chain_df.loc[:,"Implied Volatility"] = max_implied_vol
			self.CalculateImpliedD12()
			self.CalculateIVValue()
			max_price = self.options_chain_df.loc[:,"IV Value"]

			# Calculate the minimum price of the option
			self.options_chain_df.loc[:,"Implied Volatility"] = min_implied_vol
			self.CalculateImpliedD12()
			self.CalculateIVValue()
			min_price = self.options_chain_df.loc[:,"IV Value"]

			# Calculate the mid price of the option
			mid_implied_vol = (max_implied_vol + min_implied_vol)/2
			self.options_chain_df.loc[:,"Implied Volatility"] = mid_implied_vol
			self.CalculateImpliedD12()
			self.CalculateIVValue()
			mid_price = self.options_chain_df.loc[:,"IV Value"]

			# Create a boolean Series that is true where the mark price is above the max price
			mark_above_max_mask = self.options_chain_df.loc[:,"Mark"] > max_price
			# Double the maximum implied votility if the mark price was above the max price
			min_implied_vol[mark_above_max_mask] = max_implied_vol[mark_above_max_mask]
			max_implied_vol[mark_above_max_mask] *= 2

			# Create a boolean Series that is true where the mark price is below the min price
			mark_below_min_mask = self.options_chain_df.loc[:,"Mark"] < min_price
			# Half the minimum implied volatility if the mark price was below the min price
			max_implied_vol[mark_below_min_mask] = min_implied_vol[mark_below_min_mask]
			min_implied_vol[mark_below_min_mask] /= 2

			# Create a boolean Series that is true where the mark price is between the max and mid price
			max_mark_mid_mask = (max_price > self.options_chain_df.loc[:,"Mark"]) & (self.options_chain_df.loc[:,"Mark"] > mid_price)
			# Set the minimum implied volatility to the mid if the mark price was between the max and mid
			min_implied_vol[max_mark_mid_mask] = mid_implied_vol[max_mark_mid_mask]

			# Create a boolean Series that is true where the mark price is between the mid and min price
			mid_mark_min_mask = (mid_price > self.options_chain_df.loc[:,"Mark"]) & (self.options_chain_df.loc[:,"Mark"] > min_price)
			# Set the maximum implied volatility to the mid if the mark price was between the mid and min
			max_implied_vol[mid_mark_min_mask] = mid_implied_vol[mid_mark_min_mask]

	def CreateIVSurface(self):
		"""
		Creates the implied volatility surface
			TODO: Log moneyness on columns and maturity on rows
		"""
		pass

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




