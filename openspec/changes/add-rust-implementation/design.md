# Design Document: Rust Implementation

## 架构设计

### 1. 项目结构

```
datongzi-rules/
├── python/                           # 现有 Python 实现（重命名）
│   ├── src/datongzi_rules/
│   ├── tests/
│   ├── pyproject.toml
│   └── run.py
│
├── rust/                             # 新增 Rust 实现
│   ├── Cargo.toml                    # Workspace 根配置
│   ├── rust-toolchain.toml           # 固定 Rust 版本
│   │
│   ├── datongzi-rules/               # 核心库 crate
│   │   ├── Cargo.toml
│   │   ├── src/
│   │   │   ├── lib.rs               # 公开 API 导出
│   │   │   ├── models/              # 数据模型层
│   │   │   │   ├── mod.rs
│   │   │   │   ├── card.rs          # Card, Rank, Suit, Deck
│   │   │   │   └── config.rs        # GameConfig
│   │   │   ├── patterns/            # 牌型识别层
│   │   │   │   ├── mod.rs
│   │   │   │   ├── recognizer.rs    # PlayType, PlayPattern, PatternRecognizer
│   │   │   │   ├── validators.rs    # PlayValidator, PlayFormationValidator
│   │   │   │   └── finders.rs       # PatternFinder
│   │   │   ├── scoring/             # 计分引擎层
│   │   │   │   ├── mod.rs
│   │   │   │   └── computation.rs   # BonusType, ScoringEvent, ScoreComputation
│   │   │   ├── ai_helpers/          # AI 辅助工具层
│   │   │   │   ├── mod.rs
│   │   │   │   ├── play_generator.rs
│   │   │   │   └── hand_pattern_analyzer.rs
│   │   │   ├── variants/            # 规则变体层
│   │   │   │   ├── mod.rs
│   │   │   │   └── config_factory.rs
│   │   │   └── error.rs             # 统一错误类型
│   │   ├── tests/                   # 集成测试
│   │   │   └── integration_tests.rs
│   │   └── benches/                 # 单元基准测试
│   │
│   ├── benches/                      # Workspace 级性能测试
│   │   ├── pattern_recognition.rs
│   │   ├── play_generation.rs
│   │   ├── scoring.rs
│   │   └── full_game.rs
│   │
│   └── examples/                     # 示例程序
│       ├── basic_usage.rs
│       ├── game_simulation.rs
│       └── performance_comparison.rs
│
├── tests/                            # 跨语言测试套件
│   ├── cross-language/
│   │   ├── test_cases.json          # 统一测试用例
│   │   ├── run_python.py            # Python 测试运行器
│   │   └── run_rust.sh              # Rust 测试运行器
│   └── fixtures/                    # 共享测试数据
│
├── docs/                             # 共享文档
│   ├── GAME_RULE.md
│   ├── ARCHITECTURE.md
│   ├── RUST_MIGRATION.md            # 新增
│   └── API_COMPARISON.md            # 新增：Python vs Rust API
│
├── .github/workflows/
│   ├── python-ci.yml                # Python CI（保持不变）
│   ├── rust-ci.yml                  # 新增：Rust CI
│   └── cross-language-tests.yml     # 新增：一致性测试
│
└── README.md                         # 更新：双语言说明
```

---

## 2. 核心设计决策

### 2.1 Rust 版本与特性

**Rust 版本**：1.75+（2024 Edition 预备）

**启用特性**：
```toml
[package]
edition = "2021"
rust-version = "1.75"

[dependencies]
serde = { version = "1.0", features = ["derive"], optional = true }
thiserror = "1.0"
rand = "0.8"

[dev-dependencies]
criterion = { version = "0.5", features = ["html_reports"] }
proptest = "1.4"  # 属性测试
```

**Clippy 配置**（严格模式）：
```toml
[lints.clippy]
all = "warn"
pedantic = "warn"
nursery = "warn"
cargo = "warn"

# 允许的例外
module_name_repetitions = "allow"  # 允许如 CardCard 命名
```

### 2.2 内存管理与所有权

**设计原则**：
1. **不可变优先**：默认使用 `&[Card]` 而非 `Vec<Card>`
2. **零拷贝**：尽量使用引用，避免克隆
3. **Copy 类型**：`Card`, `Rank`, `Suit` 实现 `Copy`（小对象）
4. **借用检查器友好**：避免复杂的生命周期

**示例**：
```rust
// Card 实现 Copy（12 bytes）
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub struct Card {
    pub suit: Suit,
    pub rank: Rank,
}

// PlayPattern 不可变
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PlayPattern {
    pub play_type: PlayType,
    pub primary_rank: Rank,
    pub card_count: usize,
    // ... 其他字段
}

// API 使用切片而非 Vec
pub fn analyze_cards(cards: &[Card]) -> Result<PlayPattern, PatternError>
```

### 2.3 错误处理

**统一错误类型**（使用 `thiserror`）：
```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum DatongziError {
    #[error("Invalid pattern: {0}")]
    PatternError(String),

    #[error("Invalid play: {0}")]
    PlayError(String),

    #[error("Configuration error: {0}")]
    ConfigError(String),

    #[error("Too many combinations: {found}, max allowed: {max}")]
    TooManyCombinations { found: usize, max: usize },
}

pub type Result<T> = std::result::Result<T, DatongziError>;
```

**错误处理策略**：
- 公开 API 返回 `Result<T, DatongziError>`
- 内部辅助函数使用 `Option<T>` 或 panic（不可恢复错误）
- 验证失败返回详细错误信息

### 2.4 类型设计对照表

| Python 类型 | Rust 类型 | 设计理由 |
|------------|-----------|----------|
| `Enum` | `enum` | 直接对应 |
| `IntEnum` | `#[repr(u8)] enum` | 数值枚举 |
| `@dataclass(frozen=True)` | `struct` | 不可变结构体 |
| `@dataclass` | `struct` | 可变结构体 |
| `list[Card]` | `Vec<Card>` 或 `&[Card]` | 所有权/借用 |
| `dict[str, int]` | `HashMap<String, i32>` | 标准库 |
| `Optional[T]` | `Option<T>` | 显式可空 |
| `raise ValueError` | `Err(DatongziError::...)` | 错误处理 |

---

## 3. 性能优化策略

### 3.1 牌型识别优化

**Python 实现问题**：
- 大量列表操作和复制
- 字典查找开销
- GIL 限制

**Rust 优化**：
```rust
// 1. 使用排序数组 + 二分查找
pub fn analyze_cards(cards: &[Card]) -> Result<PlayPattern> {
    let mut sorted_cards = cards.to_vec();
    sorted_cards.sort_unstable();  // 原地排序，无分配

    // 2. 使用数组计数（栈分配）而非 HashMap
    let mut rank_counts = [0u8; 13];  // 13 种点数
    for card in &sorted_cards {
        rank_counts[card.rank as usize - 3] += 1;
    }

    // 3. 提前返回，避免不必要的检查
    if cards.len() == 1 {
        return Ok(PlayPattern::single(cards[0]));
    }

    // ...
}
```

**预期提升**：150K ops/sec → 1M ops/sec（~6.6x）

### 3.2 出牌生成优化

**Python 实现问题**：
- 递归生成大量中间列表
- 组合爆炸（41 张牌 > 500 组合）

**Rust 优化**：
```rust
// 1. 使用迭代器而非 Vec（懒计算）
pub fn generate_all_plays(hand: &[Card]) -> impl Iterator<Item = Vec<Card>> + '_ {
    // 返回迭代器，避免一次性生成所有组合
    PatternIterator::new(hand)
}

// 2. 使用位掩码表示组合（空间优化）
struct PatternIterator {
    hand: Vec<Card>,
    current_mask: u64,  // 最多支持 64 张牌
    max_mask: u64,
}

// 3. 剪枝策略
impl Iterator for PatternIterator {
    fn next(&mut self) -> Option<Vec<Card>> {
        // 跳过无效组合（提前验证）
        while self.current_mask < self.max_mask {
            let cards = self.mask_to_cards();
            if self.is_valid_pattern(&cards) {
                return Some(cards);
            }
            self.current_mask += 1;
        }
        None
    }
}
```

**预期提升**：6.38ms/op → <1ms/op（>6x）

### 3.3 内存分配优化

**策略**：
1. **对象池**：复用 `Vec<Card>` 避免重复分配
2. **栈分配**：小数组（<= 13 个元素）使用 `SmallVec`
3. **Copy 类型**：`Card` 实现 `Copy`，避免引用计数

```rust
use smallvec::SmallVec;

// 栈分配小向量（避免堆分配）
type SmallCardVec = SmallVec<[Card; 13]>;

pub fn find_all_pairs(hand: &[Card]) -> Vec<SmallCardVec> {
    // 大多数对子 <= 13 个，使用栈分配
    let mut pairs = Vec::new();
    // ...
    pairs
}
```

### 3.4 并发优化（可选）

**场景**：大量游戏模拟（AI 训练）

**策略**：
```rust
use rayon::prelude::*;

pub fn simulate_games_parallel(count: usize) -> Vec<GameResult> {
    (0..count)
        .into_par_iter()  // 并行迭代器
        .map(|_| simulate_single_game())
        .collect()
}
```

**注意**：核心 API 保持单线程，并发由用户控制。

---

## 4. 测试策略

### 4.1 单元测试

**覆盖率目标**：>90%（vs Python 88.66%）

**测试组织**：
```rust
// 模块级测试
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_card_ordering() {
        let ace = Card::new(Suit::SPADES, Rank::ACE);
        let king = Card::new(Suit::SPADES, Rank::KING);
        assert!(ace > king);
    }

    // 迁移 Python 测试
    #[test]
    fn test_analyze_single_card() {
        // 对应 tests/unit/test_patterns.py::test_single_card
        // ...
    }
}
```

**属性测试**（Property-based testing）：
```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn test_scoring_is_zero_sum(
        players in prop::collection::vec(any::<String>(), 2..=4)
    ) {
        let scores = calculate_finish_bonuses(&players);
        let total: i32 = scores.values().sum();
        prop_assert_eq!(total, 0);  // 零和游戏
    }
}
```

### 4.2 集成测试

**跨语言一致性测试**：
```json
// tests/cross-language/test_cases.json
{
  "pattern_recognition": [
    {
      "name": "single_ace",
      "input": [{"suit": "SPADES", "rank": "ACE"}],
      "expected": {
        "play_type": "SINGLE",
        "primary_rank": "ACE",
        "card_count": 1
      }
    }
  ]
}
```

**Rust 测试运行器**：
```rust
#[test]
fn test_cross_language_consistency() {
    let test_cases: TestCases = serde_json::from_str(
        include_str!("../../tests/cross-language/test_cases.json")
    ).unwrap();

    for case in test_cases.pattern_recognition {
        let result = PatternRecognizer::analyze_cards(&case.input).unwrap();
        assert_eq!(result.play_type, case.expected.play_type);
        // ...
    }
}
```

### 4.3 性能基准测试

**使用 Criterion**：
```rust
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn bench_pattern_recognition(c: &mut Criterion) {
    let cards = vec![
        Card::new(Suit::SPADES, Rank::ACE),
        Card::new(Suit::HEARTS, Rank::ACE),
        Card::new(Suit::CLUBS, Rank::ACE),
    ];

    c.bench_function("analyze_triple", |b| {
        b.iter(|| PatternRecognizer::analyze_cards(black_box(&cards)))
    });
}

criterion_group!(benches, bench_pattern_recognition);
criterion_main!(benches);
```

**性能回归检测**：
```yaml
# .github/workflows/rust-ci.yml
- name: Run benchmarks
  run: cargo bench --bench pattern_recognition -- --save-baseline main

- name: Compare with previous
  run: cargo bench --bench pattern_recognition -- --baseline main
```

---

## 5. 依赖管理

### 5.1 核心依赖（最小化）

```toml
[dependencies]
# 错误处理（必需）
thiserror = "1.0"

# 随机数生成（洗牌）
rand = "0.8"

# 序列化（可选，用于跨语言测试）
serde = { version = "1.0", features = ["derive"], optional = true }
serde_json = { version = "1.0", optional = true }

[features]
default = []
serde = ["dep:serde", "dep:serde_json"]
```

### 5.2 开发依赖

```toml
[dev-dependencies]
# 性能测试
criterion = { version = "0.5", features = ["html_reports"] }

# 属性测试
proptest = "1.4"

# 快速测试运行
cargo-nextest = "0.9"

# 代码覆盖率
tarpaulin = "0.27"
```

### 5.3 依赖审计

**每周自动检查**：
```yaml
# .github/workflows/security-audit.yml
name: Security Audit
on:
  schedule:
    - cron: '0 0 * * 0'  # 每周日运行
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: cargo install cargo-audit
      - run: cargo audit
```

---

## 6. 文档策略

### 6.1 API 文档（Rustdoc）

**文档级别**：
1. **Crate 级**（`lib.rs`）：概览、快速开始、示例
2. **模块级**（`mod.rs`）：模块职责、关键概念
3. **类型级**：结构体/枚举说明、使用场景
4. **方法级**：参数、返回值、示例、错误

**示例**：
```rust
//! # Datongzi Rules Engine
//!
//! 零依赖的打筒子游戏规则引擎库。
//!
//! ## 快速开始
//!
//! ```rust
//! use datongzi_rules::{Card, Rank, Suit, PatternRecognizer};
//!
//! let cards = vec![
//!     Card::new(Suit::SPADES, Rank::ACE),
//!     Card::new(Suit::HEARTS, Rank::ACE),
//! ];
//!
//! let pattern = PatternRecognizer::analyze_cards(&cards)?;
//! assert_eq!(pattern.play_type, PlayType::PAIR);
//! ```

/// 分析给定的卡牌，识别牌型。
///
/// # Arguments
///
/// * `cards` - 要分析的卡牌切片
///
/// # Returns
///
/// 返回识别出的牌型，如果无法识别则返回错误。
///
/// # Examples
///
/// ```rust
/// let cards = vec![Card::new(Suit::SPADES, Rank::ACE)];
/// let pattern = PatternRecognizer::analyze_cards(&cards)?;
/// assert_eq!(pattern.play_type, PlayType::SINGLE);
/// ```
///
/// # Errors
///
/// 当以下情况发生时返回 `PatternError`：
/// - 卡牌数量为 0
/// - 卡牌组合不符合任何已知牌型
pub fn analyze_cards(cards: &[Card]) -> Result<PlayPattern, PatternError>
```

### 6.2 迁移指南

**目标读者**：熟悉 Python 版本的开发者

**内容结构**：
1. **概念映射**：Python 类型 → Rust 类型
2. **API 对照表**：每个 Python API 的 Rust 等价
3. **常见模式**：错误处理、迭代器、所有权
4. **性能差异**：何时使用 Rust 版本

**示例片段**（`docs/RUST_MIGRATION.md`）：
```markdown
## API 对照表

### 牌型识别

**Python**:
```python
from datongzi_rules import PatternRecognizer

pattern = PatternRecognizer.analyze_cards(cards)
print(f"Type: {pattern.play_type}")
```

**Rust**:
```rust
use datongzi_rules::PatternRecognizer;

let pattern = PatternRecognizer::analyze_cards(&cards)?;
println!("Type: {:?}", pattern.play_type);
```

**差异**：
- Rust 使用 `&cards`（借用）而非 `cards`（所有权转移）
- Rust 返回 `Result`，需要 `?` 操作符或 `unwrap()`
```

---

## 7. CI/CD 流程

### 7.1 Rust CI Pipeline

```yaml
name: Rust CI

on: [push, pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: dtolnay/rust-toolchain@stable

      - name: Check formatting
        run: cargo fmt -- --check

      - name: Run clippy
        run: cargo clippy --all-targets --all-features -- -D warnings

      - name: Build
        run: cargo build --verbose

      - name: Run tests
        run: cargo nextest run

      - name: Generate coverage
        run: |
          cargo install cargo-tarpaulin
          cargo tarpaulin --out Xml --output-dir coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: coverage/cobertura.xml

      - name: Run benchmarks
        run: cargo bench --no-run  # 仅编译，不运行
```

### 7.2 跨语言一致性测试

```yaml
name: Cross-Language Tests

on: [push, pull_request]

jobs:
  consistency:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Setup Rust
        uses: dtolnay/rust-toolchain@stable

      - name: Run Python tests with JSON output
        run: |
          cd python
          python tests/cross-language/run_python.py > results_python.json

      - name: Run Rust tests with JSON output
        run: |
          cd rust
          cargo test --test cross_language_tests -- --format json > results_rust.json

      - name: Compare results
        run: python tests/cross-language/compare.py results_python.json results_rust.json
```

---

## 8. 未来扩展

### 8.1 PyO3 绑定（Phase 9，可选）

**目标**：让 Python 代码可以透明调用 Rust 实现

**架构**：
```
rust/
├── datongzi-rules/       # 纯 Rust 核心库
└── datongzi-rules-py/    # PyO3 绑定层
    ├── Cargo.toml
    └── src/
        └── lib.rs        # Python C Extension
```

**示例**：
```rust
use pyo3::prelude::*;

#[pyclass]
struct Card {
    #[pyo3(get)]
    suit: Suit,
    #[pyo3(get)]
    rank: Rank,
}

#[pymethods]
impl Card {
    #[new]
    fn new(suit: Suit, rank: Rank) -> Self {
        Card { suit, rank }
    }
}

#[pymodule]
fn datongzi_rules_rs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Card>()?;
    Ok(())
}
```

**优势**：
- Python 代码无需修改，自动获得性能提升
- 逐步迁移，低风险

### 8.2 WebAssembly 支持

**目标**：在浏览器中运行规则引擎

```toml
[lib]
crate-type = ["cdylib"]  # 动态库

[dependencies]
wasm-bindgen = "0.2"
```

**示例**：
```rust
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn analyze_cards_wasm(cards_json: &str) -> String {
    let cards: Vec<Card> = serde_json::from_str(cards_json).unwrap();
    let pattern = PatternRecognizer::analyze_cards(&cards).unwrap();
    serde_json::to_string(&pattern).unwrap()
}
```

### 8.3 C FFI（外部系统集成）

**目标**：让 C/C++ 游戏引擎调用规则库

```rust
#[no_mangle]
pub extern "C" fn datongzi_analyze_cards(
    cards_ptr: *const Card,
    cards_len: usize,
    out_pattern: *mut PlayPattern,
) -> i32 {
    // C ABI 安全封装
    // ...
}
```

---

## 9. 风险与缓解

### 9.1 技术风险

| 风险 | 影响 | 概率 | 缓解措施 |
|-----|------|------|---------|
| 逻辑差异导致不一致 | 高 | 中 | 跨语言测试覆盖所有边界情况 |
| 性能未达预期 | 中 | 低 | 提前 Profile，预留优化时间 |
| Rust 学习曲线陡峭 | 中 | 高 | 详细文档、代码审查、最佳实践 |
| 依赖安全漏洞 | 高 | 低 | 每周 `cargo audit`，锁定版本 |

### 9.2 项目风险

| 风险 | 影响 | 概率 | 缓解措施 |
|-----|------|------|---------|
| 双语言维护负担 | 高 | 高 | 自动化测试、代码生成工具 |
| 团队 Rust 经验不足 | 中 | 中 | 培训、外部顾问、逐步推进 |
| 功能不对等 | 高 | 低 | 严格测试覆盖，阻塞 PR |

---

## 10. 决策记录

### DR-001: 使用 Cargo Workspace 而非 Monorepo

**决策**：采用 Cargo workspace 结构，而非将 Rust 代码放在 `src/` 顶层。

**理由**：
1. 清晰分离 Python 和 Rust 代码
2. 独立的依赖管理和构建配置
3. 便于未来拆分为独立仓库

### DR-002: Card 实现 Copy 而非 Clone

**决策**：`Card` 实现 `Copy` trait。

**理由**：
1. `Card` 只有 2 个字段（suit, rank），总共 2 bytes
2. 拷贝比引用更快（栈拷贝 vs 指针解引用）
3. 简化 API（无需 `&card` 到处传递）

### DR-003: 不引入异步运行时

**决策**：不使用 `tokio` 或 `async-std`。

**理由**：
1. 规则引擎是纯计算，无 I/O 操作
2. 避免异步复杂度和运行时开销
3. 用户可在外部使用异步（如 `tokio::spawn`）

### DR-004: 使用 thiserror 而非自定义错误宏

**决策**：使用 `thiserror` 库定义错误类型。

**理由**：
1. 行业标准，社区广泛使用
2. 自动实现 `Display`, `Error` trait
3. 减少样板代码

---

## 11. 附录

### 11.1 代码风格指南

**命名约定**：
- 类型：`PascalCase`（如 `PlayType`, `Card`）
- 函数/变量：`snake_case`（如 `analyze_cards`, `card_count`）
- 常量：`SCREAMING_SNAKE_CASE`（如 `MAX_PLAYERS`）
- 模块：`snake_case`（如 `patterns`, `ai_helpers`）

**代码组织**：
```rust
// 1. 导入
use std::collections::HashMap;
use crate::models::Card;

// 2. 类型定义
pub struct PatternRecognizer;

// 3. 实现
impl PatternRecognizer {
    // 公开 API 在前
    pub fn analyze_cards(cards: &[Card]) -> Result<PlayPattern> { }

    // 私有辅助函数在后
    fn is_consecutive(ranks: &[Rank]) -> bool { }
}

// 4. 测试
#[cfg(test)]
mod tests { }
```

### 11.2 术语对照表

| 中文 | Python | Rust | 说明 |
|-----|--------|------|------|
| 卡牌 | `Card` | `Card` | 不可变值类型 |
| 牌型 | `PlayPattern` | `PlayPattern` | 不可变结构体 |
| 识别器 | `PatternRecognizer` | `PatternRecognizer` | 静态方法集合 |
| 验证器 | `PlayValidator` | `PlayValidator` | 静态方法集合 |
| 计分引擎 | `ScoreComputation` | `ScoreComputation` | 有状态结构体 |
| 错误 | `raise ValueError` | `Err(DatongziError)` | 错误枚举 |

### 11.3 参考资源

**Rust 学习**：
- [The Rust Book](https://doc.rust-lang.org/book/)
- [Rust by Example](https://doc.rust-lang.org/rust-by-example/)
- [Effective Rust](https://www.lurklurk.org/effective-rust/)

**性能优化**：
- [The Rust Performance Book](https://nnethercote.github.io/perf-book/)
- [Criterion.rs Guide](https://bheisler.github.io/criterion.rs/book/)

**测试最佳实践**：
- [Rust Testing Guide](https://doc.rust-lang.org/book/ch11-00-testing.html)
- [Property Testing in Rust](https://altsysrq.github.io/proptest-book/)
