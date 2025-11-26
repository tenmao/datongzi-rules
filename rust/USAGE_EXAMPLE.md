# 如何在其他Rust代码中引用 datongzi-rules

## 当前状态 ✅

`datongzi-rules` 已经是一个完整的Rust库(library crate),可以被其他代码引用。

**项目结构**:
```
rust/
├── Cargo.toml              # Workspace 配置
└── datongzi-rules/         # Library crate
    ├── Cargo.toml
    └── src/
        └── lib.rs          # ✅ 已导出所有公共API
```

## 方案1: 在同一个Workspace添加新Crate

### 步骤1: 创建新的应用crate

```bash
cd /Users/timxia/Workspace/games_cards/datongzi-rules/rust
cargo new datongzi-game
```

### 步骤2: 修改workspace配置

编辑 `rust/Cargo.toml`:

```toml
[workspace]
resolver = "2"
members = [
    "datongzi-rules",
    "datongzi-game",    # 新增
]
```

### 步骤3: 添加依赖

编辑 `rust/datongzi-game/Cargo.toml`:

```toml
[package]
name = "datongzi-game"
version.workspace = true
edition.workspace = true

[dependencies]
datongzi-rules = { path = "../datongzi-rules" }
```

### 步骤4: 使用API

编辑 `rust/datongzi-game/src/main.rs`:

```rust
use datongzi_rules::{
    Card, Rank, Suit, Deck, GameConfig,
    PatternRecognizer, PlayValidator,
    PlayGenerator, HandPatternAnalyzer,
    ConfigFactory,
};

fn main() {
    // 1. 创建卡牌
    let card = Card::new(Suit::Spades, Rank::Ace);
    println!("Card: {}", card);

    // 2. 使用配置工厂
    let config = ConfigFactory::create_standard_3deck_3player();
    println!("Config: {:?}", config);

    // 3. 创建并洗牌
    let mut deck = Deck::new(&config);
    deck.shuffle();
    println!("Deck size: {}", deck.remaining());

    // 4. 识别牌型
    let cards = vec![
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Ace),
    ];
    let pattern = PatternRecognizer::analyze_cards(&cards, &config);
    println!("Pattern: {:?}", pattern);

    // 5. 生成合法出牌
    let hand = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Spades, Rank::Queen),
    ];
    let plays = PlayGenerator::generate_all_plays(&hand, &config);
    println!("Valid plays: {}", plays.len());

    // 6. 分析手牌结构
    let hand_patterns = HandPatternAnalyzer::analyze_hand(&hand, &config);
    println!("Hand patterns: {:?}", hand_patterns);
}
```

### 步骤5: 构建运行

```bash
cd rust
cargo build
cargo run -p datongzi-game
```

## 方案2: 从外部独立项目引用

如果你有一个完全独立的Rust项目(在其他目录):

### 本地路径引用

编辑外部项目的 `Cargo.toml`:

```toml
[dependencies]
datongzi-rules = { path = "/Users/timxia/Workspace/games_cards/datongzi-rules/rust/datongzi-rules" }
```

### Git仓库引用

```toml
[dependencies]
datongzi-rules = { git = "https://github.com/yourusername/datongzi-rules", branch = "main" }
```

### Crates.io引用 (发布后)

```toml
[dependencies]
datongzi-rules = "0.1.0"
```

## 可用的公共API

`datongzi-rules` 在 `lib.rs:35-41` 导出了以下类型:

```rust
// 数据模型
pub use models::{Card, Deck, GameConfig, Rank, Suit};

// 牌型识别和验证
pub use patterns::{PatternRecognizer, PlayPattern, PlayType, PlayValidator};

// AI辅助工具
pub use ai_helpers::{HandPatternAnalyzer, HandPatterns, PlayGenerator};

// 计分系统
pub use scoring::{BonusType, GameSummary, ScoreComputation, ScoringEvent};

// 规则变体
pub use variants::{ConfigFactory, VariantValidator};

// 错误类型
pub use error::{DatongziError, Result};
```

## 验证引用是否正确

```bash
# 检查库是否可以编译
cd rust
cargo check

# 运行测试
cargo test

# 查看文档
cargo doc --open --package datongzi-rules
```

## 注意事项

1. **库已经完全配置好**,不需要修改 `lib.rs`
2. **所有模块已声明为 `pub mod`**,可以被外部访问
3. **常用类型已 re-export**,可以直接 `use datongzi_rules::Card`
4. **workspace结构**允许在同一仓库管理多个相关crate

## 下一步建议

1. 在同一workspace创建示例应用(`datongzi-game`)
2. 实现游戏逻辑,使用规则库提供的API
3. 遵循依赖方向: `datongzi-game` → `datongzi-rules` (单向依赖)
