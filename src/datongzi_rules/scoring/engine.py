"""Scoring rules and calculations for Da Tong Zi game - Zero Dependency Version."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import logging

from ..models.card import Card, Rank
from ..models.config import GameConfig
from ..patterns.recognizer import PlayPattern, PlayType

logger = logging.getLogger(__name__)


class BonusType(Enum):
    """Types of bonus scoring in the game."""

    ROUND_WIN = "round_win"
    K_TONGZI = "k_tongzi"
    A_TONGZI = "a_tongzi"
    TWO_TONGZI = "two_tongzi"
    DIZHA = "dizha"
    FINISH_FIRST = "finish_first"
    FINISH_SECOND = "finish_second"
    FINISH_THIRD = "finish_third"


@dataclass
class ScoringEvent:
    """Represents a single scoring event."""

    player_id: str
    bonus_type: BonusType
    points: int
    reason: str
    round_number: int | None = None
    cards_involved: list[str] = field(default_factory=list)


class ScoringEngine:
    """
    Handles all scoring calculations and bonus awards.
    
    Note: This is a pure calculation engine. It does NOT modify player state.
    Server layer is responsible for applying scores to players.
    """

    def __init__(self, config: GameConfig):
        """Initialize scoring engine with game configuration."""
        self.config = config
        self.scoring_events: list[ScoringEvent] = []

    def calculate_round_base_score(self, cards: list[Card]) -> int:
        """
        Calculate base score from cards in a round.

        Args:
            cards: All cards played in the round

        Returns:
            Total points from scoring cards (5, 10, K)
        """
        total_score = 0
        scoring_cards = []

        for card in cards:
            if card.is_scoring_card:
                points = card.score_value
                total_score += points
                scoring_cards.append(str(card))

        logger.debug(
            f"Round base score calculated: total_score={total_score}, "
            f"scoring_cards={scoring_cards}, total_cards={len(cards)}"
        )

        return total_score

    def create_round_win_event(
        self, player_id: str, round_cards: list[Card], round_number: int
    ) -> ScoringEvent | None:
        """
        Create scoring event for round winner.

        Args:
            player_id: ID of the player who won
            round_cards: All cards played in the round
            round_number: Current round number

        Returns:
            ScoringEvent for this award, or None if no points
        """
        base_score = self.calculate_round_base_score(round_cards)

        if base_score > 0:
            event = ScoringEvent(
                player_id=player_id,
                bonus_type=BonusType.ROUND_WIN,
                points=base_score,
                reason=f"Round {round_number} win with {base_score} scoring cards",
                round_number=round_number,
                cards_involved=[str(c) for c in round_cards if c.is_scoring_card],
            )

            self.scoring_events.append(event)

            logger.info(
                f"Round win event created: player={player_id}, "
                f"points={base_score}, round={round_number}"
            )

            return event

        return None

    def create_special_bonus_events(
        self,
        player_id: str,
        winning_pattern: PlayPattern,
        round_number: int,
        is_round_winning_play: bool = True
    ) -> list[ScoringEvent]:
        """
        Create scoring events for special bonuses (Tongzi, Dizha).

        IMPORTANT: According to game rules, only the FINAL winning play of a round
        receives special bonuses. If player A plays K Tongzi and player B beats it
        with A Tongzi, only player B gets the bonus (200 points), player A gets nothing.

        Args:
            player_id: ID of the player who won
            winning_pattern: The winning pattern
            round_number: Current round number
            is_round_winning_play: Whether this is the final winning play of the round.
                Only when True will special bonuses be awarded. Default True for
                backward compatibility.

        Returns:
            List of ScoringEvents for bonuses (empty if not round winning play)
        """
        events = []

        # Only award special bonuses if this is the round winning play
        if not is_round_winning_play:
            logger.debug(
                f"Skipping special bonus for non-winning play: player={player_id}, "
                f"pattern={winning_pattern.play_type.name}"
            )
            return events

        if winning_pattern.play_type == PlayType.TONGZI:
            bonus_points = self._get_tongzi_bonus(winning_pattern.primary_rank)
            bonus_type = self._get_tongzi_bonus_type(winning_pattern.primary_rank)

            if bonus_points > 0:
                event = ScoringEvent(
                    player_id=player_id,
                    bonus_type=bonus_type,
                    points=bonus_points,
                    reason=f"{winning_pattern.primary_rank.name} Tongzi in round {round_number}",
                    round_number=round_number,
                )
                events.append(event)
                self.scoring_events.append(event)

                logger.info(
                    f"Tongzi bonus event created: player={player_id}, "
                    f"rank={winning_pattern.primary_rank.name}, bonus={bonus_points}"
                )

        elif winning_pattern.play_type == PlayType.DIZHA:
            bonus_points = self.config.dizha_bonus

            event = ScoringEvent(
                player_id=player_id,
                bonus_type=BonusType.DIZHA,
                points=bonus_points,
                reason=f"{winning_pattern.primary_rank.name} Dizha in round {round_number}",
                round_number=round_number,
            )
            events.append(event)
            self.scoring_events.append(event)

            logger.info(
                f"Dizha bonus event created: player={player_id}, "
                f"rank={winning_pattern.primary_rank.name}, bonus={bonus_points}"
            )

        return events

    def create_finish_bonus_events(
        self, player_ids_in_finish_order: list[str]
    ) -> list[ScoringEvent]:
        """
        Create finish position bonus events (上游, 二游, 三游).

        Args:
            player_ids_in_finish_order: Player IDs sorted by finish order

        Returns:
            List of ScoringEvents for finish bonuses
        """
        events = []

        for i, player_id in enumerate(player_ids_in_finish_order):
            if i < len(self.config.finish_bonus):
                bonus_points = self.config.finish_bonus[i]

                # Determine bonus type
                if i == 0:
                    bonus_type = BonusType.FINISH_FIRST
                    position_name = "上游"
                elif i == 1:
                    bonus_type = BonusType.FINISH_SECOND
                    position_name = "二游"
                else:
                    bonus_type = BonusType.FINISH_THIRD
                    position_name = "三游"

                event = ScoringEvent(
                    player_id=player_id,
                    bonus_type=bonus_type,
                    points=bonus_points,
                    reason=f"Finished in position {i+1} ({position_name})",
                )
                events.append(event)
                self.scoring_events.append(event)

                logger.info(
                    f"Finish bonus event created: player={player_id}, "
                    f"position={i+1}, position_name={position_name}, bonus={bonus_points}"
                )

        return events

    def _get_tongzi_bonus(self, rank: Rank) -> int:
        """Get bonus points for Tongzi of specific rank."""
        if rank == Rank.KING:
            return self.config.k_tongzi_bonus
        elif rank == Rank.ACE:
            return self.config.a_tongzi_bonus
        elif rank == Rank.TWO:
            return self.config.two_tongzi_bonus
        return 0

    def _get_tongzi_bonus_type(self, rank: Rank) -> BonusType:
        """Get bonus type for Tongzi of specific rank."""
        if rank == Rank.KING:
            return BonusType.K_TONGZI
        elif rank == Rank.ACE:
            return BonusType.A_TONGZI
        elif rank == Rank.TWO:
            return BonusType.TWO_TONGZI
        return BonusType.ROUND_WIN

    def calculate_total_score_for_player(self, player_id: str) -> int:
        """
        Calculate total score for a player from all events.

        Args:
            player_id: Player ID to calculate for

        Returns:
            Total score from all events
        """
        return sum(
            event.points for event in self.scoring_events if event.player_id == player_id
        )

    def get_game_summary(self, player_ids: list[str]) -> dict[str, Any]:
        """
        Generate a comprehensive game scoring summary.

        Args:
            player_ids: All player IDs in the game

        Returns:
            Dictionary with detailed scoring breakdown
        """
        # Calculate final scores
        final_scores = {
            pid: self.calculate_total_score_for_player(pid) for pid in player_ids
        }

        summary: dict[str, Any] = {
            "final_scores": final_scores,
            "winner_id": max(final_scores.items(), key=lambda x: x[1])[0]
            if final_scores
            else None,
            "total_events": len(self.scoring_events),
            "events_by_type": {},
            "events_by_player": {},
            "round_breakdown": {},
        }

        # Group events by type
        for event in self.scoring_events:
            event_type = event.bonus_type.value
            if event_type not in summary["events_by_type"]:
                summary["events_by_type"][event_type] = []
            summary["events_by_type"][event_type].append(
                {
                    "player_id": event.player_id,
                    "points": event.points,
                    "reason": event.reason,
                    "round": event.round_number,
                }
            )

        # Group events by player
        for player_id in player_ids:
            player_events = [
                e for e in self.scoring_events if e.player_id == player_id
            ]
            summary["events_by_player"][player_id] = {
                "total_score": final_scores[player_id],
                "events": [
                    {
                        "type": e.bonus_type.value,
                        "points": e.points,
                        "reason": e.reason,
                        "round": e.round_number,
                    }
                    for e in player_events
                ],
            }

        # Group events by round
        for event in self.scoring_events:
            if event.round_number is not None:
                round_key = f"round_{event.round_number}"
                if round_key not in summary["round_breakdown"]:
                    summary["round_breakdown"][round_key] = []
                summary["round_breakdown"][round_key].append(
                    {
                        "player_id": event.player_id,
                        "type": event.bonus_type.value,
                        "points": event.points,
                        "reason": event.reason,
                    }
                )

        logger.info(
            f"Game scoring summary generated: total_events={len(self.scoring_events)}, "
            f"winner_id={summary['winner_id']}, final_scores={summary['final_scores']}"
        )

        return summary

    def validate_scores(self, player_scores: dict[str, int]) -> bool:
        """
        Validate that provided scores match recorded events.

        Args:
            player_scores: Dict of player_id -> current_score

        Returns:
            True if scores are consistent with events
        """
        calculated_scores = {
            pid: self.calculate_total_score_for_player(pid)
            for pid in player_scores.keys()
        }

        for player_id, recorded_score in player_scores.items():
            calculated_score = calculated_scores.get(player_id, 0)
            if calculated_score != recorded_score:
                logger.error(
                    f"Score validation failed: player_id={player_id}, "
                    f"recorded_score={recorded_score}, calculated_score={calculated_score}"
                )
                return False

        logger.info("Score validation passed")
        return True
