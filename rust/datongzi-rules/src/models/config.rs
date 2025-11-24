//! Game configuration.

/// Game configuration parameters
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct GameConfig {
    /// Number of decks
    pub num_decks: u8,
    /// Number of players
    pub num_players: u8,
    /// Cards per player
    pub cards_per_player: usize,
    /// Cards dealt aside (bottom cards)
    pub cards_dealt_aside: usize,
}

impl Default for GameConfig {
    fn default() -> Self {
        Self {
            num_decks: 3,
            num_players: 3,
            cards_per_player: 41,
            cards_dealt_aside: 9,
        }
    }
}

impl GameConfig {
    /// Creates a new game configuration
    #[must_use]
    pub const fn new(
        num_decks: u8,
        num_players: u8,
        cards_per_player: usize,
        cards_dealt_aside: usize,
    ) -> Self {
        Self {
            num_decks,
            num_players,
            cards_per_player,
            cards_dealt_aside,
        }
    }

    /// Returns the number of decks
    #[must_use]
    pub const fn num_decks(&self) -> u8 {
        self.num_decks
    }

    /// Returns the number of players
    #[must_use]
    pub const fn num_players(&self) -> u8 {
        self.num_players
    }

    /// Returns the number of cards per player
    #[must_use]
    pub const fn cards_per_player(&self) -> usize {
        self.cards_per_player
    }

    /// Returns the number of cards dealt aside
    #[must_use]
    pub const fn cards_dealt_aside(&self) -> usize {
        self.cards_dealt_aside
    }

    /// Validates the configuration
    ///
    /// # Errors
    ///
    /// Returns an error if the configuration is invalid
    pub fn validate(&self) -> crate::Result<()> {
        let total_cards = usize::from(self.num_decks) * 52;
        let required_cards = self.cards_per_player * usize::from(self.num_players) + self.cards_dealt_aside;

        if required_cards > total_cards {
            return Err(crate::DatongziError::ConfigError(
                format!("Not enough cards: need {required_cards}, have {total_cards}")
            ));
        }

        if !(2..=4).contains(&self.num_players) {
            return Err(crate::DatongziError::ConfigError(
                format!("Invalid number of players: {}", self.num_players)
            ));
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_default_config() {
        let config = GameConfig::default();
        assert_eq!(config.num_decks, 3);
        assert_eq!(config.num_players, 3);
        assert!(config.validate().is_ok());
    }
}
