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
                #if new open
                if self.bullish:

                    #buy
                    if self.current_candle['open'] > self.open_ema.iloc[-1]:                      
                        self.is_long = True
                        self.send_order('initial', 'buy', self.shares)
                        print(f'\nTraded Long @ {self.current_price} swap price is {self.support}')
                        return

                    #sell
                    elif self.current_candle['open'] < self.open_ema.iloc[-1]:
                        self.is_long = False
                        self.send_order('initial', 'sell', self.shares)
                        print(f'\nTraded short @ {self.current_price} swap price is {self.resistance}')
                        return
                
                elif not self.bullish:

                    #buy
                    if self.current_candle['open'] > self.open_ema.iloc[-1]:
                        self.is_long = True
                        self.send_order('initial', 'buy', self.shares)
                        print(f'\nTraded Long @ {self.current_price} swap price is {self.support}')
                        return
                   
                    #sell
                    elif self.current_candle['open'] < self.open_ema.iloc[-1]:
                        self.is_long = False
                        self.send_order('initial', 'sell', self.shares)
                        print(f'\nTraded short @ {self.current_price} swap price is {self.resistance}')
                        return
                
            #check for swap if we didn't trade at the midpoint and swap count is divisible by 2
            if self.in_trade and self.swap_count % 2 == 0:
                
                if self.opened_above_ema and self.current_price < self.open_ema.iloc[-1]:
                    print('swapped')
                    self.swap()
                elif self.opened_below_ema and self.current_price > self.open_ema.iloc[-1]:
                    print('swapped')
                    self.swap()
            
            elif self.in_trade and self.swap_count % 2 != 0:
                
                if self.opened_above_ema and self.current_price > self.current_candle['open']:
                    print('swapped')
                    self.swap()
                elif self.opened_below_ema and self.current_price < self.current_candle['open']:
                    print('swapped')
                    self.swap()



            #check to insert trailing stop on initial trade
            if self.profit_seen and not self.in_swap:
                self.trailing_stop() 
            
            # #when in swap check that previous candle forms above the break_even point before taking profit/adding trailstop/stop_loss
            if self.profit >= self.current_shares * 3 and self.in_swap:
                self.take_profit()

            #make a copy of the current candle to determine entry point
            self.current_copy = self.current_candle
            #time.sleep(1)




