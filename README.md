# Implied Volatility Surface

![ImpliedVolatilitySurface](https://user-images.githubusercontent.com/108612856/192565158-d5fe556d-c6ce-4907-a9aa-fb8bee1c624c.png)

- Uses the Deribit API to obtain data on all the options currently trading on the exchange
- Uses the bisection method to calculate the implied volatility of Bitcoin, Ethereum and Solana options on the Deribit crypto options and futures derivatives exchange. 
- Uses polynomial regression to estimate the implied determinsic volatility function (Dumas, Fleming and Whaley 1996)
- Plots the implied volatility surface

# TODO/Improvements
1. On the day of initial testing, model ended up fitting the implied volatility data poorly with an R squared statistic of 0.2! Possible ways to improve the fit are
- Come up with a way of filtering out options that should not be included in the model (low volume, low open interest, wide spreads etc...)
- The most important options are the options traded in large volumes (ATM options). Think about weighting the model so it fits these points more closely? 
- Is this the model we used suitable? Try other machine learning methods to estimate thee implied deterministic function and try different features
2. Calculate the implied volatility bid and ask and be able to plot the bid, ask and mark implied volatility surface.
3. Have columns containing the bid, ask and mark price for the underlying contract. This is necessary for when I start trading since the bid/ask is used to value options depending on if you are taking a long market position or short market position.
4. Binance recently added options. Write a script which can produce a DataFrame containing information on all the options contracts that are currently trading on a certain instrument in the correct format. This can then be passed into the OptionsChain
constructor (the same can be done with any other platform. Maybe interactive brokers next? This would involve generaling this to dividend paying stocks, American options and knowing how to deterime which risk free rate to use)
5. Add a feature where we can specify our positioning in each option. We could then have something like the interface of the volcube simulator where we can view our position and overall exposure.
6. Be able to use a forecast volatility to determine the theoretical value of all the options. We can then compare the theoretical value to the market price and begin options trading!
