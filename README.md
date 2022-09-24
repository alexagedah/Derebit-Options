# Derebit-Options
Produces plots of the implied volatility surface of crypto options on the Deribit exchange

Underlying
Instances of the Underlying class are used to represent the underlying contract for the options

Option
Instances of the Option class are used to represent the option contract

- First we interact with the Derebit API to get a list of all the option contracts currently trading
- We then use this list of options contract to plot the implied volatlity surface based on the mark price
