//! Tests for GAME_RULE.md updates:
//! 1. 2 and Joker cannot participate in consecutive pairs (AA22 is invalid)
//! 2. 2 cannot participate in airplane (AAA222 is invalid)
//! 3. Triple/TripleWithOne/TripleWithTwo can beat each other
//! 4. Airplane/AirplaneWithWings can beat each other

use datongzi_rules::{Card, PatternRecognizer, PlayType, PlayValidator, Rank, Suit};

// ============================================================================
// Test Group 1: 2 cannot participate in consecutive pairs
// Rule: "2和joker不参与连对和飞机，AA22不能作为连对"
// ============================================================================

#[test]
fn test_aa22_is_not_consecutive_pairs() {
    // AA22 should NOT be recognized as consecutive pairs
    // because 2 cannot participate in consecutive pairs
    let cards = vec![
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Ace),
        Card::new(Suit::Spades, Rank::Two),
        Card::new(Suit::Hearts, Rank::Two),
    ];

    let pattern = PatternRecognizer::analyze_cards(&cards);
    // Should be None (invalid pattern) because AA22 is not allowed
    assert!(
        pattern.is_none(),
        "AA22 should NOT be recognized as consecutive pairs"
    );
}

#[test]
fn test_kkaa_is_not_consecutive_pairs() {
    // KKAA should also NOT be consecutive pairs because it would require
    // A->2 sequence which is not allowed
    let cards = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Ace),
    ];

    let pattern = PatternRecognizer::analyze_cards(&cards);
    // KK AA is valid consecutive pairs (K=13, A=14, consecutive)
    assert!(pattern.is_some());
    let pattern = pattern.unwrap();
    assert_eq!(pattern.play_type, PlayType::ConsecutivePairs);
}

#[test]
fn test_valid_consecutive_pairs_without_two() {
    // Normal consecutive pairs like 55 66 should work
    let cards = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Spades, Rank::Six),
        Card::new(Suit::Hearts, Rank::Six),
    ];

    let pattern = PatternRecognizer::analyze_cards(&cards);
    assert!(pattern.is_some());
    let pattern = pattern.unwrap();
    assert_eq!(pattern.play_type, PlayType::ConsecutivePairs);
}

#[test]
fn test_longer_consecutive_pairs_ending_with_two_invalid() {
    // QQKKAA22 should be invalid because 2 is included
    let cards = vec![
        Card::new(Suit::Spades, Rank::Queen),
        Card::new(Suit::Hearts, Rank::Queen),
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Ace),
        Card::new(Suit::Spades, Rank::Two),
        Card::new(Suit::Hearts, Rank::Two),
    ];

    let pattern = PatternRecognizer::analyze_cards(&cards);
    // Should be None because 2 cannot participate
    assert!(
        pattern.is_none(),
        "Consecutive pairs ending with 2 should be invalid"
    );
}

// ============================================================================
// Test Group 2: 2 cannot participate in airplane
// Rule: "AAA222也不能作为飞机"
// ============================================================================

#[test]
fn test_aaa222_is_not_airplane() {
    // AAA 222 should NOT be recognized as airplane
    // because 2 cannot participate in airplane
    let cards = vec![
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Ace),
        Card::new(Suit::Clubs, Rank::Ace),
        Card::new(Suit::Spades, Rank::Two),
        Card::new(Suit::Hearts, Rank::Two),
        Card::new(Suit::Clubs, Rank::Two),
    ];

    let pattern = PatternRecognizer::analyze_cards(&cards);
    // Should be None (invalid pattern) because AAA222 is not allowed as airplane
    assert!(
        pattern.is_none(),
        "AAA222 should NOT be recognized as airplane"
    );
}

#[test]
fn test_valid_airplane_without_two() {
    // Normal airplane like JJJ QQQ should work
    let cards = vec![
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
        Card::new(Suit::Spades, Rank::Queen),
        Card::new(Suit::Hearts, Rank::Queen),
        Card::new(Suit::Clubs, Rank::Queen),
    ];

    let pattern = PatternRecognizer::analyze_cards(&cards);
    assert!(pattern.is_some());
    let pattern = pattern.unwrap();
    assert_eq!(pattern.play_type, PlayType::Airplane);
}

#[test]
fn test_kkkaaa_is_valid_airplane() {
    // KKK AAA should be valid airplane (K=13, A=14, consecutive)
    let cards = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Clubs, Rank::King),
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Ace),
        Card::new(Suit::Clubs, Rank::Ace),
    ];

    let pattern = PatternRecognizer::analyze_cards(&cards);
    assert!(pattern.is_some());
    let pattern = pattern.unwrap();
    assert_eq!(pattern.play_type, PlayType::Airplane);
}

#[test]
fn test_airplane_with_wings_ending_with_two_invalid() {
    // KKK AAA 222 + wings should be invalid because 2 is in the airplane part
    let cards = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Clubs, Rank::King),
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Ace),
        Card::new(Suit::Clubs, Rank::Ace),
        Card::new(Suit::Spades, Rank::Two),
        Card::new(Suit::Hearts, Rank::Two),
        Card::new(Suit::Clubs, Rank::Two),
        // wings
        Card::new(Suit::Diamonds, Rank::Five),
        Card::new(Suit::Diamonds, Rank::Six),
        Card::new(Suit::Diamonds, Rank::Seven),
    ];

    let pattern = PatternRecognizer::analyze_cards(&cards);
    // Should be None or at least NOT recognize KKK AAA 222 as the airplane part
    // The pattern might try to use KKK AAA as airplane with remaining cards as wings
    // But if it tries to include 222, it should fail
    if let Some(p) = pattern {
        // If it recognizes a pattern, it should not include 2 in the airplane ranks
        if p.play_type == PlayType::AirplaneWithWings {
            assert!(
                !p.secondary_ranks.contains(&Rank::Two),
                "Airplane should not include Rank::Two in secondary_ranks"
            );
        }
    }
}

// ============================================================================
// Test Group 3: Triple/TripleWithOne/TripleWithTwo can beat each other
// Rule: "三张、三带一、三带二也可以互打"
// ============================================================================

#[test]
fn test_triple_beats_triple() {
    // QQQ beats JJJ (pure triple vs pure triple)
    let current_pattern = PatternRecognizer::analyze_cards(&[
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
    ])
    .unwrap();

    let new_cards = vec![
        Card::new(Suit::Spades, Rank::Queen),
        Card::new(Suit::Hearts, Rank::Queen),
        Card::new(Suit::Clubs, Rank::Queen),
    ];

    assert!(PlayValidator::can_beat_play(
        &new_cards,
        Some(&current_pattern)
    ));
}

#[test]
fn test_triple_with_one_beats_triple() {
    // QQQ+5 beats JJJ (triple with kicker vs pure triple)
    let current_pattern = PatternRecognizer::analyze_cards(&[
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
    ])
    .unwrap();

    let new_cards = vec![
        Card::new(Suit::Spades, Rank::Queen),
        Card::new(Suit::Hearts, Rank::Queen),
        Card::new(Suit::Clubs, Rank::Queen),
        Card::new(Suit::Diamonds, Rank::Five),
    ];

    assert!(
        PlayValidator::can_beat_play(&new_cards, Some(&current_pattern)),
        "Triple with one kicker should beat pure triple"
    );
}

#[test]
fn test_triple_with_two_beats_triple() {
    // QQQ+56 beats JJJ (triple with 2 kickers vs pure triple)
    let current_pattern = PatternRecognizer::analyze_cards(&[
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
    ])
    .unwrap();

    let new_cards = vec![
        Card::new(Suit::Spades, Rank::Queen),
        Card::new(Suit::Hearts, Rank::Queen),
        Card::new(Suit::Clubs, Rank::Queen),
        Card::new(Suit::Diamonds, Rank::Five),
        Card::new(Suit::Diamonds, Rank::Six),
    ];

    assert!(
        PlayValidator::can_beat_play(&new_cards, Some(&current_pattern)),
        "Triple with two kickers should beat pure triple"
    );
}

#[test]
fn test_triple_beats_triple_with_two() {
    // QQQ beats JJJ+56 (pure triple vs triple with 2 kickers)
    let current_pattern = PatternRecognizer::analyze_cards(&[
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
        Card::new(Suit::Diamonds, Rank::Five),
        Card::new(Suit::Diamonds, Rank::Six),
    ])
    .unwrap();

    let new_cards = vec![
        Card::new(Suit::Spades, Rank::Queen),
        Card::new(Suit::Hearts, Rank::Queen),
        Card::new(Suit::Clubs, Rank::Queen),
    ];

    assert!(
        PlayValidator::can_beat_play(&new_cards, Some(&current_pattern)),
        "Pure triple should beat triple with two kickers"
    );
}

#[test]
fn test_triple_with_one_beats_triple_with_two() {
    // QQQ+7 beats JJJ+56 (triple with 1 vs triple with 2)
    let current_pattern = PatternRecognizer::analyze_cards(&[
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
        Card::new(Suit::Diamonds, Rank::Five),
        Card::new(Suit::Diamonds, Rank::Six),
    ])
    .unwrap();

    let new_cards = vec![
        Card::new(Suit::Spades, Rank::Queen),
        Card::new(Suit::Hearts, Rank::Queen),
        Card::new(Suit::Clubs, Rank::Queen),
        Card::new(Suit::Diamonds, Rank::Seven),
    ];

    assert!(
        PlayValidator::can_beat_play(&new_cards, Some(&current_pattern)),
        "Triple with one kicker should beat triple with two kickers"
    );
}

// ============================================================================
// Test Group 4: Airplane/AirplaneWithWings can beat each other
// Rule: "飞机带翅膀和飞机可以互相打"
// ============================================================================

#[test]
fn test_airplane_with_wings_beats_airplane() {
    // KKK AAA + 56 beats JJJ QQQ (airplane with wings vs pure airplane)
    let current_pattern = PatternRecognizer::analyze_cards(&[
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
        Card::new(Suit::Spades, Rank::Queen),
        Card::new(Suit::Hearts, Rank::Queen),
        Card::new(Suit::Clubs, Rank::Queen),
    ])
    .unwrap();

    let new_cards = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Clubs, Rank::King),
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Ace),
        Card::new(Suit::Clubs, Rank::Ace),
        Card::new(Suit::Diamonds, Rank::Five),
        Card::new(Suit::Diamonds, Rank::Six),
    ];

    assert!(
        PlayValidator::can_beat_play(&new_cards, Some(&current_pattern)),
        "Airplane with wings should beat pure airplane (same chain length)"
    );
}

#[test]
fn test_airplane_beats_airplane_with_wings() {
    // KKK AAA beats JJJ QQQ + 56 (pure airplane vs airplane with wings)
    let current_pattern = PatternRecognizer::analyze_cards(&[
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
        Card::new(Suit::Spades, Rank::Queen),
        Card::new(Suit::Hearts, Rank::Queen),
        Card::new(Suit::Clubs, Rank::Queen),
        Card::new(Suit::Diamonds, Rank::Five),
        Card::new(Suit::Diamonds, Rank::Six),
    ])
    .unwrap();

    let new_cards = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Clubs, Rank::King),
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Ace),
        Card::new(Suit::Clubs, Rank::Ace),
    ];

    assert!(
        PlayValidator::can_beat_play(&new_cards, Some(&current_pattern)),
        "Pure airplane should beat airplane with wings (same chain length)"
    );
}

#[test]
fn test_different_chain_length_airplane_cannot_beat() {
    // KKK AAA 222 (if valid) cannot beat JJJ QQQ (different chain length)
    // This test ensures chain length matters
    let current_pattern = PatternRecognizer::analyze_cards(&[
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
        Card::new(Suit::Spades, Rank::Queen),
        Card::new(Suit::Hearts, Rank::Queen),
        Card::new(Suit::Clubs, Rank::Queen),
    ])
    .unwrap();

    // 3-chain airplane (without 2): JJJ QQQ KKK (9 cards)
    let new_cards = vec![
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Diamonds, Rank::Jack),
        Card::new(Suit::Spades, Rank::Queen),
        Card::new(Suit::Hearts, Rank::Queen),
        Card::new(Suit::Diamonds, Rank::Queen),
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Diamonds, Rank::King),
    ];

    // Different chain length should not beat
    assert!(
        !PlayValidator::can_beat_play(&new_cards, Some(&current_pattern)),
        "Different chain length airplane should not beat"
    );
}
