use datongzi_rules::{Card, PatternRecognizer, PlayValidator, Rank, Suit};

#[test]
fn test_bomb_with_duplicate_suits() {
    // Case 1: 4 Kings with different suits (valid bomb)
    let valid_bomb = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Clubs, Rank::King),
        Card::new(Suit::Diamonds, Rank::King),
    ];
    let result = PatternRecognizer::analyze_cards(&valid_bomb);
    println!("Valid bomb (K♠K♥K♣K♦): {:?}", result);
    assert!(result.is_some());

    // Case 2: 4 Kings with duplicate suits (potentially invalid)
    let dup_suit_bomb = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Spades, Rank::King), // Duplicate!
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Diamonds, Rank::King),
    ];
    let result = PatternRecognizer::analyze_cards(&dup_suit_bomb);
    println!("Dup suit bomb (K♠K♠K♥K♦): {:?}", result);
    // What does the recognizer say?

    // Case 3: 6 Queens with only 3 suits (from the log)
    let six_queens = vec![
        Card::new(Suit::Clubs, Rank::Queen),
        Card::new(Suit::Spades, Rank::Queen),
        Card::new(Suit::Clubs, Rank::Queen),
        Card::new(Suit::Hearts, Rank::Queen),
        Card::new(Suit::Hearts, Rank::Queen),
        Card::new(Suit::Spades, Rank::Queen),
    ];
    let result = PatternRecognizer::analyze_cards(&six_queens);
    println!("6 Queens (Q♣Q♠Q♣Q♥Q♥Q♠): {:?}", result);

    // Case 4: Test can_beat_play with the 5-card J bomb vs 6 Queens
    let five_jacks = vec![
        Card::new(Suit::Diamonds, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Diamonds, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
    ];
    let j_pattern = PatternRecognizer::analyze_cards(&five_jacks);
    println!("5 Jacks pattern: {:?}", j_pattern);

    let can_beat = PlayValidator::can_beat_play(&six_queens, j_pattern.as_ref());
    println!("Can 6 Queens beat 5 Jacks? {}", can_beat);
}
