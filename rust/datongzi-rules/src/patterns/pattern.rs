//! Pattern types and structures for card combinations.

use crate::models::{Rank, Suit};

/// Play types in order of strength.
///
/// Higher values beat lower values, with special rules for some types.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
#[repr(u8)]
pub enum PlayType {
    /// Single card (单牌)
    Single = 1,
    /// Pair of cards (对子)
    Pair = 2,
    /// Consecutive pairs (连对, 2+ pairs in sequence)
    ConsecutivePairs = 3,
    /// Triple (三张)
    Triple = 4,
    /// Triple with two kickers (三带二)
    TripleWithTwo = 5,
    /// Airplane - consecutive triples (飞机)
    Airplane = 6,
    /// Airplane with wings (飞机带翅膀)
    AirplaneWithWings = 7,
    /// Bomb - 4+ same rank (炸弹)
    Bomb = 8,
    /// Tongzi - 3 same rank same suit (筒子)
    Tongzi = 9,
    /// Dizha - 2 of each suit for same rank (地炸, 8 cards)
    Dizha = 10,
}

/// Represents a recognized pattern of cards.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PlayPattern {
    /// Type of play
    pub play_type: PlayType,
    /// Main rank of the pattern
    pub primary_rank: Rank,
    /// Primary suit (for suit-dependent patterns like Tongzi)
    pub primary_suit: Option<Suit>,
    /// Secondary ranks (for consecutive patterns)
    pub secondary_ranks: Vec<Rank>,
    /// Total number of cards in this pattern
    pub card_count: usize,
    /// Calculated strength for comparison
    pub strength: u32,
}

impl PlayPattern {
    /// Creates a new PlayPattern
    #[must_use]
    pub fn new(
        play_type: PlayType,
        primary_rank: Rank,
        primary_suit: Option<Suit>,
        secondary_ranks: Vec<Rank>,
        card_count: usize,
        strength: u32,
    ) -> Self {
        Self {
            play_type,
            primary_rank,
            primary_suit,
            secondary_ranks,
            card_count,
            strength,
        }
    }

    /// Returns the play type
    #[must_use]
    pub const fn play_type(&self) -> PlayType {
        self.play_type
    }

    /// Returns the primary rank
    #[must_use]
    pub const fn primary_rank(&self) -> Rank {
        self.primary_rank
    }

    /// Returns the primary suit if any
    #[must_use]
    pub const fn primary_suit(&self) -> Option<Suit> {
        self.primary_suit
    }

    /// Returns the secondary ranks
    #[must_use]
    pub fn secondary_ranks(&self) -> &[Rank] {
        &self.secondary_ranks
    }

    /// Returns the total card count
    #[must_use]
    pub const fn card_count(&self) -> usize {
        self.card_count
    }

    /// Returns the pattern strength
    #[must_use]
    pub const fn strength(&self) -> u32 {
        self.strength
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_play_type_ordering() {
        assert!(PlayType::Single < PlayType::Pair);
        assert!(PlayType::Pair < PlayType::Bomb);
        assert!(PlayType::Bomb < PlayType::Tongzi);
        assert!(PlayType::Tongzi < PlayType::Dizha);
    }

    #[test]
    fn test_play_pattern_creation() {
        let pattern = PlayPattern::new(
            PlayType::Single,
            Rank::Ace,
            Some(Suit::Spades),
            vec![],
            1,
            14,
        );

        assert_eq!(pattern.play_type(), PlayType::Single);
        assert_eq!(pattern.primary_rank(), Rank::Ace);
        assert_eq!(pattern.primary_suit(), Some(Suit::Spades));
        assert_eq!(pattern.card_count(), 1);
        assert_eq!(pattern.strength(), 14);
    }
}
