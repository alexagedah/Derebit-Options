# Derebit-Options
Produces plots of the implied volatility surface of crypto options on the Deribit exchange

Underlying
Instances of the Underlying class are used to represent the underlying contract for the options

Option
Instances of the Option class are used to represent the option contract

- First interact with the Derebit API to get a DataFrame containing information on all the options contracts that are currently trading
- Convert this DataFrame into a dictionry which has the expirations as keys and lists of all the options contracts as values. The options contracts are
represented by Option objects.
- We then use this list of options contract to plot the implied volatlity surface based on the mark price


Underlying Class Improvements
- The underlying class can be extended to have attributes such as the bid, ask, mark and mid price. This would be needed for practical trading since 
when we take long market positions, we value options using the bid and when we take short market positions we value options using the offer.

Options Class Improvements
- The Option class can be extended so that it can interact with a forecast volatility surface. We can then use this to calculate the theoretical value
of options and then be able to trade the options
- The risk-free rate input of the option is current 0 by default which is fine for Deribit. For other options contracts, we would need to be able to
get the correct risk-free rate to use.
- Currently the implied volatility is calculated using the bisection method. If this program was scaled up to deal with options on a vareity of instruments
and on many exchanges, it may be necessary to use a faster converging numerical method. Note that the Newton Rahpson method was originally used however
this did not converge in all cases
