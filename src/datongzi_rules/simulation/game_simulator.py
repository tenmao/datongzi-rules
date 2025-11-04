"""Complete game flow simulator with rule validation and logging."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable
import logging
import random

from ..models.card import Card, Deck
from ..models.config import GameConfig
from ..patterns.recognizer import PatternRecognizer, PlayPattern, PlayValidator
from ..scoring.engine import ScoringEngine

logger = logging.getLogger(__name__)


class PlayerAction(Enum):
    """Types of player actions in a round."""

    PLAY = "play"
    PASS = "pass"
    SKIP_NO_CARDS = "skip_no_cards"


@dataclass
class RoundLog:
    """Log entry for a single action in a round."""

    round_number: int
    action_number: int
    player_id: str
    action: PlayerAction
    cards_played: list[Card] = field(default_factory=list)
    pattern: PlayPattern | None = None
    reason: str = ""
    hand_size_before: int = 0
    hand_size_after: int = 0
    is_round_winner: bool = False


@dataclass
class GameState:
    """Complete state of the game at any point."""

    config: GameConfig
    player_ids: list[str]
    player_hands: dict[str, list[Card]]
    aside_cards: list[Card]
    scoring_engine: ScoringEngine

    current_round: int = 1
    current_player_index: int = 0
    current_round_plays: list[tuple[str, list[Card], PlayPattern]] = field(default_factory=list)
    current_best_play: PlayPattern | None = None
    last_player_who_played: str | None = None
    consecutive_passes: int = 0

    finished_players: list[str] = field(default_factory=list)
    round_logs: list[RoundLog] = field(default_factory=list)
    game_over: bool = False

    def get_current_player(self) -> str:
        """Get current player ID."""
        return self.player_ids[self.current_player_index]

    def get_next_player_index(self) -> int:
        """Get next player index (循环)."""
        return (self.current_player_index + 1) % len(self.player_ids)

    def advance_to_next_player(self) -> None:
        """Move to next player."""
        self.current_player_index = self.get_next_player_index()

    def is_player_finished(self, player_id: str) -> bool:
        """Check if player has finished (no cards left)."""
        return player_id in self.finished_players

    def get_active_players(self) -> list[str]:
        """Get list of players still in game."""
        return [pid for pid in self.player_ids if not self.is_player_finished(pid)]


class GameSimulator:
    """
    Complete game flow simulator that implements all Da Tong Zi rules.

    Features:
    - Full round management
    - "Must beat" rule (有牌必打)
    - Correct bonus scoring (only for round-winning plays)
    - Complete logging for every action
    - Rule validation at every step
    """

    def __init__(
        self,
        config: GameConfig,
        player_ids: list[str],
        verbose: bool = True
    ):
        """
        Initialize game simulator.

        Args:
            config: Game configuration
            player_ids: List of player IDs
            verbose: Whether to log详细信息
        """
        if len(player_ids) != config.num_players:
            raise ValueError(
                f"Number of players ({len(player_ids)}) does not match "
                f"config ({config.num_players})"
            )

        self.verbose = verbose

        # Create and shuffle deck
        deck = Deck.create_standard_deck(num_decks=config.num_decks)
        deck.shuffle()

        # Deal cards
        player_hands = {}
        for player_id in player_ids:
            hand = deck.deal_cards(config.cards_per_player)
            player_hands[player_id] = sorted(hand)

        # Aside cards
        aside_cards = deck.deal_cards(config.cards_dealt_aside)

        # Create game state
        self.state = GameState(
            config=config,
            player_ids=player_ids,
            player_hands=player_hands,
            aside_cards=aside_cards,
            scoring_engine=ScoringEngine(config),
            current_player_index=random.randint(0, len(player_ids) - 1)
        )

        self._log(f"Game initialized with {len(player_ids)} players")
        self._log(f"Starting player: {self.state.get_current_player()}")
        for player_id in player_ids:
            self._log(
                f"  {player_id}: {len(player_hands[player_id])} cards"
            )

    def play_full_game(
        self,
        play_decision_func: Callable[[GameState, str], list[Card] | None] | None = None
    ) -> dict:
        """
        Play a complete game until only one player remains.

        Args:
            play_decision_func: Function that decides which cards to play.
                Signature: (game_state, player_id) -> cards_to_play | None
                If None, uses default random valid play strategy.

        Returns:
            Dict with game results and complete log
        """
        if play_decision_func is None:
            play_decision_func = self._default_play_strategy

        action_number = 0

        while not self.state.game_over:
            current_player = self.state.get_current_player()

            # Skip if player finished
            if self.state.is_player_finished(current_player):
                self.state.advance_to_next_player()
                continue

            # Get player decision
            cards_to_play = play_decision_func(self.state, current_player)

            # Execute action
            action_number += 1
            self._execute_player_action(
                current_player,
                cards_to_play,
                action_number
            )

            # Check for round end
            if self._check_round_end():
                self._end_round(action_number)

            # Check for game end
            if self._check_game_end():
                self._end_game()
                break

            # Move to next player
            self.state.advance_to_next_player()

        return self._generate_game_report()

    def _execute_player_action(
        self,
        player_id: str,
        cards_to_play: list[Card] | None,
        action_number: int
    ) -> None:
        """Execute a single player action and log it."""
        hand = self.state.player_hands[player_id]
        hand_size_before = len(hand)

        # No cards - skip
        if hand_size_before == 0:
            log_entry = RoundLog(
                round_number=self.state.current_round,
                action_number=action_number,
                player_id=player_id,
                action=PlayerAction.SKIP_NO_CARDS,
                reason="No cards left",
                hand_size_before=0,
                hand_size_after=0
            )
            self.state.round_logs.append(log_entry)
            self._log_action(log_entry)
            return

        # Pass
        if cards_to_play is None or len(cards_to_play) == 0:
            self.state.consecutive_passes += 1

            log_entry = RoundLog(
                round_number=self.state.current_round,
                action_number=action_number,
                player_id=player_id,
                action=PlayerAction.PASS,
                reason="Chose to pass",
                hand_size_before=hand_size_before,
                hand_size_after=hand_size_before
            )
            self.state.round_logs.append(log_entry)
            self._log_action(log_entry)
            return

        # Validate play
        pattern = PatternRecognizer.analyze_cards(cards_to_play)
        if pattern is None:
            raise ValueError(
                f"Invalid pattern: {[str(c) for c in cards_to_play]}"
            )

        if not PlayValidator.can_beat_play(cards_to_play, self.state.current_best_play):
            raise ValueError(
                f"Cannot beat current play: {self.state.current_best_play}"
            )

        # Valid play - execute
        for card in cards_to_play:
            if card not in hand:
                raise ValueError(f"Card {card} not in hand")
            hand.remove(card)

        # Update round state
        self.state.current_best_play = pattern
        self.state.last_player_who_played = player_id
        self.state.current_round_plays.append((player_id, cards_to_play, pattern))
        self.state.consecutive_passes = 0

        # Log
        log_entry = RoundLog(
            round_number=self.state.current_round,
            action_number=action_number,
            player_id=player_id,
            action=PlayerAction.PLAY,
            cards_played=cards_to_play.copy(),
            pattern=pattern,
            reason=f"Played {pattern.play_type.name}",
            hand_size_before=hand_size_before,
            hand_size_after=len(hand)
        )
        self.state.round_logs.append(log_entry)
        self._log_action(log_entry)

        # Check if player finished
        if len(hand) == 0 and player_id not in self.state.finished_players:
            self.state.finished_players.append(player_id)
            self._log(f"🎉 {player_id} finished! Position: {len(self.state.finished_players)}")

    def _check_round_end(self) -> bool:
        """Check if current round has ended."""
        active_players = self.state.get_active_players()

        # Round ends if only one player left or all others passed
        if len(active_players) <= 1:
            return True

        # Round ends if all other players passed after last play
        if self.state.consecutive_passes >= len(active_players) - 1:
            return True

        return False

    def _end_round(self, last_action_number: int) -> None:
        """End current round and award points."""
        if self.state.last_player_who_played is None:
            self._log("Round ended with no plays")
            self._start_new_round()
            return

        winner_id = self.state.last_player_who_played
        winning_pattern = self.state.current_best_play

        # Mark round winner in last action log
        for log in reversed(self.state.round_logs):
            if log.action_number == last_action_number or log.player_id == winner_id:
                log.is_round_winner = True
                break

        self._log(f"📍 Round {self.state.current_round} winner: {winner_id}")

        # Collect all cards from this round
        round_cards = []
        for _, cards, _ in self.state.current_round_plays:
            round_cards.extend(cards)

        # Award base score from round cards
        round_event = self.state.scoring_engine.create_round_win_event(
            winner_id,
            round_cards,
            self.state.current_round
        )
        if round_event:
            self._log(f"  💰 Base score: +{round_event.points}")

        # Award special bonuses (only for round-winning play)
        if winning_pattern:
            special_events = self.state.scoring_engine.create_special_bonus_events(
                winner_id,
                winning_pattern,
                self.state.current_round,
                is_round_winning_play=True
            )
            for event in special_events:
                self._log(f"  🎁 {event.bonus_type.value}: +{event.points}")

        self._start_new_round()

    def _start_new_round(self) -> None:
        """Start a new round."""
        self.state.current_round += 1
        self.state.current_round_plays = []
        self.state.current_best_play = None
        self.state.consecutive_passes = 0

        # Next round starts from winner (if still in game) or next player
        if self.state.last_player_who_played:
            winner_idx = self.state.player_ids.index(self.state.last_player_who_played)

            # If winner finished, start from next active player
            if self.state.is_player_finished(self.state.last_player_who_played):
                self.state.current_player_index = self._find_next_active_player(winner_idx)
            else:
                self.state.current_player_index = winner_idx

        self._log(f"🔄 Starting round {self.state.current_round}")

    def _find_next_active_player(self, start_idx: int) -> int:
        """Find next active player from start index."""
        for i in range(1, len(self.state.player_ids) + 1):
            next_idx = (start_idx + i) % len(self.state.player_ids)
            if not self.state.is_player_finished(self.state.player_ids[next_idx]):
                return next_idx
        return start_idx

    def _check_game_end(self) -> bool:
        """Check if game has ended."""
        active_players = self.state.get_active_players()
        return len(active_players) <= 1

    def _end_game(self) -> None:
        """End game and award finish bonuses."""
        self._log("=" * 60)
        self._log("🏁 GAME OVER")
        self._log("=" * 60)

        # Award finish bonuses
        finish_events = self.state.scoring_engine.create_finish_bonus_events(
            self.state.finished_players
        )

        self._log("\nFinish Order:")
        for i, player_id in enumerate(self.state.finished_players):
            bonus = finish_events[i].points if i < len(finish_events) else 0
            self._log(f"  {i+1}. {player_id}: {bonus:+d}")

        # Final scores
        self._log("\nFinal Scores:")
        for player_id in self.state.player_ids:
            score = self.state.scoring_engine.calculate_total_score_for_player(player_id)
            remaining = len(self.state.player_hands[player_id])
            self._log(f"  {player_id}: {score:+d} ({remaining} cards left)")

        self.state.game_over = True

    def _default_play_strategy(
        self,
        state: GameState,
        player_id: str
    ) -> list[Card] | None:
        """
        Default play strategy: play smallest valid cards.

        This is a simple strategy for testing. Real AI should use more
        sophisticated logic.
        """
        hand = state.player_hands[player_id]
        current_play = state.current_best_play

        # Starting new round - play smallest single
        if current_play is None:
            return [hand[0]]

        # Try to find smallest valid play
        # For simplicity, try single, pair, triple
        for count in [1, 2, 3, 4]:
            if len(hand) < count:
                continue

            for i in range(len(hand) - count + 1):
                cards = hand[i:i+count]
                if PlayValidator.can_beat_play(cards, current_play):
                    return cards

        # Can't beat - pass (if must_beat_rule, caller should detect this)
        return None

    def _log(self, message: str) -> None:
        """Log message if verbose."""
        if self.verbose:
            logger.info(message)
            print(message)

    def _log_action(self, log_entry: RoundLog) -> None:
        """Log a player action."""
        if not self.verbose:
            return

        if log_entry.action == PlayerAction.PLAY:
            cards_str = ", ".join(str(c) for c in log_entry.cards_played)
            msg = (
                f"  [{log_entry.round_number}.{log_entry.action_number}] "
                f"{log_entry.player_id}: "
                f"{log_entry.pattern.play_type.name if log_entry.pattern else 'UNKNOWN'} "
                f"({cards_str}) "
                f"[{log_entry.hand_size_after} cards left]"
            )
            if log_entry.is_round_winner:
                msg += " ✓ ROUND WIN"
            self._log(msg)
        elif log_entry.action == PlayerAction.PASS:
            self._log(
                f"  [{log_entry.round_number}.{log_entry.action_number}] "
                f"{log_entry.player_id}: PASS "
                f"[{log_entry.hand_size_after} cards left]"
            )

    def _generate_game_report(self) -> dict:
        """Generate complete game report."""
        report = {
            "game_over": self.state.game_over,
            "total_rounds": self.state.current_round - 1,
            "total_actions": len(self.state.round_logs),
            "finish_order": self.state.finished_players.copy(),
            "final_scores": {},
            "logs": [],
            "scoring_summary": self.state.scoring_engine.get_game_summary(
                self.state.player_ids
            )
        }

        # Final scores
        for player_id in self.state.player_ids:
            report["final_scores"][player_id] = {
                "score": self.state.scoring_engine.calculate_total_score_for_player(player_id),
                "cards_left": len(self.state.player_hands[player_id])
            }

        # Action logs
        for log in self.state.round_logs:
            report["logs"].append({
                "round": log.round_number,
                "action": log.action_number,
                "player": log.player_id,
                "action_type": log.action.value,
                "pattern": log.pattern.play_type.name if log.pattern else None,
                "cards": [str(c) for c in log.cards_played],
                "hand_size_after": log.hand_size_after,
                "is_round_winner": log.is_round_winner
            })

        return report
