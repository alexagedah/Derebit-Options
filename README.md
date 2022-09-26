# Implied Volatility Surface
Plotting the implied volatility surface of options on the Deribit cryptocurrency derivatives exchange using machine learning techniques.


# Steps
- First interact with the Derebit API to get a DataFrame containing information on all the options contracts that are currently trading. Get this DataFrame into the correct format so it can be passed into the OptionsChain constructor
represented by Option objects.
- Use the OptionsChain class to calculate the implied volatility of the options using the bisection method
- Assume implied volatility is a function of the overall level of implied volatility, the strike of the option and the time to expiry. Machine learning techniques can then be used to relationship between implied volatility and these features. The implied volatility surface can then be plotted.

# OptionChain
Instances of this class are used to represent the options that are trading on an instrument.
Originally I approaches this by having an option class and creating objects to represent each option but I think it makes
more sense to have an object which represents the whole options chain. The main attribute of the OptionsChain object is the
DataFrame containing all the information about the options.

# TODO/Improvements
1. Calculate the implied volatility bid and ask and be able to plot the bid, ask and mark implied volatility surface.
2. Have columns containing the bid, ask and mark price for the underlying contract. This is necessary for when I start trading since the bid/ask is used to value options depending on if you are taking a long market position or short market position
3. Add a feature where we can specify our positioning in each option. We could then have something like the interface of the volcube simulator where we can view our position and overall exposure. W
4. Be able to use a forecast volatility to determine the theoretical value of all the options. We can then compare the theoretical value to the market price and begin options trading!
5. Binance recently added options. Write a script which can produce a DataFrame containing information on all the options contracts that are currently trading on a certain instrument in the correct format. This can then be passed into the OptionsChain
constructor (the same can be done with any other platform. Maybe interactive brokers next? This would involve generaling this to dividend paying stocks, American options and knowing how to deterime which risk free rate to use)
