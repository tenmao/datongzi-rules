//! Tests for combinatorial explosion scenarios in PlayGenerator
//!
//! These tests document known performance bottlenecks that need optimization.
//! They are marked with #[ignore] by default to prevent CI slowdowns.

use datongzi_rules::{Card, PlayGenerator, Rank, Suit};
use std::time::{Duration, Instant};

/// Helper to create a hand with many consecutive triples and pairs
/// This simulates a worst-case scenario for airplane-with-wings generation
fn create_explosion_hand() -> Vec<Card> {
    let mut hand = Vec::new();

    // Create 6 consecutive triples: 5, 6, 7, 8, 9, 10
    // This allows generating airplanes of length 2, 3, 4, 5, 6
    for rank in [
        Rank::Five,
        Rank::Six,
        Rank::Seven,
        Rank::Eight,
        Rank::Nine,
        Rank::Ten,
    ] {
        hand.push(Card::new(Suit::Spades, rank));
        hand.push(Card::new(Suit::Hearts, rank));
        hand.push(Card::new(Suit::Clubs, rank));
    }

    // Create 10 pairs for wings: J, Q, K, A, 2, and 5 more ranks
    let wing_ranks = [
        Rank::Jack,
        Rank::Queen,
        Rank::King,
        Rank::Ace,
        Rank::Two,
        Rank::Five,  // Reuse Five (we have 3, so 2 left for pair)
        Rank::Six,   // Reuse Six
        Rank::Seven, // Reuse Seven
        Rank::Eight, // Reuse Eight
        Rank::Nine,  // Reuse Nine
    ];

    for rank in wing_ranks {
        hand.push(Card::new(Suit::Diamonds, rank));
        // For ranks 5-9, we already have 3 cards, so use different suit
        if matches!(
            rank,
            Rank::Five | Rank::Six | Rank::Seven | Rank::Eight | Rank::Nine
        ) {
            hand.push(Card::new(Suit::Diamonds, rank)); // Now we have 4 of this rank
        } else {
            hand.push(Card::new(Suit::Spades, rank));
        }
    }

    hand
}

#[test]
#[ignore] // Ignored by default - this test documents the combinatorial explosion problem
fn test_airplane_with_wings_combinatorial_explosion() {
    let hand = create_explosion_hand();

    println!("Hand size: {} cards", hand.len());
    println!("Testing generate_all_plays with large max_combinations...");

    let start = Instant::now();
    let result = PlayGenerator::generate_all_plays(&hand, 100_000);
    let elapsed = start.elapsed();

    match result {
        Ok(plays) => {
            println!("✓ Generated {} plays in {:?}", plays.len(), elapsed);
            println!(
                "  Performance: {:.0} plays/sec",
                plays.len() as f64 / elapsed.as_secs_f64()
            );

            // Count airplane-with-wings specifically
            use datongzi_rules::{PatternRecognizer, PlayType};
            let airplane_wings: Vec<_> = plays
                .iter()
                .filter(|p| {
                    PatternRecognizer::analyze_cards(p)
                        .map_or(false, |pat| pat.play_type == PlayType::AirplaneWithWings)
                })
                .collect();
            println!("  Airplane-with-wings: {} variations", airplane_wings.len());

            // This test documents current performance - we expect it to be slow
            if elapsed > Duration::from_secs(10) {
                println!("⚠️  SLOW: This demonstrates the combinatorial explosion problem");
                println!("    Need to optimize the algorithm, not just limit combinations");
            }
        }
        Err(e) => {
            println!("✗ Hit combination limit: {}", e);
            println!("  Elapsed: {:?}", elapsed);
        }
    }

    // This test is for documentation - it doesn't fail
    // Real optimization should come from algorithmic improvements
}

#[test]
#[ignore] // Ignored by default
fn test_bomb_combinatorial_explosion() {
    // Create a hand with 12 cards of the same rank (3 decks)
    let mut hand = Vec::new();
    let rank = Rank::King;

    // 3 decks × 4 suits = 12 cards
    for _ in 0..3 {
        hand.push(Card::new(Suit::Spades, rank));
        hand.push(Card::new(Suit::Hearts, rank));
        hand.push(Card::new(Suit::Clubs, rank));
        hand.push(Card::new(Suit::Diamonds, rank));
    }

    println!("Hand: 12 Kings (3 decks)");
    println!("Testing bomb generation...");

    let start = Instant::now();
    let result = PlayGenerator::generate_all_plays(&hand, 100_000);
    let elapsed = start.elapsed();

    match result {
        Ok(plays) => {
            println!("✓ Generated {} plays in {:?}", plays.len(), elapsed);

            use datongzi_rules::{PatternRecognizer, PlayType};
            let bombs: Vec<_> = plays
                .iter()
                .filter(|p| {
                    PatternRecognizer::analyze_cards(p)
                        .map_or(false, |pat| pat.play_type == PlayType::Bomb)
                })
                .collect();
            println!("  Bombs: {} variations", bombs.len());

            // With 12 cards, we can make bombs of size 4, 5, 6, 7, 8, 9, 10, 11, 12
            // Total combinations: C(12,4) + C(12,5) + ... + C(12,12)
            // = 495 + 792 + 924 + 792 + 495 + 220 + 66 + 12 + 1 = 3797 combinations!
            println!("  Theoretical max bombs: C(12,4)+...+C(12,12) = 3797");

            if elapsed > Duration::from_secs(5) {
                println!("⚠️  SLOW: Bomb generation needs optimization");
            }
        }
        Err(e) => {
            println!("✗ Hit combination limit: {}", e);
        }
    }
}

#[test]
fn test_realistic_mcts_scenario() {
    // A more realistic hand during MCTS simulation (mid-game, ~20 cards)
    let mut hand = Vec::new();

    // 3 consecutive triples (can make 2-length or 3-length airplane)
    for rank in [Rank::Five, Rank::Six, Rank::Seven] {
        hand.push(Card::new(Suit::Spades, rank));
        hand.push(Card::new(Suit::Hearts, rank));
        hand.push(Card::new(Suit::Clubs, rank));
    }

    // 5 pairs for wings
    for rank in [Rank::Eight, Rank::Nine, Rank::Ten, Rank::Jack, Rank::Queen] {
        hand.push(Card::new(Suit::Spades, rank));
        hand.push(Card::new(Suit::Hearts, rank));
    }

    // Some singles
    hand.push(Card::new(Suit::Diamonds, Rank::King));
    hand.push(Card::new(Suit::Diamonds, Rank::Ace));

    println!("Realistic mid-game hand: {} cards", hand.len());

    let start = Instant::now();
    let result = PlayGenerator::generate_all_plays(&hand, 10_000);
    let elapsed = start.elapsed();

    match result {
        Ok(plays) => {
            println!("✓ Generated {} plays in {:?}", plays.len(), elapsed);

            // For realistic gameplay, this should be fast (<100ms)
            assert!(
                elapsed < Duration::from_millis(500),
                "Realistic scenario took too long: {:?}",
                elapsed
            );
        }
        Err(e) => {
            panic!("Realistic scenario failed: {}", e);
        }
    }
}
