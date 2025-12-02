//! Test: Tongzi vs Bomb scenarios

use datongzi_rules::patterns::PlayType;
use datongzi_rules::{Card, PatternRecognizer, PlayValidator, Rank, Suit};

#[test]
fn test_three_six_clubs_is_tongzi() {
    // From log: choice=SixClubs,SixClubs,SixClubs
    let choice = vec![
        Card::new(Suit::Clubs, Rank::Six),
        Card::new(Suit::Clubs, Rank::Six),
        Card::new(Suit::Clubs, Rank::Six),
    ];

    let pattern = PatternRecognizer::analyze_cards(&choice);
    println!("3x SixClubs pattern: {:?}", pattern);

    assert!(pattern.is_some(), "3x SixClubs should be a valid pattern");
    let p = pattern.unwrap();
    assert_eq!(
        p.play_type,
        PlayType::Tongzi,
        "3x same suit same rank should be Tongzi"
    );
}

#[test]
fn test_tongzi_beats_bomb() {
    // Tongzi: 3x SixClubs
    let tongzi = vec![
        Card::new(Suit::Clubs, Rank::Six),
        Card::new(Suit::Clubs, Rank::Six),
        Card::new(Suit::Clubs, Rank::Six),
    ];

    // Bomb: 5x Queen
    let bomb = vec![
        Card::new(Suit::Spades, Rank::Queen),
        Card::new(Suit::Hearts, Rank::Queen),
        Card::new(Suit::Clubs, Rank::Queen),
        Card::new(Suit::Diamonds, Rank::Queen),
        Card::new(Suit::Spades, Rank::Queen),
    ];

    let bomb_pattern = PatternRecognizer::analyze_cards(&bomb).unwrap();
    println!("Bomb pattern: {:?}", bomb_pattern);
    assert_eq!(bomb_pattern.play_type, PlayType::Bomb);

    let can_beat = PlayValidator::can_beat_play(&tongzi, Some(&bomb_pattern));
    println!("Can Tongzi (6♣6♣6♣) beat 5x Queen Bomb? {}", can_beat);

    assert!(can_beat, "Tongzi should beat any Bomb!");
}

#[test]
fn test_tongzi_strength_12005_scenario() {
    // From log: pattern=Bomb strength=12005, choice=SixClubs,SixClubs,SixClubs
    // Bomb strength 12005 = Queen (rank 12) x 5 cards

    // Build the bomb pattern
    let bomb = vec![
        Card::new(Suit::Spades, Rank::Queen),
        Card::new(Suit::Hearts, Rank::Queen),
        Card::new(Suit::Clubs, Rank::Queen),
        Card::new(Suit::Diamonds, Rank::Queen),
        Card::new(Suit::Spades, Rank::Queen),
    ];

    let bomb_pattern = PatternRecognizer::analyze_cards(&bomb).unwrap();
    println!("Bomb pattern strength: {}", bomb_pattern.strength);
    // Note: actual strength might differ from 12005 based on encoding

    // AI's choice
    let choice = vec![
        Card::new(Suit::Clubs, Rank::Six),
        Card::new(Suit::Clubs, Rank::Six),
        Card::new(Suit::Clubs, Rank::Six),
    ];

    let choice_pattern = PatternRecognizer::analyze_cards(&choice);
    println!("Choice pattern: {:?}", choice_pattern);

    assert!(choice_pattern.is_some());
    let cp = choice_pattern.unwrap();
    assert_eq!(cp.play_type, PlayType::Tongzi);

    let can_beat = PlayValidator::can_beat_play(&choice, Some(&bomb_pattern));
    println!("Can choice beat bomb? {}", can_beat);

    assert!(
        can_beat,
        "Tongzi should beat Bomb - this is the failing scenario from logs!"
    );
}
