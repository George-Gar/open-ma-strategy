import MetaTrader5 as mt5 
import pandas as pd
import ta
import datetime
import pytz
import numpy as np
from config import *


class futures_methods:
    def __init__(self, symbol):
        
        #mt5 initialize
        self.ini = mt5.initialize(login=account, password=password)
        self.login = mt5.login(account)
        #assign variable to args & make variable for current price & list for order id's
        #position variable must come after symbol since its used in positions function
        self.symbol = symbol
        self.total_positions = 0 #all open positions in account
        self.open_positions = 0 #open positions specific to the symbol
        self.market = float(mt5.SYMBOL_TRADE_EXECUTION_MARKET)
        self.current_price = 0.0
        self.bid = 0.0
        self.ask = 0.0
        self.time = 0.0
        self.order_id = []
        #previous candles & trend
        self.bars_frame = {} #data frame of all bars
        self.current_candle = 0.0
        self.current_copy = pd.DataFrame() #don't make this == to first candle on init
        self.first_candle = 0.0
        self.second_candle = 0.0
        self.third_candle = 0.0
        self.fourth_candle = 0.0
        self.fifth_candle = 0.0
        self.ghost_candle = {}
        self.swap_candle = {} #fixed candle for swapping
        self.open_ema = 0.0
        self.trend = ''
        #booleans
        self.in_trade = False
        self.is_long = False
        self.in_swap = False
        self.half_sold = False
        self.fixed = False
        self.bullish = False
        self.swap_candle_bullish = False #checks if swap candle is bearish or bullish
        self.profit_seen = False  
        self.swap_trail_trigger_seen = False  #boolean for determining when to call trailing swap function   
        self.trailing = False   
        self.open_inside = False # used to check if current open is inside or outside previous candle body
        self.price_inside = False #used to check if current open is inside or outside previous candle body
        self.crossed = False #used to see if current price crosses previous candle open or close if current candle opens outside of previous candle
        self.midpoint_crossed = False #used to see if midpoint on ghost candle gets crossed in current open is above or below it
        self.above_midpoint = False #used to see if current open is above midpoint but still inside candle
        self.below_midpoint = False #used to see if current open is below midpoint but still inside candle
        self.traded_mid = False #checks to see if we traded at the midpoint
        self.price_below_mid = False
        self.price_above_mid = False
        self.doji = False #checks to see if the body of the candle is a doji
        self.new_open = False #detects when a new candle has opened
        self.opened_above_ema = False # a boolean to check where the current candle opened
        self.opened_below_ema = False # a boolean to check where the current candle opened
        #swap point & entry point & profit
        self.support = 0.0
        self.resistance = 0.0
        self.entry_point = 0.0
        self.profit = 0.0
        self.loss = 0.0
        #accumulate losses and create a breakeven point
        self.losses = 0.0
        self.break_even = 0.0
        #share amount & current shares for p/l. current shares keeps track of how many shares we have along the way.
        self.shares = 1.0
        self.current_shares = 0.0
        #initiate take profit, trail price, and ceiling
        self.tp = 4.00
        self.trail_price = 0.0
        self.ceiling = 0.0
        self.swap_trail_ceiling = 0.0 #ceiling for trailing swap
        self.swap_trail_trigger = 2.00 
        #create median for swap_trailing_stop
        self.median = 0.0
        #increment variables 
        self.swap_count = 0
    

    def flush_variables(self):
        """ This function resets all of our variables/parameters"""
       
        self.in_trade = False
        self.is_long = False
        self.in_swap = False
        self.swap_point = 0.0
        self.entry_point = 0.0
        self.profit = 0.0
        self.loss = 0.0
        self.ceiling = 0.0
        self.median = 0.0 
        self.shares = 1.0
        self.tp = 4.00
        self.swap_trailing_point = 2
        self.break_even = 0.0
        self.losses = 0.0
        self.half_sold = False
        self.fixed = False
        self.bullish = False
        self.profit_seen = False
        self.open_inside = False
        self.price_inside = False
        self.crossed = False
        self.midpoint_crossed = False
        self.above_midpoint = False
        self.below_midpoint = False
        self.price_below_mid = False
        self.price_above_mid = False
        self.traded_mid = False
        self.swap_candle = {}
        self.doji = False
        self.swap_count = 0
        self.trailing = False
        self.swap_trail_trigger_seen = False
        self.swap_trailing_point = 2.00
        self.swap_trail_ceiling = 0.0
        self.swap_trail_trigger = 2.00 
        self.current_copy = pd.DataFrame()
        self.new_open = False
        self.opened_above_ema = False
        self.opened_below_ema = False
        

    def delta(self, day):
        """This is a function we use to calculate future, current, or previous days"""
        
        dt_utcnow = datetime.datetime.now(tz=pytz.UTC)
        dt_est = dt_utcnow.astimezone(pytz.timezone('US/Eastern'))
        #get today's date
        if day == 'td':
            return dt_est
        #get yesterday's date
        elif day == 'yd':
            tdelta = datetime.timedelta(days=1)
            yday = dt_est - tdelta
            return yday


    def market_hours(self, dt):
        """This function specifies market hours so we know when it opens/closes"""
        
        #create datetime objects
        dt_utcnow = datetime.datetime.now(tz=pytz.UTC)
        dt_est = dt_utcnow.astimezone(pytz.timezone('US/Eastern'))
        day = dt_est.weekday()
        time = dt_est.time()
        open = datetime.time(9,30,0,0)
        close = datetime.time(15,45,0,0)

        #filter between day or time using the arguments
        if dt == 'day':
            return day
        elif dt == 'time':
            return time
        elif dt == 'open':
            return open
        elif dt == 'close':
            return close
        elif dt == 'today':
            return dt_est.date()


    def get_ticks(self):
        """This function gets every tick including price, bid, ask, etc."""

        ticks = mt5.copy_ticks_range(self.symbol, self.delta('yd'), self.delta('td'), mt5.COPY_TICKS_ALL)
        # create DataFrame out of the obtained data
        ticks_frame = pd.DataFrame(ticks)
        # convert time in seconds into the datetime format
        ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s')

        #assign bid, ask, and price
        self.bid = ticks_frame.iloc[-1]['bid']
        self.ask = ticks_frame.iloc[-1]['ask']
        self.current_price = ticks_frame.iloc[-1]['last']
        self.time = ticks_frame.iloc[-1]['time']
        #print(f'BID: {self.bid} ASK: {self.ask} PRICE: {self.current_price}\n')
        return ticks_frame.iloc[-1]
    

    def get_bars(self, timeframe):
        """This function gets the bar data based on selected timeframe"""

        if timeframe == 'min':
            bars = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M1, 0, 1440)
            # create DataFrame out of the obtained data
            bars_frame = pd.DataFrame(bars)
            # convert time in seconds into the datetime format
            bars_frame['time'] = pd.to_datetime(bars_frame['time'], unit='s')

            #add body column to bars_frame
            bars_frame['body'] = bars_frame['high'] - bars_frame['low']
            #assign df to a variable --> highest number is the most current index in this df
            self.bars_frame = bars_frame

            #calculate 2 day open moving average
            open_ema = ta.trend.EMAIndicator(self.bars_frame['open'], 2).ema_indicator()
            self.open_ema = open_ema
            
            #assign candles of data frame
            self.current_candle = bars_frame.iloc[3]
            self.first_candle = bars_frame.iloc[2]
            self.second_candle = bars_frame.iloc[1]
            self.third_candle = bars_frame.iloc[0]

            #check if a new candle has opened
            if not self.current_copy.empty:
                if self.first_candle['high'] == self.current_copy['high'] and self.first_candle['low'] == self.current_copy['low']:
                    self.new_open = True

            return open_ema

        
    def s_r(self):
        """This function creates a self adjusting support/resistance channel"""
        
        #find swapping point after each trade is taken and move it with each new candle
        if self.in_trade and not self.fixed and not self.trailing:
            lows = []
            highs = []
            lows.extend((float(self.first_candle['low']), float(self.second_candle['low']), float(self.third_candle['low'])))
            highs.extend((float(self.first_candle['high']), float(self.second_candle['high']), float(self.third_candle['high'])))
            self.support = round(min(lows), 2)
            self.resistance = round(max(highs), 2)
            lows = []
            highs = []
        
        #stop moving the swap point when half sold and in trailing stop so we don't swap in profit
        elif self.in_trade and self.trailing:
            self.fixed = True
            self.support = self.support
            self.resistance = self.resistance
        
        #create a fixed channel by setting a fixed swapping point + resistance/support
        if self.in_trade and self.is_long and self.current_price < self.first_candle['low']:
            self.fixed = True
            self.resistance = self.resistance
            self.support = self.support
        
        elif self.in_trade and not self.is_long and self.current_price > self.first_candle['high']:
            self.fixed = True
            self.resistance = self.resistance
            self.support = self.support
        
        #move swapping point point if in swap &  once the price exceeds the resistance in a long position
        if self.is_long and self.current_price > self.resistance and self.in_swap:
            self.fixed = False
        
        #move swapping point if in swap & once the price exceeds the drops below the support in a short position
        elif not self.is_long and self.current_price < self.support and self.in_swap:
            self.fixed = False
        
        
        #create the swapping candle for the first two swaps
        self.swap_candle = self.first_candle
        
        print(f'\nSUPPORT: {self.support} - RESISTANCE: {self.resistance}')


    def bearish_bullish(self):
        """This function checks if the previous candle is bearish or bullish"""
        
        #check for bullish/bearish previous candle
        if self.first_candle['close'] > self.first_candle['open']:
            self.bullish = True
        elif self.first_candle['close'] < self.first_candle['open']:
            self.bullish = False
        
        #check if candle opened above or below ema open 2
        if self.current_candle['open'] > self.open_ema.iloc[-1]:
            self.opened_above_ema = True
            self.opened_below_ema = False
        elif self.current_candle['open'] < self.open_ema.iloc[-1]:
            self.opened_below_ema = True
            self.opened_above_ema = False
        else:
            self.opened_above_ema = False
            self.opened_below_ema = False
        
        #check if previous candle is a doji
        self.Doji()
        #create the ghost candle
        self.Ghost_Candle()


    def Doji(self):
        
        if self.first_candle['body'] in np.arange(0, 3.0, 0.01):
            self.doji = True
        else:
            self.doji = False
        return self.doji


    def Ghost_Candle(self):
        #calculate the total length of the candle from high to low
        total_length = self.first_candle['high'] - self.first_candle['low']
        #calculate half of total_length
        half = total_length / 2
        #calculate 90% of the candle and 10% of the candle
        ninety_percent = total_length * 0.9
        ten_percent = total_length * 0.1
        #create open, close
        if self.bullish:
            open = self.first_candle['high'] - ninety_percent
            close = self.first_candle['high'] - ten_percent
        elif not self.bullish:
            open = round(self.first_candle['high'] - ten_percent, 2) 
            close = round(self.first_candle['high'] - ninety_percent, 2)
        #create highs, lows, and midpoint
        midpoint = round(self.first_candle['high'] - half, 2)
        high = round(self.first_candle['high'], 2)
        low = round(self.first_candle['low'], 2)

        #add values to ghost candle dictionary
        self.ghost_candle = {
            'open' : open,
            'close': close,
            'midpoint': midpoint,
            'high': high,
            'low': low
        }
        return


    def Trend(self):
        """This function detects the current trend"""

        if self.first_candle['low'] > self.second_candle['low'] > self.third_candle['low']:
            self.trend = 'up'
        elif self.first_candle['high'] < self.second_candle['high'] < self.third_candle['high']:
            self.trend = 'down'
        else:
            self.trend = 'sideways'
        return f'{self.trend} trend'
    

    def In_and_Out(self):
        if not self.in_trade and not self.open_positions:
            
            if self.bullish:
                #parameters for current candle being outside previous candle
                if self.current_candle['open'] > self.ghost_candle['close']:
                    self.open_inside = False                         
                elif self.current_candle['open'] < self.ghost_candle['open']:
                    self.open_inside = False
                
                #parameters for current candle being inside previous candle
                elif self.current_candle['open'] <= self.ghost_candle['close'] and self.current_candle['open'] >= self.ghost_candle['open']:
                    self.open_inside = True
                    self.crossed = False
                    #check if the current price goes inside or is inside previous candle body
                    if self.current_price <= self.ghost_candle['close'] and self.current_price >= self.ghost_candle['open']:
                        self.price_inside = True
                   
                    #check if current open is above or below ghost candle midpoint
                    if self.current_candle['open'] > self.ghost_candle['midpoint']:
                        self.above_midpoint = True
                        self.below_midpoint = False
                        #check if current price is below ghost candle midpoint
                        if self.current_price < self.ghost_candle['midpoint'] and self.current_price >= self.ghost_candle['open']:
                            self.price_below_mid = True
                        elif self.current_price > self.ghost_candle['midpoint'] and self.current_price <= self.ghost_candle['close']:
                            self.price_above_mid = True   
                    if self.current_candle['open'] < self.ghost_candle['midpoint']:
                        self.below_midpoint = True
                        self.above_midpoint = False
                        #check if current price is above ghost candle midpoint
                        if self.current_price > self.ghost_candle['midpoint'] and self.current_price <= self.ghost_candle['close']:
                            self.price_above_mid = True
                        elif self.current_price < self.ghost_candle['midpoint'] and self.current_price >= self.ghost_candle['open']:
                            self.price_below_mid = True    
                    

                
                #check to see if current price crossed if current candle formed outside
                if not self.open_inside:
                    #open below
                    if self.current_candle['open'] < self.ghost_candle['open'] and self.current_price > self.ghost_candle['open']:
                        self.crossed = True
                    #open above
                    elif self.current_candle['open'] > self.ghost_candle['close'] and self.current_price < self.ghost_candle['close']:
                        self.crossed = True
                #check to see if current price crossed midpoint if current candle formed above/below midpoint
                if self.above_midpoint and self.current_price < self.ghost_candle['midpoint'] or self.below_midpoint and self.current_price > self.ghost_candle['midpoint']:
                    self.midpoint_crossed = True

            
            
            
            elif not self.bullish:
                
                #parameters for current candle being outside previous candle
                if self.current_candle['open'] > self.ghost_candle['open']:
                    self.open_inside = False     
                elif self.current_candle['open'] < self.ghost_candle['close']:
                    self.open_inside = False
                
                #parameters for current candle being inside previous candle
                elif self.current_candle['open'] >= self.ghost_candle['close'] and self.current_candle['open'] <= self.ghost_candle['open']:
                    self.open_inside = True
                    self.crossed = False
                    #check if the current price goes inside or is inside previous candle body
                    if self.current_price >= self.ghost_candle['close'] and self.current_price <= self.ghost_candle['open']:
                        self.price_inside = True
                    
                    #check if current open is above or below ghost candle midpoint
                    if self.current_candle['open'] > self.ghost_candle['midpoint']:
                        self.above_midpoint = True
                        self.below_midpoint = False
                        #check if current price is below ghost candle midpoint
                        if self.current_price < self.ghost_candle['midpoint'] and self.current_price >= self.ghost_candle['close']:
                            self.price_below_mid = True
                        elif self.current_price > self.ghost_candle['midpoint'] and self.current_price <= self.ghost_candle['open']:
                            self.price_above_mid = True
                    if self.current_candle['open'] < self.ghost_candle['midpoint']:
                        self.below_midpoint = True
                        self.above_midpoint = False
                        #check if current price is above ghost candle midpoint
                        if self.current_price > self.ghost_candle['midpoint'] and self.current_price <= self.ghost_candle['open']:
                            self.price_above_mid = True
                        elif self.current_price < self.ghost_candle['midpoint'] and self.current_price >= self.ghost_candle['close']:
                            self.price_below_mid = True
                
                
                
                #check to see if current price crossed if current candle formed outside
                if not self.open_inside:
                    #open below
                    if self.current_candle['open'] < self.ghost_candle['close'] and self.current_price > self.ghost_candle['close']:
                        self.crossed = True
                    #open above
                    elif self.current_candle['open'] > self.ghost_candle['open'] and self.current_price < self.ghost_candle['open']:
                        self.crossed = True
                #check to see if current price crossed midpoint if current candle formed above/below midpoint
                if self.above_midpoint and self.current_price < self.ghost_candle['midpoint'] or self.below_midpoint and self.current_price > self.ghost_candle['midpoint']:
                    self.midpoint_crossed = True
                    
            # return self.inside


    def request_type(self, type, side, shares):
        '''this function defines what kind of order we want to make in the mt5.order_send function that we use in our send_order() function'''
        
        if type == 'initial' and side =='buy':
            request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": shares,
            "type": mt5.ORDER_TYPE_BUY,
            "price": self.market,
            "deviation": 20,
            "magic": 234000,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN   
            }
            self.is_long = True
        elif type == 'initial' and side =='sell':
            request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": shares,
            "type": mt5.ORDER_TYPE_SELL,
            "price": self.market,
            "deviation": 20,
            "magic": 234000,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN   
            }
            self.is_long = False
       
        #conditions for selling half/only used when the initial trade is in profit
        elif type == 'half' and side =='buy':
            request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": shares / 2.0,
            "type": mt5.ORDER_TYPE_BUY,
            "price": self.market,
            "deviation": 20,
            "magic": 234000,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN   
            }
        elif type == 'half' and side =='sell':
            request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": shares / 2.0,
            "type": mt5.ORDER_TYPE_SELL,
            "price": self.market,
            "deviation": 20,
            "magic": 234000,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN   
            }
        
        #conditions for closing out a position
        elif type == 'close' and side =='buy':
            request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": shares,
            "type": mt5.ORDER_TYPE_BUY,
            "price": self.market,
            "deviation": 20,
            "magic": 234000,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN   
            }
        elif type == 'close' and side =='sell':
            request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": shares,
            "type": mt5.ORDER_TYPE_SELL,
            "price": self.market,
            "deviation": 20,
            "magic": 234000,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN   
            }
            
        #conditions for selling half/only used when the initial trade is in profit
        elif type == 'swap' and side =='buy':
            request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": shares,
            "type": mt5.ORDER_TYPE_BUY,
            "price": self.market,
            "deviation": 20,
            "magic": 234000,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN   
            }
            self.is_long = True
        elif type == 'swap' and side =='sell':
            request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": shares,
            "type": mt5.ORDER_TYPE_SELL,
            "price": self.market,
            "deviation": 20,
            "magic": 234000,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN 
            }
            self.is_long = False

        #only adjust the parameters below on the initial trade
        if type == 'initial':
            #create the channel and increment shares in the case we need to swap
            self.in_trade = True
            self.current_shares = shares
            #reset new open to false and copy to current candle
            self.new_open = False
            self.current_copy = self.current_candle
            #create a swap candle
            self.swap_candle = self.ghost_candle
        return request


    def send_order(self, type, side, shares):
        '''function that simplifies mt5.order_send and passes our request_type() function as an argument'''
       
        order = mt5.order_send(self.request_type(type, side, shares))
        return order


    def close_position(self):
        """ This function closes all open positions for the specific symbol. """
        
        if self.is_long:
            self.send_order('close', 'sell', self.current_shares)
        elif not self.is_long:
            self.send_order('close', 'buy', self.current_shares)


    def P_L(self):
        """This function tracks the current profit/loss"""

        #track open positions for current symbol as well as total positions within account
        self.open_positions = mt5.positions_get(symbol=self.symbol)
        self.total_positions = mt5.positions_total()
        #check if we have any open positions
        if self.open_positions:
            #get profit using mt5 method
            profit = self.open_positions
            profit = pd.DataFrame(list(profit),columns=profit[0]._asdict().keys())
            if profit.iloc[0]['profit'] > 0.0:
                self.profit = profit.iloc[0]['profit']
                
            elif profit.iloc[0]['profit'] < 0.0:
                self.loss = profit.iloc[0]['profit']
                
            else:
                self.profit = 0.0
            
            #check for self.profit_seen for trailing stop
            if self.profit >= self.tp:
                self.profit_seen = True
            #if we arent trailing check if the trigger for swapping is seen
            if self.profit >= self.swap_trail_trigger and not self.trailing:
                self.swap_trail_trigger_seen = True
                

    def sell_half(self):
        """ This function sells half of the specified symbol's position. """

        if self.is_long:
            self.send_order('half', 'sell', self.current_shares)
        elif not self.is_long:
            self.send_order('half', 'buy', self.current_shares)
        self.half_sold = True
        #adjust amount of shares and call the profit loss function to adjust the profit before trailstop kicks in
        self.current_shares = self.current_shares / 2


    def trailing_stop(self):
        """ This function sets a 50% trailing stop on the opening trade's profit. """
        
        #update the trail ceiling for everytime the profit increases which also increases the stop out
        if self.profit > self.ceiling and self.ceiling >= 0.0:
            self.ceiling = self.profit
            print(self.ceiling)
            self.trailing = True
        #take profit at 50%
        if self.ceiling >= self.tp and self.ceiling < self.tp * 2:
            if self.profit <= self.ceiling / 2 > 0.0:
                self.close_position()
                self.flush_variables()               
        #take profit @60%
        elif self.ceiling >= self.tp * 2 and self.ceiling < self.tp * 3:
            print('trailing @ 60')
            if self.profit <= self.ceiling * 0.6 > 0.0:
                self.close_position()
                self.flush_variables()                
        #take profit @70%
        elif self.ceiling >= self.tp * 3 and self.ceiling < self.tp * 4:
            print('trailing @ 70')
            if self.profit <= self.ceiling * 0.7 > 0.0:
                self.close_position()
                self.flush_variables()               
        #take profit @80%
        elif self.ceiling >= self.tp * 4 and self.ceiling < self.tp * 5:
            print('trailing @ 80')
            if self.profit <= self.ceiling * 0.8 > 0.0:
                self.close_position()
                self.flush_variables()
        #take profit @90%
        elif self.ceiling >= self.tp * 5:
            print('trailing @ 90')
            if self.profit <= self.ceiling * 0.9 > 0.0:
                self.close_position()
                self.flush_variables()


    def swap(self):
        """ This function swaps your position with double the lots/shares. """

        #close current positions
        self.close_position()
        #make the  shares = our current shares plus the loss we just took
        self.current_shares = float(round(self.current_shares + abs(self.loss)))
        
        if self.is_long:
            #close current long & open short with double the shares
            self.send_order('swap', 'sell', self.current_shares)
            
        elif not self.is_long:
            #close current short & open long with double the shares
            self.send_order('swap', 'buy', self.current_shares)
            
        #update variables


        #flag that checks if we are in a swap
        self.in_swap = True 
        #reset self.swap_trail_trigger_seen
        self.swap_trail_trigger_seen = False  
        #reset loss so that it doesn't keep swapping
        self.loss = 0.0
        #flag for halting support & resistance
        self.fixed = False 
        #increment swap count
        self.swap_count += 1
        #change trigger if swap count > 0
        if self.swap_count > 0:
            self.swap_trail_trigger = float(self.current_shares * 2)
        
           
    def swap_trailing_stop(self, trigger):
        """ This function sets a 50% trailing stop on the swap trade's profit.
        profit will be the arg for when it hits the positive trigger and loss will be the negative trigger """
        
        if trigger == 'profit':
        #update the trail ceiling for everytime the profit increases which also increases the stop out
            if self.profit > self.swap_trail_ceiling and self.swap_trail_ceiling >= 0.0:
                self.swap_trail_ceiling = self.profit
                print(self.swap_trail_ceiling)
            
            #swap at 50% of trigger after it is seen and you haven't swapped yet
            if self.swap_count == 0:
                if self.swap_trail_ceiling >= self.swap_trail_trigger and self.swap_trail_ceiling < self.tp:
                    if self.profit <= self.swap_trail_ceiling / 2 > 0.0:
                        self.swap()
            #swap at 50% of trigger after it is seen and you've swapped
            elif self.swap_count > 0:
                if self.swap_trail_ceiling >= self.swap_trail_trigger and self.swap_trail_ceiling < self.current_shares * 3:
                    if self.profit <= self.swap_trail_ceiling / 2 > 0.0:
                        self.swap()
        
        elif trigger == 'loss':
            if not self.swap_trail_trigger_seen:
                if self.loss <= float(-self.current_shares * 1):
                    self.swap()
                

    def take_profit(self):
        """ This function takes profit by closing out our position and flushing our variables. """
        
        if self.in_trade:
            #close current current trade at current profit
            self.close_position()
        
        self.flush_variables()


if __name__ == '__main__':
    r = futures_methods('MNQM21')
    print(r.get_bars('min'))
    print(r.open_ema.iloc[-1])
    # print(type(r.first_candle['body']))
    # for bars in r.bars_frame.iterrows():
    #     print(bars)
    # r.Doji()
    
    # print(r.ghost_candle)
    # r.bearish_bullish()
    # print(r.Doji())
    # print(r.In_and_Out())
    # print(r.total_positions)
    # r.send_order('initial', 'sell', r.shares)
    # r.P_L()
    # print(r.total_positions)
    # time.sleep(2)
    # r.swap()
    # mt5.symbol_select(r.symbol, True)
    # while True:
    #     r.get_ticks()
    #     r.get_bars('min')
    #     r.P_L()
    #     r.trailing_stop()
    #     print(r.ceiling)
    # while True:
    #     (r.get_ticks())
    #     r.get_bars('min')
    #     r.P_L()
    #     print(f'PROFITS: {r.profit}, LOSSES: {r.loss}')
    # i = 1.5
    # for i in np.arange(0,4,round(0.01,2)):
    #     print(round(i,2))


    


