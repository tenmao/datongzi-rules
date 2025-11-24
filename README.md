# Da Tong Zi Rules Engine

零依赖的打筒子游戏规则引擎库 - **Python + Rust 双语言实现**

![Rust CI](https://github.com/tenmao/datongzi-rules/workflows/Rust%20CI/badge.svg)
![Python CI](https://github.com/tenmao/datongzi-rules/workflows/Python%20CI/badge.svg)
[![Cross-Language Consistency Tests](https://github.com/tenmao/datongzi-rules/actions/workflows/cross-language-tests.yml/badge.svg)](https://github.com/tenmao/datongzi-rules/actions/workflows/cross-language-tests.yml)

---

## 🚀 双语言实现

本项目提供两个功能完全对等的实现：

| 实现 | 性能 | 用途 | 状态 |
|-----|------|-----|------|
| **Python** | 基准 | 快速开发、原型验证 | ✅ 完整（270+ 测试，88.66% 覆盖率）|
| **Rust** | 10-100x | 高性能场景、生产环境 | 🚧 Phase 1 完成（基础架构）|

**为什么需要两个实现？**
- 🐍 **Python**: 易于学习和修改，适合规则验证和快速迭代
- 🦀 **Rust**: 高性能、类型安全，适合 AI 训练、实时对战等高性能场景

---

## 📦 选择你的实现

### Python 实现

```bash
# 安装
cd python
pip install -e .

# 使用
from datongzi_rules import Card, Rank, Suit, PatternRecognizer

cards = [Card(Suit.SPADES, Rank.ACE)] * 3
pattern = PatternRecognizer.analyze_cards(cards)
print(pattern.play_type)  # PlayType.TRIPLE
```

[📖 Python 完整文档](python/README.md)

### Rust 实现

```bash
# 安装
cd rust
cargo build --release

# 使用
use datongzi_rules::{Card, Rank, Suit};

let card = Card::new(Suit::Spades, Rank::Ace);
println!("Card: {}", card);
```

[📖 Rust 完整文档](rust/README.md)

---

## 🎮 特性

### 核心功能

- ✅ **完整游戏规则**：10 种牌型，回合制计分
- ✅ **牌型识别**：单牌、对子、连对、三张、飞机、炸弹、筒子、地炸
- ✅ **出牌验证**：支持"有牌必打"规则
- ✅ **计分系统**：回合基础分、特殊奖励、完成位置奖励
- ✅ **AI 辅助工具**：出牌生成、手牌结构分析
- ✅ **规则变体**：支持多种配置（2-4 人，不同牌副数）

### 代码质量

| 指标 | Python | Rust |
|-----|--------|------|
| 测试用例 | 270+ | 🚧 Phase 2+ |
| 代码覆盖率 | 88.66% | 🚧 目标 >90% |
| 性能基准 | ~150K ops/sec | 🚧 目标 >1M ops/sec |
| 类型检查 | mypy (strict) | rustc (强制) |

---

## 🏗️ 项目结构

```
datongzi-rules/
├── python/                # Python 实现
│   ├── src/datongzi_rules/
│   │   ├── models/        # 数据模型
│   │   ├── patterns/      # 牌型识别
│   │   ├── scoring/       # 计分系统
│   │   ├── ai_helpers/    # AI 辅助工具
│   │   └── variants/      # 规则变体
│   ├── tests/             # 270+ 测试用例
│   └── README.md
│
├── rust/                  # Rust 实现
│   ├── datongzi-rules/    # 核心库 crate
│   │   └── src/
│   │       ├── models/    # 数据模型
│   │       ├── patterns/  # 牌型识别（Phase 3）
│   │       ├── scoring/   # 计分系统（Phase 4）
│   │       ├── ai_helpers/# AI 辅助工具（Phase 5）
│   │       └── variants/  # 规则变体（Phase 6）
│   └── README.md
│
├── tests/
│   └── cross-language/    # 跨语言一致性测试
│       ├── test_cases.json
│       └── run_tests.py
│
├── docs/                  # 共享文档
│   ├── GAME_RULE.md       # 游戏规则
│   ├── ARCHITECTURE.md    # 架构设计
│   └── API_COMPARISON.md  # API 对照表
│
└── .github/workflows/     # CI/CD 配置
    ├── rust-ci.yml
    ├── python-ci.yml
    └── cross-language-tests.yml
```

---

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/datongzi-rules.git
cd datongzi-rules
```

### 2. Python 开发

```bash
cd python
pip install -e ".[dev]"
python run.py test        # 运行测试
python run.py benchmark   # 性能测试
```

### 3. Rust 开发

```bash
cd rust
cargo build              # 构建
cargo test               # 运行测试
cargo bench              # 性能测试（Phase 7）
```

### 4. 跨语言测试

```bash
python tests/cross-language/run_tests.py
```

---

## 📊 性能对比

| 操作 | Python | Rust（目标）| 提升倍数 |
|-----|--------|------------|---------|
| 牌型识别 | ~150K ops/sec | >1M ops/sec | **6.6x** |
| 满手牌出牌生成 | 6.38ms/op | <1ms/op | **>6x** |
| 游戏设置 | ~5K games/sec | >50K games/sec | **10x** |
| 计分计算 | ~140K ops/sec | >1M ops/sec | **7x** |

*Rust 性能数据将在 Phase 7 完成后更新*

---

## 🔧 开发

### 运行测试

```bash
# Python 测试
cd python && python run.py test

# Rust 测试
cd rust && cargo test

# 跨语言一致性测试
python tests/cross-language/run_tests.py
```

### 代码格式化

```bash
# Python
cd python && black src/ tests/

# Rust
cd rust && cargo fmt
```

### 代码检查

```bash
# Python
cd python && ruff check src/ tests/
cd python && mypy src/

# Rust
cd rust && cargo clippy
```

---

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: 添加新功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

**重要**：
- 所有 PR 必须通过 CI/CD 检查
- Python 和 Rust 实现必须保持一致
- 测试覆盖率不能下降

查看完整贡献指南：[CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📖 文档

- [游戏规则详解](GAME_RULE.md)
- [架构设计](ARCHITECTURE.md)
- [Python API 文档](python/README.md)
- [Rust API 文档](rust/README.md)
- [跨语言测试指南](tests/cross-language/README.md)
- [GitHub 设置指南](GITHUB_SETUP.md)
- [OpenSpec 提案](openspec/changes/add-rust-implementation/)

---

## 📝 开发路线图

### Phase 1: 基础设施 ✅ (已完成)
- [x] 创建 Cargo Workspace
- [x] 重组项目结构
- [x] 设置 CI/CD
- [x] 创建跨语言测试框架

### Phase 2: 核心数据模型 🚧 (进行中)
- [x] Card, Rank, Suit (基础实现)
- [x] Deck (基础实现)
- [x] GameConfig (基础实现)
- [ ] 完整单元测试
- [ ] 完整文档

### Phase 3-7: 后续阶段
- [ ] Phase 3: 牌型识别 (P0)
- [ ] Phase 4: 计分引擎 (P0)
- [ ] Phase 5: AI 辅助工具 (P1)
- [ ] Phase 6: 规则变体 (P1)
- [ ] Phase 7: 性能优化 (P2)

---

## 📄 许可证

MIT License - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 🙏 致谢

- 打筒子游戏规则来自传统扑克牌游戏
- 使用了 Rust 和 Python 社区的优秀工具和库

---

## 📮 联系方式

- Issues: https://github.com/yourusername/datongzi-rules/issues
- Discussions: https://github.com/yourusername/datongzi-rules/discussions

---

**注意**：本项目处于积极开发中，Rust 实现正在逐步完善。Python 实现已完整可用。
