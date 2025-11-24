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
