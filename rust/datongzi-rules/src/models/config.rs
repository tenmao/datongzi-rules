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
    /// Finish position bonuses (上游, 二游, 三游)
    pub finish_bonus: Vec<i32>,
    /// K Tongzi bonus points
    pub k_tongzi_bonus: i32,
    /// A Tongzi bonus points
    pub a_tongzi_bonus: i32,
    /// 2 Tongzi bonus points
    pub two_tongzi_bonus: i32,
    /// Dizha bonus points
    pub dizha_bonus: i32,
}

impl Default for GameConfig {
    fn default() -> Self {
        Self {
            num_decks: 3,
            num_players: 3,
            cards_per_player: 41,
            cards_dealt_aside: 9,
            finish_bonus: vec![100, -40, -60],
            k_tongzi_bonus: 100,
            a_tongzi_bonus: 200,
            two_tongzi_bonus: 300,
            dizha_bonus: 400,
        }
    }
}

impl GameConfig {
    /// Creates a new game configuration with scoring defaults
    #[must_use]
    #[allow(clippy::too_many_arguments)]
    pub fn new(
        num_decks: u8,
        num_players: u8,
        cards_per_player: usize,
        cards_dealt_aside: usize,
        finish_bonus: Vec<i32>,
        k_tongzi_bonus: i32,
        a_tongzi_bonus: i32,
        two_tongzi_bonus: i32,
        dizha_bonus: i32,
    ) -> Self {
        Self {
            num_decks,
            num_players,
            cards_per_player,
            cards_dealt_aside,
            finish_bonus,
            k_tongzi_bonus,
            a_tongzi_bonus,
            two_tongzi_bonus,
            dizha_bonus,
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

    /// Returns the finish bonus list
    #[must_use]
    pub fn finish_bonus(&self) -> &[i32] {
        &self.finish_bonus
    }

    /// Returns the K Tongzi bonus
    #[must_use]
    pub const fn k_tongzi_bonus(&self) -> i32 {
        self.k_tongzi_bonus
    }

    /// Returns the A Tongzi bonus
    #[must_use]
    pub const fn a_tongzi_bonus(&self) -> i32 {
        self.a_tongzi_bonus
    }

    /// Returns the 2 Tongzi bonus
    #[must_use]
    pub const fn two_tongzi_bonus(&self) -> i32 {
        self.two_tongzi_bonus
    }

    /// Returns the Dizha bonus
    #[must_use]
    pub const fn dizha_bonus(&self) -> i32 {
        self.dizha_bonus
    }

    /// Validates the configuration
    ///
    /// # Errors
    ///
    /// Returns an error if the configuration is invalid
    pub fn validate(&self) -> crate::Result<()> {
        let total_cards = usize::from(self.num_decks) * 52;
        let required_cards =
            self.cards_per_player * usize::from(self.num_players) + self.cards_dealt_aside;

        if required_cards > total_cards {
            return Err(crate::DatongziError::ConfigError(format!(
                "Not enough cards: need {required_cards}, have {total_cards}"
            )));
        }

        if !(2..=4).contains(&self.num_players) {
            return Err(crate::DatongziError::ConfigError(format!(
                "Invalid number of players: {}",
                self.num_players
            )));
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
