from typing import Optional

from pydantic import BaseModel, Field, field_validator

# Local
from enums import Topic, OrderType, MarketSide, Action


class Base(BaseModel):
    """
    Base Model
    """
    class Config:
        use_enum_values = True


class Order(Base):
    ticker: str # Make enum
    dollar_amount: float = Field(ge=10)
    stop_loss: Optional[float] = Field(None, gt=0)
    take_profit: Optional[float] = Field(None, gt=0)
    open_price: Optional[float] = Field(None, gt=0)


class MarketOrder(Order):
    side: MarketSide = Field(description="Either long or short")

    @field_validator('entry_price', check_fields=False)
    def validate_entry_price(cls, entry_price):
        if entry_price:
            raise ValueError("Market order doesn't allow user entry price")


class BuyLimit(Order):
    side: Optional[MarketSide] = MarketSide.LONG
    @field_validator('entry_price', check_fields=False)
    def validate_entry_price(cls, entry_price, values):
        tp, sl = values.get('take_profit'), values.get('stop_loss')
        if not sl < entry_price < tp:
            raise ValueError('Entry digits invalid')
        return entry_price


class SellLimit(Order):
    side: Optional[MarketSide] = MarketSide.SHORT
    @field_validator('entry_price', check_fields=False)
    def validate_entry_price(cls, entry_price, values):
        tp, sl = values.get('take_profit'), values.get('stop_loss')
        if not sl > entry_price > tp:
            raise ValueError('Entry digits invalid')
        return entry_price


class OrderDetails(Base):
    market_order: Optional[MarketOrder] = Field(None, description="Market Order")
    buy_limit: Optional[BuyLimit] = Field(None, description="Creates a buy limit")
    sell_limit: Optional[SellLimit] = Field(None, description="Creats sell limit")


class CreateTradeRequest(Base):
    """
    Create order model
    """
    action: Action
    type: OrderType
    order_details: OrderDetails


class CloseTrade(Base):
    """
    close trade, takes order id and action of close
    """
    action: Action
    trade_id: str


class TradeUpdate(Base):
    topic: Topic
    order_id: Optional[str] = None
    value: Optional[float] = None
