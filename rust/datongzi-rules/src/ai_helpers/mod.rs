//! AI helper utilities.
//!
//! This module provides tools for AI decision making:
//! - [`PlayGenerator`]: Generate valid plays from hand
//! - [`HandPatternAnalyzer`]: Analyze hand structure (non-overlapping decomposition)
//! - [`HandPatterns`]: Structured representation of hand resources

mod hand_pattern_analyzer;
mod play_generator;

pub use hand_pattern_analyzer::{HandPatternAnalyzer, HandPatterns};
pub use play_generator::PlayGenerator;
