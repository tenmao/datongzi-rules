"""Hand evaluation for AI assistance - Zero Dependency Version."""

from collections import Counter
import logging

from ..models.card import Card, Rank
from ..patterns.recognizer import PlayType
from .play_generator import PlayGenerator

logger = logging.getLogger(__name__)


class HandEvaluator:
    """
    Evaluate the strength of a hand of cards.
    
    This provides a comprehensive evaluation score considering:
    - Special cards (bombs, tongzi, dizha)
    - Number of playable combinations
    - Card distribution
    - Remaining card count
    """

    @staticmethod
    def evaluate_hand(hand: list[Card]) -> float:
        """
        Evaluate hand strength and return a score.
        
        Higher score = stronger hand
        
        Args:
            hand: List of cards to evaluate
            
        Returns:
            Comprehensive strength score (0-1000+)
        """
        if not hand:
            return 0.0
        
        score = 0.0
        
        # 1. Card count penalty (fewer cards = better)
        score += HandEvaluator._evaluate_card_count(hand)
        
        # 2. Special patterns bonus (bombs, tongzi, dizha)
        score += HandEvaluator._evaluate_special_patterns(hand)
        
        # 3. High cards bonus
        score += HandEvaluator._evaluate_high_cards(hand)
        
        # 4. Playability (how many valid plays can be made)
        score += HandEvaluator._evaluate_playability(hand)
        
        # 5. Distribution (balanced ranks = better)
        score += HandEvaluator._evaluate_distribution(hand)
        
        logger.debug(f"Hand evaluation: cards={len(hand)}, score={score:.2f}")
        
        return score

    @staticmethod
    def evaluate_play_strength(cards: list[Card]) -> float:
        """
        Evaluate the strength of a specific play.
        
        Args:
            cards: Cards in the play
            
        Returns:
            Strength score for this play
        """
        from ..patterns.recognizer import PatternRecognizer
        
        pattern = PatternRecognizer.analyze_cards(cards)
        if not pattern:
            return 0.0
        
        # Base score from pattern type
        type_scores = {
            PlayType.SINGLE: 1,
            PlayType.PAIR: 5,
            PlayType.CONSECUTIVE_PAIRS: 15,
            PlayType.TRIPLE: 10,
            PlayType.TRIPLE_WITH_TWO: 20,
            PlayType.AIRPLANE: 30,
            PlayType.AIRPLANE_WITH_WINGS: 50,
            PlayType.BOMB: 100,
            PlayType.TONGZI: 200,
            PlayType.DIZHA: 500,
        }
        
        base_score = type_scores.get(pattern.play_type, 0)
        
        # Rank bonus (higher ranks = better)
        rank_bonus = pattern.primary_rank.value * 2
        
        # Card count bonus for bombs
        if pattern.play_type == PlayType.BOMB:
            rank_bonus += (pattern.card_count - 4) * 20
        
        return base_score + rank_bonus

    @staticmethod
    def _evaluate_card_count(hand: list[Card]) -> float:
        """Evaluate based on card count (fewer = better)."""
        # Maximum penalty at 41 cards (full hand)
        # No penalty at 0 cards
        max_cards = 41
        return max(0, (max_cards - len(hand)) * 2.0)

    @staticmethod
    def _evaluate_special_patterns(hand: list[Card]) -> float:
        """Evaluate special patterns (bombs, tongzi, dizha)."""
        score = 0.0
        
        # Count bombs
        bombs = PlayGenerator._generate_bombs(hand)
        for bomb_cards in bombs:
            # Larger bombs worth more
            score += 100 * (len(bomb_cards) - 3)
        
        # Count tongzi
        tongzi = PlayGenerator._generate_tongzi(hand)
        score += len(tongzi) * 200
        
        # Count dizha
        dizha = PlayGenerator._generate_dizha(hand)
        score += len(dizha) * 500
        
        return score

    @staticmethod
    def _evaluate_high_cards(hand: list[Card]) -> float:
        """Evaluate high cards (2, A, K)."""
        score = 0.0
        
        for card in hand:
            if card.rank == Rank.TWO:
                score += 15
            elif card.rank == Rank.ACE:
                score += 12
            elif card.rank == Rank.KING:
                score += 10
            elif card.rank == Rank.QUEEN:
                score += 8
            elif card.rank == Rank.JACK:
                score += 6
        
        return score

    @staticmethod
    def _evaluate_playability(hand: list[Card]) -> float:
        """Evaluate how many valid plays can be made."""
        all_plays = PlayGenerator.generate_all_plays(hand)
        
        # More plays = better (up to a point)
        # Use logarithmic scale to avoid over-weighting
        import math
        if len(all_plays) > 0:
            return min(100, math.log(len(all_plays) + 1) * 15)
        return 0.0

    @staticmethod
    def _evaluate_distribution(hand: list[Card]) -> float:
        """Evaluate card distribution (balanced = better)."""
        rank_counts = Counter(card.rank for card in hand)
        
        score = 0.0
        
        # Bonus for complete sets (pairs, triples, quads)
        for count in rank_counts.values():
            if count == 2:
                score += 5  # Pair
            elif count == 3:
                score += 10  # Triple
            elif count >= 4:
                score += 20  # Bomb potential
        
        # Penalty for singles (harder to play out)
        singles = sum(1 for count in rank_counts.values() if count == 1)
        score -= singles * 2
        
        return score

    @staticmethod
    def suggest_best_play(
        hand: list[Card], current_pattern: "PlayPattern | None" = None
    ) -> list[Card] | None:
        """
        Suggest the best play to make from hand.
        
        Args:
            hand: Cards in hand
            current_pattern: Current pattern to beat (None if starting)
            
        Returns:
            Best play to make, or None if cannot play
        """
        if current_pattern is None:
            # Starting round - suggest weakest valid play
            all_plays = PlayGenerator.generate_all_plays(hand)
        else:
            # Must beat current pattern
            all_plays = PlayGenerator.generate_valid_responses(hand, current_pattern)
        
        if not all_plays:
            return None
        
        # Evaluate each play
        play_scores = []
        for play in all_plays:
            # Prefer plays that empty hand or create good remaining hand
            remaining_hand = [c for c in hand if c not in play]
            remaining_score = HandEvaluator.evaluate_hand(remaining_hand)
            
            # Balance: good play + good remaining hand
            play_strength = HandEvaluator.evaluate_play_strength(play)
            
            # Prefer plays that leave better remaining hand
            total_score = remaining_score - play_strength * 0.1
            
            play_scores.append((total_score, play))
        
        # Sort by score (higher = better remaining hand)
        play_scores.sort(key=lambda x: x[0], reverse=True)
        
        best_play = play_scores[0][1]
        
        logger.debug(
            f"Suggested best play: {len(best_play)} cards, "
            f"score={play_scores[0][0]:.2f}"
        )
        
        return best_play


class HandAnalyzer:
    """Analyze hand composition and provide strategic insights."""

    @staticmethod
    def analyze_hand(hand: list[Card]) -> dict:
        """
        Provide detailed analysis of hand composition.
        
        Args:
            hand: Cards to analyze
            
        Returns:
            Dictionary with analysis results
        """
        rank_counts = Counter(card.rank for card in hand)
        
        analysis = {
            "total_cards": len(hand),
            "singles": sum(1 for count in rank_counts.values() if count == 1),
            "pairs": sum(1 for count in rank_counts.values() if count == 2),
            "triples": sum(1 for count in rank_counts.values() if count == 3),
            "quads_plus": sum(1 for count in rank_counts.values() if count >= 4),
            "bombs": len(PlayGenerator._generate_bombs(hand)),
            "tongzi": len(PlayGenerator._generate_tongzi(hand)),
            "dizha": len(PlayGenerator._generate_dizha(hand)),
            "total_plays": len(PlayGenerator.generate_all_plays(hand)),
            "strength_score": HandEvaluator.evaluate_hand(hand),
        }
        
        logger.info(
            f"Hand analysis: cards={analysis['total_cards']}, "
            f"bombs={analysis['bombs']}, strength={analysis['strength_score']:.2f}"
        )
        
        return analysis
