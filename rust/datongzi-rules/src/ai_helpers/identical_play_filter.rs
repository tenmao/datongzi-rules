//! Identical Play Filtering
//!
//! Reduces duplicate play patterns by filtering identical plays (same rank, different suits)
//! while protecting Tongzi (筒子) and Dizha (地炸) structures.
//!
//! ## Rules:
//! - **Singles**: Keep only one suit per rank, prefer non-protected suits
//! - **Pairs**: Keep only one suit combination per rank
//! - **Triples**: Keep only one combination per rank (except Tongzi)
//! - **Bombs**: No filtering needed (4+ cards)
//!
//! ## Tongzi and Dizha:
//! - **Tongzi (筒子)**: 3 cards of same suit and same rank (e.g., ♠5♠5♠5)
//! - **Dizha (地炸)**: Each suit has 2 cards of the same rank (e.g., ♠J♠J + ♥J♥J + ♣J♣J + ♦J♦J)

use crate::models::{Card, Rank, Suit};
use std::collections::HashSet;

/// Detects all Tongzi (筒子) structures in hand.
///
/// A Tongzi is 3 cards of the same suit and same rank.
///
/// # Example
/// ```
/// // ♠5♠5♠5 is a Tongzi
/// // Returns: vec![(Suit::Spades, Rank::Five)]
/// ```
pub fn detect_tongzi(hand: &[Card]) -> Vec<(Suit, Rank)> {
    let mut tongzi_list = Vec::new();

    // Count cards by (suit, rank)
    for suit in [Suit::Spades, Suit::Hearts, Suit::Clubs, Suit::Diamonds] {
        for rank in [
            Rank::Five,
            Rank::Six,
            Rank::Seven,
            Rank::Eight,
            Rank::Nine,
            Rank::Ten,
            Rank::Jack,
            Rank::Queen,
            Rank::King,
            Rank::Ace,
            Rank::Two,
        ] {
            let count = hand
                .iter()
                .filter(|c| c.suit == suit && c.rank == rank)
                .count();

            // Tongzi requires exactly 3 cards of same suit and rank
            if count >= 3 {
                tongzi_list.push((suit, rank));
            }
        }
    }

    tongzi_list
}

/// Detects all Dizha (地炸) structures in hand.
///
/// A Dizha requires each of the 4 suits to have exactly 2 cards of the same rank.
///
/// # Example
/// ```
/// // ♠J♠J + ♥J♥J + ♣J♣J + ♦J♦J (8 cards total) is a Dizha
/// // Returns: vec![Rank::Jack]
/// ```
pub fn detect_dizha(hand: &[Card]) -> Vec<Rank> {
    let mut dizha_list = Vec::new();

    for rank in [
        Rank::Five,
        Rank::Six,
        Rank::Seven,
        Rank::Eight,
        Rank::Nine,
        Rank::Ten,
        Rank::Jack,
        Rank::Queen,
        Rank::King,
        Rank::Ace,
        Rank::Two,
    ] {
        // Check if all 4 suits have at least 2 cards of this rank
        let mut all_suits_have_pair = true;
        for suit in [Suit::Spades, Suit::Hearts, Suit::Clubs, Suit::Diamonds] {
            let count = hand
                .iter()
                .filter(|c| c.suit == suit && c.rank == rank)
                .count();
            if count < 2 {
                all_suits_have_pair = false;
                break;
            }
        }

        if all_suits_have_pair {
            dizha_list.push(rank);
        }
    }

    dizha_list
}

/// Gets all protected suits for a specific rank.
///
/// A suit is protected if removing a card of that rank would break a Tongzi or Dizha.
///
/// # Arguments
/// * `hand` - Complete hand
/// * `rank` - The rank to check
///
/// # Returns
/// Set of protected suits for this rank
pub fn get_protected_suits(hand: &[Card], rank: Rank) -> HashSet<Suit> {
    let mut protected = HashSet::new();

    // Detect all Tongzi and Dizha
    let tongzi_list = detect_tongzi(hand);
    let dizha_list = detect_dizha(hand);

    // Check if this rank is part of any Tongzi
    // Tongzi: (suit, rank) means that suit+rank has 3+ cards
    for (suit, tongzi_rank) in tongzi_list {
        if tongzi_rank == rank {
            protected.insert(suit);
        }
    }

    // Check if this rank is part of any Dizha
    // Dizha: all 4 suits have 2+ cards of this rank
    for dizha_rank in dizha_list {
        if dizha_rank == rank {
            // All suits are protected for this rank
            protected.insert(Suit::Spades);
            protected.insert(Suit::Hearts);
            protected.insert(Suit::Clubs);
            protected.insert(Suit::Diamonds);
        }
    }

    protected
}

/// Selects a safe suit for a given rank.
///
/// Prefers suits that are not protected (not in Tongzi/Dizha).
/// If all suits are protected, returns the lowest suit value.
///
/// # Arguments
/// * `hand` - Complete hand
/// * `rank` - The rank to select a suit for
///
/// # Returns
/// The selected safe suit
pub fn select_safe_suit(hand: &[Card], rank: Rank) -> Option<Suit> {
    let cards_of_rank: Vec<&Card> = hand.iter().filter(|c| c.rank == rank).collect();

    if cards_of_rank.is_empty() {
        return None;
    }

    let protected_suits = get_protected_suits(hand, rank);

    // Try to find a non-protected suit
    for card in &cards_of_rank {
        if !protected_suits.contains(&card.suit) {
            return Some(card.suit);
        }
    }

    // All suits are protected, return the lowest suit
    Some(cards_of_rank[0].suit)
}

/// Filters singles to keep only one per rank.
///
/// For each rank, keeps only one card with a safe suit (preferring non-protected suits).
///
/// # Arguments
/// * `hand` - Complete hand
///
/// # Returns
/// Filtered list of single cards
pub fn filter_singles(hand: &[Card]) -> Vec<Vec<Card>> {
    let mut singles = Vec::new();
    let mut seen_ranks = HashSet::new();

    // Group by rank
    let mut ranks: Vec<Rank> = hand.iter().map(|c| c.rank).collect();
    ranks.sort_by_key(|r| *r as u8);
    ranks.dedup();

    for rank in ranks {
        if seen_ranks.contains(&rank) {
            continue;
        }
        seen_ranks.insert(rank);

        // Select safe suit for this rank
        if let Some(suit) = select_safe_suit(hand, rank) {
            // Find the card with this rank and suit
            if let Some(card) = hand.iter().find(|c| c.rank == rank && c.suit == suit) {
                singles.push(vec![card.clone()]);
            }
        }
    }

    singles
}

/// Filters pairs to keep only one combination per rank.
///
/// For each rank with 2+ cards, keeps only one pair using safe suits.
///
/// # Arguments
/// * `hand` - Complete hand
///
/// # Returns
/// Filtered list of pairs
pub fn filter_pairs(hand: &[Card]) -> Vec<Vec<Card>> {
    let mut pairs = Vec::new();
    let mut seen_ranks = HashSet::new();

    // Group by rank
    let mut rank_groups: Vec<(Rank, Vec<&Card>)> = Vec::new();
    for rank in [
        Rank::Five,
        Rank::Six,
        Rank::Seven,
        Rank::Eight,
        Rank::Nine,
        Rank::Ten,
        Rank::Jack,
        Rank::Queen,
        Rank::King,
        Rank::Ace,
        Rank::Two,
    ] {
        let cards: Vec<&Card> = hand.iter().filter(|c| c.rank == rank).collect();
        if cards.len() >= 2 {
            rank_groups.push((rank, cards));
        }
    }

    for (rank, cards) in rank_groups {
        if seen_ranks.contains(&rank) {
            continue;
        }
        seen_ranks.insert(rank);

        let protected_suits = get_protected_suits(hand, rank);

        // Find 2 cards with different suits, preferring non-protected
        let mut selected = Vec::new();

        // First, try to get 2 non-protected suits
        for card in &cards {
            if !protected_suits.contains(&card.suit) && selected.len() < 2 {
                selected.push((*card).clone());
            }
        }

        // If not enough, add protected suits
        if selected.len() < 2 {
            for card in &cards {
                if selected.len() < 2 && !selected.iter().any(|c| c.suit == card.suit) {
                    selected.push((*card).clone());
                }
            }
        }

        if selected.len() == 2 {
            pairs.push(selected);
        }
    }

    pairs
}

/// Filters triples to keep only one combination per rank.
///
/// For each rank with 3+ cards, keeps only one triple using safe suits.
///
/// # Arguments
/// * `hand` - Complete hand
///
/// # Returns
/// Filtered list of triples
pub fn filter_triples(hand: &[Card]) -> Vec<Vec<Card>> {
    let mut triples = Vec::new();
    let mut seen_ranks = HashSet::new();

    // Group by rank
    let mut rank_groups: Vec<(Rank, Vec<&Card>)> = Vec::new();
    for rank in [
        Rank::Five,
        Rank::Six,
        Rank::Seven,
        Rank::Eight,
        Rank::Nine,
        Rank::Ten,
        Rank::Jack,
        Rank::Queen,
        Rank::King,
        Rank::Ace,
        Rank::Two,
    ] {
        let cards: Vec<&Card> = hand.iter().filter(|c| c.rank == rank).collect();
        if cards.len() >= 3 {
            rank_groups.push((rank, cards));
        }
    }

    for (rank, cards) in rank_groups {
        if seen_ranks.contains(&rank) {
            continue;
        }
        seen_ranks.insert(rank);

        let protected_suits = get_protected_suits(hand, rank);

        // Find 3 cards with different suits, preferring non-protected
        let mut selected = Vec::new();

        // First, try to get 3 non-protected suits
        for card in &cards {
            if !protected_suits.contains(&card.suit) && selected.len() < 3 {
                selected.push((*card).clone());
            }
        }

        // If not enough, add protected suits
        if selected.len() < 3 {
            for card in &cards {
                if selected.len() < 3 && !selected.iter().any(|c| c.suit == card.suit) {
                    selected.push((*card).clone());
                }
            }
        }

        if selected.len() == 3 {
            triples.push(selected);
        }
    }

    triples
}

/// Filters consecutive pairs to keep only one combination per (start_rank, length).
///
/// For each sequence of consecutive ranks, keeps only one suit combination,
/// preferring non-protected suits.
///
/// # Arguments
/// * `hand` - Complete hand
///
/// # Returns
/// Filtered list of consecutive pairs
pub fn filter_consecutive_pairs(hand: &[Card]) -> Vec<Vec<Card>> {
    use std::collections::HashMap;

    let mut result = Vec::new();
    let mut seen_sequences = HashSet::new();

    // Group by rank
    let mut rank_groups: HashMap<Rank, Vec<&Card>> = HashMap::new();
    for card in hand {
        rank_groups.entry(card.rank).or_insert_with(Vec::new).push(card);
    }

    // Get ranks that have at least 2 cards
    let mut valid_ranks: Vec<Rank> = rank_groups
        .iter()
        .filter(|(_r, cards)| cards.len() >= 2)
        .map(|(r, _cards)| *r)
        .collect();
    valid_ranks.sort_by_key(|r| *r as u8);

    // Try all consecutive sequences of length 2+
    for length in 2..=valid_ranks.len() {
        for i in 0..=valid_ranks.len().saturating_sub(length) {
            let ranks: Vec<Rank> = valid_ranks[i..i + length].to_vec();

            // Check if consecutive
            if is_consecutive_ranks(&ranks) {
                // Create a key for this sequence
                let sequence_key = (ranks[0], length);

                // Skip if already seen
                if seen_sequences.contains(&sequence_key) {
                    continue;
                }
                seen_sequences.insert(sequence_key);

                // Select 2 cards from each rank, preferring non-protected suits
                let mut selected_cards = Vec::new();
                for rank in &ranks {
                    let cards_of_rank: Vec<&Card> = rank_groups[rank].clone();
                    let protected_suits = get_protected_suits(hand, *rank);

                    // Select 2 cards, preferring non-protected suits
                    let mut selected = Vec::new();

                    // First, try to get 2 non-protected suits
                    for card in &cards_of_rank {
                        if !protected_suits.contains(&card.suit) && selected.len() < 2 {
                            selected.push((*card).clone());
                        }
                    }

                    // If not enough, add protected suits
                    if selected.len() < 2 {
                        for card in &cards_of_rank {
                            if selected.len() < 2 && !selected.iter().any(|c| c.suit == card.suit) {
                                selected.push((*card).clone());
                            }
                        }
                    }

                    // If still not enough (should have at least 2), take what we can
                    if selected.len() < 2 {
                        for card in &cards_of_rank {
                            if selected.len() < 2 {
                                selected.push((*card).clone());
                            }
                        }
                    }

                    selected_cards.extend(selected);
                }

                if selected_cards.len() == length * 2 {
                    result.push(selected_cards);
                }
            }
        }
    }

    result
}

/// Helper function to check if ranks are consecutive
fn is_consecutive_ranks(ranks: &[Rank]) -> bool {
    if ranks.len() < 2 {
        return false;
    }

    for i in 1..ranks.len() {
        if (ranks[i] as u8) != (ranks[i - 1] as u8) + 1 {
            return false;
        }
    }
    true
}

#[cfg(test)]
mod tests {
    use super::*;

    fn make_card(suit: Suit, rank: Rank) -> Card {
        Card { suit, rank }
    }

    #[test]
    fn test_detect_tongzi_basic() {
        // ♠5♠5♠5 forms a Tongzi (same suit, same rank, 3 cards)
        let hand = vec![
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Spades, Rank::Five),
        ];

        let tongzi = detect_tongzi(&hand);
        assert_eq!(tongzi.len(), 1);
        assert_eq!(tongzi[0], (Suit::Spades, Rank::Five));
    }

    #[test]
    fn test_detect_tongzi_no_match() {
        // ♠5♥5♦5 (different suits) should not form a Tongzi
        let hand = vec![
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Diamonds, Rank::Five),
        ];

        let tongzi = detect_tongzi(&hand);
        assert_eq!(tongzi.len(), 0);
    }

    #[test]
    fn test_detect_dizha_basic() {
        // ♠J♠J + ♥J♥J + ♣J♣J + ♦J♦J forms a Dizha (all 4 suits have 2+ cards)
        let hand = vec![
            make_card(Suit::Spades, Rank::Jack),
            make_card(Suit::Spades, Rank::Jack),
            make_card(Suit::Hearts, Rank::Jack),
            make_card(Suit::Hearts, Rank::Jack),
            make_card(Suit::Clubs, Rank::Jack),
            make_card(Suit::Clubs, Rank::Jack),
            make_card(Suit::Diamonds, Rank::Jack),
            make_card(Suit::Diamonds, Rank::Jack),
        ];

        let dizha = detect_dizha(&hand);
        assert_eq!(dizha.len(), 1);
        assert_eq!(dizha[0], Rank::Jack);
    }

    #[test]
    fn test_get_protected_suits_tongzi() {
        // ♠5♠5♠5 - Rank Five should be protected (Spades suit only)
        let hand = vec![
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Spades, Rank::Five),
        ];

        let protected = get_protected_suits(&hand, Rank::Five);
        assert!(protected.contains(&Suit::Spades));
        assert_eq!(protected.len(), 1);
    }

    #[test]
    fn test_select_safe_suit_prefers_non_protected() {
        // ♠5♠5♠5♥5 - For Rank Five, should prefer Hearts (non-protected)
        let hand = vec![
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
        ];

        let suit = select_safe_suit(&hand, Rank::Five);
        assert_eq!(suit, Some(Suit::Hearts));
    }

    #[test]
    fn test_filter_singles_basic() {
        // ♠5♥5♦5 - Should keep only one 5
        let hand = vec![
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Diamonds, Rank::Five),
        ];

        let singles = filter_singles(&hand);
        assert_eq!(singles.len(), 1);
        assert_eq!(singles[0].len(), 1);
        assert_eq!(singles[0][0].rank, Rank::Five);
    }

    #[test]
    fn test_filter_pairs_basic() {
        // ♠5♥5♦5♣5 - Should keep only one pair of 5
        let hand = vec![
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Diamonds, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
        ];

        let pairs = filter_pairs(&hand);
        assert_eq!(pairs.len(), 1);
        assert_eq!(pairs[0].len(), 2);
        assert_eq!(pairs[0][0].rank, Rank::Five);
        assert_eq!(pairs[0][1].rank, Rank::Five);
        assert_ne!(pairs[0][0].suit, pairs[0][1].suit);
    }

    #[test]
    fn test_filter_triples_basic() {
        // ♠5♥5♦5♣5 - Should keep only one triple of 5
        let hand = vec![
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Diamonds, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
        ];

        let triples = filter_triples(&hand);
        assert_eq!(triples.len(), 1);
        assert_eq!(triples[0].len(), 3);
        assert_eq!(triples[0][0].rank, Rank::Five);
    }

    #[test]
    fn test_filter_consecutive_pairs_basic() {
        // ♠5♥5♦5♣5 + ♠6♥6♦6♣6 - Should keep only one 5-6 consecutive pair
        let hand = vec![
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Diamonds, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
            make_card(Suit::Spades, Rank::Six),
            make_card(Suit::Hearts, Rank::Six),
            make_card(Suit::Diamonds, Rank::Six),
            make_card(Suit::Clubs, Rank::Six),
        ];

        let consecutive_pairs = filter_consecutive_pairs(&hand);
        // Should produce: [56] (one sequence)
        assert_eq!(consecutive_pairs.len(), 1);
        assert_eq!(consecutive_pairs[0].len(), 4); // 2 pairs = 4 cards
        assert_eq!(consecutive_pairs[0][0].rank, Rank::Five);
        assert_eq!(consecutive_pairs[0][2].rank, Rank::Six);
    }
}
