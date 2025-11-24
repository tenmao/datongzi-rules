//! Basic integration tests for datongzi-rules

use datongzi_rules::{Card, Deck, GameConfig, Rank, Suit};

#[test]
fn test_card_creation() {
    let card = Card::new(Suit::Spades, Rank::Ace);
    assert_eq!(card.suit(), Suit::Spades);
    assert_eq!(card.rank(), Rank::Ace);
}

#[test]
fn test_card_scoring() {
    let five = Card::new(Suit::Hearts, Rank::Five);
    assert!(five.is_scoring_card());
    assert_eq!(five.score_value(), 5);

    let ten = Card::new(Suit::Diamonds, Rank::Ten);
    assert!(ten.is_scoring_card());
    assert_eq!(ten.score_value(), 10);

    let king = Card::new(Suit::Clubs, Rank::King);
    assert!(king.is_scoring_card());
    assert_eq!(king.score_value(), 10);

    let ace = Card::new(Suit::Spades, Rank::Ace);
    assert!(!ace.is_scoring_card());
    assert_eq!(ace.score_value(), 0);
}

#[test]
fn test_deck_creation() {
    let deck = Deck::new(1, &[]);
    assert_eq!(deck.remaining(), 52);

    let deck_no_3_4 = Deck::new(1, &[Rank::Three, Rank::Four]);
    assert_eq!(deck_no_3_4.remaining(), 44);
}

#[test]
fn test_deck_dealing() {
    let mut deck = Deck::new(1, &[]);
    let hand = deck.deal(13);
    assert_eq!(hand.len(), 13);
    assert_eq!(deck.remaining(), 39);
}

#[test]
fn test_game_config_default() {
    let config = GameConfig::default();
    assert!(config.validate().is_ok());
}

#[test]
fn test_game_config_custom() {
    let config = GameConfig::new(3, 3, 44, 0, vec![100, -40, -60], 100, 200, 300, 400);
    assert!(config.validate().is_ok());
    assert_eq!(config.num_decks(), 3);
    assert_eq!(config.num_players(), 3);
}
