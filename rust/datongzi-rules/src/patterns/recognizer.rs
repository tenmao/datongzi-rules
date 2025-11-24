//! Pattern recognition logic for card combinations.

use std::collections::HashMap;

use crate::models::{Card, Rank, Suit};
use super::{PlayPattern, PlayType};

/// Recognizes and analyzes card patterns.
pub struct PatternRecognizer;

impl PatternRecognizer {
    /// Analyze a list of cards and return the recognized pattern.
    ///
    /// Returns `None` if no valid pattern is found.
    ///
    /// # Arguments
    ///
    /// * `cards` - Slice of cards to analyze
    ///
    /// # Returns
    ///
    /// `Some(PlayPattern)` if a valid pattern is recognized, `None` otherwise.
    #[must_use]
    pub fn analyze_cards(cards: &[Card]) -> Option<PlayPattern> {
        if cards.is_empty() {
            return None;
        }

        // Sort cards for easier analysis
        let mut sorted_cards = cards.to_vec();
        sorted_cards.sort();

        // Count cards by rank
        let mut rank_counts: HashMap<Rank, usize> = HashMap::new();
        for card in cards {
            *rank_counts.entry(card.rank).or_insert(0) += 1;
        }

        // Count cards by (suit, rank) for special patterns
        let mut suit_rank_counts: HashMap<(Suit, Rank), usize> = HashMap::new();
        for card in cards {
            *suit_rank_counts.entry((card.suit, card.rank)).or_insert(0) += 1;
        }

        // Check for special patterns first (highest priority)
        if let Some(pattern) = Self::check_dizha(cards, &suit_rank_counts, &rank_counts) {
            return Some(pattern);
        }

        if let Some(pattern) = Self::check_tongzi(cards, &suit_rank_counts, &rank_counts) {
            return Some(pattern);
        }

        if let Some(pattern) = Self::check_bomb(cards, &rank_counts) {
            return Some(pattern);
        }

        // Check for airplane patterns
        // IMPORTANT: Check pure AIRPLANE first, then AIRPLANE_WITH_WINGS
        if let Some(pattern) = Self::check_airplane(cards, &rank_counts) {
            return Some(pattern);
        }

        if let Some(pattern) = Self::check_airplane_with_wings(cards, &rank_counts) {
            return Some(pattern);
        }

        // Check for basic patterns
        if let Some(pattern) = Self::check_triple_with_two(cards, &rank_counts) {
            return Some(pattern);
        }

        if let Some(pattern) = Self::check_triple(cards, &rank_counts) {
            return Some(pattern);
        }

        if let Some(pattern) = Self::check_consecutive_pairs(cards, &rank_counts) {
            return Some(pattern);
        }

        if let Some(pattern) = Self::check_pair(cards, &rank_counts) {
            return Some(pattern);
        }

        if let Some(pattern) = Self::check_single(cards, &rank_counts) {
            return Some(pattern);
        }

        None
    }

    /// Check for single card pattern.
    fn check_single(cards: &[Card], _rank_counts: &HashMap<Rank, usize>) -> Option<PlayPattern> {
        if cards.len() != 1 {
            return None;
        }

        let card = cards[0];
        Some(PlayPattern::new(
            PlayType::Single,
            card.rank,
            Some(card.suit),
            vec![],
            1,
            u32::from(card.rank.value()),
        ))
    }

    /// Check for pair pattern.
    fn check_pair(cards: &[Card], rank_counts: &HashMap<Rank, usize>) -> Option<PlayPattern> {
        if cards.len() != 2 || rank_counts.len() != 1 {
            return None;
        }

        let (&rank, &count) = rank_counts.iter().next()?;
        if count != 2 {
            return None;
        }

        Some(PlayPattern::new(
            PlayType::Pair,
            rank,
            None,
            vec![],
            2,
            u32::from(rank.value()),
        ))
    }

    /// Check for consecutive pairs pattern (连对).
    fn check_consecutive_pairs(
        cards: &[Card],
        rank_counts: &HashMap<Rank, usize>,
    ) -> Option<PlayPattern> {
        if cards.len() < 4 || cards.len() % 2 != 0 {
            return None;
        }

        // All ranks must have exactly 2 cards
        if rank_counts.values().any(|&count| count != 2) {
            return None;
        }

        let mut ranks: Vec<Rank> = rank_counts.keys().copied().collect();
        ranks.sort_by_key(|r| r.value());

        // Check if ranks are consecutive
        if !Self::are_consecutive(&ranks) {
            return None;
        }

        let highest_rank = *ranks.last()?;
        let ranks_len = ranks.len();
        Some(PlayPattern::new(
            PlayType::ConsecutivePairs,
            highest_rank,
            None,
            ranks,
            cards.len(),
            u32::from(highest_rank.value()) * 1000 + ranks_len as u32,
        ))
    }

    /// Check for triple pattern.
    fn check_triple(cards: &[Card], rank_counts: &HashMap<Rank, usize>) -> Option<PlayPattern> {
        if cards.len() != 3 || rank_counts.len() != 1 {
            return None;
        }

        let (&rank, &count) = rank_counts.iter().next()?;
        if count != 3 {
            return None;
        }

        Some(PlayPattern::new(
            PlayType::Triple,
            rank,
            None,
            vec![],
            3,
            u32::from(rank.value()),
        ))
    }

    /// Check for triple with two pattern (三带二).
    fn check_triple_with_two(
        cards: &[Card],
        rank_counts: &HashMap<Rank, usize>,
    ) -> Option<PlayPattern> {
        if cards.len() != 5 || rank_counts.len() != 2 {
            return None;
        }

        let counts: Vec<usize> = rank_counts.values().copied().collect();
        if !(counts.contains(&3) && counts.contains(&2)) {
            return None;
        }

        // Find the triple rank
        let triple_rank = rank_counts
            .iter()
            .find_map(|(&rank, &count)| if count == 3 { Some(rank) } else { None })?;

        Some(PlayPattern::new(
            PlayType::TripleWithTwo,
            triple_rank,
            None,
            vec![],
            5,
            u32::from(triple_rank.value()),
        ))
    }

    /// Check for airplane pattern (consecutive triples).
    fn check_airplane(cards: &[Card], rank_counts: &HashMap<Rank, usize>) -> Option<PlayPattern> {
        if cards.len() < 6 || cards.len() % 3 != 0 {
            return None;
        }

        // All ranks must have exactly 3 cards
        if rank_counts.values().any(|&count| count != 3) {
            return None;
        }

        let mut ranks: Vec<Rank> = rank_counts.keys().copied().collect();
        ranks.sort_by_key(|r| r.value());

        // Check if ranks are consecutive
        if !Self::are_consecutive(&ranks) {
            return None;
        }

        let highest_rank = *ranks.last()?;
        let ranks_len = ranks.len();
        Some(PlayPattern::new(
            PlayType::Airplane,
            highest_rank,
            None,
            ranks,
            cards.len(),
            u32::from(highest_rank.value()) * 1000 + ranks_len as u32,
        ))
    }

    /// Check for airplane with wings pattern (飞机带翅膀).
    ///
    /// Rules: N consecutive triples + K wing cards
    /// where N <= K <= 2N
    /// Wings can be any cards (singles, pairs, triples, bombs, etc.)
    ///
    /// Key: Greedily select the LARGEST consecutive triple sequence
    fn check_airplane_with_wings(
        cards: &[Card],
        rank_counts: &HashMap<Rank, usize>,
    ) -> Option<PlayPattern> {
        if cards.len() < 8 {
            // Minimum: 2 triples (6) + 2 wings (2)
            return None;
        }

        // Find all ranks with at least 3 cards
        let mut triple_candidates: Vec<Rank> = rank_counts
            .iter()
            .filter(|(_, &count)| count >= 3)
            .map(|(&rank, _)| rank)
            .collect();

        if triple_candidates.len() < 2 {
            return None;
        }

        // Sort candidates by rank value
        triple_candidates.sort_by_key(|r| r.value());

        // Strategy: Greedily select the LARGEST consecutive triple sequence
        // Try all possible consecutive triple combinations, preferring larger airplanes
        for length in (2..=triple_candidates.len()).rev() {
            // Start from longest
            for i in 0..=triple_candidates.len() - length {
                let candidate_ranks = &triple_candidates[i..i + length];

                if Self::are_consecutive(candidate_ranks) {
                    let num_triples = candidate_ranks.len();
                    let triple_cards = num_triples * 3;
                    let wing_cards = cards.len() - triple_cards;

                    // Check if wing count is valid: N <= wings <= 2N
                    if wing_cards >= num_triples && wing_cards <= 2 * num_triples {
                        let highest_rank = *candidate_ranks.last()?;
                        return Some(PlayPattern::new(
                            PlayType::AirplaneWithWings,
                            highest_rank,
                            None,
                            candidate_ranks.to_vec(),
                            cards.len(),
                            u32::from(highest_rank.value()) * 1000 + candidate_ranks.len() as u32,
                        ));
                    }
                }
            }
        }

        None
    }

    /// Check for bomb pattern (4+ same rank).
    fn check_bomb(cards: &[Card], rank_counts: &HashMap<Rank, usize>) -> Option<PlayPattern> {
        if cards.len() < 4 || rank_counts.len() != 1 {
            return None;
        }

        let (&rank, &count) = rank_counts.iter().next()?;

        if count < 4 {
            return None;
        }

        Some(PlayPattern::new(
            PlayType::Bomb,
            rank,
            None,
            vec![],
            count,
            u32::from(rank.value()) * 1000 + count as u32,
        ))
    }

    /// Check for tongzi pattern (3 same rank same suit).
    fn check_tongzi(
        cards: &[Card],
        suit_rank_counts: &HashMap<(Suit, Rank), usize>,
        rank_counts: &HashMap<Rank, usize>,
    ) -> Option<PlayPattern> {
        if cards.len() != 3 || rank_counts.len() != 1 {
            return None;
        }

        // Must have exactly one suit-rank combination with 3 cards
        if suit_rank_counts.len() != 1 {
            return None;
        }

        let (&(suit, rank), &count) = suit_rank_counts.iter().next()?;
        if count != 3 {
            return None;
        }

        Some(PlayPattern::new(
            PlayType::Tongzi,
            rank,
            Some(suit),
            vec![],
            3,
            u32::from(rank.value()) * 10000 + u32::from(suit.value()) * 1000,
        ))
    }

    /// Check for dizha pattern (2 of each suit for same rank).
    fn check_dizha(
        cards: &[Card],
        suit_rank_counts: &HashMap<(Suit, Rank), usize>,
        rank_counts: &HashMap<Rank, usize>,
    ) -> Option<PlayPattern> {
        if cards.len() != 8 || rank_counts.len() != 1 {
            return None;
        }

        let &rank = rank_counts.keys().next()?;

        // Must have exactly 2 cards of each suit for this rank
        let suits_for_rank: Vec<Suit> = suit_rank_counts
            .keys()
            .filter(|(_, r)| *r == rank)
            .map(|(s, _)| *s)
            .collect();

        if suits_for_rank.len() != 4 {
            // All 4 suits
            return None;
        }

        // Each suit must have exactly 2 cards
        for suit in [Suit::Diamonds, Suit::Clubs, Suit::Hearts, Suit::Spades] {
            if suit_rank_counts.get(&(suit, rank)) != Some(&2) {
                return None;
            }
        }

        Some(PlayPattern::new(
            PlayType::Dizha,
            rank,
            None,
            vec![],
            8,
            u32::from(rank.value()) * 100000,
        ))
    }

    /// Check if ranks are consecutive.
    fn are_consecutive(ranks: &[Rank]) -> bool {
        if ranks.len() <= 1 {
            return true;
        }

        // Convert to values for comparison
        let values: Vec<u8> = ranks.iter().map(|r| r.value()).collect();

        // Check normal consecutive sequence
        for i in 1..values.len() {
            if values[i] != values[i - 1] + 1 {
                return false;
            }
        }

        true
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_single_pattern() {
        let cards = vec![Card::new(Suit::Spades, Rank::Ace)];
        let pattern = PatternRecognizer::analyze_cards(&cards);
        assert!(pattern.is_some());
        let pattern = pattern.unwrap();
        assert_eq!(pattern.play_type, PlayType::Single);
        assert_eq!(pattern.primary_rank, Rank::Ace);
        assert_eq!(pattern.strength, 14);
    }

    #[test]
    fn test_pair_pattern() {
        let cards = vec![
            Card::new(Suit::Spades, Rank::Ace),
            Card::new(Suit::Hearts, Rank::Ace),
        ];
        let pattern = PatternRecognizer::analyze_cards(&cards);
        assert!(pattern.is_some());
        let pattern = pattern.unwrap();
        assert_eq!(pattern.play_type, PlayType::Pair);
        assert_eq!(pattern.primary_rank, Rank::Ace);
    }

    #[test]
    fn test_consecutive_pairs() {
        let cards = vec![
            Card::new(Suit::Spades, Rank::Three),
            Card::new(Suit::Hearts, Rank::Three),
            Card::new(Suit::Spades, Rank::Four),
            Card::new(Suit::Hearts, Rank::Four),
        ];
        let pattern = PatternRecognizer::analyze_cards(&cards);
        assert!(pattern.is_some());
        let pattern = pattern.unwrap();
        assert_eq!(pattern.play_type, PlayType::ConsecutivePairs);
        assert_eq!(pattern.primary_rank, Rank::Four);
    }

    #[test]
    fn test_triple_pattern() {
        let cards = vec![
            Card::new(Suit::Spades, Rank::King),
            Card::new(Suit::Hearts, Rank::King),
            Card::new(Suit::Clubs, Rank::King),
        ];
        let pattern = PatternRecognizer::analyze_cards(&cards);
        assert!(pattern.is_some());
        let pattern = pattern.unwrap();
        // Should be Triple, not Tongzi (different suits)
        assert_eq!(pattern.play_type, PlayType::Triple);
        assert_eq!(pattern.primary_rank, Rank::King);
    }

    #[test]
    fn test_tongzi_pattern() {
        let cards = vec![
            Card::new(Suit::Spades, Rank::King),
            Card::new(Suit::Spades, Rank::King),
            Card::new(Suit::Spades, Rank::King),
        ];
        let pattern = PatternRecognizer::analyze_cards(&cards);
        assert!(pattern.is_some());
        let pattern = pattern.unwrap();
        assert_eq!(pattern.play_type, PlayType::Tongzi);
        assert_eq!(pattern.primary_rank, Rank::King);
        assert_eq!(pattern.primary_suit, Some(Suit::Spades));
    }

    #[test]
    fn test_bomb_pattern() {
        let cards = vec![
            Card::new(Suit::Spades, Rank::Ace),
            Card::new(Suit::Hearts, Rank::Ace),
            Card::new(Suit::Clubs, Rank::Ace),
            Card::new(Suit::Diamonds, Rank::Ace),
        ];
        let pattern = PatternRecognizer::analyze_cards(&cards);
        assert!(pattern.is_some());
        let pattern = pattern.unwrap();
        assert_eq!(pattern.play_type, PlayType::Bomb);
        assert_eq!(pattern.primary_rank, Rank::Ace);
        assert_eq!(pattern.card_count, 4);
    }

    #[test]
    fn test_dizha_pattern() {
        let cards = vec![
            Card::new(Suit::Spades, Rank::Two),
            Card::new(Suit::Spades, Rank::Two),
            Card::new(Suit::Hearts, Rank::Two),
            Card::new(Suit::Hearts, Rank::Two),
            Card::new(Suit::Clubs, Rank::Two),
            Card::new(Suit::Clubs, Rank::Two),
            Card::new(Suit::Diamonds, Rank::Two),
            Card::new(Suit::Diamonds, Rank::Two),
        ];
        let pattern = PatternRecognizer::analyze_cards(&cards);
        assert!(pattern.is_some());
        let pattern = pattern.unwrap();
        assert_eq!(pattern.play_type, PlayType::Dizha);
        assert_eq!(pattern.primary_rank, Rank::Two);
    }

    #[test]
    fn test_airplane_pattern() {
        let cards = vec![
            Card::new(Suit::Spades, Rank::Three),
            Card::new(Suit::Hearts, Rank::Three),
            Card::new(Suit::Clubs, Rank::Three),
            Card::new(Suit::Spades, Rank::Four),
            Card::new(Suit::Hearts, Rank::Four),
            Card::new(Suit::Clubs, Rank::Four),
        ];
        let pattern = PatternRecognizer::analyze_cards(&cards);
        assert!(pattern.is_some());
        let pattern = pattern.unwrap();
        assert_eq!(pattern.play_type, PlayType::Airplane);
        assert_eq!(pattern.primary_rank, Rank::Four);
    }

    #[test]
    fn test_are_consecutive() {
        let ranks = vec![Rank::Three, Rank::Four, Rank::Five];
        assert!(PatternRecognizer::are_consecutive(&ranks));

        let ranks = vec![Rank::Three, Rank::Five];
        assert!(!PatternRecognizer::are_consecutive(&ranks));

        let ranks = vec![Rank::Ace];
        assert!(PatternRecognizer::are_consecutive(&ranks));
    }
}
