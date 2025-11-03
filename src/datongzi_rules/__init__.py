"""Da Tong Zi Rules Engine - Zero Dependency Game Rules Library."""

from .models import Card, Rank, Suit, Deck, GameConfig
from .patterns import PlayType, PlayPattern, PatternRecognizer, PlayValidator
from .scoring import BonusType, ScoringEvent, ScoringEngine
from .ai_helpers import PlayGenerator, HandEvaluator, HandAnalyzer, PatternSuggester

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
    # AI Helpers
    "PlayGenerator",
    "HandEvaluator",
    "HandAnalyzer",
    "PatternSuggester",
    # Version
    "__version__",
]
