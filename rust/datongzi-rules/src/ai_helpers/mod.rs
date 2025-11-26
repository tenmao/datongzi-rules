//! AI helper utilities.
//!
//! This module provides tools for AI decision making:
//! - [`PlayGenerator`]: Generate valid plays from hand
//! - [`HandPatternAnalyzer`]: Analyze hand structure (non-overlapping decomposition)
//! - [`HandPatterns`]: Structured representation of hand resources
//! - [`kicker`]: Multi-track kicker selection algorithm
//! - [`identical_play_filter`]: Identical play filtering to reduce duplicates

mod hand_pattern_analyzer;
mod identical_play_filter;
mod kicker;
mod play_generator;

pub use hand_pattern_analyzer::{HandPatternAnalyzer, HandPatterns};
pub use identical_play_filter::{
    detect_dizha, detect_tongzi, filter_consecutive_pairs, filter_pairs, filter_singles,
    filter_triples, get_protected_suits, select_safe_suit,
};
pub use kicker::{select_kickers, Block, KnapsackResult, Tactic};
pub use play_generator::PlayGenerator;
