"""Play generation for AI assistance - Zero Dependency Version."""

from collections import Counter
from itertools import combinations
import logging

from ..models.card import Card, Rank
from ..patterns.recognizer import PatternRecognizer, PlayPattern, PlayType, PlayValidator

logger = logging.getLogger(__name__)


class PlayGenerator:
    """
    Generate all valid plays from a hand of cards.
    
    This is a pure utility class for AI assistance. It does not maintain state
    and can be used by AI players, auto-play features, or hint systems.
    """

    @staticmethod
    def generate_all_plays(hand: list[Card]) -> list[list[Card]]:
        """
        Generate all possible valid plays from hand.
        
        Args:
            hand: List of cards in hand
            
        Returns:
            List of all valid play combinations (each is a list of cards)
        """
        if not hand:
            return []
        
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
        
        logger.debug(f"Generated {len(all_plays)} total plays from {len(hand)} cards")
        
        return all_plays

    @staticmethod
    def generate_valid_responses(
        hand: list[Card], current_pattern: PlayPattern
    ) -> list[list[Card]]:
        """
        Generate all valid plays that can beat the current pattern.
        
        Args:
            hand: List of cards in hand
            current_pattern: Current play pattern to beat
            
        Returns:
            List of valid response plays
        """
        all_plays = PlayGenerator.generate_all_plays(hand)
        
        valid_responses = [
            play for play in all_plays
            if PlayValidator.can_beat_play(play, current_pattern)
        ]
        
        logger.debug(
            f"Generated {len(valid_responses)} valid responses to "
            f"{current_pattern.play_type.name}"
        )
        
        return valid_responses

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
