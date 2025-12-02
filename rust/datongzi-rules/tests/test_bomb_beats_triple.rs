//! Test: Bomb beats various patterns

use datongzi_rules::{Card, PatternRecognizer, PlayValidator, Rank, Suit};

#[test]
fn test_six_fives_bomb_beats_triple_nine() {
    // From log: choice=FiveDiamonds,FiveSpades,FiveHearts,FiveClubs,FiveDiamonds,FiveSpades
    let choice = vec![
        Card::new(Suit::Diamonds, Rank::Five),
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Clubs, Rank::Five),
        Card::new(Suit::Diamonds, Rank::Five), // duplicate suit from another deck
        Card::new(Suit::Spades, Rank::Five),   // duplicate suit from another deck
    ];

    let pattern = PatternRecognizer::analyze_cards(&choice);
    println!("6 Fives pattern: {:?}", pattern);
    assert!(
        pattern.is_some(),
        "6 Fives should be recognized as a pattern"
    );

    let p = pattern.unwrap();
    assert_eq!(
        p.play_type,
        datongzi_rules::patterns::PlayType::Bomb,
        "6 Fives should be a Bomb"
    );
    assert_eq!(p.card_count, 6, "Should have 6 cards");

    // Triple of 9s
    let triple = vec![
        Card::new(Suit::Spades, Rank::Nine),
        Card::new(Suit::Hearts, Rank::Nine),
        Card::new(Suit::Clubs, Rank::Nine),
    ];
    let triple_pattern = PatternRecognizer::analyze_cards(&triple).unwrap();
    println!("Triple 9s pattern: {:?}", triple_pattern);
    assert_eq!(
        triple_pattern.play_type,
        datongzi_rules::patterns::PlayType::Triple
    );

    let can_beat = PlayValidator::can_beat_play(&choice, Some(&triple_pattern));
    println!("Can 6 Fives beat Triple 9s? {}", can_beat);
    assert!(can_beat, "6-card Bomb should beat Triple!");
}

#[test]
fn test_four_jacks_bomb_beats_triple_nine() {
    // From log: choice=JackDiamonds,JackSpades,JackSpades,JackClubs
    let choice = vec![
        Card::new(Suit::Diamonds, Rank::Jack),
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Spades, Rank::Jack), // duplicate suit
        Card::new(Suit::Clubs, Rank::Jack),
    ];

    let pattern = PatternRecognizer::analyze_cards(&choice);
    println!("4 Jacks pattern: {:?}", pattern);
    assert!(
        pattern.is_some(),
        "4 Jacks should be recognized as a pattern"
    );

    let p = pattern.unwrap();
    assert_eq!(
        p.play_type,
        datongzi_rules::patterns::PlayType::Bomb,
        "4 Jacks should be a Bomb"
    );
    assert_eq!(p.card_count, 4, "Should have 4 cards");

    // Triple of 9s (strength=9)
    let triple = vec![
        Card::new(Suit::Spades, Rank::Nine),
        Card::new(Suit::Hearts, Rank::Nine),
        Card::new(Suit::Clubs, Rank::Nine),
    ];
    let triple_pattern = PatternRecognizer::analyze_cards(&triple).unwrap();

    let can_beat = PlayValidator::can_beat_play(&choice, Some(&triple_pattern));
    println!("Can 4 Jacks beat Triple 9s? {}", can_beat);
    assert!(can_beat, "4-card Bomb should beat Triple!");
}

#[test]
fn test_bomb_beats_airplane_with_wings() {
    // From log: pattern=AirplaneWithWings strength=10002, choice=NineDiamonds,NineClubs,NineHearts,NineSpades
    let choice = vec![
        Card::new(Suit::Diamonds, Rank::Nine),
        Card::new(Suit::Clubs, Rank::Nine),
        Card::new(Suit::Hearts, Rank::Nine),
        Card::new(Suit::Spades, Rank::Nine),
    ];

    let pattern = PatternRecognizer::analyze_cards(&choice);
    println!("4 Nines pattern: {:?}", pattern);
    assert!(
        pattern.is_some(),
        "4 Nines should be recognized as a pattern"
    );
    let p = pattern.unwrap();
    assert_eq!(
        p.play_type,
        datongzi_rules::patterns::PlayType::Bomb,
        "4 Nines should be a Bomb"
    );

    // AirplaneWithWings: 888999 + 2 kickers = strength 10002
    // Let's create a simple AirplaneWithWings for testing
    let airplane = vec![
        Card::new(Suit::Spades, Rank::Eight),
        Card::new(Suit::Hearts, Rank::Eight),
        Card::new(Suit::Clubs, Rank::Eight),
        Card::new(Suit::Spades, Rank::Nine),
        Card::new(Suit::Hearts, Rank::Nine),
        Card::new(Suit::Clubs, Rank::Nine),
        Card::new(Suit::Spades, Rank::Five), // kicker
        Card::new(Suit::Hearts, Rank::Six),  // kicker
    ];
    let airplane_pattern = PatternRecognizer::analyze_cards(&airplane);
    println!("AirplaneWithWings pattern: {:?}", airplane_pattern);
    assert!(airplane_pattern.is_some());
    let ap = airplane_pattern.unwrap();
    assert_eq!(
        ap.play_type,
        datongzi_rules::patterns::PlayType::AirplaneWithWings
    );

    let can_beat = PlayValidator::can_beat_play(&choice, Some(&ap));
    println!("Can 4 Nines (Bomb) beat AirplaneWithWings? {}", can_beat);
    assert!(can_beat, "Bomb should beat AirplaneWithWings!");
}

#[test]
fn test_eight_jacks_is_dizha() {
    // From log: choice=JackSpades,JackSpades,JackHearts,JackHearts,JackClubs,JackClubs,JackDiamonds,JackDiamonds
    let choice = vec![
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
        Card::new(Suit::Diamonds, Rank::Jack),
        Card::new(Suit::Diamonds, Rank::Jack),
    ];

    let pattern = PatternRecognizer::analyze_cards(&choice);
    println!("8 Jacks pattern: {:?}", pattern);
    assert!(
        pattern.is_some(),
        "8 Jacks should be recognized as a pattern"
    );
    let p = pattern.unwrap();
    assert_eq!(
        p.play_type,
        datongzi_rules::patterns::PlayType::Dizha,
        "8 Jacks (2 each suit) should be Dizha"
    );
    assert_eq!(p.card_count, 8);
}

#[test]
fn test_triple_with_two_kickers() {
    // From log: choice=NineSpades,NineClubs,NineHearts,SixHearts,SixHearts
    // This is Triple (999) + 2 kickers (66)
    let choice = vec![
        Card::new(Suit::Spades, Rank::Nine),
        Card::new(Suit::Clubs, Rank::Nine),
        Card::new(Suit::Hearts, Rank::Nine),
        Card::new(Suit::Hearts, Rank::Six),
        Card::new(Suit::Hearts, Rank::Six),
    ];

    let pattern = PatternRecognizer::analyze_cards(&choice);
    println!("Triple 999 + 66 pattern: {:?}", pattern);
    assert!(pattern.is_some(), "Triple with 2 kickers should be valid");
    let p = pattern.unwrap();
    assert_eq!(p.play_type, datongzi_rules::patterns::PlayType::Triple);
    assert_eq!(p.card_count, 5);
}

#[test]
fn test_invalid_pattern_66_77() {
    // From log: choice=SixClubs,SixDiamonds,SevenClubs,SevenHearts
    // This is 2x6 + 2x7, NOT consecutive pairs (5,6 is consecutive, 6,7 is consecutive)
    // Wait - 6 and 7 ARE consecutive!
    let choice = vec![
        Card::new(Suit::Clubs, Rank::Six),
        Card::new(Suit::Diamonds, Rank::Six),
        Card::new(Suit::Clubs, Rank::Seven),
        Card::new(Suit::Hearts, Rank::Seven),
    ];

    let pattern = PatternRecognizer::analyze_cards(&choice);
    println!("66 + 77 pattern: {:?}", pattern);
    // 6677 should be ConsecutivePairs!
    assert!(pattern.is_some(), "66+77 should be valid ConsecutivePairs");
}

#[test]
fn test_five_sevens_bomb() {
    // From log: choice=SevenDiamonds,SevenClubs,SevenClubs,SevenHearts,SevenDiamonds
    // This is 5 sevens (with duplicate suits) - should be Bomb
    let choice = vec![
        Card::new(Suit::Diamonds, Rank::Seven),
        Card::new(Suit::Clubs, Rank::Seven),
        Card::new(Suit::Clubs, Rank::Seven), // duplicate
        Card::new(Suit::Hearts, Rank::Seven),
        Card::new(Suit::Diamonds, Rank::Seven), // duplicate
    ];

    let pattern = PatternRecognizer::analyze_cards(&choice);
    println!("5 Sevens pattern: {:?}", pattern);
    assert!(pattern.is_some(), "5 Sevens should be valid Bomb");
    let p = pattern.unwrap();
    assert_eq!(p.play_type, datongzi_rules::patterns::PlayType::Bomb);
    assert_eq!(p.card_count, 5);
}

#[test]
fn test_triple_with_dup_suit_and_kickers() {
    // From log: choice=SevenClubs,SevenDiamonds,SevenClubs,NineHearts,TwoHearts
    // This is 3 sevens (2 clubs, 1 diamond) + kickers
    let choice = vec![
        Card::new(Suit::Clubs, Rank::Seven),
        Card::new(Suit::Diamonds, Rank::Seven),
        Card::new(Suit::Clubs, Rank::Seven), // duplicate suit
        Card::new(Suit::Hearts, Rank::Nine),
        Card::new(Suit::Hearts, Rank::Two),
    ];

    let pattern = PatternRecognizer::analyze_cards(&choice);
    println!("Triple 7(dup suit) + kickers pattern: {:?}", pattern);
    // Should be valid Triple with 2 kickers
    assert!(
        pattern.is_some(),
        "Triple with dup suit + kickers should be valid"
    );
    let p = pattern.unwrap();
    assert_eq!(p.play_type, datongzi_rules::patterns::PlayType::Triple);
}

#[test]
fn test_99_1010_not_consec_pairs() {
    // From log: choice=NineSpades,NineSpades,TenSpades,TenClubs
    // 2 nines (both spades) + 2 tens (spades + clubs)
    let choice = vec![
        Card::new(Suit::Spades, Rank::Nine),
        Card::new(Suit::Spades, Rank::Nine), // duplicate suit
        Card::new(Suit::Spades, Rank::Ten),
        Card::new(Suit::Clubs, Rank::Ten),
    ];

    let pattern = PatternRecognizer::analyze_cards(&choice);
    println!("99(dup)+1010 pattern: {:?}", pattern);
    // Should be ConsecutivePairs - 9,10 are consecutive
    assert!(pattern.is_some(), "Should be valid ConsecutivePairs");
}
