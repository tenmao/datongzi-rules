"""Game configuration for Da Tong Zi rules."""

from dataclasses import dataclass, field

from .card import Rank


@dataclass
class GameConfig:
    """Configuration for Da Tong Zi game scoring and rules."""

    num_decks: int = 3
    num_players: int = 3
    cards_dealt_aside: int = 9
    excluded_ranks: set[Rank] = field(default_factory=set)

    # Scoring configuration
    finish_bonus: list[int] = field(
        default_factory=lambda: [100, -40, -60]
    )  # 上游, 二游, 三游

    # Special scoring bonuses
    k_tongzi_bonus: int = 100  # K筒子
    a_tongzi_bonus: int = 200  # A筒子
    two_tongzi_bonus: int = 300  # 2筒子
    dizha_bonus: int = 400  # 地炸

    # Rule variations
    must_beat_rule: bool = True  # 有牌必打

    def __post_init__(self) -> None:
        """Validate and adjust configuration after creation."""
        if self.num_players < 2:
            raise ValueError("Must have at least 2 players")
        if self.num_decks < 1:
            raise ValueError("Must have at least 1 deck")

        # Auto-adjust finish_bonus for different player counts
        if len(self.finish_bonus) != self.num_players:
            if self.num_players == 2:
                object.__setattr__(self, "finish_bonus", [100, -100])
            elif self.num_players == 4:
                object.__setattr__(self, "finish_bonus", [100, -20, -40, -80])
            else:
                # Generic case
                penalty = 100 // (self.num_players - 1)
                new_bonus = [100] + [-penalty] * (self.num_players - 1)
                object.__setattr__(self, "finish_bonus", new_bonus)

    @property
    def total_cards(self) -> int:
        """Calculate total cards in game."""
        cards_per_deck = len(Rank) - len(self.excluded_ranks)
        return self.num_decks * cards_per_deck * 4  # 4 suits

    @property
    def cards_per_player(self) -> int:
        """Calculate cards dealt to each player."""
        available_cards = self.total_cards - self.cards_dealt_aside
        return available_cards // self.num_players
