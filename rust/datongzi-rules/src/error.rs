//! Error types for the datongzi-rules library.

use thiserror::Error;

/// Main error type for the datongzi-rules library.
#[derive(Error, Debug, Clone, PartialEq, Eq)]
pub enum DatongziError {
    /// Invalid pattern error
    #[error("Invalid pattern: {0}")]
    PatternError(String),

    /// Invalid play error
    #[error("Invalid play: {0}")]
    PlayError(String),

    /// Configuration error
    #[error("Configuration error: {0}")]
    ConfigError(String),

    /// Too many combinations generated
    #[error("Too many combinations: found {found}, max allowed: {max}")]
    TooManyCombinations {
        /// Number of combinations found
        found: usize,
        /// Maximum allowed combinations
        max: usize,
    },

    /// Invalid input
    #[error("Invalid input: {0}")]
    InvalidInput(String),
}

/// Result type alias for the datongzi-rules library.
pub type Result<T> = std::result::Result<T, DatongziError>;
