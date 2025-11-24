//! Unit tests for HandPatternAnalyzer.

use datongzi_rules::{Card, HandPatternAnalyzer, Rank, Suit};

#[test]
fn test_analyze_empty_hand() {
    let patterns = HandPatternAnalyzer::analyze_patterns(&[]);

    assert_eq!(patterns.total_cards, 0);
    assert_eq!(patterns.trump_count, 0);
    assert_eq!(patterns.singles.len(), 0);
}

#[test]
fn test_analyze_singles_only() {
    let hand = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Seven),
        Card::new(Suit::Clubs, Rank::Nine),
    ];

    let patterns = HandPatternAnalyzer::analyze_patterns(&hand);

    assert_eq!(patterns.total_cards, 3);
    assert_eq!(patterns.singles.len(), 3);
    assert_eq!(patterns.pairs.len(), 0);
    assert_eq!(patterns.trump_count, 0);
}

#[test]
fn test_analyze_pairs() {
    let hand = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Clubs, Rank::Five),
        Card::new(Suit::Diamonds, Rank::Five),
    ];

    let patterns = HandPatternAnalyzer::analyze_patterns(&hand);

    assert_eq!(patterns.total_cards, 4);
    assert_eq!(patterns.pairs.len(), 2);
    assert_eq!(patterns.singles.len(), 0);
}

#[test]
fn test_analyze_triples() {
    let hand = vec![
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Ace),
        Card::new(Suit::Clubs, Rank::Ace),
    ];

    let patterns = HandPatternAnalyzer::analyze_patterns(&hand);

    assert_eq!(patterns.total_cards, 3);
    assert_eq!(patterns.triples.len(), 1);
    assert_eq!(patterns.triples[0].len(), 3);
}

#[test]
fn test_analyze_bomb() {
    let hand = vec![
        Card::new(Suit::Spades, Rank::Ten),
        Card::new(Suit::Hearts, Rank::Ten),
        Card::new(Suit::Clubs, Rank::Ten),
        Card::new(Suit::Diamonds, Rank::Ten),
    ];

    let patterns = HandPatternAnalyzer::analyze_patterns(&hand);

    assert_eq!(patterns.total_cards, 4);
    assert_eq!(patterns.bombs.len(), 1);
    assert_eq!(patterns.trump_count, 1);
    assert_eq!(patterns.bombs[0].len(), 4);
}

#[test]
fn test_analyze_tongzi() {
    let hand = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Spades, Rank::King),
    ];

    let patterns = HandPatternAnalyzer::analyze_patterns(&hand);

    assert_eq!(patterns.total_cards, 3);
    assert_eq!(patterns.tongzi.len(), 1);
    assert_eq!(patterns.trump_count, 1);
}

#[test]
fn test_analyze_consecutive_pairs() {
    let hand = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Spades, Rank::Six),
        Card::new(Suit::Hearts, Rank::Six),
        Card::new(Suit::Spades, Rank::Seven),
        Card::new(Suit::Hearts, Rank::Seven),
    ];

    let patterns = HandPatternAnalyzer::analyze_patterns(&hand);

    assert_eq!(patterns.total_cards, 6);
    assert_eq!(patterns.consecutive_pair_chains.len(), 1);
    assert_eq!(patterns.consecutive_pair_chains[0].len(), 6);
}

#[test]
fn test_analyze_airplane_chain() {
    let hand = vec![
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
        Card::new(Suit::Spades, Rank::Queen),
        Card::new(Suit::Hearts, Rank::Queen),
        Card::new(Suit::Clubs, Rank::Queen),
    ];

    let patterns = HandPatternAnalyzer::analyze_patterns(&hand);

    assert_eq!(patterns.total_cards, 6);
    assert_eq!(patterns.airplane_chains.len(), 1);
    assert_eq!(patterns.airplane_chains[0].len(), 6);
}

#[test]
fn test_analyze_complex_hand() {
    let hand = vec![
        // Bomb
        Card::new(Suit::Spades, Rank::Ten),
        Card::new(Suit::Hearts, Rank::Ten),
        Card::new(Suit::Clubs, Rank::Ten),
        Card::new(Suit::Diamonds, Rank::Ten),
        // Triple
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Ace),
        Card::new(Suit::Clubs, Rank::Ace),
        // Pair
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        // Singles
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Seven),
    ];

    let patterns = HandPatternAnalyzer::analyze_patterns(&hand);

    assert_eq!(patterns.total_cards, 11);
    assert_eq!(patterns.bombs.len(), 1);
    assert_eq!(patterns.triples.len(), 1);
    assert_eq!(patterns.pairs.len(), 1);
    assert_eq!(patterns.singles.len(), 2);
    assert_eq!(patterns.trump_count, 1);
    assert!(patterns.has_control_cards); // Has ACE and KING
}

#[test]
fn test_analyze_dizha() {
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

    let patterns = HandPatternAnalyzer::analyze_patterns(&hand);

    assert_eq!(patterns.total_cards, 8);
    assert_eq!(patterns.dizha.len(), 1);
    assert_eq!(patterns.trump_count, 1);
}

#[test]
fn test_non_overlapping_structure_analysis() {
    let hand = vec![
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Ace),
        Card::new(Suit::Clubs, Rank::Ace),
        Card::new(Suit::Diamonds, Rank::Ace),
    ];

    let patterns = HandPatternAnalyzer::analyze_patterns(&hand);

    // Should be classified as bomb, not triple + single
    assert_eq!(patterns.bombs.len(), 1);
    assert_eq!(patterns.triples.len(), 0);
    assert_eq!(patterns.singles.len(), 0);

    // Verify total cards match
    let total_in_patterns = patterns.dizha.iter().map(|d| d.len()).sum::<usize>()
        + patterns.tongzi.iter().map(|t| t.len()).sum::<usize>()
        + patterns.bombs.iter().map(|b| b.len()).sum::<usize>()
        + patterns
            .airplane_chains
            .iter()
            .map(|a| a.len())
            .sum::<usize>()
        + patterns
            .consecutive_pair_chains
            .iter()
            .map(|c| c.len())
            .sum::<usize>()
        + patterns.triples.iter().map(|t| t.len()).sum::<usize>()
        + patterns.pairs.iter().map(|p| p.len()).sum::<usize>()
        + patterns.singles.len();

    assert_eq!(total_in_patterns, patterns.total_cards);
}

#[test]
fn test_patterns_sorting() {
    let hand = vec![
        // Two pairs
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        // Two singles
        Card::new(Suit::Clubs, Rank::Six),
        Card::new(Suit::Clubs, Rank::Ace),
    ];

    let patterns = HandPatternAnalyzer::analyze_patterns(&hand);

    // Pairs should be sorted by rank (descending)
    assert_eq!(patterns.pairs.len(), 2);
    assert_eq!(patterns.pairs[0][0].rank, Rank::King);
    assert_eq!(patterns.pairs[1][0].rank, Rank::Five);

    // Singles should be sorted by rank (descending)
    assert_eq!(patterns.singles.len(), 2);
    assert_eq!(patterns.singles[0].rank, Rank::Ace);
    assert_eq!(patterns.singles[1].rank, Rank::Six);
}

#[test]
fn test_hand_patterns_display() {
    let hand = vec![
        Card::new(Suit::Spades, Rank::Ten),
        Card::new(Suit::Hearts, Rank::Ten),
        Card::new(Suit::Clubs, Rank::Ten),
        Card::new(Suit::Diamonds, Rank::Ten),
    ];

    let patterns = HandPatternAnalyzer::analyze_patterns(&hand);
    let str_repr = format!("{}", patterns);

    assert!(str_repr.contains("HandPatterns"));
    assert!(str_repr.contains("4 cards"));
    assert!(str_repr.contains("Bombs:1"));
}

#[test]
fn test_control_cards_detection() {
    // Hand with no control cards
    let hand1 = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Six),
    ];
    let patterns1 = HandPatternAnalyzer::analyze_patterns(&hand1);
    assert!(!patterns1.has_control_cards);

    // Hand with 2 (control card)
    let hand2 = vec![
        Card::new(Suit::Spades, Rank::Two),
        Card::new(Suit::Hearts, Rank::Five),
    ];
    let patterns2 = HandPatternAnalyzer::analyze_patterns(&hand2);
    assert!(patterns2.has_control_cards);

    // Hand with ACE (control card)
    let hand3 = vec![
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Five),
    ];
    let patterns3 = HandPatternAnalyzer::analyze_patterns(&hand3);
    assert!(patterns3.has_control_cards);

    // Hand with KING (control card)
    let hand4 = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::Five),
    ];
    let patterns4 = HandPatternAnalyzer::analyze_patterns(&hand4);
    assert!(patterns4.has_control_cards);
}

#[test]
fn test_triple_vs_consecutive_pairs_priority() {
    // Hand that could be either triples or consecutive pairs
    // Priority: Triples should be extracted first
    let hand = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Clubs, Rank::Five),
        Card::new(Suit::Spades, Rank::Six),
        Card::new(Suit::Hearts, Rank::Six),
        Card::new(Suit::Clubs, Rank::Six),
    ];

    let patterns = HandPatternAnalyzer::analyze_patterns(&hand);

    // Should extract as airplane chain (consecutive triples), not as consecutive pairs
    // Because airplanes are extracted before consecutive pairs
    assert_eq!(patterns.airplane_chains.len(), 1);
    assert_eq!(patterns.consecutive_pair_chains.len(), 0);
    assert_eq!(patterns.triples.len(), 0);
}
