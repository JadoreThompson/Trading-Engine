from enum import Enum

class Action(str, Enum):
    OPEN = 'open'
    CLOSE = 'close'

class Topic(str, Enum):
    CREATE = 'create'
    CLOSE = 'close'
    UPDATE = 'update'

class MarketSide(str, Enum):
    LONG = 'long'
    SHORT = 'short'

class OrderType(str, Enum):
    MARKET_ORDER = 'mo'
    BUY_LIMIT = 'bl'
    SELL_LIMIT ='sl'
