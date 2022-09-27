# Implied Volatility Surface
- Uses the Deribit API to obtain data on all the options currently trading on the exchange
- Uses the bisection method to calculate the implied volatility of Bitcoin, Ethereum and Solana options on the Deribit crypto options and futures derivatives exchange. 
- Uses polynomial regression to estimate the implied determinsic volatility function (Dumas, Fleming and Whaley 1996)
- Plots the implied volatility surface

The implied volatility surface for Bitcoin on Tuesday 27th September based on the Dumas, Fleming and Whaley model.
![ImpliedVolatilitySurface](https://user-images.githubusercontent.com/108612856/192565158-d5fe556d-c6ce-4907-a9aa-fb8bee1c624c.png)

The implied volatility surface for Solana on Tuesday 27th September based on the Dumas, Fleming and Whaley model.
![SolImpliedVolatilitySurface](https://user-images.githubusercontent.com/108612856/192576998-e3696f27-0092-4889-91a3-238734f40b5c.png)


The implied volatility of Bitcoin options on the Deribit crypto options and futures exchange on Tuesday 27th September.
![ImpliedVolatility](https://user-images.githubusercontent.com/108612856/192574703-698578d4-8163-4761-b5ba-d8c511c05d41.png)

The implied volatility of Solana options on the Deribit crypto options and futures exchange on Tuesday 27th September.
![SolanaImpliedVolatility](https://user-images.githubusercontent.com/108612856/192577049-fe4f5d41-0e3f-4040-9bf8-22c86f5bcbdf.png)
- The volatility smile can be observed across options
- There are far OTM options which have very low open interest and very low volume. These have mark prices of 0 therefore their implied volatilities are 0


# TODO/Improvements
1. Change the options change class so it takes an exchange and an instrument as the input in the constructor and then creates the appropriate OptionsChain object.
2. On the day of initial testing, model ended up fitting the implied volatility data poorly with an R squared statistic of ~ 0.2! Possible ways to improve the fit are
- Come up with a way of filtering out options that should not be included in the model (low volume, low open interest, wide spreads etc...)
- The most important options are the options traded in large volumes (ATM options). Think about weighting the model so it fits these points more closely? 
- Is this the model we used suitable? Try other machine learning methods (KNN) to estimate thee implied deterministic function and try different features. 
3. Calculate the implied volatility bid and ask and be able to plot the bid, ask and mark implied volatility surface.
4. Have columns containing the bid, ask and mark price for the underlying contract. This is necessary for when I start trading since the bid/ask is used to value options depending on if you are taking a long market position or short market position.
5. Binance recently added options. Write a script which can produce a DataFrame containing information on all the options contracts that are currently trading on a certain instrument in the correct format. This can then be passed into the OptionsChain
constructor (the same can be done with any other platform. Maybe interactive brokers next? This would involve generaling this to dividend paying stocks, American options and knowing how to deterime which risk free rate to use)
6. Add a feature where we can specify our positioning in each option. We could then have something like the interface of the volcube simulator where we can view our position and overall exposure.
7. Be able to use a forecast volatility to determine the theoretical value of all the options. We can then compare the theoretical value to the market price and begin options trading!
