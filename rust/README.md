# Datongzi Rules Engine (Rust Implementation)

零依赖的打筒子游戏规则引擎库 - Rust 实现。

## 特性

- ✅ **零运行时依赖**：仅使用 Rust 标准库
- ✅ **高性能**：目标 10-100x 性能提升（vs Python 实现）
- ✅ **类型安全**：完整类型系统，编译期错误检测
- ✅ **完整测试**：>90% 代码覆盖率

## 快速开始

### 安装

```bash
cargo add datongzi-rules
```

### 使用示例

```rust
use datongzi_rules::{Card, Rank, Suit, Deck, GameConfig, ScoreComputation, PlayPattern, PlayType};

fn main() {
    // 创建卡牌
    let ace_of_spades = Card::new(Suit::Spades, Rank::Ace);
    println!("Card: {}", ace_of_spades);

    // 创建并洗牌
    let mut deck = Deck::create_standard_deck(3);
    deck.shuffle();

    // 发牌
    let hand = deck.deal_cards(13);
    println!("Hand size: {}", hand.len());

    // 计分系统
    let config = GameConfig::default();
    let mut scoring = ScoreComputation::new(config);

    // 创建回合胜利事件
    let round_cards = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Ten),
    ];
    if let Some(event) = scoring.create_round_win_event(
        "player1".to_string(),
        &round_cards,
        1
    ) {
        println!("Round win: {} points", event.points);
    }

    // 创建筒子奖励
    let tongzi_pattern = PlayPattern::new(
        PlayType::Tongzi,
        Rank::King,
        Some(Suit::Spades),
        vec![],
        3,
        0,
    );
    let bonuses = scoring.create_special_bonus_events(
        "player1".to_string(),
        &tongzi_pattern,
        1,
        true,
    );
    for bonus in bonuses {
        println!("Bonus: {} points", bonus.points);
    }
}
```

## 开发

### 构建

```bash
cargo build
```

### 运行测试

```bash
cargo test
```

### 运行性能基准测试

```bash
cargo bench
```

### 生成文档

```bash
cargo doc --open
```

## 项目结构

```
rust/
├── Cargo.toml           # Workspace 配置
├── rust-toolchain.toml  # Rust 版本锁定
├── datongzi-rules/      # 核心库 crate
│   ├── src/
│   │   ├── models/      # ✅ 数据模型
│   │   ├── patterns/    # ✅ 牌型识别
│   │   ├── scoring/     # ✅ 计分系统 (Phase 3)
│   │   ├── ai_helpers/  # 🚧 AI 辅助工具 (Phase 4)
│   │   └── variants/    # 🚧 规则变体 (Phase 5)
│   └── tests/           # 集成测试
├── benches/             # 性能基准测试
└── examples/            # 示例程序
```

## 实现进度

- ✅ **Phase 1**: 核心数据模型 (Card, Rank, Suit, Deck, GameConfig)
- ✅ **Phase 2**: 牌型识别系统 (PatternRecognizer, PlayValidator)
- ✅ **Phase 3**: 计分系统 (ScoreComputation, BonusType, ScoringEvent)
- 🚧 **Phase 4**: AI 辅助工具 (PlayGenerator, HandPatternAnalyzer)
- 🚧 **Phase 5**: 规则变体配置 (ConfigFactory, VariantValidator)

### 当前测试统计

- **单元测试**: 39 passed
- **集成测试**: 10 passed (basic: 6, scoring: 4)
- **文档测试**: 1 passed
- **总计**: 50 tests, 100% passed
- **代码覆盖率**: >85% (目标: >90%)

## 与 Python 版本的关系

这是与 Python 实现完全对等的 Rust 版本：

- **功能对等**：所有游戏规则和算法完全一致
- **独立维护**：两个版本独立演进
- **跨语言测试**：共享测试用例确保一致性

查看 Python 版本：`../python/`

## 许可证

MIT License

## 贡献

查看 [CONTRIBUTING.md](../docs/CONTRIBUTING.md) 了解贡献指南。
