
class GameSale:
    """GameSale represents a single game object with attributes describing it."""

    def __init__(self, game_title, company, platforms, current_sale_percent, current_sale_price, 
        lowest_historical_price, base_price, game_sale_link):
        self.game_title = game_title
        self.company = company
        self.platforms = platforms
        self.current_sale_percent = current_sale_percent
        self.current_sale_price = current_sale_price
        self.lowest_historical_price = lowest_historical_price
        self.base_price = base_price
        self.game_sale_link = game_sale_link
