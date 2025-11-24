//! Unit tests for PlayGenerator.

use datongzi_rules::{Card, PatternRecognizer, PlayGenerator, PlayType, Rank, Suit};

#[test]
fn test_generate_singles() {
    let hand = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Seven),
        Card::new(Suit::Clubs, Rank::Nine),
    ];

    let plays = PlayGenerator::generate_all_plays(&hand, 1000).unwrap();

    // Should generate 3 singles
    let singles: Vec<_> = plays
        .iter()
        .filter(|p| {
            p.len() == 1
                && PatternRecognizer::analyze_cards(p)
                    .map_or(false, |pat| pat.play_type == PlayType::Single)
        })
        .collect();

    assert_eq!(singles.len(), 3);
}

#[test]
fn test_generate_pairs() {
    let hand = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Clubs, Rank::Five),
        Card::new(Suit::Diamonds, Rank::Five),
    ];

    let plays = PlayGenerator::generate_all_plays(&hand, 1000).unwrap();

    // Should generate 2 pairs
    let pairs: Vec<_> = plays
        .iter()
        .filter(|p| {
            PatternRecognizer::analyze_cards(p).map_or(false, |pat| pat.play_type == PlayType::Pair)
        })
        .collect();

    assert_eq!(pairs.len(), 2); // K-K and 5-5
}

#[test]
fn test_generate_triples() {
    let hand = vec![
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Ace),
        Card::new(Suit::Clubs, Rank::Ace),
    ];

    let plays = PlayGenerator::generate_all_plays(&hand, 1000).unwrap();

    // Should generate 1 triple
    let triples: Vec<_> = plays
        .iter()
        .filter(|p| {
            PatternRecognizer::analyze_cards(p)
                .map_or(false, |pat| pat.play_type == PlayType::Triple)
        })
        .collect();

    assert_eq!(triples.len(), 1);
}

#[test]
fn test_generate_bombs() {
    let hand = vec![
        Card::new(Suit::Spades, Rank::Ten),
        Card::new(Suit::Hearts, Rank::Ten),
        Card::new(Suit::Clubs, Rank::Ten),
        Card::new(Suit::Diamonds, Rank::Ten),
    ];

    let plays = PlayGenerator::generate_all_plays(&hand, 1000).unwrap();

    // Should generate 1 bomb (4 cards)
    let bombs: Vec<_> = plays
        .iter()
        .filter(|p| {
            PatternRecognizer::analyze_cards(p).map_or(false, |pat| pat.play_type == PlayType::Bomb)
        })
        .collect();

    assert_eq!(bombs.len(), 1);
}

#[test]
fn test_generate_tongzi() {
    let hand = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Spades, Rank::King),
    ];

    let plays = PlayGenerator::generate_all_plays(&hand, 1000).unwrap();

    // Should generate 1 tongzi
    let tongzi: Vec<_> = plays
        .iter()
        .filter(|p| {
            PatternRecognizer::analyze_cards(p)
                .map_or(false, |pat| pat.play_type == PlayType::Tongzi)
        })
        .collect();

    assert_eq!(tongzi.len(), 1);
}

#[test]
fn test_generate_dizha() {
    let hand = vec![
        // 2 spades
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Spades, Rank::King),
        // 2 hearts
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        // 2 clubs
        Card::new(Suit::Clubs, Rank::King),
        Card::new(Suit::Clubs, Rank::King),
        // 2 diamonds
        Card::new(Suit::Diamonds, Rank::King),
        Card::new(Suit::Diamonds, Rank::King),
    ];

    let plays = PlayGenerator::generate_all_plays(&hand, 1000).unwrap();

    // Should generate 1 dizha
    let dizha: Vec<_> = plays
        .iter()
        .filter(|p| {
            PatternRecognizer::analyze_cards(p)
                .map_or(false, |pat| pat.play_type == PlayType::Dizha)
        })
        .collect();

    assert_eq!(dizha.len(), 1);
}

#[test]
fn test_generate_beating_plays_same_type() {
    let hand = vec![
        Card::new(Suit::Spades, Rank::Seven),
        Card::new(Suit::Hearts, Rank::Seven),
        Card::new(Suit::Clubs, Rank::Nine),
    ];

    // Current play: single 5
    let current_play = vec![Card::new(Suit::Spades, Rank::Five)];
    let current_pattern = PatternRecognizer::analyze_cards(&current_play).unwrap();

    let beating_plays =
        PlayGenerator::generate_beating_plays_with_same_type_or_trump(&hand, &current_pattern);

    // Should generate singles: 7 (x2) and 9
    assert_eq!(beating_plays.len(), 3);
}

#[test]
fn test_generate_beating_plays_trump() {
    let hand = vec![
        // Bomb
        Card::new(Suit::Spades, Rank::Ten),
        Card::new(Suit::Hearts, Rank::Ten),
        Card::new(Suit::Clubs, Rank::Ten),
        Card::new(Suit::Diamonds, Rank::Ten),
        // Single
        Card::new(Suit::Spades, Rank::Three),
    ];

    // Current play: single King (cannot beat with single Three)
    let current_play = vec![Card::new(Suit::Spades, Rank::King)];
    let current_pattern = PatternRecognizer::analyze_cards(&current_play).unwrap();

    let beating_plays =
        PlayGenerator::generate_beating_plays_with_same_type_or_trump(&hand, &current_pattern);

    // Should generate: 1 bomb (trump beats normal play)
    assert_eq!(beating_plays.len(), 1);
    assert_eq!(beating_plays[0].len(), 4); // Bomb is 4 cards
}

#[test]
fn test_count_all_plays() {
    let hand = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
    ];

    let count = PlayGenerator::count_all_plays(&hand);

    // Should count: 2 singles + 1 pair = 3
    assert_eq!(count, 3);
}

#[test]
fn test_generate_consecutive_pairs() {
    let hand = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Spades, Rank::Six),
        Card::new(Suit::Hearts, Rank::Six),
        Card::new(Suit::Spades, Rank::Seven),
        Card::new(Suit::Hearts, Rank::Seven),
    ];

    let plays = PlayGenerator::generate_all_plays(&hand, 1000).unwrap();

    // Should generate consecutive pairs
    let consec_pairs: Vec<_> = plays
        .iter()
        .filter(|p| {
            PatternRecognizer::analyze_cards(p)
                .map_or(false, |pat| pat.play_type == PlayType::ConsecutivePairs)
        })
        .collect();

    // Should have at least one consecutive pair pattern (5-5-6-6, 6-6-7-7, 5-5-6-6-7-7)
    assert!(!consec_pairs.is_empty());
}

#[test]
fn test_generate_airplanes() {
    let hand = vec![
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
        Card::new(Suit::Spades, Rank::Queen),
        Card::new(Suit::Hearts, Rank::Queen),
        Card::new(Suit::Clubs, Rank::Queen),
    ];

    let plays = PlayGenerator::generate_all_plays(&hand, 1000).unwrap();

    // Should generate airplane
    let airplanes: Vec<_> = plays
        .iter()
        .filter(|p| {
            PatternRecognizer::analyze_cards(p)
                .map_or(false, |pat| pat.play_type == PlayType::Airplane)
        })
        .collect();

    assert_eq!(airplanes.len(), 1);
}

#[test]
fn test_generate_all_plays_empty_hand() {
    let hand: Vec<Card> = vec![];

    let plays = PlayGenerator::generate_all_plays(&hand, 1000).unwrap();

    assert!(plays.is_empty());
}

#[test]
fn test_generate_all_plays_exceeds_limit() {
    // Create a hand that will generate many combinations
    let mut hand = Vec::new();
    for _ in 0..3 {
        for rank in [Rank::Three, Rank::Four, Rank::Five, Rank::Six, Rank::Seven] {
            hand.push(Card::new(Suit::Spades, rank));
            hand.push(Card::new(Suit::Hearts, rank));
        }
    }

    // Use a very low limit to trigger error
    let result = PlayGenerator::generate_all_plays(&hand, 10);

    assert!(result.is_err());
    assert!(result.unwrap_err().contains("exceeds limit"));
}

#[test]
fn test_generate_beating_plays_empty_hand() {
    let hand: Vec<Card> = vec![];
    let current_play = vec![Card::new(Suit::Spades, Rank::Five)];
    let current_pattern = PatternRecognizer::analyze_cards(&current_play).unwrap();

    let beating_plays =
        PlayGenerator::generate_beating_plays_with_same_type_or_trump(&hand, &current_pattern);

    assert!(beating_plays.is_empty());
}

#[test]
fn test_count_all_plays_empty_hand() {
    let hand: Vec<Card> = vec![];

    let count = PlayGenerator::count_all_plays(&hand);

    assert_eq!(count, 0);
}
