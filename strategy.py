from futures_functions import futures_methods as fm 


class Strategy(fm):

    def __init__(self, symbol):
        """initialize attributes of the futures_methods parent class"""
        super().__init__(symbol)
    
    def strategy(self):
        
        #assign current price variable to yahoo close function for real time data
        self.get_bars('min')
        self.bearish_bullish()
        self.get_ticks()
        self.In_and_Out()
        self.P_L()
        
        
###
        #strategy

        if self.market_hours('day') in range(0,5) and self.market_hours('time') >= self.market_hours('open') and self.market_hours('time') <= self.market_hours('close'):
            
        
        
            # #check for entry 
            if not self.in_trade and not self.open_positions and self.new_open:
            #     # #if inside of candle
            #     if self.bullish and self.open_inside and self.price_inside:

                    #buy
                    # if self.current_price > self.ghost_candle['close']:                      
                self.is_long = True
                self.send_order('initial', 'buy', self.shares)
                print(f'\nTraded Long @ {self.current_price} swap price is {self.support}')
                return

            #         #sell
            #         elif self.current_price < self.ghost_candle['open']:
            #             self.is_long = False
            #             self.send_order('initial', 'sell', self.shares)
            #             print(f'\nTraded short @ {self.current_price} swap price is {self.resistance}')
            #             return
                
            #     elif not self.bullish and self.open_inside and self.price_inside:

            #         #buy
            #         if self.current_price > self.ghost_candle['open']:
            #             self.is_long = True
            #             self.send_order('initial', 'buy', self.shares)
            #             print(f'\nTraded Long @ {self.current_price} swap price is {self.support}')
            #             return
                   
            #         #sell
            #         elif self.current_price < self.ghost_candle['close']:
            #             self.is_long = False
            #             self.send_order('initial', 'sell', self.shares)
            #             print(f'\nTraded short @ {self.current_price} swap price is {self.resistance}')
            #             return
                
            #     #if outside of candle
            #     elif self.bullish and not self.open_inside and self.crossed:

            #         #buy
            #         if self.current_price > self.ghost_candle['close']:
            #             self.is_long = True
            #             self.send_order('initial', 'buy', self.shares)                       
            #             print(f'\nTraded Long @ {self.current_price} swap price is {self.support}')
            #             return

            #         #sell
            #         elif self.current_price < self.ghost_candle['open']:
            #             self.is_long = False
            #             self.send_order('initial', 'sell', self.shares)
            #             print(f'\nTraded short @ {self.current_price} swap price is {self.resistance}')
            #             return

            #     elif not self.bullish and not self.open_inside and self.crossed:

            #         #buy
            #         if self.current_price > self.ghost_candle['open']:
            #             self.is_long = True
            #             self.send_order('initial', 'buy', self.shares)                       
            #             print(f'\nTraded Long @ {self.current_price} swap price is {self.support}')
                    
            #         #sell
            #         elif self.current_price < self.ghost_candle['close']:
            #             self.is_long = False
            #             self.send_order('initial', 'sell', self.shares)
            #             print(f'\nTraded short @ {self.current_price} swap price is {self.resistance}')
            #             return

               
            #     #midpoint entries
            #     if self.bullish and self.below_midpoint and self.price_below_mid:

            #         #buy
            #         if self.current_price > self.ghost_candle['midpoint']:
            #             self.is_long = True
            #             self.send_order('initial', 'buy', self.shares)
            #             self.traded_mid = True
            #             print(f'\nTraded Long @ {self.current_price} swap price is {self.support}')
            #             return
            
                
            #     elif not self.bullish and self.above_midpoint and self.price_above_mid:

            #         #sell
            #         if self.current_price < self.ghost_candle['midpoint']:
            #             self.is_long = False
            #             self.send_order('initial', 'sell', self.shares)
            #             self.traded_mid = True
            #             print(f'\nTraded short @ {self.current_price} swap price is {self.support}')
            #             return

            #     #midpoint entries for crosses
            #     elif self.bullish and self.above_midpoint and self.midpoint_crossed:

            #         #buy
            #         if self.current_price > self.ghost_candle['midpoint']:
            #             self.is_long = True
            #             self.send_order('initial', 'buy', self.shares)
            #             self.traded_mid = True
            #             print(f'\nTraded Long @ {self.current_price} swap price is {self.support}')
            #             return

                        
                
            #     elif not self.bullish and self.below_midpoint and self.midpoint_crossed: 

            #         #sell
            #         if self.current_price < self.ghost_candle['midpoint']:
            #             self.is_long = False
            #             self.send_order('initial', 'sell', self.shares)
            #             self.traded_mid = True
            #             print(f'\nTraded short @ {self.current_price} swap price is {self.support}')
            #             return  

                          
            
           
           
            # #check for swap if we didn't see the swap trigger in profit
            # if self.in_trade:
            #     self.swap_trailing_stop('loss')


            # #check to insert trailing stop on initial trade
            # if self.profit_seen and not self.in_swap:
            #     self.trailing_stop()
            # #check to insert trailing swap
            # elif self.swap_trail_trigger_seen and not self.trailing:
            #     self.swap_trailing_stop('profit')
            #     print('trigger seen') 
            
            # #when in swap check that previous candle forms above the break_even point before taking profit/adding trailstop/stop_loss
            # if self.profit >= self.current_shares * 3 and self.in_swap:
            #     self.take_profit()

            #make a copy of the current candle to determine entry point
            self.current_copy = self.current_candle
            #time.sleep(1)




