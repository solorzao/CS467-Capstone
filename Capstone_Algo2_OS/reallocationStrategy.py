from datetime import datetime,timedelta
import pandas as pd
import numpy as np

class ETFReallocationStrategy(QCAlgorithm):
    
    def Initialize(self):
        self.SetStartDate(2010,2,11)  ## set start date to first date that has available data for current universe
        self.SetEndDate(2020, 11,20)
        # set cash for algo
        self.SetCash(100000)
        # set risk management models
        self.SetRiskManagement(TrailingStopRiskManagementModel(0.15))
        self.SetRiskManagement(MaximumDrawdownPercentPerSecurity(0.70))
        # set leverage
        # self.UniverseSettings.Leverage = 2
        # select equities from 3x leverage ETF universe
        self.first = self.AddEquity("UPRO",Resolution.Daily)
        self.second = self.AddEquity("TQQQ",Resolution.Daily)
        self.third = self.AddEquity("URTY",Resolution.Daily)
        self.fourth = self.AddEquity("UDOW",Resolution.Daily)
        self.weeks = -1
        #weekly scheduled event but rebalancing will run on a monthly basis
        self.Schedule.On(self.DateRules.Every(DayOfWeek.Monday), self.TimeRules.At(6, 30), self.Reallocate)

    def Reallocate(self):
        self.weeks +=1
        if(self.weeks%4==0):
            #retrieves prices from 28 days ago
            history_call = self.History(self.Securities.Keys,timedelta(days=28))
            
            if not history_call.empty:
                # get short term prices
                first_bars = history_call.loc[self.first.Symbol.Value]
                last_p1 = first_bars["close"].iloc[0]
                second_bars = history_call.loc[self.second.Symbol.Value]
                last_p2 = second_bars["close"].iloc[0]
                third_bars = history_call.loc[self.third.Symbol.Value]
                last_p3 = third_bars["close"].iloc[0]
                fourth_bars = history_call.loc[self.fourth.Symbol.Value]
                last_p4 = fourth_bars["close"].iloc[0]
                
                performance_rank = []
                
                # calculates performance of funds over the prior four weeks
                first_performance = (float(self.Securities[self.first.Symbol].Price) / float(last_p1))
                performance_rank.append(first_performance)
                
                second_performance = (float(self.Securities[self.second.Symbol].Price) / float(last_p2))
                performance_rank.append(second_performance)
                
                third_performance = (float(self.Securities[self.third.Symbol].Price) / float(last_p3))
                performance_rank.append(third_performance)
                
                fourth_performance = (float(self.Securities[self.fourth.Symbol].Price) / float(last_p4))
                performance_rank.append(fourth_performance)
                
                performance_rank.sort()
                
                
                if performance_rank[3] < 0.85:
                    if(self.Securities[self.first.Symbol].Invested==True):
                        self.Liquidate(self.first.Symbol)
                    elif(self.Securities[self.second.Symbol].Invested==True):
                        self.Liquidate(self.second.Symbol)
                    elif(self.Securities[self.third.Symbol].Invested==True):
                        self.Liquidate(self.third.Symbol)
                    elif(self.Securities[self.fourth.Symbol].Invested==True):
                        self.Liquidate(self.fourth.Symbol)
                else:
                    #buys the fund that has the highest return during the period
                    if(first_performance > second_performance and first_performance > third_performance and first_performance > fourth_performance):
                        # check if positions are currently held in other equities, liquidate
                        if(self.Securities[self.second.Symbol].Invested==True):
                            self.Liquidate(self.second.Symbol)
                        elif(self.Securities[self.third.Symbol].Invested==True):
                            self.Liquidate(self.third.Symbol)
                        elif(self.Securities[self.fourth.Symbol].Invested==True):
                            self.Liquidate(self.fourth.Symbol)
                        
                        # after liquidating any held positions, buy equity number one
                        if(self.Securities[self.first.Symbol].Invested!=True):
                            quantity = self.CalculateOrderQuantity(self.first.Symbol, 0.99)
                            self.MarketOrder(self.first.Symbol, quantity)
                
                    elif(second_performance > first_performance and second_performance > third_performance and second_performance > fourth_performance):
                        # check if positions are currently held in other equities, liquidate
                        if(self.Securities[self.first.Symbol].Invested==True):
                            self.Liquidate(self.first.Symbol)
                        elif(self.Securities[self.third.Symbol].Invested==True):
                            self.Liquidate(self.third.Symbol)
                        elif(self.Securities[self.fourth.Symbol].Invested==True):
                            self.Liquidate(self.fourth.Symbol)
                    
                        # after liquidating any held positions, buy equity number two
                        if(self.Securities[self.second.Symbol].Invested!=True):
                            quantity = self.CalculateOrderQuantity(self.second.Symbol, 0.99)
                            self.MarketOrder(self.second.Symbol, quantity)
                        
                    elif(third_performance > first_performance and third_performance > second_performance and third_performance > fourth_performance):
                        # check if positions are currently held in other equities, liquidate
                        if(self.Securities[self.first.Symbol].Invested==True):
                            self.Liquidate(self.first.Symbol)
                        elif(self.Securities[self.second.Symbol].Invested==True):
                            self.Liquidate(self.second.Symbol)
                        elif(self.Securities[self.fourth.Symbol].Invested==True):
                            self.Liquidate(self.fourth.Symbol)
    
                        # after liquidating any held positions, buy equity number three
                        if(self.Securities[self.third.Symbol].Invested!=True):
                            quantity = self.CalculateOrderQuantity(self.third.Symbol, 0.99)
                            self.MarketOrder(self.third.Symbol, quantity)
                        
                    elif(fourth_performance > first_performance and fourth_performance > second_performance and fourth_performance > third_performance):
                        # check if positions are currently held in other equities, liquidate
                        if(self.Securities[self.first.Symbol].Invested==True):
                            self.Liquidate(self.first.Symbol)
                        elif(self.Securities[self.second.Symbol].Invested==True):
                            self.Liquidate(self.second.Symbol)
                        elif(self.Securities[self.third.Symbol].Invested==True):
                            self.Liquidate(self.third.Symbol)
    
                        # after liquidating any held positions, buy equity number four
                        if(self.Securities[self.fourth.Symbol].Invested!=True):
                            quantity = self.CalculateOrderQuantity(self.fourth.Symbol, 0.99)
                            self.MarketOrder(self.fourth.Symbol, quantity)



    def OnData(self, data):
        pass
