//! Card-related data structures.

use std::fmt;

/// Card suit with ordering: SPADES > HEARTS > CLUBS > DIAMONDS
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
#[repr(u8)]
pub enum Suit {
    /// Diamonds (方块) - lowest suit
    Diamonds = 1,
    /// Clubs (梅花)
    Clubs = 2,
    /// Hearts (红桃)
    Hearts = 3,
    /// Spades (黑桃) - highest suit
    Spades = 4,
}

impl Suit {
    /// Returns the numeric value of the suit (1-4)
    #[must_use]
    pub const fn value(self) -> u8 {
        self as u8
    }
}

impl fmt::Display for Suit {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let symbol = match self {
            Self::Spades => "♠",
            Self::Hearts => "♥",
            Self::Clubs => "♣",
            Self::Diamonds => "♦",
        };
        write!(f, "{symbol}")
    }
}

/// Card rank with ordering: TWO > ACE > KING > ... > THREE
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
#[repr(u8)]
pub enum Rank {
    /// Three - lowest rank
    Three = 3,
    /// Four
    Four = 4,
    /// Five (scoring card: 5 points)
    Five = 5,
    /// Six
    Six = 6,
    /// Seven
    Seven = 7,
    /// Eight
    Eight = 8,
    /// Nine
    Nine = 9,
    /// Ten (scoring card: 10 points)
    Ten = 10,
    /// Jack
    Jack = 11,
    /// Queen
    Queen = 12,
    /// King (scoring card: 10 points)
    King = 13,
    /// Ace
    Ace = 14,
    /// Two - highest rank
    Two = 15,
}

impl Rank {
    /// Returns the numeric value of the rank (3-15)
    #[must_use]
    pub const fn value(self) -> u8 {
        self as u8
    }
}

impl fmt::Display for Rank {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let s = match self {
            Self::Three => "3",
            Self::Four => "4",
            Self::Five => "5",
            Self::Six => "6",
            Self::Seven => "7",
            Self::Eight => "8",
            Self::Nine => "9",
            Self::Ten => "10",
            Self::Jack => "J",
            Self::Queen => "Q",
            Self::King => "K",
            Self::Ace => "A",
            Self::Two => "2",
        };
        write!(f, "{s}")
    }
}

/// A playing card with suit and rank
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct Card {
    /// Card suit
    pub suit: Suit,
    /// Card rank
    pub rank: Rank,
}

impl Card {
    /// Creates a new card
    #[must_use]
    pub const fn new(suit: Suit, rank: Rank) -> Self {
        Self { suit, rank }
    }

    /// Returns the suit of this card
    #[must_use]
    pub const fn suit(&self) -> Suit {
        self.suit
    }

    /// Returns the rank of this card
    #[must_use]
    pub const fn rank(&self) -> Rank {
        self.rank
    }

    /// Returns true if this is a scoring card (5, 10, or K)
    #[must_use]
    pub const fn is_scoring_card(&self) -> bool {
        matches!(self.rank, Rank::Five | Rank::Ten | Rank::King)
    }

    /// Returns the score value of this card (5, 10, or 0)
    #[must_use]
    pub const fn score_value(&self) -> i32 {
        match self.rank {
            Rank::Five => 5,
            Rank::Ten | Rank::King => 10,
            _ => 0,
        }
    }
}

impl PartialOrd for Card {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for Card {
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        // Cards are ordered by rank first, then by suit
        self.rank.cmp(&other.rank).then(self.suit.cmp(&other.suit))
    }
}

impl fmt::Display for Card {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}{}", self.rank, self.suit)
    }
}

/// A deck of cards
#[derive(Debug, Clone)]
pub struct Deck {
    cards: Vec<Card>,
}

impl Deck {
    /// Creates a new deck with the specified number of decks and excluded ranks
    ///
    /// # Arguments
    ///
    /// * `num_decks` - Number of standard 52-card decks to include
    /// * `excluded_ranks` - Ranks to exclude from the deck (e.g., &[Rank::Three, Rank::Four])
    #[must_use]
    pub fn new(num_decks: u8, excluded_ranks: &[Rank]) -> Self {
        let mut cards = Vec::with_capacity(usize::from(num_decks) * 52);

        for _ in 0..num_decks {
            for suit in [Suit::Diamonds, Suit::Clubs, Suit::Hearts, Suit::Spades] {
                for rank in [
                    Rank::Three,
                    Rank::Four,
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
                    if !excluded_ranks.contains(&rank) {
                        cards.push(Card::new(suit, rank));
                    }
                }
            }
        }

        Self { cards }
    }

    /// Creates a standard deck with the specified number of decks
    #[must_use]
    pub fn create_standard_deck(num_decks: u8) -> Self {
        Self::new(num_decks, &[])
    }

    /// Shuffles the deck
    pub fn shuffle(&mut self) {
        use rand::seq::SliceRandom;
        use rand::thread_rng;

        let mut rng = thread_rng();
        self.cards.shuffle(&mut rng);
    }

    /// Deals the specified number of cards from the deck
    ///
    /// # Panics
    ///
    /// Panics if there are not enough cards in the deck
    #[must_use]
    pub fn deal_cards(&mut self, count: usize) -> Vec<Card> {
        self.cards.split_off(self.cards.len() - count)
    }

    /// Deals the specified number of cards from the deck (alias for deal_cards)
    ///
    /// # Panics
    ///
    /// Panics if there are not enough cards in the deck
    #[must_use]
    pub fn deal(&mut self, count: usize) -> Vec<Card> {
        self.deal_cards(count)
    }

    /// Returns the number of cards remaining in the deck
    #[must_use]
    pub fn len(&self) -> usize {
        self.cards.len()
    }

    /// Returns the number of cards remaining in the deck (alias for len)
    #[must_use]
    pub fn remaining(&self) -> usize {
        self.len()
    }

    /// Returns true if the deck is empty
    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.cards.is_empty()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_suit_ordering() {
        assert!(Suit::Spades > Suit::Hearts);
        assert!(Suit::Hearts > Suit::Clubs);
        assert!(Suit::Clubs > Suit::Diamonds);
    }

    #[test]
    fn test_rank_ordering() {
        assert!(Rank::Two > Rank::Ace);
        assert!(Rank::Ace > Rank::King);
        assert!(Rank::King > Rank::Three);
    }

    #[test]
    fn test_card_creation() {
        let card = Card::new(Suit::Spades, Rank::Ace);
        assert_eq!(card.suit, Suit::Spades);
        assert_eq!(card.rank, Rank::Ace);
    }

    #[test]
    fn test_scoring_cards() {
        assert!(Card::new(Suit::Spades, Rank::Five).is_scoring_card());
        assert!(Card::new(Suit::Spades, Rank::Ten).is_scoring_card());
        assert!(Card::new(Suit::Spades, Rank::King).is_scoring_card());
        assert!(!Card::new(Suit::Spades, Rank::Ace).is_scoring_card());
    }

    #[test]
    fn test_score_value() {
        assert_eq!(Card::new(Suit::Spades, Rank::Five).score_value(), 5);
        assert_eq!(Card::new(Suit::Spades, Rank::Ten).score_value(), 10);
        assert_eq!(Card::new(Suit::Spades, Rank::King).score_value(), 10);
        assert_eq!(Card::new(Suit::Spades, Rank::Ace).score_value(), 0);
    }

    #[test]
    fn test_deck_creation() {
        let deck = Deck::create_standard_deck(3);
        assert_eq!(deck.len(), 156); // 3 * 52 cards
    }

    #[test]
    fn test_deck_deal() {
        let mut deck = Deck::create_standard_deck(1);
        let hand = deck.deal_cards(13);
        assert_eq!(hand.len(), 13);
        assert_eq!(deck.len(), 39);
    }
}
