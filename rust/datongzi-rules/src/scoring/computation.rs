//! Scoring rules and calculations for Da Tong Zi game.

use std::collections::HashMap;

use crate::models::{Card, GameConfig, Rank};
use crate::patterns::{PlayPattern, PlayType};

/// Types of bonus scoring in the game.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum BonusType {
    /// Round win bonus (base score from 5/10/K)
    RoundWin,
    /// K Tongzi bonus (100 points default)
    KTongzi,
    /// A Tongzi bonus (200 points default)
    ATongzi,
    /// 2 Tongzi bonus (300 points default)
    TwoTongzi,
    /// Dizha bonus (400 points default)
    Dizha,
    /// Finish first (上游, +100 default)
    FinishFirst,
    /// Finish second (二游, -40 default)
    FinishSecond,
    /// Finish third (三游, -60 default)
    FinishThird,
}

/// Represents a single scoring event.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ScoringEvent {
    /// Player ID
    pub player_id: String,
    /// Type of bonus
    pub bonus_type: BonusType,
    /// Points awarded (can be negative)
    pub points: i32,
    /// Human-readable reason
    pub reason: String,
    /// Round number (if applicable)
    pub round_number: Option<usize>,
    /// Cards involved in scoring (display format)
    pub cards_involved: Vec<String>,
}

/// Game scoring summary
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct GameSummary {
    /// Final scores for each player
    pub final_scores: HashMap<String, i32>,
    /// Winner player ID
    pub winner_id: Option<String>,
    /// Total number of scoring events
    pub total_events: usize,
}

impl ScoringEvent {
    /// Creates a new scoring event
    #[must_use]
    pub fn new(
        player_id: String,
        bonus_type: BonusType,
        points: i32,
        reason: String,
        round_number: Option<usize>,
        cards_involved: Vec<String>,
    ) -> Self {
        Self {
            player_id,
            bonus_type,
            points,
            reason,
            round_number,
            cards_involved,
        }
    }
}

/// Handles all scoring calculations and bonus awards.
///
/// Note: This is a pure calculation engine. It does NOT modify player state.
/// Server layer is responsible for applying scores to players.
#[derive(Debug, Clone)]
pub struct ScoreComputation {
    config: GameConfig,
    scoring_events: Vec<ScoringEvent>,
}

impl ScoreComputation {
    /// Creates a new scoring computation engine with game configuration
    #[must_use]
    pub fn new(config: GameConfig) -> Self {
        Self {
            config,
            scoring_events: Vec::new(),
        }
    }

    /// Calculates base score from cards in a round.
    ///
    /// # Arguments
    ///
    /// * `cards` - All cards played in the round
    ///
    /// # Returns
    ///
    /// Total points from scoring cards (5, 10, K)
    #[must_use]
    pub fn calculate_round_base_score(&self, cards: &[Card]) -> i32 {
        cards
            .iter()
            .filter(|c| c.is_scoring_card())
            .map(|c| c.score_value())
            .sum()
    }

    /// Creates scoring event for round winner.
    ///
    /// # Arguments
    ///
    /// * `player_id` - ID of the player who won
    /// * `round_cards` - All cards played in the round
    /// * `round_number` - Current round number
    ///
    /// # Returns
    ///
    /// `Some(ScoringEvent)` if there are scoring cards, `None` otherwise
    pub fn create_round_win_event(
        &mut self,
        player_id: String,
        round_cards: &[Card],
        round_number: usize,
    ) -> Option<ScoringEvent> {
        let base_score = self.calculate_round_base_score(round_cards);

        if base_score > 0 {
            let scoring_cards: Vec<String> = round_cards
                .iter()
                .filter(|c| c.is_scoring_card())
                .map(|c| c.to_string())
                .collect();

            let event = ScoringEvent::new(
                player_id,
                BonusType::RoundWin,
                base_score,
                format!("Round {round_number} win with {base_score} scoring cards"),
                Some(round_number),
                scoring_cards,
            );

            self.scoring_events.push(event.clone());
            return Some(event);
        }

        None
    }

    /// Creates scoring events for special bonuses (Tongzi, Dizha).
    ///
    /// IMPORTANT: According to game rules, only the FINAL winning play of a round
    /// receives special bonuses. If player A plays K Tongzi and player B beats it
    /// with A Tongzi, only player B gets the bonus (200 points), player A gets nothing.
    ///
    /// # Arguments
    ///
    /// * `player_id` - ID of the player who won
    /// * `winning_pattern` - The winning pattern
    /// * `round_number` - Current round number
    /// * `is_round_winning_play` - Whether this is the final winning play of the round.
    ///   Only when `true` will special bonuses be awarded. Default `true` for
    ///   backward compatibility.
    ///
    /// # Returns
    ///
    /// List of `ScoringEvent`s for bonuses (empty if not round winning play)
    pub fn create_special_bonus_events(
        &mut self,
        player_id: String,
        winning_pattern: &PlayPattern,
        round_number: usize,
        is_round_winning_play: bool,
    ) -> Vec<ScoringEvent> {
        let mut events = Vec::new();

        // Only award special bonuses if this is the round winning play
        if !is_round_winning_play {
            return events;
        }

        match winning_pattern.play_type {
            PlayType::Tongzi => {
                if let Some((bonus_points, bonus_type)) =
                    self.get_tongzi_bonus(winning_pattern.primary_rank)
                {
                    let event = ScoringEvent::new(
                        player_id,
                        bonus_type,
                        bonus_points,
                        format!(
                            "{:?} Tongzi in round {round_number}",
                            winning_pattern.primary_rank
                        ),
                        Some(round_number),
                        Vec::new(),
                    );
                    events.push(event.clone());
                    self.scoring_events.push(event);
                }
            }
            PlayType::Dizha => {
                let bonus_points = self.config.dizha_bonus();
                let event = ScoringEvent::new(
                    player_id,
                    BonusType::Dizha,
                    bonus_points,
                    format!(
                        "{:?} Dizha in round {round_number}",
                        winning_pattern.primary_rank
                    ),
                    Some(round_number),
                    Vec::new(),
                );
                events.push(event.clone());
                self.scoring_events.push(event);
            }
            _ => {}
        }

        events
    }

    /// Creates finish position bonus events (上游, 二游, 三游).
    ///
    /// # Arguments
    ///
    /// * `player_ids_in_finish_order` - Player IDs sorted by finish order
    ///
    /// # Returns
    ///
    /// List of `ScoringEvent`s for finish bonuses
    pub fn create_finish_bonus_events(
        &mut self,
        player_ids_in_finish_order: &[String],
    ) -> Vec<ScoringEvent> {
        let mut events = Vec::new();

        for (i, player_id) in player_ids_in_finish_order.iter().enumerate() {
            if i < self.config.finish_bonus().len() {
                let bonus_points = self.config.finish_bonus()[i];

                let (bonus_type, position_name) = match i {
                    0 => (BonusType::FinishFirst, "上游"),
                    1 => (BonusType::FinishSecond, "二游"),
                    _ => (BonusType::FinishThird, "三游"),
                };

                let event = ScoringEvent::new(
                    player_id.clone(),
                    bonus_type,
                    bonus_points,
                    format!("Finished in position {} ({position_name})", i + 1),
                    None,
                    Vec::new(),
                );
                events.push(event.clone());
                self.scoring_events.push(event);
            }
        }

        events
    }

    /// Calculates total score for a player from all events.
    ///
    /// # Arguments
    ///
    /// * `player_id` - Player ID to calculate for
    ///
    /// # Returns
    ///
    /// Total score from all events
    #[must_use]
    pub fn calculate_total_score_for_player(&self, player_id: &str) -> i32 {
        self.scoring_events
            .iter()
            .filter(|e| e.player_id == player_id)
            .map(|e| e.points)
            .sum()
    }

    /// Validates that provided scores match recorded events.
    ///
    /// # Arguments
    ///
    /// * `player_scores` - Map of player_id -> current_score
    ///
    /// # Returns
    ///
    /// `true` if scores are consistent with events
    #[must_use]
    pub fn validate_scores(&self, player_scores: &HashMap<String, i32>) -> bool {
        for (player_id, &recorded_score) in player_scores {
            let calculated_score = self.calculate_total_score_for_player(player_id);
            if calculated_score != recorded_score {
                return false;
            }
        }
        true
    }

    /// Returns a reference to all scoring events
    #[must_use]
    pub fn scoring_events(&self) -> &[ScoringEvent] {
        &self.scoring_events
    }

    /// Generates a comprehensive game scoring summary.
    ///
    /// # Arguments
    ///
    /// * `player_ids` - All player IDs in the game
    ///
    /// # Returns
    ///
    /// `GameSummary` containing detailed scoring breakdown
    #[must_use]
    pub fn get_game_summary(&self, player_ids: &[String]) -> GameSummary {
        let mut final_scores = HashMap::new();
        for player_id in player_ids {
            final_scores.insert(
                player_id.clone(),
                self.calculate_total_score_for_player(player_id),
            );
        }

        let winner_id = final_scores
            .iter()
            .max_by_key(|(_, &score)| score)
            .map(|(id, _)| id.clone());

        GameSummary {
            final_scores,
            winner_id,
            total_events: self.scoring_events.len(),
        }
    }

    // Private helper methods

    fn get_tongzi_bonus(&self, rank: Rank) -> Option<(i32, BonusType)> {
        match rank {
            Rank::King => Some((self.config.k_tongzi_bonus(), BonusType::KTongzi)),
            Rank::Ace => Some((self.config.a_tongzi_bonus(), BonusType::ATongzi)),
            Rank::Two => Some((self.config.two_tongzi_bonus(), BonusType::TwoTongzi)),
            _ => None,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::models::Suit;

    #[test]
    fn test_calculate_round_base_score() {
        let config = GameConfig::default();
        let engine = ScoreComputation::new(config);

        let cards = vec![
            Card::new(Suit::Spades, Rank::Five),  // 5 points
            Card::new(Suit::Hearts, Rank::Ten),   // 10 points
            Card::new(Suit::Clubs, Rank::King),   // 10 points
            Card::new(Suit::Diamonds, Rank::Six), // 0 points
        ];

        let score = engine.calculate_round_base_score(&cards);
        assert_eq!(score, 25, "Expected 25, got {score}");
    }

    #[test]
    fn test_calculate_round_base_score_no_scoring_cards() {
        let config = GameConfig::default();
        let engine = ScoreComputation::new(config);

        let cards = vec![
            Card::new(Suit::Spades, Rank::Six),
            Card::new(Suit::Hearts, Rank::Seven),
            Card::new(Suit::Clubs, Rank::Eight),
        ];

        let score = engine.calculate_round_base_score(&cards);
        assert_eq!(score, 0, "Expected 0, got {score}");
    }

    #[test]
    fn test_create_round_win_event() {
        let config = GameConfig::default();
        let mut engine = ScoreComputation::new(config);

        let cards = vec![
            Card::new(Suit::Spades, Rank::Five),
            Card::new(Suit::Hearts, Rank::Ten),
        ];

        let event = engine.create_round_win_event("player1".to_string(), &cards, 1);

        assert!(event.is_some());
        let event = event.unwrap();
        assert_eq!(event.player_id, "player1");
        assert_eq!(event.bonus_type, BonusType::RoundWin);
        assert_eq!(event.points, 15);
        assert_eq!(event.round_number, Some(1));
        assert_eq!(event.cards_involved.len(), 2);
    }

    #[test]
    fn test_create_round_win_event_no_points() {
        let config = GameConfig::default();
        let mut engine = ScoreComputation::new(config);

        let cards = vec![Card::new(Suit::Spades, Rank::Six)];

        let event = engine.create_round_win_event("player1".to_string(), &cards, 1);

        assert!(event.is_none());
    }

    #[test]
    fn test_tongzi_bonuses() {
        let config = GameConfig::default();
        let mut engine = ScoreComputation::new(config);

        // K Tongzi
        let pattern = PlayPattern::new(
            PlayType::Tongzi,
            Rank::King,
            Some(Suit::Spades),
            vec![],
            3,
            0,
        );
        let events = engine.create_special_bonus_events("player1".to_string(), &pattern, 1, true);
        assert_eq!(events.len(), 1);
        assert_eq!(events[0].bonus_type, BonusType::KTongzi);
        assert_eq!(events[0].points, 100);

        // A Tongzi
        let pattern = PlayPattern::new(
            PlayType::Tongzi,
            Rank::Ace,
            Some(Suit::Hearts),
            vec![],
            3,
            0,
        );
        let events = engine.create_special_bonus_events("player2".to_string(), &pattern, 2, true);
        assert_eq!(events.len(), 1);
        assert_eq!(events[0].bonus_type, BonusType::ATongzi);
        assert_eq!(events[0].points, 200);

        // 2 Tongzi
        let pattern =
            PlayPattern::new(PlayType::Tongzi, Rank::Two, Some(Suit::Clubs), vec![], 3, 0);
        let events = engine.create_special_bonus_events("player3".to_string(), &pattern, 3, true);
        assert_eq!(events.len(), 1);
        assert_eq!(events[0].bonus_type, BonusType::TwoTongzi);
        assert_eq!(events[0].points, 300);
    }

    #[test]
    fn test_dizha_bonus() {
        let config = GameConfig::default();
        let mut engine = ScoreComputation::new(config);

        let pattern = PlayPattern::new(PlayType::Dizha, Rank::Ten, None, vec![], 8, 0);
        let events = engine.create_special_bonus_events("player1".to_string(), &pattern, 1, true);

        assert_eq!(events.len(), 1);
        assert_eq!(events[0].bonus_type, BonusType::Dizha);
        assert_eq!(events[0].points, 400);
    }

    #[test]
    fn test_finish_bonus_events() {
        let config = GameConfig::default();
        let mut engine = ScoreComputation::new(config);

        let player_ids = vec![
            "player1".to_string(),
            "player2".to_string(),
            "player3".to_string(),
        ];

        let events = engine.create_finish_bonus_events(&player_ids);

        assert_eq!(events.len(), 3);

        // First place (上游)
        assert_eq!(events[0].player_id, "player1");
        assert_eq!(events[0].bonus_type, BonusType::FinishFirst);
        assert_eq!(events[0].points, 100);

        // Second place (二游)
        assert_eq!(events[1].player_id, "player2");
        assert_eq!(events[1].bonus_type, BonusType::FinishSecond);
        assert_eq!(events[1].points, -40);

        // Third place (三游)
        assert_eq!(events[2].player_id, "player3");
        assert_eq!(events[2].bonus_type, BonusType::FinishThird);
        assert_eq!(events[2].points, -60);
    }

    #[test]
    fn test_calculate_total_score() {
        let config = GameConfig::default();
        let mut engine = ScoreComputation::new(config);

        // Manually add events
        engine.scoring_events.push(ScoringEvent::new(
            "player1".to_string(),
            BonusType::RoundWin,
            15,
            "Round 1".to_string(),
            Some(1),
            vec![],
        ));
        engine.scoring_events.push(ScoringEvent::new(
            "player1".to_string(),
            BonusType::KTongzi,
            100,
            "K Tongzi".to_string(),
            Some(1),
            vec![],
        ));
        engine.scoring_events.push(ScoringEvent::new(
            "player2".to_string(),
            BonusType::RoundWin,
            25,
            "Round 2".to_string(),
            Some(2),
            vec![],
        ));
        engine.scoring_events.push(ScoringEvent::new(
            "player1".to_string(),
            BonusType::FinishFirst,
            100,
            "First place".to_string(),
            None,
            vec![],
        ));

        let score1 = engine.calculate_total_score_for_player("player1");
        let score2 = engine.calculate_total_score_for_player("player2");

        assert_eq!(score1, 215, "Expected 215, got {score1}");
        assert_eq!(score2, 25, "Expected 25, got {score2}");
    }

    #[test]
    fn test_round_winning_play_only() {
        let config = GameConfig::default();
        let mut engine = ScoreComputation::new(config);

        let pattern = PlayPattern::new(
            PlayType::Tongzi,
            Rank::King,
            Some(Suit::Spades),
            vec![],
            3,
            0,
        );

        // Not a round winning play - should get no bonus
        let events = engine.create_special_bonus_events("player1".to_string(), &pattern, 1, false);
        assert_eq!(events.len(), 0);

        // Round winning play - should get bonus
        let events = engine.create_special_bonus_events("player2".to_string(), &pattern, 1, true);
        assert_eq!(events.len(), 1);
        assert_eq!(events[0].points, 100);
    }

    #[test]
    fn test_validate_scores() {
        let config = GameConfig::default();
        let mut engine = ScoreComputation::new(config);

        engine.scoring_events.push(ScoringEvent::new(
            "player1".to_string(),
            BonusType::RoundWin,
            15,
            "Round 1".to_string(),
            Some(1),
            vec![],
        ));
        engine.scoring_events.push(ScoringEvent::new(
            "player2".to_string(),
            BonusType::RoundWin,
            25,
            "Round 2".to_string(),
            Some(2),
            vec![],
        ));

        let mut correct_scores = HashMap::new();
        correct_scores.insert("player1".to_string(), 15);
        correct_scores.insert("player2".to_string(), 25);
        assert!(engine.validate_scores(&correct_scores));

        let mut incorrect_scores = HashMap::new();
        incorrect_scores.insert("player1".to_string(), 20);
        incorrect_scores.insert("player2".to_string(), 25);
        assert!(!engine.validate_scores(&incorrect_scores));
    }

    #[test]
    fn test_custom_config_bonuses() {
        let config = GameConfig::new(3, 3, 41, 9, vec![200, -50, -150], 150, 250, 350, 500);
        let mut engine = ScoreComputation::new(config);

        // Test K Tongzi with custom bonus
        let pattern = PlayPattern::new(
            PlayType::Tongzi,
            Rank::King,
            Some(Suit::Spades),
            vec![],
            3,
            0,
        );
        let events = engine.create_special_bonus_events("player1".to_string(), &pattern, 1, true);
        assert_eq!(events.len(), 1);
        assert_eq!(events[0].points, 150);

        // Test finish bonuses with custom values
        let finish_events = engine.create_finish_bonus_events(&[
            "p1".to_string(),
            "p2".to_string(),
            "p3".to_string(),
        ]);
        assert_eq!(finish_events[0].points, 200);
        assert_eq!(finish_events[1].points, -50);
        assert_eq!(finish_events[2].points, -150);
    }
}
