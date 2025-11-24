//! Pattern recognition and validation.
//!
//! This module contains:
//! - Pattern types and structures ([`PlayType`], [`PlayPattern`])
//! - Pattern recognition logic ([`PatternRecognizer`])
//! - Play validation logic ([`PlayValidator`])
//!
//! **Status**: Phase 2 - In progress

mod pattern;
mod recognizer;

pub use pattern::{PlayPattern, PlayType};
pub use recognizer::PatternRecognizer;
