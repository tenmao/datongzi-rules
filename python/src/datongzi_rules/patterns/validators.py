"""Pattern formation validators for Da Tong Zi game.

This module provides validators to check if a hand can form specific patterns.
Used primarily for the must-beat rule (有牌必打) implementation.
"""

from collections import Counter
from typing import Any

from ..models.card import Card


class PlayFormationValidator:
    """Validates if a hand can form specific play patterns."""

    @staticmethod
    def can_form_consecutive_pairs(
        hand: list[Card], num_pairs: int, min_rank: Any
    ) -> bool:
        """Check if player can form N consecutive pairs with highest rank higher than min_rank.

        Args:
            hand: Player's hand
            num_pairs: Number of consecutive pairs needed
            min_rank: Minimum rank to beat (primary_rank of current play)

        Returns:
            True if player can form the pattern
        """
        rank_counts = Counter(card.rank for card in hand)

        # Filter ranks that have at least 2 cards (can form pairs)
        pair_ranks = sorted(
            [rank for rank, count in rank_counts.items() if count >= 2],
            key=lambda r: r.value,
        )

        # Find consecutive sequences of required length
        for i in range(len(pair_ranks) - num_pairs + 1):
            # Check if we can form consecutive pairs starting from pair_ranks[i]
            is_consecutive = True
            for j in range(num_pairs - 1):
                if pair_ranks[i + j].value + 1 != pair_ranks[i + j + 1].value:
                    is_consecutive = False
                    break

            if is_consecutive:
                # For consecutive pairs, primary_rank is the HIGHEST rank
                highest_rank = pair_ranks[i + num_pairs - 1]
                if highest_rank.value > min_rank.value:
                    return True

        return False

    @staticmethod
    def can_form_airplane(hand: list[Card], num_triples: int, min_rank: Any) -> bool:
        """Check if player can form N consecutive triples with highest rank higher than min_rank.

        Args:
            hand: Player's hand
            num_triples: Number of consecutive triples needed
            min_rank: Minimum rank to beat (primary_rank of current play)

        Returns:
            True if player can form the pattern
        """
        rank_counts = Counter(card.rank for card in hand)

        # Filter ranks that have at least 3 cards (can form triples)
        triple_ranks = sorted(
            [rank for rank, count in rank_counts.items() if count >= 3],
            key=lambda r: r.value,
        )

        # Find consecutive sequences of required length
        for i in range(len(triple_ranks) - num_triples + 1):
            # Check if we can form consecutive triples starting from triple_ranks[i]
            is_consecutive = True
            for j in range(num_triples - 1):
                if triple_ranks[i + j].value + 1 != triple_ranks[i + j + 1].value:
                    is_consecutive = False
                    break

            if is_consecutive:
                # For airplane, primary_rank is the HIGHEST rank
                highest_rank = triple_ranks[i + num_triples - 1]
                if highest_rank.value > min_rank.value:
                    return True

        return False

    @staticmethod
    def can_form_airplane_with_wings(
        hand: list[Card], num_triples: int, min_rank: Any
    ) -> bool:
        """Check if player can form airplane_with_wings (N consecutive triples + N pairs).

        Args:
            hand: Player's hand
            num_triples: Number of consecutive triples needed
            min_rank: Minimum rank to beat (primary_rank of current play)

        Returns:
            True if player can form the pattern
        """
        rank_counts = Counter(card.rank for card in hand)

        # Filter ranks that have at least 3 cards (can form triples)
        triple_ranks = sorted(
            [rank for rank, count in rank_counts.items() if count >= 3],
            key=lambda r: r.value,
        )

        # Find consecutive sequences of required length
        for i in range(len(triple_ranks) - num_triples + 1):
            # Check if we can form consecutive triples starting from triple_ranks[i]
            is_consecutive = True
            for j in range(num_triples - 1):
                if triple_ranks[i + j].value + 1 != triple_ranks[i + j + 1].value:
                    is_consecutive = False
                    break

            if is_consecutive:
                # For airplane_with_wings, primary_rank is the HIGHEST rank of the airplane
                highest_rank = triple_ranks[i + num_triples - 1]
                if highest_rank.value > min_rank.value:
                    # Found valid airplane, now check if we have enough pairs for wings
                    airplane_ranks = set(triple_ranks[i : i + num_triples])

                    # Count available pairs (can be from airplane ranks if we have extras)
                    available_pairs = 0
                    for rank, count in rank_counts.items():
                        if rank in airplane_ranks:
                            # For ranks used in airplane, check for extra cards
                            remaining = count - 3
                            if remaining >= 2:
                                available_pairs += 1
                        else:
                            # For other ranks, check if we have pairs
                            if count >= 2:
                                available_pairs += 1

                    if available_pairs >= num_triples:
                        return True

        return False

    @staticmethod
    def can_form_triple_with_two(hand: list[Card], min_rank: Any) -> bool:
        """Check if player can form triple_with_two (triple + pair) with triple rank > min_rank.

        Args:
            hand: Player's hand
            min_rank: Minimum rank to beat (primary_rank of current play)

        Returns:
            True if player can form the pattern
        """
        rank_counts = Counter(card.rank for card in hand)

        # Find triples with rank > min_rank
        valid_triples = [
            rank
            for rank, count in rank_counts.items()
            if count >= 3 and rank.value > min_rank.value
        ]

        if not valid_triples:
            return False

        # Find pairs (can be any rank, including the triple rank if we have extras)
        for triple_rank in valid_triples:
            # Check if we have at least one pair (different from the triple, or extra cards of same rank)
            for rank, count in rank_counts.items():
                if rank == triple_rank:
                    # Same rank: need at least 5 cards total (3 for triple + 2 for pair)
                    if count >= 5:
                        return True
                else:
                    # Different rank: need at least 2 cards
                    if count >= 2:
                        return True

        return False
