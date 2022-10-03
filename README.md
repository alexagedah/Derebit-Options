# Implied Volatility Surface
Most of the trading on cryptocurrencies is done through spot contracts and perpetual futures contracts. Options trading is relatively small however I expect it to grow over the coming years. This gives an opportunity to options traders who can exploit the inefficiencies that might exist in the early stages of crypto options trading. This project involves
1. interacting with the Deribit crypto options and futures derivatives exchange to retrieve the data on the options currently trading
2. calculating the implied volatility of the options useing the bisection method
3. uses polynomial regression to estimate the implied determinsic volatility function (Dumas, Fleming and Whaley 1996)
4. Plots the implied volatility surface

# Results
Initially, the implied volatility of the options was calculated using the Newton-Rahpson method however in some cases this diverged from the value of implied volatility. To avoid this issue, the bisection method was used. The relationship between the implied volatility of an option and its strike K and time to expiry T was assumed to be
IV = a + bK + cK^2 + dT + eT^2 + fKT + error_term. The ordinary least squares method was then used to obtain estimates for the regression coefficients. To asses the quality of fit, the R squared statistic was used. The R squared statistic of the model was 0.2 which is a very poor fit. Possible reasons for a poor fit are
- Cryptocurrencies have far OTM options with very low volume and open interest that are very difficult to trade and have unrealistic implide volatilities. These are also high leverage points therefore have a large effect on the least squares regression line. Come up with a way of filtering out these options that should not be included in the model
- The most important options are the options traded in large volumes (ATM options). Think about weighting the model so it fits these points more closely? Weighted least squares?
- Is this the model we used suitable? Are there other independet variables to include? Try other machine learning methods (KNN) to estimate thee implied deterministic function?

The implied volatility surface for Bitcoin on Tuesday 27th September based on the Dumas, Fleming and Whaley model.
![ImpliedVolatilitySurface](https://user-images.githubusercontent.com/108612856/192565158-d5fe556d-c6ce-4907-a9aa-fb8bee1c624c.png)

The implied volatility surface for Solana on Tuesday 27th September based on the Dumas, Fleming and Whaley model.
![SolImpliedVolatilitySurface](https://user-images.githubusercontent.com/108612856/192576998-e3696f27-0092-4889-91a3-238734f40b5c.png)

The implied volatility of Bitcoin options on the Deribit crypto options and futures exchange on Tuesday 27th September.
![ImpliedVolatility](https://user-images.githubusercontent.com/108612856/192574703-698578d4-8163-4761-b5ba-d8c511c05d41.png)

The implied volatility of Solana options on the Deribit crypto options and futures exchange on Tuesday 27th September.
![SolanaImpliedVolatility](https://user-images.githubusercontent.com/108612856/192577049-fe4f5d41-0e3f-4040-9bf8-22c86f5bcbdf.png)


# Next Steps
1. Change the options change class so it takes an exchange and an instrument as the input in the constructor and then creates the appropriate OptionsChain object. This will help when extending the project to work on multiple exchanges.
2. Calculate the implied volatility bid and ask and be able to plot the bid, ask and mark implied volatility surface.
3. Have columns containing the bid, ask and mark price for the underlying contract. This is necessary for when I start trading since the bid/ask is used to value options depending on if you are taking a long market position or short market position.
4. Binance recently added options. Write a script which can produce a DataFrame containing information on all the options contracts that are currently trading on a certain instrument in the correct format. This can then be passed into the OptionsChain
constructor (the same can be done with any other platform. Maybe interactive brokers next? This would involve generaling this to dividend paying stocks, American options and knowing how to deterime which risk free rate to use)
5. Add a feature where we can specify our positioning in each option. We could then have something like the interface of the volcube simulator where we can view our position and overall exposure.
6. Be able to use a forecast volatility to determine the theoretical value of all the options. We can then compare the theoretical value to the market price and begin options trading!
