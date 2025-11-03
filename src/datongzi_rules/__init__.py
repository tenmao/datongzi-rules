"""Da Tong Zi Rules Engine - Zero Dependency Game Rules Library."""

from .models import Card, Rank, Suit, Deck, GameConfig
from .patterns import PlayType, PlayPattern, PatternRecognizer, PlayValidator
from .scoring import BonusType, ScoringEvent, ScoringEngine

__version__ = "0.1.0"

__all__ = [
    # Models
    "Card",
    "Rank",
    "Suit",
    "Deck",
    "GameConfig",
    # Patterns
    "PlayType",
    "PlayPattern",
    "PatternRecognizer",
    "PlayValidator",
    # Scoring
    "BonusType",
    "ScoringEvent",
    "ScoringEngine",
    # Version
    "__version__",
]
