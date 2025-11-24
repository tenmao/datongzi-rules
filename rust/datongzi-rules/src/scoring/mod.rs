//! Scoring system for Da Tong Zi game.
//!
//! This module provides the scoring engine for calculating points, bonuses,
//! and game results. It is a pure calculation engine that does not manage
//! game state - that is the responsibility of the upper layer (game engine).

mod computation;

pub use computation::{BonusType, GameSummary, ScoreComputation, ScoringEvent};
