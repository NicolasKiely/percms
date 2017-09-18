''' Runtime library for crypto trading '''

class Runtime(object):
    ''' Stores argument information '''
    def __init__(self, args):
        self.stamp = args['time']
        self.revert_signal()


    def revert_signal(self):
        ''' Resets buy/sell signal '''
        self.signal = ''
        self.confidence = 0


    def signal_buy(self, confidence):
        ''' Signals a buy, with an integer confidence between 0 and 100 '''
        self.signal = 'BUY'
        self.confidence = confidence


    def signal_sell(self, confidence):
        ''' Signals a sell, with an integer confidence between 0 and 100 '''
        self.signal = 'SELL'
        self.confidence = confidence
