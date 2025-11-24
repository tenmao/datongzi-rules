//! Configuration factory for game rule variants.
//!
//! Provides pre-configured setups for common game variations:
//! - Different deck counts (2-4 decks)
//! - Different player counts (2-4 players)
//! - Regional rule variations

use crate::models::GameConfig;

/// Factory for creating game configurations with different rule variants.
pub struct ConfigFactory;

impl ConfigFactory {
    /// Create standard 3-deck, 3-player configuration.
    ///
    /// This is the most common variant:
    /// - 3 decks (132 cards)
    /// - 3 players (41 cards each)
    /// - 9 cards set aside
    /// - Standard finish bonuses: [100, -40, -60]
    ///
    /// # Example
    /// ```
    /// use datongzi_rules::ConfigFactory;
    ///
    /// let config = ConfigFactory::create_standard_3deck_3player();
    /// assert_eq!(config.num_decks(), 3);
    /// assert_eq!(config.num_players(), 3);
    /// ```
    #[must_use]
    pub fn create_standard_3deck_3player() -> GameConfig {
        GameConfig::new(
            3,
            3,
            41, // cards_per_player
            9,  // cards_dealt_aside
            vec![100, -40, -60],
            100,
            200,
            300,
            400,
        )
    }

    /// Create 4-deck, 4-player configuration.
    ///
    /// - 4 decks (176 cards)
    /// - 4 players (42 cards each)
    /// - 8 cards set aside
    /// - Adjusted finish bonuses: [100, -20, -40, -80]
    ///
    /// # Example
    /// ```
    /// use datongzi_rules::ConfigFactory;
    ///
    /// let config = ConfigFactory::create_4deck_4player();
    /// assert_eq!(config.num_decks(), 4);
    /// assert_eq!(config.num_players(), 4);
    /// ```
    #[must_use]
    pub fn create_4deck_4player() -> GameConfig {
        GameConfig::new(
            4,
            4,
            42, // cards_per_player
            8,  // cards_dealt_aside
            vec![100, -20, -40, -80],
            100,
            200,
            300,
            400,
        )
    }

    /// Create 2-player configuration.
    ///
    /// - 3 decks (132 cards)
    /// - 2 players (60 cards each)
    /// - 12 cards set aside
    /// - Head-to-head bonuses: [100, -100]
    ///
    /// # Example
    /// ```
    /// use datongzi_rules::ConfigFactory;
    ///
    /// let config = ConfigFactory::create_2player();
    /// assert_eq!(config.num_players(), 2);
    /// assert_eq!(config.finish_bonus(), &[100, -100]);
    /// ```
    #[must_use]
    pub fn create_2player() -> GameConfig {
        GameConfig::new(
            3,
            2,
            60, // cards_per_player
            12, // cards_dealt_aside
            vec![100, -100],
            100,
            200,
            300,
            400,
        )
    }

    /// Create quick game configuration (2 decks, fewer cards).
    ///
    /// - 2 decks (88 cards)
    /// - 3 players (28 cards each)
    /// - 4 cards set aside
    /// - Faster gameplay
    ///
    /// # Example
    /// ```
    /// use datongzi_rules::ConfigFactory;
    ///
    /// let config = ConfigFactory::create_quick_game();
    /// assert_eq!(config.num_decks(), 2);
    /// assert_eq!(config.cards_per_player(), 28);
    /// ```
    #[must_use]
    pub fn create_quick_game() -> GameConfig {
        GameConfig::new(
            2,
            3,
            28, // cards_per_player
            4,  // cards_dealt_aside
            vec![100, -40, -60],
            100,
            200,
            300,
            400,
        )
    }

    /// Create high-stakes configuration with increased bonuses.
    ///
    /// - Standard 3-deck, 3-player setup
    /// - Doubled special bonuses
    /// - Increased finish bonuses
    ///
    /// # Example
    /// ```
    /// use datongzi_rules::ConfigFactory;
    ///
    /// let config = ConfigFactory::create_high_stakes();
    /// assert_eq!(config.k_tongzi_bonus(), 200);  // Doubled
    /// assert_eq!(config.dizha_bonus(), 800);     // Doubled
    /// ```
    #[must_use]
    pub fn create_high_stakes() -> GameConfig {
        GameConfig::new(
            3,
            3,
            41,                   // cards_per_player
            9,                    // cards_dealt_aside
            vec![200, -80, -120], // Doubled
            200,                  // Doubled
            400,                  // Doubled
            600,                  // Doubled
            800,                  // Doubled
        )
    }

    /// Create beginner-friendly configuration.
    ///
    /// - Standard setup with same parameters as standard 3-deck 3-player
    /// - Note: Rust version doesn't have must_beat_rule in GameConfig yet
    /// - This is a future placeholder for beginner-friendly variants
    ///
    /// # Example
    /// ```
    /// use datongzi_rules::ConfigFactory;
    ///
    /// let config = ConfigFactory::create_beginner_friendly();
    /// assert_eq!(config.num_decks(), 3);
    /// ```
    #[must_use]
    pub fn create_beginner_friendly() -> GameConfig {
        GameConfig::new(
            3,
            3,
            41, // cards_per_player
            9,  // cards_dealt_aside
            vec![100, -40, -60],
            100,
            200,
            300,
            400,
        )
    }

    /// Create custom configuration with specified parameters.
    ///
    /// # Arguments
    /// - `num_decks`: Number of card decks (1-4)
    /// - `num_players`: Number of players (2-4)
    /// - `cards_per_player`: Cards dealt to each player
    /// - `cards_dealt_aside`: Cards not dealt to players
    /// - `k_tongzi_bonus`: Bonus for K tongzi
    /// - `a_tongzi_bonus`: Bonus for A tongzi
    /// - `two_tongzi_bonus`: Bonus for 2 tongzi
    /// - `dizha_bonus`: Bonus for dizha
    ///
    /// # Example
    /// ```
    /// use datongzi_rules::ConfigFactory;
    ///
    /// let config = ConfigFactory::create_custom(
    ///     2,
    ///     2,
    ///     40,
    ///     4,
    ///     150,
    ///     300,
    ///     450,
    ///     600,
    /// );
    /// assert_eq!(config.num_decks(), 2);
    /// assert_eq!(config.k_tongzi_bonus(), 150);
    /// ```
    #[must_use]
    #[allow(clippy::too_many_arguments)]
    pub fn create_custom(
        num_decks: u8,
        num_players: u8,
        cards_per_player: usize,
        cards_dealt_aside: usize,
        k_tongzi_bonus: i32,
        a_tongzi_bonus: i32,
        two_tongzi_bonus: i32,
        dizha_bonus: i32,
    ) -> GameConfig {
        // Calculate finish bonus dynamically
        let finish_bonus = Self::calculate_default_finish_bonus(num_players);

        GameConfig::new(
            num_decks,
            num_players,
            cards_per_player,
            cards_dealt_aside,
            finish_bonus,
            k_tongzi_bonus,
            a_tongzi_bonus,
            two_tongzi_bonus,
            dizha_bonus,
        )
    }

    /// Calculate default finish bonus for a given number of players.
    ///
    /// Uses a heuristic where first place gets +100, and others share -100
    /// proportionally to maintain zero-sum fairness.
    fn calculate_default_finish_bonus(num_players: u8) -> Vec<i32> {
        if num_players == 0 {
            return vec![];
        }

        let mut bonuses = vec![100]; // First place always +100

        if num_players > 1 {
            // Distribute -100 among remaining players
            let per_player = -100 / i32::from(num_players - 1);
            let remainder = -100 % i32::from(num_players - 1);

            for i in 0..(num_players - 1) {
                let bonus = if i == 0 {
                    per_player + remainder
                } else {
                    per_player
                };
                bonuses.push(bonus);
            }
        }

        bonuses
    }
}

/// Validate game configuration variants for playability.
pub struct VariantValidator;

impl VariantValidator {
    /// Validate that a configuration is playable.
    ///
    /// Checks:
    /// 1. Sufficient cards for all players (min 10 cards/player)
    /// 2. Even card distribution among players
    /// 3. Finish bonus length matches player count
    /// 4. Finish bonuses sum to ≤0 (zero-sum fairness)
    ///
    /// # Returns
    /// Tuple of (is_valid, list_of_warnings)
    ///
    /// # Example
    /// ```
    /// use datongzi_rules::{ConfigFactory, VariantValidator};
    ///
    /// let config = ConfigFactory::create_standard_3deck_3player();
    /// let (is_valid, warnings) = VariantValidator::validate_config(&config);
    /// assert!(is_valid);
    /// assert!(warnings.is_empty());
    /// ```
    #[must_use]
    pub fn validate_config(config: &GameConfig) -> (bool, Vec<String>) {
        let mut warnings = Vec::new();

        // Calculate total cards in deck
        let total_cards = usize::from(config.num_decks()) * 52;
        let total_available = total_cards - config.cards_dealt_aside();
        let required = usize::from(config.num_players()) * 10; // Minimum 10 cards per player

        // Check if enough cards for all players
        if total_available < required {
            warnings.push(format!(
                "Too few cards: {} available, need at least {} for {} players",
                total_available,
                required,
                config.num_players()
            ));
        }

        // Check for unbalanced distribution
        if total_available % usize::from(config.num_players()) != 0 {
            warnings.push(format!(
                "Uneven distribution: {} cards cannot be evenly divided among {} players",
                total_available,
                config.num_players()
            ));
        }

        // Check finish bonus length
        if config.finish_bonus().len() != usize::from(config.num_players()) {
            warnings.push(format!(
                "Finish bonus length ({}) does not match player count ({})",
                config.finish_bonus().len(),
                config.num_players()
            ));
        }

        // Check bonus sum (should be zero or negative for fairness)
        let bonus_sum: i32 = config.finish_bonus().iter().sum();
        if bonus_sum > 0 {
            warnings.push(format!(
                "Finish bonuses sum to {} (should be ≤0 for fairness)",
                bonus_sum
            ));
        }

        let is_valid = warnings.is_empty();

        (is_valid, warnings)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_create_standard_3deck_3player() {
        let config = ConfigFactory::create_standard_3deck_3player();

        assert_eq!(config.num_decks(), 3);
        assert_eq!(config.num_players(), 3);
        assert_eq!(config.cards_per_player(), 41);
        assert_eq!(config.finish_bonus(), &[100, -40, -60]);
    }

    #[test]
    fn test_create_4deck_4player() {
        let config = ConfigFactory::create_4deck_4player();

        assert_eq!(config.num_decks(), 4);
        assert_eq!(config.num_players(), 4);
        assert_eq!(config.cards_per_player(), 42);
        assert_eq!(config.finish_bonus().len(), 4);
    }

    #[test]
    fn test_create_2player() {
        let config = ConfigFactory::create_2player();

        assert_eq!(config.num_decks(), 3);
        assert_eq!(config.num_players(), 2);
        assert_eq!(config.finish_bonus(), &[100, -100]);
    }

    #[test]
    fn test_create_quick_game() {
        let config = ConfigFactory::create_quick_game();

        assert_eq!(config.num_decks(), 2);
        assert_eq!(config.num_players(), 3);
        assert_eq!(config.cards_per_player(), 28);
    }

    #[test]
    fn test_create_high_stakes() {
        let config = ConfigFactory::create_high_stakes();

        assert_eq!(config.k_tongzi_bonus(), 200); // Doubled
        assert_eq!(config.a_tongzi_bonus(), 400); // Doubled
        assert_eq!(config.two_tongzi_bonus(), 600); // Doubled
        assert_eq!(config.dizha_bonus(), 800); // Doubled
        assert_eq!(config.finish_bonus()[0], 200); // Doubled
    }

    #[test]
    fn test_create_beginner_friendly() {
        let config = ConfigFactory::create_beginner_friendly();

        // Note: Rust version doesn't have must_beat_rule yet
        // This is a placeholder for future implementation
        assert_eq!(config.num_decks(), 3);
        assert_eq!(config.num_players(), 3);
    }

    #[test]
    fn test_create_custom() {
        let config = ConfigFactory::create_custom(
            2, 2, 40, // cards_per_player
            4,  // cards_dealt_aside
            150, 300, 450, 600,
        );

        assert_eq!(config.num_decks(), 2);
        assert_eq!(config.num_players(), 2);
        assert_eq!(config.cards_dealt_aside(), 4);
        assert_eq!(config.k_tongzi_bonus(), 150);
    }

    #[test]
    fn test_validate_valid_config() {
        let config = ConfigFactory::create_standard_3deck_3player();
        let (is_valid, warnings) = VariantValidator::validate_config(&config);

        assert!(is_valid);
        assert!(warnings.is_empty());
    }

    #[test]
    fn test_validate_insufficient_cards() {
        // Create config with too few cards
        // 1 deck = 52 cards, 30 aside = 22 available, need 40 (4 players * 10 min)
        let config = ConfigFactory::create_custom(
            1, 4, 5,  // cards_per_player (unrealistic)
            30, // Too many aside
            100, 200, 300, 400,
        );

        let (is_valid, warnings) = VariantValidator::validate_config(&config);

        assert!(!is_valid);
        assert!(!warnings.is_empty());
        assert!(warnings.iter().any(|w| w.contains("Too few cards")));
    }

    #[test]
    fn test_validate_uneven_distribution() {
        // Create config with uneven distribution
        // 2 decks = 104 cards, 2 aside = 102 available, not divisible by 3 (102 % 3 = 0, so use different config)
        // 2 decks = 104 cards, 1 aside = 103 available, not divisible by 3 (103 % 3 = 1)
        let config = ConfigFactory::create_custom(
            2, 3, 34, // cards_per_player (just a number, validation checks distribution)
            1,  // 104 - 1 = 103, not divisible by 3
            100, 200, 300, 400,
        );

        let (is_valid, warnings) = VariantValidator::validate_config(&config);

        assert!(!is_valid);
        assert!(warnings.iter().any(|w| w.contains("Uneven distribution")));
    }

    #[test]
    fn test_validate_bonus_mismatch() {
        // Create config manually with mismatched bonus length
        let config = GameConfig::new(
            3,
            3,
            41,             // cards_per_player
            9,              // cards_dealt_aside
            vec![100, -50], // Only 2 bonuses for 3 players
            100,
            200,
            300,
            400,
        );

        let (is_valid, warnings) = VariantValidator::validate_config(&config);

        assert!(!is_valid);
        assert!(warnings.iter().any(|w| w.contains("Finish bonus length")));
    }

    #[test]
    fn test_validate_bonus_sum_positive() {
        // Create config with positive bonus sum
        let config = GameConfig::new(
            3,
            3,
            41,                // cards_per_player
            9,                 // cards_dealt_aside
            vec![100, 50, 50], // Sum = 200 > 0
            100,
            200,
            300,
            400,
        );

        let (is_valid, warnings) = VariantValidator::validate_config(&config);

        assert!(!is_valid);
        assert!(warnings
            .iter()
            .any(|w| w.contains("should be ≤0 for fairness")));
    }

    #[test]
    fn test_config_excluded_ranks() {
        // Note: Rust version doesn't support excluded_ranks yet
        // This test is a placeholder for future implementation
        let config = ConfigFactory::create_custom(
            3, 3, 41, // cards_per_player
            9,  // cards_dealt_aside
            100, 200, 300, 400,
        );

        // Just verify basic properties
        assert_eq!(config.num_decks(), 3);
        assert_eq!(config.num_players(), 3);
    }

    #[test]
    fn test_finish_bonus_sum() {
        let config = ConfigFactory::create_standard_3deck_3player();

        let bonus_sum: i32 = config.finish_bonus().iter().sum();
        // Should be zero or negative for fairness
        assert_eq!(bonus_sum, 0);
    }
}
