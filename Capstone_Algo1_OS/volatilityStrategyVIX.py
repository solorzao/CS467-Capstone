# QUANTCONNECT.COM - Democratizing Finance, Empowering Individuals.
# Lean Algorithmic Trading Engine v2.0. Copyright 2014 QuantConnect Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from clr import AddReference
AddReference("System")
AddReference("QuantConnect.Algorithm")
AddReference("QuantConnect.Algorithm.Framework")
AddReference("QuantConnect.Common")

from System import *
from QuantConnect import *
from QuantConnect.Orders import *
from QuantConnect.Algorithm import *
from QuantConnect.Algorithm.Framework import *
from QuantConnect.Algorithm.Framework.Alphas import *
from QuantConnect.Algorithm.Framework.Execution import *
from QuantConnect.Algorithm.Framework.Portfolio import *
from QuantConnect.Algorithm.Framework.Risk import *
from QuantConnect.Algorithm.Framework.Selection import *
from QuantConnect.Python import PythonQuandl
from datetime import timedelta
import numpy as np

### <summary>
### Basic template framework algorithm uses framework components to define the algorithm.
### </summary>
### <meta name="tag" content="using data" />
### <meta name="tag" content="using quantconnect" />
### <meta name="tag" content="trading and orders" />

class CapstoneAlgorithm1b(QCAlgorithm):
    '''Basic template framework algorithm uses framework components to define the algorithm.'''

    def Initialize(self):
        ''' Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized.''' 
        # Set requested data resolution
        self.UniverseSettings.Resolution = Resolution.Daily

        self.SetStartDate(2010,1,1)   #Set Start Date
        self.SetEndDate(2020,10,26)    #Set End Date
        self.SetCash(100000)           #Set Strategy Cash
        
        # set manual universe to trade only proshares for S&P 500, short and long
        symbols = [Symbol.Create("SPXU", SecurityType.Equity, Market.USA), Symbol.Create("UPRO", SecurityType.Equity, Market.USA)]

        # set algorithm framework models
        self.SetUniverseSelection(ManualUniverseSelectionModel(symbols))
        # execute trades based on VWAP
        self.SetExecution(VolumeWeightedAveragePriceExecutionModel())
        # execute equal weighting portfolio
        self.SetPortfolioConstruction(EqualWeightingPortfolioConstructionModel())
        # set trailing stop loss at 20%
        self.SetRiskManagement(TrailingStopRiskManagementModel(0.20))
        # set max drawdown
        # self.SetRiskManagement(MaximumDrawdownPercentPerSecurity(0.70))
        
        # Find more symbols here: http://quantconnect.com/data
        # Forex, CFD, Equities Resolutions: Tick, Second, Minute, Hour, Daily.
        # Futures Resolution: Tick, Second, Minute
        # Options Resolution: Minute Only.
        # build rolling window of VIX historical data, 1 year (52 weeks), consolidate daily data into weekly bars
        self.vix = 'CBOE/VIX'
        self.AddData(QuandlVix, self.vix, Resolution.Daily)
        self.window = RollingWindow[float](52)
        hist = self.History([self.vix], timedelta(7), Resolution.Daily)
        for close in hist.loc[self.vix]['vix close']:
            self.window.Add(close)



    def OnData(self, data):
        # OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        if not data.ContainsKey(self.vix): return
        self.window.Add(self.Securities[self.vix].Price)
        if not self.window.IsReady: return 
        history_close = [i for i in self.window]

        # if closing price is above 90th percentile, go short, buy SPXU
        if self.Securities[self.vix].Price >= np.percentile(history_close, 90):
            self.SetHoldings("SPXU", 1, True)
        # if closing price falls below 80th percentile, close short position (sell SPXU), go long (buy UPRO)
        elif self.Securities[self.vix].Price < np.percentile(history_close, 80):
            self.SetHoldings("SPXU", -1)
            self.SetHoldings("UPRO", 1, True)
        # if closing price falls below 10th percentile, close long position (sell UPRO)
        elif self.Securities[self.vix].Price < np.percentile(history_close, 10):
            self.SetHoldings("UPRO", -1)


class QuandlVix(PythonQuandl):
    
    def __init__(self):
        self.ValueColumnName = "VIX Close"
