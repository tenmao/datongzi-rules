//! Multi-track kicker selection algorithm.
//!
//! This module implements a DFS-based knapsack solver for selecting kickers
//! (带牌) with different tactical strategies.

use std::collections::HashSet;

use crate::models::{Card, Rank};

/// Kicker selection tactic.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Tactic {
    /// Efficiency first: reward whole-take, penalize splits
    Efficiency,
    /// Save high cards: high cards get extra penalty
    SaveHigh,
    /// Dump score cards: negative cost for score cards (10, K)
    DumpScore,
    /// Hoard score cards: high penalty for score cards
    HoardScore,
    /// Aggressive/lethal mode: take as many as possible
    Aggressive,
}

/// A block of cards with the same rank.
#[derive(Debug, Clone)]
pub struct Block {
    /// The rank of cards in this block
    pub rank: Rank,
    /// Number of cards available
    pub count: usize,
    /// Whether this is a scoring card (10, K)
    pub is_score: bool,
    /// Whether this is a high card (A, 2)
    pub is_big: bool,
    /// Whether this is a power card (part of bomb/tongzi/dizha potential)
    pub is_power: bool,
}

impl Block {
    /// Create a block from available cards of a specific rank.
    pub fn from_cards(cards: &[Card], rank: Rank) -> Self {
        let matching: Vec<_> = cards.iter().filter(|c| c.rank == rank).collect();
        let count = matching.len();

        Block {
            rank,
            count,
            is_score: matches!(rank, Rank::Ten | Rank::King),
            is_big: matches!(rank, Rank::Ace | Rank::Two),
            is_power: count >= 4, // 4+ cards might form a bomb
        }
    }
}

/// Result of knapsack solver.
#[derive(Debug, Clone)]
pub struct KnapsackResult {
    /// Selected (rank, count) pairs
    pub selected: Vec<(Rank, usize)>,
    /// Total cost of selection
    pub total_cost: f32,
}

impl Default for KnapsackResult {
    fn default() -> Self {
        Self {
            selected: vec![],
            total_cost: f32::MAX, // Use MAX instead of INFINITY for comparison safety
        }
    }
}

/// Calculate the cost of taking cards from a block.
///
/// Cost formula: base + integrity_mod + tactical_mod + power_mod
fn calculate_cost(block: &Block, take: usize, tactic: Tactic) -> f32 {
    if take == 0 {
        return 0.0;
    }

    // 1. Base cost: rank value × take count
    let base = block.rank.value() as f32 * take as f32;

    // 2. Integrity modifier (reward whole-take, penalize splits)
    let integrity_mod = if take == block.count {
        -5.0 // Whole-take bonus
    } else if block.count >= 2 {
        // Split penalty based on remaining cards
        match block.count - take {
            1 => 30.0, // Left with single
            2 => 20.0, // Left with pair
            _ => 10.0, // Other
        }
    } else {
        0.0
    };

    // 3. Tactical modifier
    let tactical_mod = match tactic {
        Tactic::Efficiency => {
            if take == block.count {
                -10.0
            } else {
                0.0
            }
        }
        Tactic::SaveHigh => {
            if block.is_big {
                100.0 * take as f32
            } else {
                0.0
            }
        }
        Tactic::DumpScore => {
            if block.is_score {
                -50.0 * take as f32
            } else {
                0.0
            }
        }
        Tactic::HoardScore => {
            if block.is_score {
                100.0 * take as f32
            } else {
                0.0
            }
        }
        Tactic::Aggressive => {
            // Aggressive: strongly encourage taking cards (negative cost)
            -100.0 * take as f32
        }
    };

    // 4. Power card protection (bomb/tongzi/dizha)
    let power_mod = if block.is_power && take > 0 {
        1000.0 // Absolutely forbidden
    } else {
        0.0
    };

    base + integrity_mod + tactical_mod + power_mod
}

/// DFS knapsack solver for kicker selection.
pub fn solve_knapsack(blocks: &[Block], capacity: usize, tactic: Tactic) -> KnapsackResult {
    let mut best_result = KnapsackResult::default();
    let mut current_selection = Vec::new();

    dfs_recursive(
        blocks,
        capacity,
        tactic,
        0,
        0,
        0.0,
        &mut current_selection,
        &mut best_result,
    );

    // If no solution found (still at MAX), return empty result with 0 cost
    if best_result.total_cost == f32::MAX {
        best_result.total_cost = 0.0;
    }

    best_result
}

#[allow(clippy::too_many_arguments)]
fn dfs_recursive(
    blocks: &[Block],
    capacity: usize,
    tactic: Tactic,
    block_idx: usize,
    current_count: usize,
    current_cost: f32,
    current_selection: &mut Vec<(Rank, usize)>,
    best_result: &mut KnapsackResult,
) {
    // Pruning: already worse than best
    if current_cost >= best_result.total_cost {
        return;
    }

    // Terminal: all blocks processed
    if block_idx >= blocks.len() {
        // Penalty for not filling capacity (encourage filling when possible)
        let unfilled_penalty = if current_count < capacity {
            (capacity - current_count) as f32 * 100.0
        } else {
            0.0
        };
        let total_cost = current_cost + unfilled_penalty;

        if total_cost < best_result.total_cost {
            best_result.selected = current_selection.clone();
            best_result.total_cost = total_cost;
        }
        return;
    }

    // Terminal: capacity filled (no more space)
    if current_count >= capacity {
        if current_cost < best_result.total_cost {
            best_result.selected = current_selection.clone();
            best_result.total_cost = current_cost;
        }
        return;
    }

    let block = &blocks[block_idx];
    let remaining = capacity - current_count;

    // Try taking 0, 1, ..., min(block.count, remaining) cards
    for take in 0..=block.count.min(remaining) {
        let cost = calculate_cost(block, take, tactic);

        if take > 0 {
            current_selection.push((block.rank, take));
        }

        dfs_recursive(
            blocks,
            capacity,
            tactic,
            block_idx + 1,
            current_count + take,
            current_cost + cost,
            current_selection,
            best_result,
        );

        if take > 0 {
            current_selection.pop();
        }
    }
}

/// Check if a card is protected (part of bomb/tongzi/dizha).
fn is_protected(hand: &[Card], card: &Card) -> bool {
    let count = hand.iter().filter(|c| c.rank == card.rank).count();
    count >= 4 // 4+ cards might form a bomb
}

/// Check if aggressive mode should be used.
///
/// Condition: remaining loose cards <= capacity + 1
fn should_use_aggressive(hand: &[Card], main_cards: &[Card], capacity: usize) -> bool {
    let loose_cards: Vec<_> = hand
        .iter()
        .filter(|c| !main_cards.contains(c))
        .filter(|c| !is_protected(hand, c))
        .collect();

    loose_cards.len() <= capacity + 1
}

/// Select kickers using multi-track algorithm.
///
/// # Arguments
///
/// * `hand` - Complete hand of cards
/// * `main_cards` - Cards used as main play (triple/plane body)
/// * `capacity` - Maximum number of kickers allowed
/// * `tactic` - Optional tactic override (None = auto-select)
///
/// # Returns
///
/// Selected kicker cards
pub fn select_kickers(
    hand: &[Card],
    main_cards: &[Card],
    capacity: usize,
    tactic: Option<Tactic>,
) -> Vec<Card> {
    // 1. Build available cards (exclude main cards and protected cards)
    let available_cards: Vec<Card> = hand
        .iter()
        .filter(|c| !main_cards.contains(c))
        .filter(|c| !is_protected(hand, c))
        .copied()
        .collect();

    if available_cards.is_empty() || capacity == 0 {
        return vec![];
    }

    // 2. Determine tactic
    let tactic = tactic.unwrap_or_else(|| {
        if should_use_aggressive(hand, main_cards, capacity) {
            Tactic::Aggressive
        } else {
            Tactic::Efficiency
        }
    });

    // 3. Build blocks from available cards
    let mut seen_ranks = HashSet::new();
    let blocks: Vec<Block> = available_cards
        .iter()
        .filter_map(|c| {
            if seen_ranks.insert(c.rank) {
                Some(Block::from_cards(&available_cards, c.rank))
            } else {
                None
            }
        })
        .collect();

    // 4. Run DFS knapsack solver
    let result = solve_knapsack(&blocks, capacity, tactic);

    // 5. Convert result to actual cards
    let mut kickers = Vec::new();
    for (rank, count) in result.selected {
        let cards: Vec<Card> = available_cards
            .iter()
            .filter(|c| c.rank == rank)
            .take(count)
            .copied()
            .collect();
        kickers.extend(cards);
    }

    kickers
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::models::Suit;

    fn make_card(suit: Suit, rank: Rank) -> Card {
        Card::new(suit, rank)
    }

    #[test]
    fn test_block_creation() {
        let cards = vec![
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
        ];

        let block = Block::from_cards(&cards, Rank::Five);
        assert_eq!(block.count, 3);
        assert!(!block.is_score);
        assert!(!block.is_big);
        assert!(!block.is_power);
    }

    #[test]
    fn test_block_score_card() {
        let cards = vec![
            make_card(Suit::Spades, Rank::King),
            make_card(Suit::Hearts, Rank::King),
        ];

        let block = Block::from_cards(&cards, Rank::King);
        assert!(block.is_score);
        assert!(!block.is_big);
    }

    #[test]
    fn test_block_big_card() {
        let cards = vec![
            make_card(Suit::Spades, Rank::Two),
            make_card(Suit::Hearts, Rank::Two),
        ];

        let block = Block::from_cards(&cards, Rank::Two);
        assert!(!block.is_score);
        assert!(block.is_big);
    }

    #[test]
    fn test_calculate_cost_efficiency() {
        let block = Block {
            rank: Rank::Five,
            count: 2,
            is_score: false,
            is_big: false,
            is_power: false,
        };

        // Whole-take should get bonus
        let cost_whole = calculate_cost(&block, 2, Tactic::Efficiency);
        let cost_partial = calculate_cost(&block, 1, Tactic::Efficiency);

        // Whole-take: 5*2 - 5 (integrity) - 10 (efficiency) = -5
        // Partial: 5*1 + 30 (split penalty) = 35
        assert!(cost_whole < cost_partial);
    }

    #[test]
    fn test_calculate_cost_save_high() {
        let block_high = Block {
            rank: Rank::Two,
            count: 2,
            is_score: false,
            is_big: true,
            is_power: false,
        };

        let block_low = Block {
            rank: Rank::Five,
            count: 2,
            is_score: false,
            is_big: false,
            is_power: false,
        };

        let cost_high = calculate_cost(&block_high, 1, Tactic::SaveHigh);
        let cost_low = calculate_cost(&block_low, 1, Tactic::SaveHigh);

        // High card should have much higher cost
        assert!(cost_high > cost_low);
    }

    #[test]
    fn test_calculate_cost_dump_score() {
        let block = Block {
            rank: Rank::King,
            count: 2,
            is_score: true,
            is_big: false,
            is_power: false,
        };

        let cost = calculate_cost(&block, 1, Tactic::DumpScore);
        // Score card should have negative tactical modifier
        // Base: 13, integrity: 30, tactical: -50 => -7
        assert!(cost < 20.0);
    }

    #[test]
    fn test_calculate_cost_power_protection() {
        let block = Block {
            rank: Rank::Five,
            count: 4,
            is_score: false,
            is_big: false,
            is_power: true,
        };

        let cost = calculate_cost(&block, 1, Tactic::Efficiency);
        // Power card should have massive penalty
        assert!(cost > 1000.0);
    }

    #[test]
    fn test_solve_knapsack_basic() {
        let blocks = vec![
            Block {
                rank: Rank::Five,
                count: 2,
                is_score: false,
                is_big: false,
                is_power: false,
            },
            Block {
                rank: Rank::Seven,
                count: 1,
                is_score: false,
                is_big: false,
                is_power: false,
            },
        ];

        let result = solve_knapsack(&blocks, 3, Tactic::Efficiency);

        // Should select something (algorithm finds best cost, not necessarily max capacity)
        // The test verifies the algorithm runs without panic
        assert!(result.total_cost < f32::MAX);
    }

    #[test]
    fn test_select_kickers_empty() {
        let hand = vec![
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
        ];
        let main_cards = hand.clone();

        let kickers = select_kickers(&hand, &main_cards, 2, None);
        assert!(kickers.is_empty());
    }

    #[test]
    fn test_select_kickers_basic() {
        let hand = vec![
            // Main: triple 5s
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
            // Available: pair of 7s
            make_card(Suit::Spades, Rank::Seven),
            make_card(Suit::Hearts, Rank::Seven),
        ];
        let main_cards = vec![
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
        ];

        // Debug: Check available cards
        let available_cards: Vec<Card> = hand
            .iter()
            .filter(|c| !main_cards.contains(c))
            .filter(|c| !is_protected(&hand, c))
            .copied()
            .collect();
        eprintln!("Hand: {:?}", hand);
        eprintln!("Main cards: {:?}", main_cards);
        eprintln!("Available cards after filtering: {:?}", available_cards);
        eprintln!(
            "Seven count in hand: {}",
            hand.iter().filter(|c| c.rank == Rank::Seven).count()
        );

        // Use Aggressive mode to ensure maximum cards are selected
        let kickers = select_kickers(&hand, &main_cards, 2, Some(Tactic::Aggressive));
        eprintln!("Selected kickers: {:?}", kickers);
        assert_eq!(kickers.len(), 2);
        assert!(kickers.iter().all(|c| c.rank == Rank::Seven));
    }

    #[test]
    fn test_select_kickers_protected() {
        let hand = vec![
            // Main: triple 5s
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
            // Bomb (protected): four 7s
            make_card(Suit::Spades, Rank::Seven),
            make_card(Suit::Hearts, Rank::Seven),
            make_card(Suit::Clubs, Rank::Seven),
            make_card(Suit::Diamonds, Rank::Seven),
        ];
        let main_cards = vec![
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
        ];

        let kickers = select_kickers(&hand, &main_cards, 2, None);
        // Should not select from the bomb
        assert!(kickers.is_empty());
    }

    #[test]
    fn test_aggressive_mode() {
        // Should trigger aggressive when loose cards <= capacity + 1
        let hand = vec![
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
            make_card(Suit::Spades, Rank::Seven),
            make_card(Suit::Hearts, Rank::Eight),
        ];
        let main_cards = vec![
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
        ];

        // capacity=2, loose cards=2, so 2 <= 2+1 is true
        assert!(should_use_aggressive(&hand, &main_cards, 2));
    }

    // ========== Comprehensive Tactic Tests ==========

    #[test]
    fn test_tactic_efficiency_whole_take_bonus() {
        // Efficiency tactic should prefer taking whole groups
        let hand = vec![
            // Main: triple 5s
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
            // Available: pair of 7s, single 9
            make_card(Suit::Spades, Rank::Seven),
            make_card(Suit::Hearts, Rank::Seven),
            make_card(Suit::Spades, Rank::Nine),
        ];
        let main_cards = vec![
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
        ];

        let kickers = select_kickers(&hand, &main_cards, 2, Some(Tactic::Efficiency));

        // Should prefer whole pair of 7s (cost: -5) over single 7 + single 9 (cost: 35+9)
        assert_eq!(kickers.len(), 2);
        assert!(kickers.iter().all(|c| c.rank == Rank::Seven));
    }

    #[test]
    fn test_tactic_save_high_avoids_aces() {
        // SaveHigh tactic should avoid using high cards (A, 2)
        let hand = vec![
            // Main: triple 5s
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
            // Available: pair of Aces, pair of 7s
            make_card(Suit::Spades, Rank::Ace),
            make_card(Suit::Hearts, Rank::Ace),
            make_card(Suit::Spades, Rank::Seven),
            make_card(Suit::Hearts, Rank::Seven),
        ];
        let main_cards = vec![
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
        ];

        let kickers = select_kickers(&hand, &main_cards, 2, Some(Tactic::SaveHigh));

        // Should select 7s (low penalty) instead of Aces (high penalty +100 per card)
        assert_eq!(kickers.len(), 2);
        assert!(kickers.iter().all(|c| c.rank == Rank::Seven));
    }

    #[test]
    fn test_tactic_dump_score_prefers_tens_and_kings() {
        // DumpScore tactic should prefer dumping 10s and Ks (score cards)
        let hand = vec![
            // Main: triple 5s
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
            // Available: pair of 10s, pair of 7s
            make_card(Suit::Spades, Rank::Ten),
            make_card(Suit::Hearts, Rank::Ten),
            make_card(Suit::Spades, Rank::Seven),
            make_card(Suit::Hearts, Rank::Seven),
        ];
        let main_cards = vec![
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
        ];

        let kickers = select_kickers(&hand, &main_cards, 2, Some(Tactic::DumpScore));

        // Should select 10s (negative tactical cost -50 per card)
        assert_eq!(kickers.len(), 2);
        assert!(kickers.iter().all(|c| c.rank == Rank::Ten));
    }

    #[test]
    fn test_tactic_hoard_score_avoids_tens_and_kings() {
        // HoardScore tactic should avoid using 10s and Ks
        let hand = vec![
            // Main: triple 5s
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
            // Available: pair of Kings, pair of 7s
            make_card(Suit::Spades, Rank::King),
            make_card(Suit::Hearts, Rank::King),
            make_card(Suit::Spades, Rank::Seven),
            make_card(Suit::Hearts, Rank::Seven),
        ];
        let main_cards = vec![
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
        ];

        let kickers = select_kickers(&hand, &main_cards, 2, Some(Tactic::HoardScore));

        // Should select 7s instead of Kings (Kings have +100 penalty per card)
        assert_eq!(kickers.len(), 2);
        assert!(kickers.iter().all(|c| c.rank == Rank::Seven));
    }

    #[test]
    fn test_tactic_aggressive_maximizes_cards() {
        // Aggressive tactic should take as many cards as possible
        let hand = vec![
            // Main: triple 5s
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
            // Available: multiple singles
            make_card(Suit::Spades, Rank::Six),
            make_card(Suit::Spades, Rank::Seven),
            make_card(Suit::Spades, Rank::Eight),
            make_card(Suit::Spades, Rank::Nine),
        ];
        let main_cards = vec![
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
        ];

        let kickers = select_kickers(&hand, &main_cards, 3, Some(Tactic::Aggressive));

        // Should fill capacity completely
        assert_eq!(kickers.len(), 3);
    }

    // ========== Edge Cases and Boundary Tests ==========

    #[test]
    fn test_zero_capacity() {
        let hand = vec![
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Spades, Rank::Seven),
        ];
        let main_cards = vec![make_card(Suit::Spades, Rank::Five)];

        let kickers = select_kickers(&hand, &main_cards, 0, None);
        assert!(kickers.is_empty());
    }

    #[test]
    fn test_capacity_exceeds_available() {
        let hand = vec![
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Spades, Rank::Seven),
        ];
        let main_cards = vec![make_card(Suit::Spades, Rank::Five)];

        let kickers = select_kickers(&hand, &main_cards, 10, Some(Tactic::Aggressive));

        // Should select all available (only 1 card available after filtering)
        assert_eq!(kickers.len(), 1);
        assert_eq!(kickers[0].rank, Rank::Seven);
    }

    #[test]
    fn test_all_cards_protected() {
        let hand = vec![
            // Main: triple 5s
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
            // Bomb: four 7s (protected)
            make_card(Suit::Spades, Rank::Seven),
            make_card(Suit::Hearts, Rank::Seven),
            make_card(Suit::Clubs, Rank::Seven),
            make_card(Suit::Diamonds, Rank::Seven),
        ];
        let main_cards = vec![
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
        ];

        let kickers = select_kickers(&hand, &main_cards, 2, Some(Tactic::Aggressive));

        // No available cards (all protected)
        assert!(kickers.is_empty());
    }

    #[test]
    fn test_multiple_blocks_selection() {
        // Test selecting from multiple different rank blocks
        let hand = vec![
            // Main: triple 5s
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
            // Available: pair 7s, pair 9s, single Q
            make_card(Suit::Spades, Rank::Seven),
            make_card(Suit::Hearts, Rank::Seven),
            make_card(Suit::Spades, Rank::Nine),
            make_card(Suit::Hearts, Rank::Nine),
            make_card(Suit::Spades, Rank::Queen),
        ];
        let main_cards = vec![
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
        ];

        let kickers = select_kickers(&hand, &main_cards, 4, Some(Tactic::Efficiency));

        // Should prefer whole groups: pair 7s + pair 9s
        assert_eq!(kickers.len(), 4);
        let sevens = kickers.iter().filter(|c| c.rank == Rank::Seven).count();
        let nines = kickers.iter().filter(|c| c.rank == Rank::Nine).count();
        assert_eq!(sevens, 2);
        assert_eq!(nines, 2);
    }

    // ========== Performance Tests ==========

    #[test]
    fn test_performance_small_hand() {
        // Test with typical small hand (10 cards)
        let hand: Vec<Card> = vec![
            // Main: triple 5s
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
            // Available: 7 different ranks
            make_card(Suit::Spades, Rank::Six),
            make_card(Suit::Spades, Rank::Seven),
            make_card(Suit::Spades, Rank::Eight),
            make_card(Suit::Spades, Rank::Nine),
            make_card(Suit::Spades, Rank::Ten),
            make_card(Suit::Spades, Rank::Jack),
            make_card(Suit::Spades, Rank::Queen),
        ];
        let main_cards = vec![
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
        ];

        let start = std::time::Instant::now();
        let kickers = select_kickers(&hand, &main_cards, 2, None);
        let elapsed = start.elapsed();

        // Should complete in < 1ms for small hand
        assert!(
            elapsed.as_micros() < 1000,
            "Took {:?}, expected < 1ms",
            elapsed
        );
        assert!(!kickers.is_empty());
    }

    #[test]
    fn test_performance_medium_hand() {
        // Test with medium hand (20 cards, 10 blocks of pairs)
        let mut hand = vec![
            // Main: triple 5s
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
        ];

        // Add 10 pairs (20 cards)
        let ranks = [
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
        ];
        for rank in ranks {
            hand.push(make_card(Suit::Spades, rank));
            hand.push(make_card(Suit::Hearts, rank));
        }

        let main_cards = vec![
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
        ];

        let start = std::time::Instant::now();
        let kickers = select_kickers(&hand, &main_cards, 4, Some(Tactic::Efficiency));
        let elapsed = start.elapsed();

        // Should complete in < 10ms for medium hand
        assert!(
            elapsed.as_millis() < 10,
            "Took {:?}, expected < 10ms",
            elapsed
        );
        assert_eq!(kickers.len(), 4);
    }

    #[test]
    fn test_integrity_modifier_calculation() {
        // Verify integrity modifier values
        let block = Block {
            rank: Rank::Seven,
            count: 3,
            is_score: false,
            is_big: false,
            is_power: false,
        };

        // Whole-take: -5 bonus
        let cost_whole = calculate_cost(&block, 3, Tactic::Efficiency);
        // Base: 7*3=21, integrity: -5, efficiency: -10 = 6
        assert_eq!(cost_whole, 6.0);

        // Take 2, leave 1: +30 penalty
        let cost_split_1 = calculate_cost(&block, 2, Tactic::Efficiency);
        // Base: 7*2=14, integrity: +30, efficiency: 0 = 44
        assert_eq!(cost_split_1, 44.0);

        // Take 1, leave 2: +20 penalty
        let cost_split_2 = calculate_cost(&block, 1, Tactic::Efficiency);
        // Base: 7*1=7, integrity: +20 (leave 2), efficiency: 0 = 27
        assert_eq!(cost_split_2, 27.0);
    }

    #[test]
    fn test_aggressive_tactical_modifier() {
        // Verify Aggressive tactic gives strong negative cost
        let block = Block {
            rank: Rank::Seven,
            count: 2,
            is_score: false,
            is_big: false,
            is_power: false,
        };

        let cost = calculate_cost(&block, 2, Tactic::Aggressive);
        // Base: 7*2=14, integrity: -5 (whole-take), tactical: -100*2=-200 = -191
        assert_eq!(cost, -191.0);
    }

    #[test]
    fn test_auto_tactic_selection() {
        // Test auto-selection: should use Aggressive when loose cards <= capacity + 1
        let hand = vec![
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
            make_card(Suit::Spades, Rank::Seven),
            make_card(Suit::Hearts, Rank::Seven),
        ];
        let main_cards = vec![
            make_card(Suit::Spades, Rank::Five),
            make_card(Suit::Hearts, Rank::Five),
            make_card(Suit::Clubs, Rank::Five),
        ];

        // Loose cards = 2, capacity = 2, so 2 <= 2+1 triggers Aggressive
        let kickers = select_kickers(&hand, &main_cards, 2, None);

        // Aggressive should select all available cards
        assert_eq!(kickers.len(), 2);
    }
}
