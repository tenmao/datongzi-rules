"""Configuration factory for game rule variants - Zero Dependency Version."""

import logging

from ..models.card import Rank
from ..models.config import GameConfig

logger = logging.getLogger(__name__)


class ConfigFactory:
    """
    Factory for creating game configurations with different rule variants.
    
    Provides pre-configured setups for common game variations:
    - Different deck counts (3-deck, 4-deck)
    - Different player counts (2-4 players)
    - Regional rule variations
    """

    @staticmethod
    def create_standard_3deck_3player() -> GameConfig:
        """
        Create standard 3-deck, 3-player configuration.
        
        This is the most common variant:
        - 3 decks (132 cards)
        - 3 players (41 cards each)
        - 9 cards set aside
        - Standard finish bonuses: [100, -40, -60]
        
        Returns:
            GameConfig for standard game
        """
        config = GameConfig(
            num_decks=3,
            num_players=3,
            cards_dealt_aside=9,
            excluded_ranks=set(),
            finish_bonus=[100, -40, -60],
            k_tongzi_bonus=100,
            a_tongzi_bonus=200,
            two_tongzi_bonus=300,
            dizha_bonus=400,
            must_beat_rule=True,
        )
        
        logger.info("Created standard 3-deck 3-player configuration")
        return config

    @staticmethod
    def create_4deck_4player() -> GameConfig:
        """
        Create 4-deck, 4-player configuration.
        
        - 4 decks (176 cards)
        - 4 players (42 cards each)
        - 8 cards set aside
        - Adjusted finish bonuses: [100, -20, -40, -80]
        
        Returns:
            GameConfig for 4-player game
        """
        config = GameConfig(
            num_decks=4,
            num_players=4,
            cards_dealt_aside=8,
            excluded_ranks=set(),
            finish_bonus=[100, -20, -40, -80],
            k_tongzi_bonus=100,
            a_tongzi_bonus=200,
            two_tongzi_bonus=300,
            dizha_bonus=400,
            must_beat_rule=True,
        )
        
        logger.info("Created 4-deck 4-player configuration")
        return config

    @staticmethod
    def create_2player() -> GameConfig:
        """
        Create 2-player configuration.
        
        - 3 decks (132 cards)
        - 2 players (60 cards each)
        - 12 cards set aside
        - Head-to-head bonuses: [100, -100]
        
        Returns:
            GameConfig for 2-player game
        """
        config = GameConfig(
            num_decks=3,
            num_players=2,
            cards_dealt_aside=12,
            excluded_ranks=set(),
            finish_bonus=[100, -100],
            k_tongzi_bonus=100,
            a_tongzi_bonus=200,
            two_tongzi_bonus=300,
            dizha_bonus=400,
            must_beat_rule=True,
        )
        
        logger.info("Created 2-player configuration")
        return config

    @staticmethod
    def create_quick_game() -> GameConfig:
        """
        Create quick game configuration (2 decks, fewer cards).
        
        - 2 decks (88 cards)
        - 3 players (28 cards each)
        - 4 cards set aside
        - Faster gameplay
        
        Returns:
            GameConfig for quick game
        """
        config = GameConfig(
            num_decks=2,
            num_players=3,
            cards_dealt_aside=4,
            excluded_ranks=set(),
            finish_bonus=[100, -40, -60],
            k_tongzi_bonus=100,
            a_tongzi_bonus=200,
            two_tongzi_bonus=300,
            dizha_bonus=400,
            must_beat_rule=True,
        )
        
        logger.info("Created quick game configuration (2 decks)")
        return config

    @staticmethod
    def create_high_stakes() -> GameConfig:
        """
        Create high-stakes configuration with increased bonuses.
        
        - Standard 3-deck, 3-player setup
        - Doubled special bonuses
        - Increased finish bonuses
        
        Returns:
            GameConfig for high-stakes game
        """
        config = GameConfig(
            num_decks=3,
            num_players=3,
            cards_dealt_aside=9,
            excluded_ranks=set(),
            finish_bonus=[200, -80, -120],  # Doubled
            k_tongzi_bonus=200,  # Doubled
            a_tongzi_bonus=400,  # Doubled
            two_tongzi_bonus=600,  # Doubled
            dizha_bonus=800,  # Doubled
            must_beat_rule=True,
        )
        
        logger.info("Created high-stakes configuration (doubled bonuses)")
        return config

    @staticmethod
    def create_beginner_friendly() -> GameConfig:
        """
        Create beginner-friendly configuration.
        
        - Standard setup but no "must beat" rule
        - Players can choose to pass even with valid plays
        - More forgiving for learning
        
        Returns:
            GameConfig for beginner game
        """
        config = GameConfig(
            num_decks=3,
            num_players=3,
            cards_dealt_aside=9,
            excluded_ranks=set(),
            finish_bonus=[100, -40, -60],
            k_tongzi_bonus=100,
            a_tongzi_bonus=200,
            two_tongzi_bonus=300,
            dizha_bonus=400,
            must_beat_rule=False,  # Relaxed rule
        )
        
        logger.info("Created beginner-friendly configuration (no must-beat rule)")
        return config

    @staticmethod
    def create_custom(
        num_decks: int = 3,
        num_players: int = 3,
        cards_dealt_aside: int = 9,
        excluded_ranks: set[Rank] | None = None,
        k_tongzi_bonus: int = 100,
        a_tongzi_bonus: int = 200,
        two_tongzi_bonus: int = 300,
        dizha_bonus: int = 400,
        must_beat_rule: bool = True,
    ) -> GameConfig:
        """
        Create custom configuration with specified parameters.
        
        Args:
            num_decks: Number of card decks (default: 3)
            num_players: Number of players (default: 3)
            cards_dealt_aside: Cards not dealt to players (default: 9)
            excluded_ranks: Ranks to exclude from deck (default: None)
            k_tongzi_bonus: Bonus for K tongzi (default: 100)
            a_tongzi_bonus: Bonus for A tongzi (default: 200)
            two_tongzi_bonus: Bonus for 2 tongzi (default: 300)
            dizha_bonus: Bonus for dizha (default: 400)
            must_beat_rule: Whether must-beat rule is enforced (default: True)
            
        Returns:
            Custom GameConfig
        """
        if excluded_ranks is None:
            excluded_ranks = set()
        
        config = GameConfig(
            num_decks=num_decks,
            num_players=num_players,
            cards_dealt_aside=cards_dealt_aside,
            excluded_ranks=excluded_ranks,
            k_tongzi_bonus=k_tongzi_bonus,
            a_tongzi_bonus=a_tongzi_bonus,
            two_tongzi_bonus=two_tongzi_bonus,
            dizha_bonus=dizha_bonus,
            must_beat_rule=must_beat_rule,
        )
        
        logger.info(
            f"Created custom configuration: decks={num_decks}, "
            f"players={num_players}, must_beat={must_beat_rule}"
        )
        
        return config


class VariantValidator:
    """Validate game configuration variants for playability."""

    @staticmethod
    def validate_config(config: GameConfig) -> tuple[bool, list[str]]:
        """
        Validate that a configuration is playable.
        
        Args:
            config: Configuration to validate
            
        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []
        
        # Check if enough cards for all players
        total_available = config.total_cards - config.cards_dealt_aside
        required = config.num_players * 10  # Minimum 10 cards per player
        
        if total_available < required:
            warnings.append(
                f"Too few cards: {total_available} available, "
                f"need at least {required} for {config.num_players} players"
            )
        
        # Check for unbalanced distribution
        if total_available % config.num_players != 0:
            warnings.append(
                f"Uneven distribution: {total_available} cards cannot be "
                f"evenly divided among {config.num_players} players"
            )
        
        # Check finish bonus length
        if len(config.finish_bonus) != config.num_players:
            warnings.append(
                f"Finish bonus length ({len(config.finish_bonus)}) does not "
                f"match player count ({config.num_players})"
            )
        
        # Check bonus sum (should be zero or negative for fairness)
        bonus_sum = sum(config.finish_bonus)
        if bonus_sum > 0:
            warnings.append(
                f"Finish bonuses sum to {bonus_sum} (should be ≤0 for fairness)"
            )
        
        is_valid = len(warnings) == 0
        
        if not is_valid:
            logger.warning(f"Configuration validation warnings: {warnings}")
        else:
            logger.info("Configuration validated successfully")
        
        return (is_valid, warnings)
