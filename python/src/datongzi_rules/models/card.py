"""Card model and related enums for Da Tong Zi game - Zero Dependency Version."""

from dataclasses import dataclass, field
from enum import IntEnum
import logging

logger = logging.getLogger(__name__)


class Suit(IntEnum):
    """Card suits with ranking order (higher value = higher rank)."""

    DIAMONDS = 1  # 方块 (lowest)
    CLUBS = 2  # 梅花
    HEARTS = 3  # 红桃
    SPADES = 4  # 黑桃 (highest)


class Rank(IntEnum):
    """Card ranks with special handling for A and 2 being highest."""

    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14
    TWO = 15  # 2 is the highest rank in this game


@dataclass(frozen=True, order=True)
class Card:
    """Represents a single playing card."""

    suit: Suit
    rank: Rank

    def __post_init__(self) -> None:
        """Validate card after creation."""
        if not isinstance(self.suit, Suit):
            raise ValueError(f"Invalid suit: {self.suit}")
        if not isinstance(self.rank, Rank):
            raise ValueError(f"Invalid rank: {self.rank}")

    @property
    def is_scoring_card(self) -> bool:
        """Return True if this card contributes to scoring (5, 10, K)."""
        return self.rank in [Rank.FIVE, Rank.TEN, Rank.KING]

    @property
    def score_value(self) -> int:
        """Return the point value of this card."""
        if self.rank == Rank.FIVE:
            return 5
        elif self.rank in [Rank.TEN, Rank.KING]:
            return 10
        return 0

    def __str__(self) -> str:
        """String representation of the card."""
        rank_names = {
            Rank.FIVE: "5",
            Rank.SIX: "6",
            Rank.SEVEN: "7",
            Rank.EIGHT: "8",
            Rank.NINE: "9",
            Rank.TEN: "10",
            Rank.JACK: "J",
            Rank.QUEEN: "Q",
            Rank.KING: "K",
            Rank.ACE: "A",
            Rank.TWO: "2",
        }
        suit_names = {
            Suit.SPADES: "♠",
            Suit.HEARTS: "♥",
            Suit.CLUBS: "♣",
            Suit.DIAMONDS: "♦",
        }
        return f"{suit_names[self.suit]}{rank_names[self.rank]}"

    def __repr__(self) -> str:
        """Detailed representation of the card."""
        return f"Card({self.suit.name}, {self.rank.name})"

    @classmethod
    def from_string(cls, card_str: str) -> "Card":
        """Create a Card from string representation like '♠A', '♥K', etc."""
        if len(card_str) < 2:
            raise ValueError(f"Invalid card string: {card_str}")

        suit_char = card_str[0]
        rank_str = card_str[1:]

        # Map suit characters to Suit enum
        suit_map = {
            "♠": Suit.SPADES,
            "♥": Suit.HEARTS,
            "♣": Suit.CLUBS,
            "♦": Suit.DIAMONDS,
        }

        if suit_char not in suit_map:
            raise ValueError(f"Invalid suit character: {suit_char}")

        # Map rank strings to Rank enum
        rank_map = {
            "5": Rank.FIVE,
            "6": Rank.SIX,
            "7": Rank.SEVEN,
            "8": Rank.EIGHT,
            "9": Rank.NINE,
            "10": Rank.TEN,
            "J": Rank.JACK,
            "Q": Rank.QUEEN,
            "K": Rank.KING,
            "A": Rank.ACE,
            "2": Rank.TWO,
        }

        if rank_str not in rank_map:
            raise ValueError(f"Invalid rank string: {rank_str}")

        return cls(suit_map[suit_char], rank_map[rank_str])


@dataclass
class Deck:
    """Represents a deck of cards for Da Tong Zi game."""

    cards: list[Card] = field(default_factory=list)

    @classmethod
    def create_standard_deck(
        cls, num_decks: int = 3, excluded_ranks: set[Rank] | None = None
    ) -> "Deck":
        """
        Create a standard Da Tong Zi deck.

        Args:
            num_decks: Number of standard decks to include (default: 3)
            excluded_ranks: Set of ranks to exclude (default: {3, 4} + Jokers)
        """
        if excluded_ranks is None:
            excluded_ranks = set()  # By default, we only include 5-A, 2

        cards = []
        for _ in range(num_decks):
            for suit in Suit:
                for rank in Rank:
                    if rank not in excluded_ranks:
                        cards.append(Card(suit, rank))

        logger.info(
            f"Created deck: num_decks={num_decks}, total_cards={len(cards)}, "
            f"excluded_ranks={[r.name for r in excluded_ranks]}"
        )

        return cls(cards=cards)

    def shuffle(self) -> None:
        """Shuffle the deck."""
        import random

        random.shuffle(self.cards)
        logger.debug(f"Deck shuffled: remaining_cards={len(self.cards)}")

    def deal_card(self) -> Card:
        """Deal one card from the deck."""
        if not self.cards:
            raise ValueError("Cannot deal from empty deck")
        card = self.cards.pop()
        logger.debug(f"Card dealt: card={str(card)}, remaining_cards={len(self.cards)}")
        return card

    def deal_cards(self, count: int) -> list[Card]:
        """Deal multiple cards from the deck."""
        if count > len(self.cards):
            raise ValueError(
                f"Cannot deal {count} cards, only {len(self.cards)} remaining"
            )

        dealt_cards = []
        for _ in range(count):
            dealt_cards.append(self.deal_card())

        logger.info(f"Cards dealt: count={count}, remaining_cards={len(self.cards)}")
        return dealt_cards

    def __len__(self) -> int:
        """Return number of cards remaining in deck."""
        return len(self.cards)
