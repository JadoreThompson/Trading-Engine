from typing import Optional
from pydantic import BaseModel, Field, field_validator
from enums import Topic, OrderType, MarketSide, Action


class Base(BaseModel):
    """
    Base model class that all other models inherit from.
    Configures enum handling for all child classes.
    """

    class Config:
        use_enum_values = True


class Order(Base):
    """
    Base order model containing common fields for all order types.

    Attributes:
        ticker (str): Trading symbol/ticker for the order
        dollar_amount (float): Amount in dollars for the order, minimum 10
        stop_loss (Optional[float]): Stop loss price, must be positive if provided
        take_profit (Optional[float]): Take profit price, must be positive if provided
        open_price (Optional[float]): Opening price, must be positive if provided
    """
    ticker: str  # Make enum
    dollar_amount: float = Field(ge=10)
    stop_loss: Optional[float] = Field(None, gt=0)
    take_profit: Optional[float] = Field(None, gt=0)
    open_price: Optional[float] = Field(None, gt=0)


class MarketOrder(Order):
    """
    Market order model for immediate execution at current market price.

    Attributes:
        side (MarketSide): Trading direction (long/short)

    Raises:
        ValueError: If entry price is provided, as market orders execute at current price
    """
    side: MarketSide = Field(description="Either long or short")

    @field_validator('entry_price', check_fields=False)
    def validate_entry_price(cls, entry_price):
        if entry_price:
            raise ValueError("Market order doesn't allow user entry price")


class BuyLimit(Order):
    """
    Buy limit order model for long positions with specified entry price.

    Attributes:
        side (Optional[MarketSide]): Defaults to LONG

    Raises:
        ValueError: If entry price is not between stop loss and take profit
    """
    side: Optional[MarketSide] = MarketSide.LONG

    @field_validator('entry_price', check_fields=False)
    def validate_entry_price(cls, entry_price, values):
        tp, sl = values.get('take_profit'), values.get('stop_loss')
        if not sl < entry_price < tp:
            raise ValueError('Entry digits invalid')
        return entry_price


class SellLimit(Order):
    """
    Sell limit order model for short positions with specified entry price.

    Attributes:
        side (Optional[MarketSide]): Defaults to SHORT

    Raises:
        ValueError: If entry price is not between take profit and stop loss
    """
    side: Optional[MarketSide] = MarketSide.SHORT

    @field_validator('entry_price', check_fields=False)
    def validate_entry_price(cls, entry_price, values):
        tp, sl = values.get('take_profit'), values.get('stop_loss')
        if not sl > entry_price > tp:
            raise ValueError('Entry digits invalid')
        return entry_price


class OrderDetails(Base):
    """
    Container model for different order types.
    Only one order type should be provided per request.

    Attributes:
        market_order (Optional[MarketOrder]): Market order details
        buy_limit (Optional[BuyLimit]): Buy limit order details
        sell_limit (Optional[SellLimit]): Sell limit order details
    """
    market_order: Optional[MarketOrder] = Field(None, description="Market Order")
    buy_limit: Optional[BuyLimit] = Field(None, description="Creates a buy limit")
    sell_limit: Optional[SellLimit] = Field(None, description="Creats sell limit")


class CreateTradeRequest(Base):
    """
    Request model for creating new trades.

    Attributes:
        action (Action): Trade action to perform
        type (OrderType): Type of order to create
        order_details (OrderDetails): Specific details for the order type
    """
    action: Action
    type: OrderType
    order_details: OrderDetails


class CloseTrade(Base):
    """
    Request model for closing existing trades.

    Attributes:
        action (Action): Must be a closing action
        trade_id (str): Identifier of the trade to close
    """
    action: Action
    trade_id: str


class TradeUpdate(Base):
    """
    Model for trade update notifications.

    Attributes:
        topic (Topic): Update topic/category
        order_id (Optional[str]): Identifier of the affected order
        value (Optional[float]): New value associated with the update
    """
    topic: Topic
    order_id: Optional[str] = None
    value: Optional[float] = None