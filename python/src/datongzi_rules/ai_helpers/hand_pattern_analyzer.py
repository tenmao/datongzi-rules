"""Hand pattern analysis for AI decision making - Zero Dependency Version."""

import logging
from collections import defaultdict
from dataclasses import dataclass, field

from ..models.card import Card, Rank
from ..patterns.recognizer import PatternRecognizer, PlayType

logger = logging.getLogger(__name__)


@dataclass
class HandPatterns:
    """
    Structured representation of hand resources grouped by pattern types.

    This provides AI with a clear view of available resources without
    generating all possible combinations.

    Design principle:
    - Each resource is a valid playable pattern
    - Resources are non-overlapping (a card only appears in its "best" category)
    - Sorted by strength (descending) within each category
    - Priority: Dizha > Tongzi > Bomb > Airplane > Triple > ConsecPairs > Pair > Single
    """

    # Trump cards (highest priority resources)
    dizha: list[list[Card]] = field(default_factory=list)
    tongzi: list[list[Card]] = field(default_factory=list)
    bombs: list[list[Card]] = field(default_factory=list)

    # Composite patterns (multi-card combinations)
    airplane_chains: list[list[Card]] = field(default_factory=list)

    # Basic patterns (triple has higher priority than consecutive pairs)
    triples: list[list[Card]] = field(default_factory=list)
    consecutive_pair_chains: list[list[Card]] = field(default_factory=list)
    pairs: list[list[Card]] = field(default_factory=list)
    singles: list[Card] = field(default_factory=list)

    # Metadata
    total_cards: int = 0
    trump_count: int = 0
    has_control_cards: bool = False  # Has 2s, As, or Ks

    def __str__(self) -> str:
        """Human-readable summary."""
        parts = [
            f"HandPatterns({self.total_cards} cards):",
            f"  Trump: {self.trump_count} (Dizha:{len(self.dizha)}, Tongzi:{len(self.tongzi)}, Bombs:{len(self.bombs)})",
            f"  Chains: Airplanes:{len(self.airplane_chains)}, ConsecPairs:{len(self.consecutive_pair_chains)})",
            f"  Basic: Triples:{len(self.triples)}, Pairs:{len(self.pairs)}, Singles:{len(self.singles)}",
        ]
        return "\n".join(parts)


class HandPatternAnalyzer:
    """
    Analyze hand patterns for AI decision making.

    This is the recommended way for AI to analyze hands, instead of generating
    all possible plays which causes combinatorial explosion.

    Key differences from PlayGenerator:
    - Returns structured data (HandPatterns) not list of plays
    - Non-overlapping decomposition (each card assigned to best category)
    - Focuses on "what resources do I have" not "what plays can I make"
    - Much more efficient for AI strategy planning

    Priority order (non-overlapping extraction):
    1. Dizha (地炸)
    2. Tongzi (筒子)
    3. Bomb (炸弹)
    4. Airplane chains (飞机)
    5. Triples (三张) ← Higher priority than consecutive pairs
    6. Consecutive pair chains (连对) ← Lower priority, extracted after triples
    7. Pairs (对子)
    8. Singles (单张)

    Example usage:
        patterns = HandPatternAnalyzer.analyze_patterns(hand)

        # AI can now decide:
        if patterns.dizha:
            # I have dizha, can control the game
        elif patterns.bombs:
            # I have bombs, can beat most plays
        elif patterns.triples:
            # I have triples, strong basic patterns
    """

    @staticmethod
    def analyze_patterns(hand: list[Card]) -> HandPatterns:
        """
        Analyze hand and extract non-overlapping patterns.

        Strategy:
        1. Extract trump cards first (dizha, tongzi, bombs)
        2. Extract airplane chains (consecutive triples)
        3. Extract standalone triples (higher priority than consecutive pairs)
        4. Re-scan remaining cards for consecutive pair chains
        5. Extract pairs from remaining cards
        6. Extract singles from remaining cards

        Args:
            hand: List of cards in hand

        Returns:
            HandPatterns with structured decomposition
        """
        if not hand:
            return HandPatterns(total_cards=0)

        patterns = HandPatterns(total_cards=len(hand))
        remaining_cards = list(hand)  # Use list, NOT set (to preserve duplicates)

        # Step 1: Extract trump cards (highest priority)
        HandPatternAnalyzer._extract_trump_cards(remaining_cards, patterns)

        # Step 2: Extract airplane chains (consecutive triples)
        HandPatternAnalyzer._extract_airplane_chains(remaining_cards, patterns)

        # Step 3: Extract standalone triples (higher priority than consecutive pairs)
        HandPatternAnalyzer._extract_triples(remaining_cards, patterns)

        # Step 4: Re-scan for consecutive pair chains (after triples extracted)
        HandPatternAnalyzer._extract_consecutive_pair_chains(remaining_cards, patterns)

        # Step 5: Extract pairs from remaining cards
        HandPatternAnalyzer._extract_pairs(remaining_cards, patterns)

        # Step 6: Extract singles from remaining cards
        HandPatternAnalyzer._extract_singles(remaining_cards, patterns)

        # Step 7: Calculate metadata
        patterns.trump_count = (
            len(patterns.dizha) + len(patterns.tongzi) + len(patterns.bombs)
        )
        patterns.has_control_cards = any(
            c.rank in [Rank.TWO, Rank.ACE, Rank.KING] for c in hand
        )

        logger.debug(
            f"Analyzed {len(hand)} cards into: "
            f"Trump={patterns.trump_count}, "
            f"Triples={len(patterns.triples)}, "
            f"Pairs={len(patterns.pairs)}, "
            f"Singles={len(patterns.singles)}"
        )

        return patterns

    @staticmethod
    def _extract_trump_cards(
        remaining_cards: list[Card], patterns: HandPatterns
    ) -> None:
        """Extract dizha, tongzi, and bombs."""
        # Extract dizha (highest priority trump)
        dizha_list = HandPatternAnalyzer._find_dizha(remaining_cards)
        for dizha in dizha_list:
            patterns.dizha.append(dizha)
            for card in dizha:
                remaining_cards.remove(card)

        # Extract tongzi
        tongzi_list = HandPatternAnalyzer._find_tongzi(remaining_cards)
        for tongzi in tongzi_list:
            patterns.tongzi.append(tongzi)
            for card in tongzi:
                remaining_cards.remove(card)

        # Extract bombs (4+ same rank)
        bombs_list = HandPatternAnalyzer._find_bombs(remaining_cards)
        for bomb in bombs_list:
            patterns.bombs.append(bomb)
            for card in bomb:
                remaining_cards.remove(card)

        # Sort by strength (descending)
        patterns.dizha.sort(key=lambda x: x[0].rank.value, reverse=True)
        patterns.tongzi.sort(
            key=lambda x: (x[0].suit.value, x[0].rank.value), reverse=True
        )
        patterns.bombs.sort(key=lambda x: (len(x), x[0].rank.value), reverse=True)

    @staticmethod
    def _extract_airplane_chains(
        remaining_cards: list[Card], patterns: HandPatterns
    ) -> None:
        """Extract airplane chains (consecutive triples)."""
        airplane_chains = HandPatternAnalyzer._find_airplane_chains(remaining_cards)
        for chain in airplane_chains:
            patterns.airplane_chains.append(chain)
            for card in chain:
                remaining_cards.remove(card)

        # Sort by length (descending), then by rank
        patterns.airplane_chains.sort(
            key=lambda x: (len(x), x[0].rank.value), reverse=True
        )

    @staticmethod
    def _extract_triples(remaining_cards: list[Card], patterns: HandPatterns) -> None:
        """Extract standalone triples."""
        triples_list = HandPatternAnalyzer._find_triples(remaining_cards)
        for triple in triples_list:
            patterns.triples.append(triple)
            for card in triple:
                remaining_cards.remove(card)

        # Sort by rank (descending)
        patterns.triples.sort(key=lambda x: x[0].rank.value, reverse=True)

    @staticmethod
    def _extract_consecutive_pair_chains(
        remaining_cards: list[Card], patterns: HandPatterns
    ) -> None:
        """Extract consecutive pair chains (after triples extracted)."""
        consec_pair_chains = HandPatternAnalyzer._find_consecutive_pair_chains(
            remaining_cards
        )
        for chain in consec_pair_chains:
            patterns.consecutive_pair_chains.append(chain)
            for card in chain:
                remaining_cards.remove(card)

        # Sort by length (descending), then by rank
        patterns.consecutive_pair_chains.sort(
            key=lambda x: (len(x), x[0].rank.value), reverse=True
        )

    @staticmethod
    def _extract_pairs(remaining_cards: list[Card], patterns: HandPatterns) -> None:
        """Extract pairs from remaining cards."""
        rank_groups = defaultdict(list)
        for card in remaining_cards:
            rank_groups[card.rank].append(card)

        # Extract pairs
        for rank in sorted(rank_groups.keys(), key=lambda r: r.value, reverse=True):
            cards = rank_groups[rank]
            while len(cards) >= 2:
                pair = cards[:2]
                patterns.pairs.append(pair)
                for card in pair:
                    remaining_cards.remove(card)
                cards = cards[2:]

    @staticmethod
    def _extract_singles(remaining_cards: list[Card], patterns: HandPatterns) -> None:
        """Extract singles from remaining cards."""
        # All remaining cards are singles
        patterns.singles = sorted(
            remaining_cards, key=lambda c: c.rank.value, reverse=True
        )
        remaining_cards.clear()

    @staticmethod
    def _find_dizha(cards: list[Card]) -> list[list[Card]]:
        """Find all dizha (2 of each suit for same rank)."""
        rank_groups = defaultdict(list)
        for card in cards:
            rank_groups[card.rank].append(card)

        dizha_list = []
        for _rank, rank_cards in rank_groups.items():
            if len(rank_cards) < 8:
                continue

            # Group by suit
            suit_groups = defaultdict(list)
            for card in rank_cards:
                suit_groups[card.suit].append(card)

            # Check if all 4 suits have at least 2 cards
            from ..models.card import Suit

            if all(len(suit_groups.get(suit, [])) >= 2 for suit in Suit):
                dizha = []
                for suit in Suit:
                    dizha.extend(suit_groups[suit][:2])

                # Validate
                pattern = PatternRecognizer.analyze_cards(dizha)
                if pattern and pattern.play_type == PlayType.DIZHA:
                    dizha_list.append(dizha)

        return dizha_list

    @staticmethod
    def _find_tongzi(cards: list[Card]) -> list[list[Card]]:
        """Find all tongzi (3 same suit, same rank)."""
        suit_rank_groups = defaultdict(list)
        for card in cards:
            key = (card.suit, card.rank)
            suit_rank_groups[key].append(card)

        tongzi_list = []
        for (_suit, _rank), group_cards in suit_rank_groups.items():
            if len(group_cards) >= 3:
                tongzi = group_cards[:3]
                pattern = PatternRecognizer.analyze_cards(tongzi)
                if pattern and pattern.play_type == PlayType.TONGZI:
                    tongzi_list.append(tongzi)

        return tongzi_list

    @staticmethod
    def _find_bombs(cards: list[Card]) -> list[list[Card]]:
        """Find all bombs (4+ same rank)."""
        rank_groups = defaultdict(list)
        for card in cards:
            rank_groups[card.rank].append(card)

        bombs_list = []
        for _rank, rank_cards in rank_groups.items():
            if len(rank_cards) >= 4:
                # Take the largest possible bomb
                bomb = rank_cards[: len(rank_cards)]
                pattern = PatternRecognizer.analyze_cards(bomb)
                if pattern and pattern.play_type == PlayType.BOMB:
                    bombs_list.append(bomb)

        return bombs_list

    @staticmethod
    def _find_triples(cards: list[Card]) -> list[list[Card]]:
        """Find all triples (3 same rank)."""
        rank_groups = defaultdict(list)
        for card in cards:
            rank_groups[card.rank].append(card)

        triples_list = []
        for _rank, rank_cards in rank_groups.items():
            if len(rank_cards) >= 3:
                triple = rank_cards[:3]
                pattern = PatternRecognizer.analyze_cards(triple)
                if pattern and pattern.play_type == PlayType.TRIPLE:
                    triples_list.append(triple)

        return triples_list

    @staticmethod
    def _find_airplane_chains(cards: list[Card]) -> list[list[Card]]:
        """Find longest airplane chains (consecutive triples)."""
        rank_groups = defaultdict(list)
        for card in cards:
            rank_groups[card.rank].append(card)

        # Get ranks with at least 3 cards
        valid_ranks = sorted([r for r, cards in rank_groups.items() if len(cards) >= 3])

        chains = []
        i = 0
        while i < len(valid_ranks):
            # Try to build longest chain starting from valid_ranks[i]
            chain_ranks = [valid_ranks[i]]
            j = i + 1

            while j < len(valid_ranks):
                if valid_ranks[j].value == chain_ranks[-1].value + 1:
                    chain_ranks.append(valid_ranks[j])
                    j += 1
                else:
                    break

            # Only keep chains of length >= 2
            if len(chain_ranks) >= 2:
                chain_cards = []
                for rank in chain_ranks:
                    chain_cards.extend(rank_groups[rank][:3])

                # Validate
                pattern = PatternRecognizer.analyze_cards(chain_cards)
                if pattern and pattern.play_type == PlayType.AIRPLANE:
                    chains.append(chain_cards)
                    i = j  # Skip to next unprocessed rank
                else:
                    i += 1
            else:
                i += 1

        return chains

    @staticmethod
    def _find_consecutive_pair_chains(cards: list[Card]) -> list[list[Card]]:
        """Find longest consecutive pair chains."""
        rank_groups = defaultdict(list)
        for card in cards:
            rank_groups[card.rank].append(card)

        # Get ranks with at least 2 cards
        valid_ranks = sorted([r for r, cards in rank_groups.items() if len(cards) >= 2])

        chains = []
        i = 0
        while i < len(valid_ranks):
            # Try to build longest chain starting from valid_ranks[i]
            chain_ranks = [valid_ranks[i]]
            j = i + 1

            while j < len(valid_ranks):
                if valid_ranks[j].value == chain_ranks[-1].value + 1:
                    chain_ranks.append(valid_ranks[j])
                    j += 1
                else:
                    break

            # Only keep chains of length >= 2
            if len(chain_ranks) >= 2:
                chain_cards = []
                for rank in chain_ranks:
                    chain_cards.extend(rank_groups[rank][:2])

                # Validate
                pattern = PatternRecognizer.analyze_cards(chain_cards)
                if pattern and pattern.play_type == PlayType.CONSECUTIVE_PAIRS:
                    chains.append(chain_cards)
                    i = j  # Skip to next unprocessed rank
                else:
                    i += 1
            else:
                i += 1

        return chains
