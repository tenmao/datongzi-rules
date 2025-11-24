"""Pattern finders for Da Tong Zi game.

This module provides utilities to find all valid card combinations in a player's hand.
All methods are extracted from AI logic to be reusable across different implementations.
"""

from collections import Counter
from itertools import combinations

from ..models.card import Card, Rank, Suit


class PatternFinder:
    """Finds valid card patterns in a hand."""

    @staticmethod
    def find_pairs(hand: list[Card]) -> list[Card]:
        """Find all pairs in hand, sorted by rank.

        Args:
            hand: List of cards to search

        Returns:
            List of cards forming pairs, sorted by rank
        """
        rank_counts: dict[Rank, list[Card]] = {}
        for card in hand:
            if card.rank not in rank_counts:
                rank_counts[card.rank] = []
            rank_counts[card.rank].append(card)

        pairs = []
        for _rank, cards in rank_counts.items():
            if len(cards) >= 2:
                # Sort by rank and take pairs
                cards.sort(key=lambda c: c.rank.value)
                for i in range(0, len(cards) - 1, 2):
                    pairs.extend(cards[i : i + 2])

        return sorted(pairs, key=lambda c: c.rank.value)

    @staticmethod
    def find_triples(hand: list[Card]) -> list[Card]:
        """Find all triples in hand, sorted by rank.

        Args:
            hand: List of cards to search

        Returns:
            List of cards forming triples, sorted by rank
        """
        rank_counts: dict[Rank, list[Card]] = {}
        for card in hand:
            if card.rank not in rank_counts:
                rank_counts[card.rank] = []
            rank_counts[card.rank].append(card)

        triples = []
        for _rank, cards in rank_counts.items():
            if len(cards) >= 3:
                cards.sort(key=lambda c: c.rank.value)
                for i in range(0, len(cards) - 2, 3):
                    triples.extend(cards[i : i + 3])

        return sorted(triples, key=lambda c: c.rank.value)

    @staticmethod
    def find_bombs(hand: list[Card]) -> list[list[Card]]:
        """Find all bombs in hand.

        Returns all possible bomb combinations (4+ cards of same rank).
        For N cards of same rank, returns bombs of sizes 4, 5, ..., N.

        Args:
            hand: List of cards to search

        Returns:
            List of bomb combinations
        """
        rank_counts: dict[Rank, list[Card]] = {}
        for card in hand:
            if card.rank not in rank_counts:
                rank_counts[card.rank] = []
            rank_counts[card.rank].append(card)

        bombs = []
        for _rank, cards in rank_counts.items():
            if len(cards) >= 4:
                cards.sort(key=lambda c: c.rank.value)
                # Generate all possible bomb sizes: 4, 5, ..., len(cards)
                for bomb_size in range(4, len(cards) + 1):
                    bombs.append(cards[:bomb_size])

        return bombs

    @staticmethod
    def find_consecutive_pairs(hand: list[Card]) -> list[Card]:
        """Find consecutive pairs in hand.

        Returns the cards that form the longest consecutive pair sequence.

        Args:
            hand: List of cards to search

        Returns:
            List of cards forming consecutive pairs (empty if none found)
        """
        rank_counts: dict[Rank, list[Card]] = {}

        # Group cards by rank
        for card in hand:
            if card.rank not in rank_counts:
                rank_counts[card.rank] = []
            rank_counts[card.rank].append(card)

        # Filter ranks that have at least 2 cards (pairs)
        pairs_by_rank: dict[Rank, list[Card]] = {}
        for rank, cards in rank_counts.items():
            if len(cards) >= 2:
                pairs_by_rank[rank] = cards[:2]

        if len(pairs_by_rank) < 2:
            return []

        # Sort ranks by value
        sorted_ranks = sorted(pairs_by_rank.keys(), key=lambda r: r.value)

        # Find the longest consecutive sequence
        best_sequence: list[Card] = []
        current_sequence: list[Card] = []

        for i, rank in enumerate(sorted_ranks):
            if not current_sequence:
                # Start new sequence
                current_sequence = list(pairs_by_rank[rank])
            else:
                # Check if this rank is consecutive with the last rank
                last_rank = sorted_ranks[i - 1]
                if rank.value == last_rank.value + 1:
                    # Consecutive - extend current sequence
                    current_sequence.extend(pairs_by_rank[rank])
                else:
                    # Not consecutive - save current sequence if it's valid
                    if len(current_sequence) >= 4:  # At least 2 pairs
                        if len(current_sequence) > len(best_sequence):
                            best_sequence = current_sequence
                    # Start new sequence
                    current_sequence = list(pairs_by_rank[rank])

        # Check final sequence
        if len(current_sequence) >= 4:
            if len(current_sequence) > len(best_sequence):
                best_sequence = current_sequence

        return best_sequence

    @staticmethod
    def find_all_consecutive_pairs(
        hand: list[Card], num_pairs: int
    ) -> list[list[Card]]:
        """Find all consecutive pairs combinations of given length.

        Args:
            hand: Player's hand
            num_pairs: Number of consecutive pairs needed (e.g., 2 means 4 cards)

        Returns:
            List of all possible consecutive pair combinations
        """
        if num_pairs < 2:
            return []

        rank_counts: dict[Rank, list[Card]] = {}

        # Group cards by rank
        for card in hand:
            if card.rank not in rank_counts:
                rank_counts[card.rank] = []
            rank_counts[card.rank].append(card)

        # Filter ranks that have at least 2 cards (pairs)
        pairs_by_rank: dict[Rank, list[Card]] = {}
        for rank, cards in rank_counts.items():
            if len(cards) >= 2:
                pairs_by_rank[rank] = cards[:2]

        if len(pairs_by_rank) < num_pairs:
            return []

        # Sort ranks by value
        sorted_ranks = sorted(pairs_by_rank.keys(), key=lambda r: r.value)

        # Find all consecutive sequences of required length
        all_combinations = []

        for i in range(len(sorted_ranks) - num_pairs + 1):
            # Check if we can form a consecutive sequence starting from sorted_ranks[i]
            is_consecutive = True
            for j in range(num_pairs - 1):
                if sorted_ranks[i + j].value + 1 != sorted_ranks[i + j + 1].value:
                    is_consecutive = False
                    break

            if is_consecutive:
                # Build the card combination
                combination = []
                for j in range(num_pairs):
                    combination.extend(pairs_by_rank[sorted_ranks[i + j]])
                all_combinations.append(combination)

        return all_combinations

    @staticmethod
    def find_all_tongzi(hand: list[Card]) -> list[list[Card]]:
        """Find all tongzi (3 of same rank and same suit) in hand.

        Returns a list of all possible tongzi combinations.

        Args:
            hand: List of cards to search

        Returns:
            List of tongzi combinations
        """
        rank_counts: dict[Rank, list[Card]] = {}

        for card in hand:
            if card.rank not in rank_counts:
                rank_counts[card.rank] = []
            rank_counts[card.rank].append(card)

        all_tongzi = []

        # Check each rank for tongzi
        for rank, cards in rank_counts.items():
            if len(cards) >= 3:
                # Group by suit
                suit_groups: dict[Suit, list[Card]] = {}
                for card in cards:
                    if card.suit not in suit_groups:
                        suit_groups[card.suit] = []
                    suit_groups[card.suit].append(card)

                # Check each suit group for tongzi
                for suit, suit_cards in suit_groups.items():
                    if len(suit_cards) >= 3:
                        all_tongzi.append(suit_cards[:3])

        return all_tongzi

    @staticmethod
    def find_triple_with_two(hand: list[Card]) -> list[Card] | None:
        """Find a triple with two (三带二) pattern.

        Returns the smallest valid triple_with_two combination.
        Pattern: 3 of same rank + 2 of same rank (e.g., 7-7-7-8-8)

        Args:
            hand: List of cards to search

        Returns:
            List of cards forming triple_with_two, or None if not found
        """
        rank_counts: dict[Rank, list[Card]] = {}
        for card in hand:
            if card.rank not in rank_counts:
                rank_counts[card.rank] = []
            rank_counts[card.rank].append(card)

        # Find triples and pairs
        triples = []
        pairs = []
        for rank, cards in rank_counts.items():
            if len(cards) >= 3:
                triples.append((rank, cards[:3]))
            if len(cards) >= 2:
                pairs.append((rank, cards[:2]))

        if not triples or not pairs:
            return None

        # Find smallest triple
        triples.sort(key=lambda x: x[0].value)
        triple_rank, triple_cards = triples[0]

        # Find smallest pair that's different from the triple
        for pair_rank, pair_cards in sorted(pairs, key=lambda x: x[0].value):
            if pair_rank != triple_rank:
                return triple_cards + pair_cards

        return None

    @staticmethod
    def find_all_triple_with_two(hand: list[Card]) -> list[list[Card]]:
        """Find all triple_with_two combinations.

        Returns all possible triple_with_two combinations.

        Args:
            hand: List of cards to search

        Returns:
            List of all triple_with_two combinations
        """
        rank_counts: dict[Rank, list[Card]] = {}
        for card in hand:
            if card.rank not in rank_counts:
                rank_counts[card.rank] = []
            rank_counts[card.rank].append(card)

        # Find all triples and pairs
        triples = []
        pairs = []
        for rank, cards in rank_counts.items():
            if len(cards) >= 3:
                triples.append((rank, cards[:3]))
            if len(cards) >= 2:
                pairs.append((rank, cards[:2]))

        if not triples or not pairs:
            return []

        # Generate all combinations
        all_combos = []
        for triple_rank, triple_cards in triples:
            for pair_rank, pair_cards in pairs:
                if triple_rank != pair_rank:
                    all_combos.append(triple_cards + pair_cards)

        return all_combos

    @staticmethod
    def find_airplane(hand: list[Card]) -> list[Card] | None:
        """Find an airplane pattern (连续三张).

        Returns the smallest valid airplane (at least 2 consecutive triples).
        Pattern: consecutive triples (e.g., 5-5-5-6-6-6)

        Args:
            hand: List of cards to search

        Returns:
            List of cards forming airplane, or None if not found
        """
        rank_counts: dict[Rank, list[Card]] = {}
        for card in hand:
            if card.rank not in rank_counts:
                rank_counts[card.rank] = []
            rank_counts[card.rank].append(card)

        # Filter ranks that have at least 3 cards (triples)
        triples_by_rank: dict[Rank, list[Card]] = {}
        for rank, cards in rank_counts.items():
            if len(cards) >= 3:
                triples_by_rank[rank] = cards[:3]

        if len(triples_by_rank) < 2:
            return None

        # Sort ranks by value
        sorted_ranks = sorted(triples_by_rank.keys(), key=lambda r: r.value)

        # Find the smallest consecutive sequence (at least 2 triples)
        for i in range(len(sorted_ranks) - 1):
            if sorted_ranks[i].value + 1 == sorted_ranks[i + 1].value:
                # Found consecutive triples
                return triples_by_rank[sorted_ranks[i]] + triples_by_rank[sorted_ranks[i + 1]]

        return None

    @staticmethod
    def find_all_airplanes(
        hand: list[Card], num_triples: int
    ) -> list[list[Card]]:
        """Find all airplane combinations of given length.

        Args:
            hand: Player's hand
            num_triples: Number of consecutive triples needed (e.g., 2 means 6 cards)

        Returns:
            List of all possible airplane combinations
        """
        if num_triples < 2:
            return []

        rank_counts: dict[Rank, list[Card]] = {}
        for card in hand:
            if card.rank not in rank_counts:
                rank_counts[card.rank] = []
            rank_counts[card.rank].append(card)

        # Filter ranks that have at least 3 cards (triples)
        triples_by_rank: dict[Rank, list[Card]] = {}
        for rank, cards in rank_counts.items():
            if len(cards) >= 3:
                triples_by_rank[rank] = cards[:3]

        if len(triples_by_rank) < num_triples:
            return []

        # Sort ranks by value
        sorted_ranks = sorted(triples_by_rank.keys(), key=lambda r: r.value)

        # Find all consecutive sequences of required length
        all_combinations = []

        for i in range(len(sorted_ranks) - num_triples + 1):
            # Check if we can form a consecutive sequence starting from sorted_ranks[i]
            is_consecutive = True
            for j in range(num_triples - 1):
                if sorted_ranks[i + j].value + 1 != sorted_ranks[i + j + 1].value:
                    is_consecutive = False
                    break

            if is_consecutive:
                # Build the card combination
                combination = []
                for j in range(num_triples):
                    combination.extend(triples_by_rank[sorted_ranks[i + j]])
                all_combinations.append(combination)

        return all_combinations

    @staticmethod
    def find_airplane_with_wings(hand: list[Card]) -> list[Card] | None:
        """Find an airplane_with_wings pattern (飞机带翅膀).

        Returns the smallest valid airplane_with_wings.
        Pattern: airplane + pairs (e.g., 5-5-5-6-6-6 + 7-7-8-8)

        Args:
            hand: List of cards to search

        Returns:
            List of cards forming airplane_with_wings, or None if not found
        """
        # First find an airplane (at least 2 consecutive triples)
        airplane = PatternFinder.find_airplane(hand)
        if not airplane:
            return None

        # Count how many triples in the airplane
        num_triples = len(airplane) // 3

        # Need to find num_triples pairs for wings
        # Get the ranks used in airplane
        airplane_ranks = set(card.rank for card in airplane)

        # Find available pairs (can be from airplane ranks if we have extras)
        rank_counts: dict[Rank, list[Card]] = {}
        for card in hand:
            if card.rank not in rank_counts:
                rank_counts[card.rank] = []
            rank_counts[card.rank].append(card)

        # Find pairs for wings
        available_pairs = []
        for rank, cards in rank_counts.items():
            # Count available cards for this rank (excluding those used in airplane)
            if rank in airplane_ranks:
                # This rank is used in airplane, check if we have extra cards
                remaining = len(cards) - 3
                if remaining >= 2:
                    # Find the extra cards not in airplane
                    extra_cards = [c for c in cards if c not in airplane]
                    if len(extra_cards) >= 2:
                        available_pairs.append((rank, extra_cards[:2]))
            else:
                # This rank is not used in airplane
                if len(cards) >= 2:
                    available_pairs.append((rank, cards[:2]))

        if len(available_pairs) < num_triples:
            return None

        # Take the smallest pairs
        available_pairs.sort(key=lambda x: x[0].value)
        wings = []
        for i in range(num_triples):
            wings.extend(available_pairs[i][1])

        return airplane + wings

    @staticmethod
    def find_all_airplane_with_wings(
        hand: list[Card], target_card_count: int
    ) -> list[list[Card]]:
        """Find all airplane_with_wings combinations.

        Args:
            hand: Player's hand
            target_card_count: Target total card count (used to infer structure)

        Returns:
            List of all possible airplane_with_wings combinations
        """
        # Infer structure: airplane_with_wings = N triples + N pairs
        # Total cards = 3N + 2N = 5N
        if target_card_count % 5 != 0:
            return []

        num_triples = target_card_count // 5
        if num_triples < 2:
            return []

        # Find all airplanes of required length
        all_airplanes = PatternFinder.find_all_airplanes(hand, num_triples)
        if not all_airplanes:
            return []

        all_combinations = []

        for airplane in all_airplanes:
            # Get ranks used in this airplane
            airplane_ranks = set(card.rank for card in airplane)

            # Find available pairs for wings
            rank_counts: dict[Rank, list[Card]] = {}
            for card in hand:
                if card.rank not in rank_counts:
                    rank_counts[card.rank] = []
                rank_counts[card.rank].append(card)

            available_pairs = []
            for rank, cards in rank_counts.items():
                if rank in airplane_ranks:
                    # Check for extra cards beyond the 3 used in airplane
                    remaining = len(cards) - 3
                    if remaining >= 2:
                        extra_cards = [c for c in cards if c not in airplane]
                        if len(extra_cards) >= 2:
                            available_pairs.append(extra_cards[:2])
                else:
                    if len(cards) >= 2:
                        available_pairs.append(cards[:2])

            if len(available_pairs) < num_triples:
                continue

            # Generate all combinations of num_triples pairs from available_pairs
            for pair_combo in combinations(available_pairs, num_triples):
                wings = []
                for pair in pair_combo:
                    wings.extend(pair)
                all_combinations.append(airplane + wings)

        return all_combinations
