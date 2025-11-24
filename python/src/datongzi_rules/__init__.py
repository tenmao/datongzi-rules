"""Da Tong Zi Rules Engine - Zero Dependency Game Rules Library."""

from .ai_helpers import (
    HandPatternAnalyzer,
    HandPatterns,
    PlayGenerator,
)
from .models import Card, Deck, GameConfig, Rank, Suit
from .patterns import (
    PatternFinder,
    PatternRecognizer,
    PlayFormationValidator,
    PlayPattern,
    PlayType,
    PlayValidator,
)
from .scoring import BonusType, ScoreComputation, ScoringEvent
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
