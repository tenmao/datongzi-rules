"""Pattern suggestion for CV error correction - Zero Dependency Version."""

from collections import Counter
import logging
from typing import Tuple

from ..models.card import Card, Rank, Suit
from ..patterns.recognizer import PatternRecognizer, PlayType

logger = logging.getLogger(__name__)


class PatternSuggester:
    """
    Suggest corrections for computer vision recognition errors.
    
    Given a set of cards that may have CV errors, this class uses game rule
    constraints to suggest the most likely correct interpretation.
    """

    @staticmethod
    def suggest_correction(
        detected_cards: list[Card], 
        expected_count: int | None = None,
        must_be_valid_pattern: bool = True
    ) -> Tuple[list[Card], float]:
        """
        Suggest corrected card list based on rule constraints.
        
        Args:
            detected_cards: Cards detected by CV (may have errors)
            expected_count: Expected number of cards (None if unknown)
            must_be_valid_pattern: If True, result must be valid pattern
            
        Returns:
            Tuple of (corrected_cards, confidence_score)
            confidence_score: 0-1, where 1 = high confidence
        """
        if not detected_cards:
            return ([], 0.0)
        
        # Check if already valid
        pattern = PatternRecognizer.analyze_cards(detected_cards)
        if pattern is not None:
            logger.debug("Detected cards already form valid pattern")
            return (detected_cards, 1.0)
        
        # Try corrections
        corrections = []
        
        # 1. Try removing duplicates
        corrected, conf = PatternSuggester._try_remove_duplicates(detected_cards)
        if corrected:
            corrections.append((corrected, conf, "remove_duplicates"))
        
        # 2. Try fixing common rank confusions
        corrected, conf = PatternSuggester._try_fix_rank_confusion(detected_cards)
        if corrected:
            corrections.append((corrected, conf, "fix_rank"))
        
        # 3. Try fixing common suit confusions
        corrected, conf = PatternSuggester._try_fix_suit_confusion(detected_cards)
        if corrected:
            corrections.append((corrected, conf, "fix_suit"))
        
        # 4. Try minimal edits to form valid pattern
        corrected, conf = PatternSuggester._try_minimal_edits(detected_cards)
        if corrected:
            corrections.append((corrected, conf, "minimal_edit"))
        
        # Filter by expected count if provided
        if expected_count is not None:
            corrections = [
                (cards, conf, method) 
                for cards, conf, method in corrections 
                if len(cards) == expected_count
            ]
        
        # Filter by valid pattern requirement
        if must_be_valid_pattern:
            corrections = [
                (cards, conf, method)
                for cards, conf, method in corrections
                if PatternRecognizer.analyze_cards(cards) is not None
            ]
        
        if not corrections:
            logger.warning("Could not find valid correction")
            return (detected_cards, 0.0)
        
        # Return best correction (highest confidence)
        corrections.sort(key=lambda x: x[1], reverse=True)
        best_cards, best_conf, best_method = corrections[0]
        
        logger.info(
            f"Suggested correction: method={best_method}, "
            f"confidence={best_conf:.2f}, cards={len(best_cards)}"
        )
        
        return (best_cards, best_conf)

    @staticmethod
    def _try_remove_duplicates(cards: list[Card]) -> Tuple[list[Card] | None, float]:
        """Try removing duplicate cards (CV double-detection)."""
        # Count card occurrences
        card_counts = Counter(cards)
        
        # Check for excessive duplicates (more than possible in 3 decks)
        has_duplicates = any(count > 3 for count in card_counts.values())
        
        if not has_duplicates:
            return (None, 0.0)
        
        # Remove excess duplicates (keep max 3)
        corrected = []
        for card, count in card_counts.items():
            corrected.extend([card] * min(count, 3))
        
        # Check if valid pattern
        pattern = PatternRecognizer.analyze_cards(corrected)
        if pattern:
            return (corrected, 0.8)
        
        return (corrected, 0.4)

    @staticmethod
    def _try_fix_rank_confusion(cards: list[Card]) -> Tuple[list[Card] | None, float]:
        """Try fixing common rank confusion (e.g., 6 vs 9, 5 vs S)."""
        # Common confusions: 6<->9, 5<->S(Spade), Q<->9, etc.
        rank_confusions = [
            (Rank.SIX, Rank.NINE),
            (Rank.QUEEN, Rank.NINE),
            (Rank.FIVE, Rank.SIX),
            (Rank.TEN, Rank.JACK),
            (Rank.KING, Rank.ACE),
        ]
        
        for rank1, rank2 in rank_confusions:
            # Try swapping rank1 -> rank2
            corrected = [
                Card(c.suit, rank2 if c.rank == rank1 else c.rank)
                for c in cards
            ]
            pattern = PatternRecognizer.analyze_cards(corrected)
            if pattern:
                return (corrected, 0.7)
            
            # Try swapping rank2 -> rank1
            corrected = [
                Card(c.suit, rank1 if c.rank == rank2 else c.rank)
                for c in cards
            ]
            pattern = PatternRecognizer.analyze_cards(corrected)
            if pattern:
                return (corrected, 0.7)
        
        return (None, 0.0)

    @staticmethod
    def _try_fix_suit_confusion(cards: list[Card]) -> Tuple[list[Card] | None, float]:
        """Try fixing common suit confusion (e.g., hearts vs diamonds)."""
        # Common confusions: Hearts<->Diamonds (red), Spades<->Clubs (black)
        suit_confusions = [
            (Suit.HEARTS, Suit.DIAMONDS),
            (Suit.SPADES, Suit.CLUBS),
        ]
        
        for suit1, suit2 in suit_confusions:
            # Try swapping suit1 -> suit2
            corrected = [
                Card(suit2 if c.suit == suit1 else c.suit, c.rank)
                for c in cards
            ]
            pattern = PatternRecognizer.analyze_cards(corrected)
            if pattern:
                return (corrected, 0.6)
            
            # Try swapping suit2 -> suit1
            corrected = [
                Card(suit1 if c.suit == suit2 else c.suit, c.rank)
                for c in cards
            ]
            pattern = PatternRecognizer.analyze_cards(corrected)
            if pattern:
                return (corrected, 0.6)
        
        return (None, 0.0)

    @staticmethod
    def _try_minimal_edits(cards: list[Card]) -> Tuple[list[Card] | None, float]:
        """Try minimal edits to form a valid pattern."""
        # Try removing one card at a time
        for i in range(len(cards)):
            subset = cards[:i] + cards[i+1:]
            pattern = PatternRecognizer.analyze_cards(subset)
            if pattern:
                return (subset, 0.5)
        
        # Try changing one card's rank
        for i in range(len(cards)):
            for new_rank in Rank:
                corrected = cards.copy()
                corrected[i] = Card(cards[i].suit, new_rank)
                pattern = PatternRecognizer.analyze_cards(corrected)
                if pattern:
                    return (corrected, 0.4)
        
        # Try changing one card's suit
        for i in range(len(cards)):
            for new_suit in Suit:
                corrected = cards.copy()
                corrected[i] = Card(new_suit, cards[i].rank)
                pattern = PatternRecognizer.analyze_cards(corrected)
                if pattern:
                    return (corrected, 0.4)
        
        return (None, 0.0)

    @staticmethod
    def validate_hand(hand: list[Card], total_deck_cards: int = 132) -> Tuple[bool, list[str]]:
        """
        Validate that a hand is legal given deck constraints.
        
        Args:
            hand: Cards in hand to validate
            total_deck_cards: Total cards in deck (default: 3 decks = 132)
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check card counts (max 3 of each card in 3-deck game)
        max_per_card = total_deck_cards // 44  # 44 unique cards per deck
        card_counts = Counter(hand)
        
        for card, count in card_counts.items():
            if count > max_per_card:
                errors.append(
                    f"Card {card} appears {count} times (max {max_per_card})"
                )
        
        # Check total cards
        if len(hand) > total_deck_cards:
            errors.append(
                f"Hand has {len(hand)} cards (max {total_deck_cards})"
            )
        
        is_valid = len(errors) == 0
        
        if not is_valid:
            logger.warning(f"Hand validation failed: {errors}")
        
        return (is_valid, errors)

    @staticmethod
    def suggest_pattern_type(cards: list[Card]) -> PlayType | None:
        """
        Suggest the most likely pattern type for given cards.
        
        This can help CV systems by providing pattern hints even if
        the exact cards are not perfectly recognized.
        
        Args:
            cards: Cards to analyze (may be invalid pattern)
            
        Returns:
            Most likely PlayType, or None if unclear
        """
        if not cards:
            return None
        
        # First check if already valid
        pattern = PatternRecognizer.analyze_cards(cards)
        if pattern:
            return pattern.play_type
        
        # Heuristics based on card count
        card_count = len(cards)
        rank_counts = Counter(c.rank for c in cards)
        suit_rank_counts = Counter((c.suit, c.rank) for c in cards)
        
        # Single
        if card_count == 1:
            return PlayType.SINGLE
        
        # Pair
        if card_count == 2 and len(rank_counts) == 1:
            return PlayType.PAIR
        
        # Triple
        if card_count == 3:
            if len(rank_counts) == 1:
                # Could be triple or tongzi
                if len(suit_rank_counts) == 1:
                    return PlayType.TONGZI
                return PlayType.TRIPLE
        
        # Triple with two
        if card_count == 5 and len(rank_counts) == 2:
            if 3 in rank_counts.values() and 2 in rank_counts.values():
                return PlayType.TRIPLE_WITH_TWO
        
        # Bomb/Tongzi
        if card_count == 4 and len(rank_counts) == 1:
            return PlayType.BOMB
        
        # Consecutive pairs
        if card_count >= 4 and card_count % 2 == 0:
            if all(count == 2 for count in rank_counts.values()):
                return PlayType.CONSECUTIVE_PAIRS
        
        # Airplane
        if card_count >= 6 and card_count % 3 == 0:
            if all(count == 3 for count in rank_counts.values()):
                return PlayType.AIRPLANE
        
        # Dizha
        if card_count == 8 and len(rank_counts) == 1:
            return PlayType.DIZHA
        
        # Airplane with wings
        if card_count >= 10:
            triple_count = sum(1 for count in rank_counts.values() if count == 3)
            pair_count = sum(1 for count in rank_counts.values() if count == 2)
            if triple_count >= 2 and pair_count >= triple_count:
                return PlayType.AIRPLANE_WITH_WINGS
        
        logger.debug(f"Could not determine pattern type for {card_count} cards")
        return None
