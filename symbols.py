from strategy import Strategy
import time

class Execute(Strategy):

    def __init__(self, symbol):
        """initialize attributes of the Strategy parent class"""
        super().__init__(symbol)

if __name__ == '__main__':
    mnqm21 = Execute('MNQM21')
    while True:
        mnqm21.strategy()
        # print(f'\nprice: {self.current_price}')
        # print(f'\nhigh: {self.first_candle["high"]}')
        # print(f'\nlow: {self.first_candle["low"]}')
        # # print(f'\nBID: {self.bid}')
        # # print(f'\nASK: {self.ask}')
        # print(f'\nentry price: {self.entry_point}')
        # print(f'\nprofit: {self.profit}')
        # print(f'\nclose trail @: {self.ceiling / 2}')
        # print(f'\ncurrent losses: {self.losses} break even @ {self.break_even}')
        # print(f'\nloss: {self.loss}')
        # print(f'\n{self.trend} trend')
        # print(f'trigger seen: {mnqm21.swap_trail_trigger_seen}')
        print(mnqm21.new_open)
        # print(mnqm21.swap_trail_trigger_seen)
        # print(f'swap count: {mnqm21.swap_count}')
        # print(f'mid point: {mnqm21.ghost_candle["midpoint"]}')
        # print(f'is doji: {mnqm21.doji}')
        # print(f'price above midpoint: {mnqm21.price_above_mid}, price below midpoint: {mnqm21.price_below_mid}')
        # print(f'\n open above: {mnqm21.above_midpoint}, open below: {mnqm21.below_midpoint}\n')
        # if mnqm21.above_midpoint:
        #     print('above')
        # elif mnqm21.below_midpoint:
        #     print('below')
        # print(mnqm21.get_bars('min'))
        # print(f'midpoint crossed: {mnqm21.midpoint_crossed}')
        # print(mnqm21.profit_seen)
        # print(mnqm21.current_price)
        # print(mnqm21.open_inside)
        # print(mnqm21.price_inside)
        # print(mnqm21.crossed)
        # print(mnqm21.open_positions)
        # print(mnqm21.in_trade)
        # if mymm21.in_trade:
            # print(mymm21.in_trade)
            # print(f"PRICE:{mymm21.current_price}, OPEN: {mymm21.swap_candle['open']}, CLOSE: {mymm21.swap_candle['close']}, High: {mymm21.swap_candle['high']}, LOW: {mymm21.swap_candle['low']}" )
            # print(mymm21.current_shares)
        time.sleep(1)

        