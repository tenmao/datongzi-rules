"""Da Tong Zi Rules Engine - Zero Dependency Game Rules Library."""

from .models import Card, Rank, Suit, Deck, GameConfig
from .patterns import (
    PatternFinder,
    PatternRecognizer,
    PlayFormationValidator,
    PlayPattern,
    PlayType,
    PlayValidator,
)
from .scoring import BonusType, ScoringEvent, ScoreComputation
from .ai_helpers import (
    PlayGenerator,
    HandPatternAnalyzer,
    HandPatterns,
)
from .variants import ConfigFactory, VariantValidator

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
    "PatternFinder",
    "PlayFormationValidator",
    # Scoring
    "BonusType",
    "ScoringEvent",
    "ScoreComputation",
    # AI Helpers
    "PlayGenerator",
    "HandPatternAnalyzer",
    "HandPatterns",
    # Variants
    "ConfigFactory",
    "VariantValidator",
    # Version
    "__version__",
]
