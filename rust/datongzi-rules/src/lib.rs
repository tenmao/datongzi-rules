//! # Datongzi Rules Engine
//!
//! 零依赖的打筒子游戏规则引擎库（Rust 实现）。
//!
//! ## 快速开始
//!
//! ```rust
//! use datongzi_rules::{Card, Rank, Suit};
//!
//! let card = Card::new(Suit::Spades, Rank::Ace);
//! println!("Card: {}", card);
//! ```
//!
//! ## 模块结构
//!

#![warn(missing_docs)]
#![warn(clippy::all)]
#![allow(clippy::module_inception)]
//! - [`models`]: 核心数据模型（Card, Rank, Suit, Deck, GameConfig）
//! - [`patterns`]: 牌型识别和验证
//! - [`scoring`]: 计分系统
//! - [`ai_helpers`]: AI 辅助工具
//! - [`variants`]: 规则变体配置

#![warn(missing_docs)]
#![warn(clippy::all)]
#![warn(clippy::pedantic)]
#![allow(clippy::module_name_repetitions)]

pub mod models;
pub mod patterns;
pub mod scoring;
pub mod ai_helpers;
pub mod variants;
pub mod error;

// Re-export commonly used types
pub use models::{Card, Rank, Suit, Deck, GameConfig};
pub use error::{DatongziError, Result};

/// Library version
pub const VERSION: &str = env!("CARGO_PKG_VERSION");

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_version() {
        assert!(!VERSION.is_empty());
    }
}
