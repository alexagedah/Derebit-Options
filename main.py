import derebit
import optionschain

import pprint
import datetime as dt

import pandas as pd
import numpy as np

btc_option_contracts = derebit.GetOptions("BTC")
btc_options_chain = optionschain.OptionsChain(btc_option_contracts)
btc_options_chain.PlotImpliedVolatilitySurface()
btc_options_chain.PlotImpliedVolatility()