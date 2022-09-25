# Derebit-Options
Produces plots of the implied volatility surface of crypto options on the Deribit exchange


Instances of this class are used to represent the options that are trading on an instrument.
Originally I approaches this by having an option class and creating objects to represent each option but I think it makes
more sense to have an object which represents the whole options chain. The main attribute of the OptionsChain object is the
DataFrame containing all the information about the options.

- First interact with the Derebit API to get a DataFrame containing information on all the options contracts that are currently trading. Get this DataFrame into the correct format so it can be passed into the OptionsChain constructor
represented by Option objects.
- We then use the OptionsChain class to calculate the implied volatility of the options using the bisection method and then
plot the implied volatility surface


# TODO/Improvements
- Binance recently added optionss. Write a script which can produce a DataFrame containing information on all the options contracts that are currently trading on a certain instrument in the correct format. This can then be passed into the OptionsChain
constructor
- Calculate the risk free rate on options properly. Derebit is easy since they all have a risk free rate of 0.
- Calculate the implied volatility bid and ask and be able to plot the bid, ask and mark implied volatility surface
- Have columns containing the bid, ask and mark price for the underlying contract. This is necessary for when I start trading
since the bid/ask is used to value options depending on if you are taking a long market position or short market position
