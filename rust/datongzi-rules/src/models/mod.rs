//! Core data models for the datongzi game.
//!
//! This module contains the fundamental data structures:
//! - [`Card`]: A playing card with suit and rank
//! - [`Rank`]: Card rank (THREE to TWO)
//! - [`Suit`]: Card suit (DIAMONDS to SPADES)
//! - [`Deck`]: A collection of cards
//! - [`GameConfig`]: Game configuration and rules

pub mod card;
pub mod config;

pub use card::{Card, Rank, Suit, Deck};
pub use config::GameConfig;
