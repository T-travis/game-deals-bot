
class GameMatch:
    """GameMatch represents a possible game match from a search for a given game."""

    def __init__(self, href, title):
        self.href = href  # used as a reference to be sent back to query and exact match
        self.title = title  # game title

    def __str__(self):
        return f'(href: {self.href}, title: {self.title})'

