'''These will be notes of functions that work so we can use them as backups'''

'''
this is the requests dictionary for sending orders that works:



lot = 1.0
point = mt5.symbol_info(r.symbol).point
price = mt5.symbol_info_tick(r.symbol).ask
deviation = 20


request = {
"action": mt5.TRADE_ACTION_DEAL,
"symbol": r.symbol,
"volume": lot,
"type": mt5.ORDER_TYPE_BUY,
"price": float(mt5.SYMBOL_TRADE_EXECUTION_MARKET),
"sl": price - 100 * point,
"tp": price + 100 * point,
"deviation": deviation,
"magic": 234000,
"type_time": mt5.ORDER_TIME_GTC,
"type_filling": mt5.ORDER_FILLING_RETURN,
}
print(r.ask, price, request['price'])

result = mt5.order_send(r.request_type('initial', 'buy'))
print(result.order)
if result.retcode != mt5.TRADE_RETCODE_DONE:
    print("2. order_send failed, retcode={}".format(result.retcode))
    # request the result as a dictionary and display it element by element
elif result.retcode == 'none':
    print('hey')

'''



""" logic for selling half and inserting a trailing stop:
 replace half_sold with profit_seen in s_r


#check to sell half
            # if self.profit >= self.tp and not self.in_swap and not self.half_sold:
            #     self.sell_half()
            #insert trailing stop
            
            # if self.half_sold and not self.in_swap:
                self.trailing_stop()





"""

'''

#when in swap check that previous candle forms above the break_even point before taking profit/adding trailstop/stop_loss
            if self.profit >= self.break_even + self.swap_trailing_point and self.in_swap:
                self.take_profit()
                
'''

'''


            
            
            #check for swaps using highs and lows if doji
            # elif self.in_trade and self.doji:
                
            #     if self.bullish and self.is_long:
            #         if self.current_price < self.ghost_candle['low']:
            #             self.swap()
            #             return

            #     elif self.bullish and not self.is_long:
            #         if self.current_price > self.ghost_candle['high']:
            #             self.swap()
            #             return

            #     elif not self.bullish and self.is_long:
            #         if self.current_price < self.ghost_candle['low']:
            #             self.swap()
            #             return

            #     elif not self.bullish and not self.is_long:
            #         if self.current_price > self.ghost_candle['high']:
            #             self.swap()
            #             return

            # #check for swap using channel if we are in a sideways market
            # elif self.in_trade and self.is_long and self.trend == 'sideways':
            #     if self.current_price < self.support:
            #         self.swap()
            #         print(f'swapped short @ {self.current_price} swap price is {self.resistance} take_profit: {self.tp}')
            
            # elif self.in_trade and not self.is_long and self.trend == 'sideways':
            #     if self.current_price > self.resistance:
            #         self.swap()
            #         print(f'swapped long @ {self.current_price} swap price is {self.support} take_profit: {self.tp}')
            # '''

'''
self.current_candle = bars_frame.iloc[9]
self.first_candle = bars_frame.iloc[8]
self.second_candle = bars_frame.iloc[7]
self.third_candle = bars_frame.iloc[6]
self.fourth_candle = bars_frame.iloc[5]
self.fifth_candle = bars_frame.iloc[4]
self.sixth_candle = bars_frame.iloc[3]
self.seventh_candle = bars_frame.iloc[2]
self.eighth_candle = bars_frame.iloc[1]
self.ninth_candle = bars_frame.iloc[0]
'''


'''candle look back





            # #reverse bars frame
            # self.bars_frame = self.bars_frame[::-1]
            
            # #look back 40 candle for one that isn't our redefined version of a doji    
            # for bar in self.bars_frame.iterrows():
            #     if bar[1]['body'] not in range:
            #         self.entry_candle = bar[1]
            #         self.doji = False
            #         # print(bar)
            #         break
'''



'''swap trailing stop


def swap_trailing_stop(self):
        """ This function sets a 50% trailing stop on the swap trade's profit. """

        #update the trail ceiling for everytime the profit increases which also increases the stop out
        if self.profit > self.swap_trail_ceiling and self.swap_trail_ceiling >= 0.0:
            self.swap_trail_ceiling = self.profit
            print(self.swap_trail_ceiling)
        #swap at 50%
        if self.swap_trail_ceiling >= self.swap_trail_trigger and self.swap_trail_ceiling < self.tp:
            if self.profit <= self.swap_trail_ceiling / 2 > 0.0:
                self.swap()
                
                
                
    in swap function   
    #reset self.swap_trail_trigger_seen
    self.swap_trail_trigger_seen = False   
                
    flush variables
    self.swap_trail_trigger_seen = False
    self.swap_trailing_point = 2.00
    self.swap_trail_ceiling = 0.0

    variables
    self.swap_trail_ceiling = 0.0 #ceiling for trailing swap
    self.swap_trail_trigger = 2.00
    self.swap_trail_trigger_seen = False  #boolean for determining when to call trailing swap function  

    PL()
    elif self.profit >= self.swap_trail_trigger and not self.trailing:
    self.swap_trail_trigger_seen = True



    #check to insert trailing swap
    # elif self.swap_trail_trigger_seen and not self.trailing:
    #     self.swap_trailing_stop()
    #     print('trigger seen')       
                '''

    