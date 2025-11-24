"""Play generation for AI assistance - Zero Dependency Version."""

from collections import Counter
from itertools import combinations
import logging

from ..models.card import Card, Rank
from ..patterns.recognizer import PatternRecognizer, PlayPattern, PlayType, PlayValidator

logger = logging.getLogger(__name__)


class PlayGenerator:
    """
    Generate valid plays from a hand of cards.

    This is a pure utility class for AI assistance. It does not maintain state
    and can be used by AI players, auto-play features, or hint systems.

    IMPORTANT: This class only generates plays that follow the core rules.
    AI strategy (which play to choose) should be implemented in the AI layer.
    """

    @staticmethod
    def generate_all_plays(hand: list[Card], max_combinations: int = 1000) -> list[list[Card]]:
        """
        Generate all possible valid plays from hand.

        ⚠️ WARNING: This method can cause combinatorial explosion with large hands.

        Valid use cases:
        1. Unit tests - Verify pattern recognition completeness
        2. Debug tools - Developer inspection of all possibilities
        3. Small hands - When hand size < 10 cards

        ❌ DO NOT use in AI decision making or production code!
        ✅ For AI: Use generate_beating_plays_with_same_type_or_trump instead
        ✅ For statistics: Use count_all_plays instead (returns count only)

        Args:
            hand: List of cards in hand
            max_combinations: Safety threshold (default 1000)

        Returns:
            List of all valid play combinations (each is a list of cards)

        Raises:
            ValueError: If combinations exceed max_combinations
        """
        if not hand:
            return []

        if len(hand) > 15:
            logger.warning(
                f"generate_all_plays called with {len(hand)} cards - "
                f"may cause combinatorial explosion"
            )

        all_plays = []

        # Generate singles
        all_plays.extend([[card] for card in hand])

        # Generate pairs
        all_plays.extend(PlayGenerator._generate_pairs(hand))

        # Generate consecutive pairs
        all_plays.extend(PlayGenerator._generate_consecutive_pairs(hand))

        # Generate triples
        all_plays.extend(PlayGenerator._generate_triples(hand))

        # Generate triple with two
        all_plays.extend(PlayGenerator._generate_triple_with_two(hand))

        # Generate airplanes
        all_plays.extend(PlayGenerator._generate_airplanes(hand))

        # Generate airplane with wings
        all_plays.extend(PlayGenerator._generate_airplane_with_wings(hand))

        # Generate bombs
        all_plays.extend(PlayGenerator._generate_bombs(hand))

        # Generate tongzi
        all_plays.extend(PlayGenerator._generate_tongzi(hand))

        # Generate dizha
        all_plays.extend(PlayGenerator._generate_dizha(hand))

        if len(all_plays) > max_combinations:
            raise ValueError(
                f"Generated {len(all_plays)} combinations exceeds limit {max_combinations}. "
                f"Use generate_beating_plays_with_same_type_or_trump or count_all_plays instead."
            )

        logger.debug(f"Generated {len(all_plays)} total plays from {len(hand)} cards")

        return all_plays

    @staticmethod
    def generate_valid_responses(
        hand: list[Card], current_pattern: PlayPattern
    ) -> list[list[Card]]:
        """
        Generate all valid plays that can beat the current pattern.

        ⚠️ DEPRECATED: Use generate_beating_plays_with_same_type_or_trump instead.
        This method is inefficient (generates all plays then filters).
        Kept for backward compatibility only.

        Args:
            hand: List of cards in hand
            current_pattern: Current play pattern to beat

        Returns:
            List of valid response plays
        """
        logger.warning(
            "generate_valid_responses is deprecated. "
            "Use generate_beating_plays_with_same_type_or_trump instead."
        )

        return PlayGenerator.generate_beating_plays_with_same_type_or_trump(
            hand, current_pattern
        )

    @staticmethod
    def generate_beating_plays_with_same_type_or_trump(
        hand: list[Card], current_pattern: PlayPattern
    ) -> list[list[Card]]:
        """
        Generate plays that can beat current pattern using same type or trump cards.

        Strategy:
        - Only use same-type plays with higher rank (no pattern breaking)
        - Or use trump cards (BOMB/TONGZI/DIZHA) to beat normal plays
        - Trump hierarchy: DIZHA > TONGZI > BOMB

        This follows the "有牌必打" rule - must play if you can beat.

        Args:
            hand: List of cards in hand
            current_pattern: Current play pattern to beat

        Returns:
            List of valid beating plays (minimal set, no wasteful combinations)
        """
        if not hand:
            return []

        beating_plays = []
        current_type = current_pattern.play_type

        # Trump cards (can beat any normal play)
        trump_types = [PlayType.DIZHA, PlayType.TONGZI, PlayType.BOMB]
        is_current_trump = current_type in trump_types

        # 1. Generate same-type plays with higher rank
        if current_type == PlayType.SINGLE:
            beating_plays.extend(
                PlayGenerator._generate_higher_singles(hand, current_pattern)
            )
        elif current_type == PlayType.PAIR:
            beating_plays.extend(
                PlayGenerator._generate_higher_pairs(hand, current_pattern)
            )
        elif current_type == PlayType.CONSECUTIVE_PAIRS:
            beating_plays.extend(
                PlayGenerator._generate_higher_consecutive_pairs(hand, current_pattern)
            )
        elif current_type == PlayType.TRIPLE:
            beating_plays.extend(
                PlayGenerator._generate_higher_triples(hand, current_pattern)
            )
        elif current_type == PlayType.TRIPLE_WITH_TWO:
            beating_plays.extend(
                PlayGenerator._generate_higher_triple_with_two(hand, current_pattern)
            )
        elif current_type == PlayType.AIRPLANE:
            beating_plays.extend(
                PlayGenerator._generate_higher_airplanes(hand, current_pattern)
            )
        elif current_type == PlayType.AIRPLANE_WITH_WINGS:
            beating_plays.extend(
                PlayGenerator._generate_higher_airplane_with_wings(hand, current_pattern)
            )

        # 2. Generate trump plays (if current is not trump, or higher trump)
        if not is_current_trump:
            # Any trump beats normal play
            beating_plays.extend(PlayGenerator._generate_bombs(hand))
            beating_plays.extend(PlayGenerator._generate_tongzi(hand))
            beating_plays.extend(PlayGenerator._generate_dizha(hand))
        else:
            # Trump vs trump - must follow hierarchy
            if current_type == PlayType.BOMB:
                # Higher bombs, or tongzi/dizha
                beating_plays.extend(
                    PlayGenerator._generate_higher_bombs(hand, current_pattern)
                )
                beating_plays.extend(PlayGenerator._generate_tongzi(hand))
                beating_plays.extend(PlayGenerator._generate_dizha(hand))
            elif current_type == PlayType.TONGZI:
                # Higher tongzi, or dizha
                beating_plays.extend(
                    PlayGenerator._generate_higher_tongzi(hand, current_pattern)
                )
                beating_plays.extend(PlayGenerator._generate_dizha(hand))
            elif current_type == PlayType.DIZHA:
                # Only higher dizha
                beating_plays.extend(
                    PlayGenerator._generate_higher_dizha(hand, current_pattern)
                )

        # 3. Validate all plays can actually beat current pattern
        valid_plays = [
            play for play in beating_plays
            if PlayValidator.can_beat_play(play, current_pattern)
        ]

        logger.debug(
            f"Generated {len(valid_plays)} beating plays for "
            f"{current_pattern.play_type.name}"
        )

        return valid_plays

    @staticmethod
    def count_all_plays(hand: list[Card]) -> int:
        """
        Count total number of valid plays without generating them.

        This is much more efficient than generate_all_plays when you only
        need the count (e.g., for hand evaluation metrics).

        Args:
            hand: List of cards in hand

        Returns:
            Total count of valid plays
        """
        if not hand:
            return 0

        count = 0

        # Count singles
        count += len(hand)

        # Count pairs
        count += len(PlayGenerator._generate_pairs(hand))

        # Count consecutive pairs
        count += len(PlayGenerator._generate_consecutive_pairs(hand))

        # Count triples
        count += len(PlayGenerator._generate_triples(hand))

        # Count triple with two
        count += len(PlayGenerator._generate_triple_with_two(hand))

        # Count airplanes
        count += len(PlayGenerator._generate_airplanes(hand))

        # Count airplane with wings
        count += len(PlayGenerator._generate_airplane_with_wings(hand))

        # Count bombs
        count += len(PlayGenerator._generate_bombs(hand))

        # Count tongzi
        count += len(PlayGenerator._generate_tongzi(hand))

        # Count dizha
        count += len(PlayGenerator._generate_dizha(hand))

        logger.debug(f"Counted {count} total plays from {len(hand)} cards")

        return count

    @staticmethod
    def _generate_pairs(hand: list[Card]) -> list[list[Card]]:
        """Generate all valid pairs from hand."""
        pairs = []
        rank_groups = PlayGenerator._group_by_rank(hand)
        
        for rank, cards in rank_groups.items():
            if len(cards) >= 2:
                # Generate all 2-card combinations
                for pair in combinations(cards, 2):
                    pair_list = list(pair)
                    pattern = PatternRecognizer.analyze_cards(pair_list)
                    if pattern and pattern.play_type == PlayType.PAIR:
                        pairs.append(pair_list)
        
        return pairs

    @staticmethod
    def _generate_consecutive_pairs(hand: list[Card]) -> list[list[Card]]:
        """Generate all valid consecutive pairs from hand."""
        consecutive_pairs = []
        rank_groups = PlayGenerator._group_by_rank(hand)
        
        # Get ranks that have at least 2 cards
        valid_ranks = sorted([r for r, cards in rank_groups.items() if len(cards) >= 2])
        
        # Try all consecutive sequences of length 2+
        for length in range(2, len(valid_ranks) + 1):
            for i in range(len(valid_ranks) - length + 1):
                ranks = valid_ranks[i:i+length]
                
                # Check if consecutive
                if PlayGenerator._is_consecutive(ranks):
                    # Take 2 cards from each rank
                    cards_list = []
                    for rank in ranks:
                        cards_list.extend(rank_groups[rank][:2])
                    
                    pattern = PatternRecognizer.analyze_cards(cards_list)
                    if pattern and pattern.play_type == PlayType.CONSECUTIVE_PAIRS:
                        consecutive_pairs.append(cards_list)
        
        return consecutive_pairs

    @staticmethod
    def _generate_triples(hand: list[Card]) -> list[list[Card]]:
        """Generate all valid triples from hand."""
        triples = []
        rank_groups = PlayGenerator._group_by_rank(hand)
        
        for rank, cards in rank_groups.items():
            if len(cards) >= 3:
                # Generate all 3-card combinations
                for triple in combinations(cards, 3):
                    triple_list = list(triple)
                    pattern = PatternRecognizer.analyze_cards(triple_list)
                    if pattern and pattern.play_type == PlayType.TRIPLE:
                        triples.append(triple_list)
        
        return triples

    @staticmethod
    def _generate_triple_with_two(hand: list[Card]) -> list[list[Card]]:
        """Generate all valid triple with two combinations."""
        results = []
        rank_groups = PlayGenerator._group_by_rank(hand)
        
        # Find all triples
        triple_ranks = [r for r, cards in rank_groups.items() if len(cards) >= 3]
        
        # Find all pairs
        pair_ranks = [r for r, cards in rank_groups.items() if len(cards) >= 2 and r not in triple_ranks]
        # Also check if triple rank has enough cards for both triple and pair
        pair_ranks.extend([r for r in triple_ranks if len(rank_groups[r]) >= 5])
        
        for triple_rank in triple_ranks:
            triple_cards = rank_groups[triple_rank][:3]
            
            for pair_rank in pair_ranks:
                if pair_rank == triple_rank:
                    # Need 5 cards of same rank
                    if len(rank_groups[pair_rank]) >= 5:
                        pair_cards = rank_groups[pair_rank][3:5]
                    else:
                        continue
                else:
                    pair_cards = rank_groups[pair_rank][:2]
                
                combo = triple_cards + pair_cards
                pattern = PatternRecognizer.analyze_cards(combo)
                if pattern and pattern.play_type == PlayType.TRIPLE_WITH_TWO:
                    results.append(combo)
        
        return results

    @staticmethod
    def _generate_airplanes(hand: list[Card]) -> list[list[Card]]:
        """Generate all valid airplane patterns (consecutive triples)."""
        airplanes = []
        rank_groups = PlayGenerator._group_by_rank(hand)
        
        # Get ranks with at least 3 cards
        valid_ranks = sorted([r for r, cards in rank_groups.items() if len(cards) >= 3])
        
        # Try all consecutive sequences of length 2+
        for length in range(2, len(valid_ranks) + 1):
            for i in range(len(valid_ranks) - length + 1):
                ranks = valid_ranks[i:i+length]
                
                # Check if consecutive
                if PlayGenerator._is_consecutive(ranks):
                    # Take 3 cards from each rank
                    cards_list = []
                    for rank in ranks:
                        cards_list.extend(rank_groups[rank][:3])
                    
                    pattern = PatternRecognizer.analyze_cards(cards_list)
                    if pattern and pattern.play_type == PlayType.AIRPLANE:
                        airplanes.append(cards_list)
        
        return airplanes

    @staticmethod
    def _generate_airplane_with_wings(hand: list[Card]) -> list[list[Card]]:
        """Generate all valid airplane with wings patterns."""
        results = []
        rank_groups = PlayGenerator._group_by_rank(hand)
        
        # Get consecutive triples (airplanes)
        valid_ranks = sorted([r for r, cards in rank_groups.items() if len(cards) >= 3])
        
        for length in range(2, len(valid_ranks) + 1):
            for i in range(len(valid_ranks) - length + 1):
                ranks = valid_ranks[i:i+length]
                
                if not PlayGenerator._is_consecutive(ranks):
                    continue
                
                # Get airplane cards
                airplane_cards = []
                for rank in ranks:
                    airplane_cards.extend(rank_groups[rank][:3])
                
                # Find available pairs for wings
                remaining_cards = [c for c in hand if c not in airplane_cards]
                remaining_groups = PlayGenerator._group_by_rank(remaining_cards)
                
                pair_ranks = [r for r, cards in remaining_groups.items() if len(cards) >= 2]
                
                # Need same number of pairs as triples
                if len(pair_ranks) >= length:
                    # Try combinations of pairs
                    for pair_combo in combinations(pair_ranks, length):
                        wing_cards = []
                        for rank in pair_combo:
                            wing_cards.extend(remaining_groups[rank][:2])
                        
                        combo = airplane_cards + wing_cards
                        pattern = PatternRecognizer.analyze_cards(combo)
                        if pattern and pattern.play_type == PlayType.AIRPLANE_WITH_WINGS:
                            results.append(combo)
        
        return results

    @staticmethod
    def _generate_bombs(hand: list[Card]) -> list[list[Card]]:
        """Generate all valid bombs from hand."""
        bombs = []
        rank_groups = PlayGenerator._group_by_rank(hand)
        
        for rank, cards in rank_groups.items():
            if len(cards) >= 4:
                # Generate bombs of all possible sizes (4, 5, 6, etc.)
                for size in range(4, len(cards) + 1):
                    for bomb in combinations(cards, size):
                        bomb_list = list(bomb)
                        pattern = PatternRecognizer.analyze_cards(bomb_list)
                        if pattern and pattern.play_type == PlayType.BOMB:
                            bombs.append(bomb_list)
        
        return bombs

    @staticmethod
    def _generate_tongzi(hand: list[Card]) -> list[list[Card]]:
        """Generate all valid tongzi patterns (3 same suit, same rank)."""
        tongzi = []
        
        # Group by (suit, rank)
        suit_rank_groups = {}
        for card in hand:
            key = (card.suit, card.rank)
            if key not in suit_rank_groups:
                suit_rank_groups[key] = []
            suit_rank_groups[key].append(card)
        
        # Find suit-rank combinations with 3+ cards
        for (suit, rank), cards in suit_rank_groups.items():
            if len(cards) >= 3:
                for triple in combinations(cards, 3):
                    triple_list = list(triple)
                    pattern = PatternRecognizer.analyze_cards(triple_list)
                    if pattern and pattern.play_type == PlayType.TONGZI:
                        tongzi.append(triple_list)
        
        return tongzi

    @staticmethod
    def _generate_dizha(hand: list[Card]) -> list[list[Card]]:
        """Generate all valid dizha patterns (2 of each suit for same rank)."""
        dizha = []
        rank_groups = PlayGenerator._group_by_rank(hand)
        
        for rank, cards in rank_groups.items():
            if len(cards) >= 8:
                # Group by suit
                suit_groups = {}
                for card in cards:
                    if card.suit not in suit_groups:
                        suit_groups[card.suit] = []
                    suit_groups[card.suit].append(card)
                
                # Check if all 4 suits have at least 2 cards
                if all(len(suit_groups.get(suit, [])) >= 2 for suit in [s for s in range(1, 5)]):
                    # Take 2 cards from each suit
                    dizha_cards = []
                    from ..models.card import Suit
                    for suit in Suit:
                        dizha_cards.extend(suit_groups[suit][:2])
                    
                    pattern = PatternRecognizer.analyze_cards(dizha_cards)
                    if pattern and pattern.play_type == PlayType.DIZHA:
                        dizha.append(dizha_cards)
        
        return dizha

    @staticmethod
    def _group_by_rank(cards: list[Card]) -> dict[Rank, list[Card]]:
        """Group cards by rank."""
        groups = {}
        for card in cards:
            if card.rank not in groups:
                groups[card.rank] = []
            groups[card.rank].append(card)
        return groups

    @staticmethod
    def _is_consecutive(ranks: list[Rank]) -> bool:
        """Check if ranks are consecutive."""
        if len(ranks) <= 1:
            return True

        values = [r.value for r in ranks]
        for i in range(1, len(values)):
            if values[i] != values[i-1] + 1:
                return False
        return True

    # ========== Helper methods for generate_beating_plays_with_same_type_or_trump ==========

    @staticmethod
    def _generate_higher_singles(hand: list[Card], current_pattern: PlayPattern) -> list[list[Card]]:
        """Generate single cards higher than current single."""
        higher_singles = []
        current_rank = current_pattern.primary_rank

        for card in hand:
            if card.rank.value > current_rank.value:
                higher_singles.append([card])

        return higher_singles

    @staticmethod
    def _generate_higher_pairs(hand: list[Card], current_pattern: PlayPattern) -> list[list[Card]]:
        """Generate pairs higher than current pair."""
        all_pairs = PlayGenerator._generate_pairs(hand)
        current_rank = current_pattern.primary_rank

        higher_pairs = []
        for pair in all_pairs:
            pair_pattern = PatternRecognizer.analyze_cards(pair)
            if pair_pattern and pair_pattern.primary_rank.value > current_rank.value:
                higher_pairs.append(pair)

        return higher_pairs

    @staticmethod
    def _generate_higher_consecutive_pairs(
        hand: list[Card], current_pattern: PlayPattern
    ) -> list[list[Card]]:
        """Generate consecutive pairs higher than current consecutive pairs."""
        all_consecutive = PlayGenerator._generate_consecutive_pairs(hand)
        current_rank = current_pattern.primary_rank
        current_count = current_pattern.card_count // 2  # Number of pairs

        higher_consecutive = []
        for consecutive in all_consecutive:
            pattern = PatternRecognizer.analyze_cards(consecutive)
            if pattern:
                # Must have same number of pairs and higher starting rank
                if (len(consecutive) == current_pattern.card_count and
                    pattern.primary_rank.value > current_rank.value):
                    higher_consecutive.append(consecutive)

        return higher_consecutive

    @staticmethod
    def _generate_higher_triples(hand: list[Card], current_pattern: PlayPattern) -> list[list[Card]]:
        """Generate triples higher than current triple."""
        all_triples = PlayGenerator._generate_triples(hand)
        current_rank = current_pattern.primary_rank

        higher_triples = []
        for triple in all_triples:
            triple_pattern = PatternRecognizer.analyze_cards(triple)
            if triple_pattern and triple_pattern.primary_rank.value > current_rank.value:
                higher_triples.append(triple)

        return higher_triples

    @staticmethod
    def _generate_higher_triple_with_two(
        hand: list[Card], current_pattern: PlayPattern
    ) -> list[list[Card]]:
        """Generate triple-with-two higher than current triple-with-two."""
        all_triple_with_two = PlayGenerator._generate_triple_with_two(hand)
        current_rank = current_pattern.primary_rank

        higher_combos = []
        for combo in all_triple_with_two:
            pattern = PatternRecognizer.analyze_cards(combo)
            if pattern and pattern.primary_rank.value > current_rank.value:
                higher_combos.append(combo)

        return higher_combos

    @staticmethod
    def _generate_higher_airplanes(
        hand: list[Card], current_pattern: PlayPattern
    ) -> list[list[Card]]:
        """Generate airplanes higher than current airplane."""
        all_airplanes = PlayGenerator._generate_airplanes(hand)
        current_rank = current_pattern.primary_rank
        current_count = current_pattern.card_count // 3  # Number of triples

        higher_airplanes = []
        for airplane in all_airplanes:
            pattern = PatternRecognizer.analyze_cards(airplane)
            if pattern:
                # Must have same number of triples and higher starting rank
                if (len(airplane) == current_pattern.card_count and
                    pattern.primary_rank.value > current_rank.value):
                    higher_airplanes.append(airplane)

        return higher_airplanes

    @staticmethod
    def _generate_higher_airplane_with_wings(
        hand: list[Card], current_pattern: PlayPattern
    ) -> list[list[Card]]:
        """Generate airplane-with-wings higher than current airplane-with-wings."""
        all_airplane_wings = PlayGenerator._generate_airplane_with_wings(hand)
        current_rank = current_pattern.primary_rank

        higher_combos = []
        for combo in all_airplane_wings:
            pattern = PatternRecognizer.analyze_cards(combo)
            if pattern:
                # Must have same card count and higher starting rank
                if (len(combo) == current_pattern.card_count and
                    pattern.primary_rank.value > current_rank.value):
                    higher_combos.append(combo)

        return higher_combos

    @staticmethod
    def _generate_higher_bombs(hand: list[Card], current_pattern: PlayPattern) -> list[list[Card]]:
        """Generate bombs higher than current bomb."""
        all_bombs = PlayGenerator._generate_bombs(hand)
        current_rank = current_pattern.primary_rank
        current_size = current_pattern.card_count

        higher_bombs = []
        for bomb in all_bombs:
            bomb_pattern = PatternRecognizer.analyze_cards(bomb)
            if bomb_pattern:
                # Higher rank with same size, or more cards with any rank
                if (len(bomb) > current_size or
                    (len(bomb) == current_size and bomb_pattern.primary_rank.value > current_rank.value)):
                    higher_bombs.append(bomb)

        return higher_bombs

    @staticmethod
    def _generate_higher_tongzi(hand: list[Card], current_pattern: PlayPattern) -> list[list[Card]]:
        """Generate tongzi higher than current tongzi."""
        all_tongzi = PlayGenerator._generate_tongzi(hand)

        higher_tongzi = []
        for tongzi in all_tongzi:
            # Validate using can_beat_play (tongzi has complex suit/rank comparison)
            if PlayValidator.can_beat_play(tongzi, current_pattern):
                higher_tongzi.append(tongzi)

        return higher_tongzi

    @staticmethod
    def _generate_higher_dizha(hand: list[Card], current_pattern: PlayPattern) -> list[list[Card]]:
        """Generate dizha higher than current dizha."""
        all_dizha = PlayGenerator._generate_dizha(hand)
        current_rank = current_pattern.primary_rank

        higher_dizha = []
        for dizha in all_dizha:
            dizha_pattern = PatternRecognizer.analyze_cards(dizha)
            if dizha_pattern and dizha_pattern.primary_rank.value > current_rank.value:
                higher_dizha.append(dizha)

        return higher_dizha
