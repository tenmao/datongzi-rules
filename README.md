# Da Tong Zi Rules Engine

零依赖的打筒子游戏规则引擎库 - **Rust 实现**

![Rust CI](https://github.com/tenmao/datongzi-rules/workflows/Rust%20CI/badge.svg)

---

## 🚀 特性

### 核心功能

- ✅ **完整游戏规则**：10 种牌型，回合制计分
- ✅ **牌型识别**：单牌、对子、连对、三张、飞机、炸弹、筒子、地炸
- ✅ **出牌验证**：支持"有牌必打"规则
- ✅ **计分系统**：回合基础分、特殊奖励、完成位置奖励
- ✅ **AI 辅助工具**：出牌生成、手牌结构分析
- ✅ **规则变体**：支持多种配置（2-4 人，不同牌副数）

### 代码质量

| 指标 | Rust |
|-----|------|
| 性能 | 高性能、类型安全 |
| 类型检查 | rustc (强制) |

---

## 📦 安装使用

### Rust 实现

```bash
# 构建
cd rust
cargo build --release

# 运行测试
cargo test

# 使用示例
use datongzi_rules::{Card, Rank, Suit};

let card = Card::new(Suit::Spades, Rank::Ace);
println!("Card: {}", card);
```

[📖 Rust 完整文档](rust/README.md)

---

## 🏗️ 项目结构

```
datongzi-rules/
├── rust/                  # Rust 实现
│   ├── datongzi-rules/    # 核心库 crate
│   │   └── src/
│   │       ├── models/    # 数据模型
│   │       ├── patterns/  # 牌型识别
│   │       ├── scoring/   # 计分系统
│   │       ├── ai_helpers/# AI 辅助工具
│   │       └── variants/  # 规则变体
│   └── README.md
│
├── docs/                  # 共享文档
│   ├── ALGORITHM_DESIGN.md
│   └── KICKER_SELECTION_ALGORITHM.md
│
└── .github/workflows/     # CI/CD 配置
    └── rust-ci.yml
```

---

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/datongzi-rules.git
cd datongzi-rules
```

### 2. Rust 开发

```bash
cd rust
cargo build              # 构建
cargo test               # 运行测试
cargo bench              # 性能测试
```

---

## 🔧 开发

### 运行测试

```bash
cd rust && cargo test
```

### 代码格式化

```bash
cd rust && cargo fmt
```

### 代码检查

```bash
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
- 测试覆盖率不能下降

查看完整贡献指南：[CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📖 文档

- [游戏规则详解](GAME_RULE.md)
- [架构设计](ARCHITECTURE.md)
- [Rust API 文档](rust/README.md)
- [GitHub 设置指南](GITHUB_SETUP.md)
- [OpenSpec 提案](openspec/changes/add-rust-implementation/)

---

## 📄 许可证

MIT License - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 🙏 致谢

- 打筒子游戏规则来自传统扑克牌游戏
- 使用了 Rust 社区的优秀工具和库

---

## 📮 联系方式

- Issues: https://github.com/yourusername/datongzi-rules/issues
- Discussions: https://github.com/yourusername/datongzi-rules/discussions
