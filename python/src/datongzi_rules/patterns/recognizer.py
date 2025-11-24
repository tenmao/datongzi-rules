"""Card combinations and play types for Da Tong Zi game."""

from collections import Counter
from dataclasses import dataclass
from enum import IntEnum
import logging

from ..models.card import Card, Rank, Suit

logger = logging.getLogger(__name__)


class PlayType(IntEnum):
    """
    Play types in order of strength.
    Higher values beat lower values, with special rules for some types.
    """

    SINGLE = 1  # 单牌
    PAIR = 2  # 对子
    CONSECUTIVE_PAIRS = 3  # 连对 (2+ pairs in sequence)
    TRIPLE = 4  # 三张
    TRIPLE_WITH_TWO = 5  # 三带二
    AIRPLANE = 6  # 飞机 (consecutive triples)
    AIRPLANE_WITH_WINGS = 7  # 飞机带翅膀
    BOMB = 8  # 炸弹 (4+ same rank)
    TONGZI = 9  # 筒子 (3 same rank same suit)
    DIZHA = 10  # 地炸 (2 of each suit for same rank)


@dataclass(frozen=True)
class PlayPattern:
    """Represents a recognized pattern of cards."""

    play_type: PlayType
    primary_rank: Rank  # Main rank of the pattern
    primary_suit: Suit | None = None  # For suit-dependent patterns
    secondary_ranks: list[Rank] | None = None  # For consecutive patterns
    card_count: int = 0  # Total number of cards
    strength: int = 0  # Calculated strength for comparison

    def __post_init__(self) -> None:
        """Initialize computed fields."""
        if self.secondary_ranks is None:
            object.__setattr__(self, "secondary_ranks", [])


class PatternRecognizer:
    """Recognizes and analyzes card patterns."""

    @staticmethod
    def analyze_cards(cards: list[Card]) -> PlayPattern | None:
        """
        Analyze a list of cards and return the recognized pattern.

        Args:
            cards: List of cards to analyze

        Returns:
            PlayPattern if valid pattern found, None otherwise
        """
        if not cards:
            return None

        # Sort cards for easier analysis
        sorted_cards = sorted(cards)

        # Count cards by rank
        rank_counts = Counter(card.rank for card in cards)

        # Count cards by suit and rank (for special patterns)
        suit_rank_counts = Counter((card.suit, card.rank) for card in cards)

        logger.debug(
            f"Analyzing card pattern: card_count={len(cards)}, "
            f"rank_counts={dict(rank_counts)}, "
            f"cards={[str(c) for c in sorted_cards]}"
        )

        # Check for special patterns first (highest priority)
        pattern = PatternRecognizer._check_dizha(cards, suit_rank_counts, rank_counts)
        if pattern:
            return pattern

        pattern = PatternRecognizer._check_tongzi(cards, suit_rank_counts, rank_counts)
        if pattern:
            return pattern

        pattern = PatternRecognizer._check_bomb(cards, rank_counts)
        if pattern:
            return pattern

        # Check for airplane patterns
        # IMPORTANT: Check pure AIRPLANE first, then AIRPLANE_WITH_WINGS
        # This ensures that if all cards form a valid airplane, we don't
        # misidentify it as airplane with wings
        pattern = PatternRecognizer._check_airplane(cards, rank_counts)
        if pattern:
            return pattern

        pattern = PatternRecognizer._check_airplane_with_wings(cards, rank_counts)
        if pattern:
            return pattern

        # Check for basic patterns
        pattern = PatternRecognizer._check_triple_with_two(cards, rank_counts)
        if pattern:
            return pattern

        pattern = PatternRecognizer._check_triple(cards, rank_counts)
        if pattern:
            return pattern

        pattern = PatternRecognizer._check_consecutive_pairs(cards, rank_counts)
        if pattern:
            return pattern

        pattern = PatternRecognizer._check_pair(cards, rank_counts)
        if pattern:
            return pattern

        pattern = PatternRecognizer._check_single(cards, rank_counts)
        if pattern:
            return pattern

        logger.debug(f"No valid pattern recognized: cards={[str(c) for c in cards]}")
        return None

    @staticmethod
    def _check_single(
        cards: list[Card], rank_counts: Counter[Rank]
    ) -> PlayPattern | None:
        """Check for single card pattern."""
        if len(cards) != 1:
            return None

        card = cards[0]
        return PlayPattern(
            play_type=PlayType.SINGLE,
            primary_rank=card.rank,
            primary_suit=card.suit,
            card_count=1,
            strength=card.rank.value,
        )

    @staticmethod
    def _check_pair(
        cards: list[Card], rank_counts: Counter[Rank]
    ) -> PlayPattern | None:
        """Check for pair pattern."""
        if len(cards) != 2 or len(rank_counts) != 1:
            return None

        rank = list(rank_counts.keys())[0]
        if rank_counts[rank] != 2:
            return None

        return PlayPattern(
            play_type=PlayType.PAIR,
            primary_rank=rank,
            card_count=2,
            strength=rank.value,
        )

    @staticmethod
    def _check_consecutive_pairs(
        cards: list[Card], rank_counts: Counter[Rank]
    ) -> PlayPattern | None:
        """Check for consecutive pairs pattern (连对)."""
        if len(cards) < 4 or len(cards) % 2 != 0:
            return None

        # All ranks must have exactly 2 cards
        if any(count != 2 for count in rank_counts.values()):
            return None

        ranks = sorted(rank_counts.keys(), key=lambda r: r.value)

        # Check if ranks are consecutive
        if not PatternRecognizer._are_consecutive(ranks):
            return None

        return PlayPattern(
            play_type=PlayType.CONSECUTIVE_PAIRS,
            primary_rank=ranks[-1],  # Highest rank
            secondary_ranks=ranks,
            card_count=len(cards),
            strength=ranks[-1].value * 1000 + len(ranks),
        )

    @staticmethod
    def _check_triple(
        cards: list[Card], rank_counts: Counter[Rank]
    ) -> PlayPattern | None:
        """Check for triple pattern."""
        if len(cards) != 3 or len(rank_counts) != 1:
            return None

        rank = list(rank_counts.keys())[0]
        if rank_counts[rank] != 3:
            return None

        return PlayPattern(
            play_type=PlayType.TRIPLE,
            primary_rank=rank,
            card_count=3,
            strength=rank.value,
        )

    @staticmethod
    def _check_triple_with_two(
        cards: list[Card], rank_counts: Counter[Rank]
    ) -> PlayPattern | None:
        """Check for triple with two pattern (三带二)."""
        if len(cards) != 5 or len(rank_counts) != 2:
            return None

        counts = list(rank_counts.values())
        if not (3 in counts and 2 in counts):
            return None

        # Find the triple rank
        triple_rank = None
        for rank, count in rank_counts.items():
            if count == 3:
                triple_rank = rank
                break

        if triple_rank is None:
            return None

        return PlayPattern(
            play_type=PlayType.TRIPLE_WITH_TWO,
            primary_rank=triple_rank,
            card_count=5,
            strength=triple_rank.value,
        )

    @staticmethod
    def _check_airplane(
        cards: list[Card], rank_counts: Counter[Rank]
    ) -> PlayPattern | None:
        """Check for airplane pattern (consecutive triples)."""
        if len(cards) < 6 or len(cards) % 3 != 0:
            return None

        # All ranks must have exactly 3 cards
        if any(count != 3 for count in rank_counts.values()):
            return None

        ranks = sorted(rank_counts.keys(), key=lambda r: r.value)

        # Check if ranks are consecutive
        if not PatternRecognizer._are_consecutive(ranks):
            return None

        return PlayPattern(
            play_type=PlayType.AIRPLANE,
            primary_rank=ranks[-1],  # Highest rank
            secondary_ranks=ranks,
            card_count=len(cards),
            strength=ranks[-1].value * 1000 + len(ranks),
        )

    @staticmethod
    def _check_airplane_with_wings(
        cards: list[Card], rank_counts: Counter[Rank]
    ) -> PlayPattern | None:
        """Check for airplane with wings pattern (飞机带翅膀).

        规则：N组连续三张（飞机主体）+ K张任意牌（翅膀）
        其中 N <= K <= 2N
        翅膀可以是任意牌（单张、对子、三张、炸弹等）

        关键：贪心选择最大的连续飞机组（如果翅膀中有3张同rank能扩展飞机，应扩展）
        """
        if len(cards) < 8:  # Minimum: 2 triples (6) + 2 wings (2)
            return None

        # Find all ranks with at least 3 cards
        triple_candidates = [rank for rank, count in rank_counts.items() if count >= 3]

        if len(triple_candidates) < 2:
            return None

        # Sort candidates by rank value
        sorted_candidates = sorted(triple_candidates, key=lambda r: r.value)

        # Strategy: Greedily select the LARGEST consecutive triple sequence
        # This ensures that if wings contain 3+ cards of same rank that can extend
        # the airplane, we prioritize the extended airplane
        best_airplane = None
        best_wing_count = None

        # Try all possible consecutive triple combinations, preferring larger airplanes
        for length in range(len(sorted_candidates), 1, -1):  # Start from longest
            for i in range(len(sorted_candidates) - length + 1):
                candidate_ranks = sorted_candidates[i:i + length]

                if PatternRecognizer._are_consecutive(candidate_ranks):
                    num_triples = len(candidate_ranks)
                    triple_cards = num_triples * 3
                    wing_cards = len(cards) - triple_cards

                    # Check if wing count is valid: N <= wings <= 2N
                    if num_triples <= wing_cards <= 2 * num_triples:
                        # Found valid combination, return immediately (greedy)
                        return PlayPattern(
                            play_type=PlayType.AIRPLANE_WITH_WINGS,
                            primary_rank=candidate_ranks[-1],
                            secondary_ranks=candidate_ranks,
                            card_count=len(cards),
                            strength=candidate_ranks[-1].value * 1000 + len(candidate_ranks),
                        )

        return None

    @staticmethod
    def _check_bomb(
        cards: list[Card], rank_counts: Counter[Rank]
    ) -> PlayPattern | None:
        """Check for bomb pattern (4+ same rank)."""
        if len(cards) < 4 or len(rank_counts) != 1:
            return None

        rank = list(rank_counts.keys())[0]
        count = rank_counts[rank]

        if count < 4:
            return None

        return PlayPattern(
            play_type=PlayType.BOMB,
            primary_rank=rank,
            card_count=count,
            strength=rank.value * 1000 + count,  # Higher count beats same rank
        )

    @staticmethod
    def _check_tongzi(
        cards: list[Card],
        suit_rank_counts: Counter[tuple[Suit, Rank]],
        rank_counts: Counter[Rank],
    ) -> PlayPattern | None:
        """Check for tongzi pattern (3 same rank same suit)."""
        if len(cards) != 3 or len(rank_counts) != 1:
            return None

        # Must have exactly one suit-rank combination with 3 cards
        if len(suit_rank_counts) != 1 or list(suit_rank_counts.values())[0] != 3:
            return None

        suit, rank = list(suit_rank_counts.keys())[0]

        return PlayPattern(
            play_type=PlayType.TONGZI,
            primary_rank=rank,
            primary_suit=suit,
            card_count=3,
            strength=rank.value * 10000 + suit.value * 1000,  # Suit matters for tongzi
        )

    @staticmethod
    def _check_dizha(
        cards: list[Card],
        suit_rank_counts: Counter[tuple[Suit, Rank]],
        rank_counts: Counter[Rank],
    ) -> PlayPattern | None:
        """Check for dizha pattern (2 of each suit for same rank)."""
        if len(cards) != 8 or len(rank_counts) != 1:
            return None

        rank = list(rank_counts.keys())[0]

        # Must have exactly 2 cards of each suit for this rank
        suits_for_rank = [suit for (suit, r) in suit_rank_counts.keys() if r == rank]
        if len(suits_for_rank) != 4:  # All 4 suits
            return None

        # Each suit must have exactly 2 cards
        for suit in Suit:
            if suit_rank_counts.get((suit, rank), 0) != 2:
                return None

        return PlayPattern(
            play_type=PlayType.DIZHA,
            primary_rank=rank,
            card_count=8,
            strength=rank.value * 100000,  # Dizha is very strong
        )

    @staticmethod
    def _are_consecutive(ranks: list[Rank]) -> bool:
        """Check if ranks are consecutive, handling wrap-around for A-2."""
        if len(ranks) <= 1:
            return True

        # Convert to values for comparison
        values = [rank.value for rank in ranks]

        # Check normal consecutive sequence
        for i in range(1, len(values)):
            if values[i] != values[i - 1] + 1:
                return False

        return True


class PlayValidator:
    """Validates plays according to Da Tong Zi rules."""

    @staticmethod
    def can_beat_play(new_cards: list[Card], current_play: PlayPattern | None) -> bool:
        """
        Check if new cards can beat the current play.

        Args:
            new_cards: Cards being played
            current_play: Current play to beat (None if starting new round)

        Returns:
            True if new cards can beat current play
        """
        if current_play is None:
            # Starting new round - any valid pattern is allowed
            pattern = PatternRecognizer.analyze_cards(new_cards)
            return pattern is not None

        new_pattern = PatternRecognizer.analyze_cards(new_cards)
        if new_pattern is None:
            logger.debug("New play has no valid pattern")
            return False

        return PlayValidator._compare_patterns(new_pattern, current_play)

    @staticmethod
    def _compare_patterns(
        new_pattern: PlayPattern, current_pattern: PlayPattern
    ) -> bool:
        """
        Compare two patterns to see if new pattern beats current pattern.

        Returns:
            True if new_pattern beats current_pattern
        """
        # Special cases: Dizha beats everything, Tongzi beats Bomb
        if new_pattern.play_type == PlayType.DIZHA:
            if current_pattern.play_type != PlayType.DIZHA:
                return True
            # Dizha vs Dizha: compare ranks
            return new_pattern.primary_rank.value > current_pattern.primary_rank.value

        if current_pattern.play_type == PlayType.DIZHA:
            return False  # Nothing beats Dizha except higher Dizha

        if new_pattern.play_type == PlayType.TONGZI:
            if current_pattern.play_type == PlayType.BOMB:
                return True  # Tongzi beats Bomb
            elif current_pattern.play_type != PlayType.TONGZI:
                return False  # Tongzi can only beat Bomb or other Tongzi
            # Tongzi vs Tongzi: compare by rank, then by suit
            if new_pattern.primary_rank.value > current_pattern.primary_rank.value:
                return True
            elif new_pattern.primary_rank.value == current_pattern.primary_rank.value:
                # Both suits must not be None for comparison
                if (
                    new_pattern.primary_suit is not None
                    and current_pattern.primary_suit is not None
                ):
                    return (
                        new_pattern.primary_suit.value
                        > current_pattern.primary_suit.value
                    )
                return False
            return False

        if current_pattern.play_type == PlayType.TONGZI:
            return False  # Only Tongzi or Dizha can beat Tongzi

        if new_pattern.play_type == PlayType.BOMB:
            if current_pattern.play_type != PlayType.BOMB:
                return True  # Bomb beats non-bomb
            # Bomb vs Bomb: compare by rank first, then count
            if new_pattern.primary_rank.value > current_pattern.primary_rank.value:
                return True
            elif new_pattern.primary_rank.value == current_pattern.primary_rank.value:
                return new_pattern.card_count > current_pattern.card_count
            return False

        if current_pattern.play_type == PlayType.BOMB:
            return False  # Only Bomb/Tongzi/Dizha can beat Bomb

        # Same type comparison
        if new_pattern.play_type != current_pattern.play_type:
            return False

        # For same types, compare by card count first (for consecutive patterns)
        if new_pattern.play_type in [
            PlayType.CONSECUTIVE_PAIRS,
            PlayType.AIRPLANE,
            PlayType.AIRPLANE_WITH_WINGS,
        ]:
            new_ranks = new_pattern.secondary_ranks or []
            current_ranks = current_pattern.secondary_ranks or []
            if len(new_ranks) != len(current_ranks):
                return False

        # Compare by strength
        return new_pattern.strength > current_pattern.strength
