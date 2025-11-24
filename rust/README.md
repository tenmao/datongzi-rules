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
use datongzi_rules::{Card, Rank, Suit, Deck};

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
│   │   ├── models/      # 数据模型
│   │   ├── patterns/    # 牌型识别
│   │   ├── scoring/     # 计分系统
│   │   ├── ai_helpers/  # AI 辅助工具
│   │   └── variants/    # 规则变体
│   └── tests/           # 集成测试
├── benches/             # 性能基准测试
└── examples/            # 示例程序
```

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
