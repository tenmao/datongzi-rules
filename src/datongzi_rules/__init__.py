"""Da Tong Zi Rules Engine - Zero Dependency Game Rules Library."""

from .models import Card, Rank, Suit, Deck
from .patterns import PlayType, PlayPattern, PatternRecognizer, PlayValidator

__version__ = "0.1.0"

__all__ = [
    # Models
    "Card",
    "Rank",
    "Suit",
    "Deck",
    # Patterns
    "PlayType",
    "PlayPattern",
    "PatternRecognizer",
    "PlayValidator",
    # Version
    "__version__",
]
