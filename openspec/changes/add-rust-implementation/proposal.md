# Proposal: Add Rust Implementation

**Change ID**: `add-rust-implementation`
**Status**: Draft
**Created**: 2025-01-23
**Author**: System

## Problem Statement

当前 Python 实现的 datongzi-rules 在性能关键场景下存在瓶颈：

1. **性能限制**：
   - 牌型识别：~150K ops/sec
   - 满手牌出牌生成：6.38ms/op
   - GIL 限制导致无法充分利用多核

2. **部署约束**：
   - Python 运行时依赖
   - 无法编译为高性能二进制
   - 难以集成到低级系统（如游戏引擎、嵌入式设备）

3. **未来扩展性**：
   - AI 训练需要大量模拟（百万级游戏）
   - 移动端/WebAssembly 部署需求
   - 性能敏感的实时对战场景

## Proposed Solution

创建完整的 Rust 实现，与 Python 版本并行维护：

### 核心目标

1. **完全功能对等**：100% 迁移所有 Python 功能
2. **逻辑一致性**：所有游戏规则和算法完全一致
3. **测试对等**：迁移所有 270+ 测试用例，覆盖率 >90%
4. **性能提升**：目标 10-100x 性能提升
5. **零破坏性**：保留原 Python 代码，独立 Rust crate

### 架构设计

使用 **Cargo Workspace** 结构：

```
datongzi-rules/
├── python/                    # 现有 Python 实现（保持不变）
│   ├── src/datongzi_rules/
│   ├── tests/
│   ├── pyproject.toml
│   └── run.py
├── rust/                      # 新增 Rust 实现
│   ├── Cargo.toml            # Workspace 根配置
│   ├── datongzi-rules/       # 核心库 crate
│   │   ├── Cargo.toml
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   ├── models/
│   │   │   ├── patterns/
│   │   │   ├── scoring/
│   │   │   ├── ai_helpers/
│   │   │   └── variants/
│   │   └── tests/
│   ├── datongzi-cli/         # CLI 工具 crate（可选）
│   │   ├── Cargo.toml
│   │   └── src/main.rs
│   └── benches/              # 性能基准测试
│       └── benchmarks.rs
├── docs/                      # 共享文档
│   ├── GAME_RULE.md
│   ├── ARCHITECTURE.md
│   └── RUST_MIGRATION.md     # 新增：迁移指南
└── README.md                  # 更新：双语言说明
```

### 技术栈

- **Rust 版本**：1.75+ (2024 Edition)
- **核心依赖**：
  - `serde`: 序列化/反序列化
  - `thiserror`: 错误处理
  - `rand`: 洗牌算法
- **开发工具**：
  - `criterion`: 性能基准测试
  - `cargo-tarpaulin`: 代码覆盖率
  - `cargo-nextest`: 快速测试运行
  - `clippy`: Lint 检查
  - `rustfmt`: 代码格式化

### 分阶段实施

#### Phase 1: 基础设施 (P0)
- 创建 Cargo workspace 结构
- 设置 CI/CD 流程（GitHub Actions）
- 建立代码质量门禁（clippy, rustfmt, tests）
- 创建跨语言性能对比框架

#### Phase 2: 核心数据模型 (P0)
- `models/card.rs`: Card, Rank, Suit, Deck
- `models/config.rs`: GameConfig
- 完整单元测试（目标 >95% 覆盖率）

#### Phase 3: 牌型识别 (P0)
- `patterns/recognizer.rs`: PlayType, PlayPattern, PatternRecognizer
- `patterns/validators.rs`: PlayValidator, PlayFormationValidator
- `patterns/finders.rs`: PatternFinder
- 迁移所有牌型识别测试

#### Phase 4: 计分引擎 (P0)
- `scoring/computation.rs`: BonusType, ScoringEvent, ScoreComputation
- 迁移所有计分测试
- 验证计分逻辑完全一致

#### Phase 5: AI 辅助工具 (P1)
- `ai_helpers/play_generator.rs`: PlayGenerator
- `ai_helpers/hand_pattern_analyzer.rs`: HandPatternAnalyzer, HandPatterns
- 优化算法性能（目标 >10x）

#### Phase 6: 规则变体 (P1)
- `variants/config_factory.rs`: ConfigFactory, VariantValidator
- 支持所有预设配置

#### Phase 7: 性能优化与集成测试 (P2)
- 性能基准测试与优化
- 跨语言一致性测试
- 文档和示例代码

## Success Criteria

### 功能完整性
- [ ] 100% API 对等（18 个公开类/函数）
- [ ] 270+ 测试用例全部通过
- [ ] 集成测试验证游戏流程一致性

### 性能指标
- [ ] 牌型识别：>1M ops/sec（>6.6x 提升）
- [ ] 满手牌出牌生成：<1ms/op（>6x 提升）
- [ ] 游戏设置：>50K games/sec（>10x 提升）
- [ ] 计分计算：>1M ops/sec（>7x 提升）

### 代码质量
- [ ] 测试覆盖率 >90%（Python 当前 88.66%）
- [ ] Clippy 无警告（严格模式）
- [ ] 所有公开 API 有文档注释
- [ ] 通过 `cargo audit` 安全检查

### 维护性
- [ ] CI/CD 自动化测试
- [ ] 性能回归检测
- [ ] 跨语言一致性检测（Python vs Rust）
- [ ] 完整的迁移文档和示例

## Impact Assessment

### 正面影响
1. **性能提升**：10-100x 性能提升，解锁高性能场景
2. **部署灵活性**：支持静态编译、WebAssembly、移动端
3. **类型安全**：Rust 强类型系统在编译期捕获错误
4. **并发能力**：无 GIL 限制，充分利用多核

### 风险与缓解
1. **开发成本**：~3800 行代码需要迁移
   - 缓解：分阶段实施，优先核心模块
2. **维护负担**：双语言维护
   - 缓解：共享测试用例，自动化一致性检测
3. **学习曲线**：团队需要 Rust 知识
   - 缓解：提供详细文档和最佳实践

### 兼容性
- **零破坏性**：Python 代码完全保留，独立演进
- **API 设计**：Rust API 尽量贴近 Python API
- **未来 PyO3 集成**：预留接口，可选支持 Python 调用 Rust

## Open Questions

1. **性能基准对比方式**：如何自动化跨语言性能对比？
   - 建议：创建统一的测试用例 JSON 格式，两种语言分别测试

2. **版本同步策略**：如何保持两个实现的功能同步？
   - 建议：每次功能变更同时修改两个实现，CI 强制一致性检测

3. **长期维护计划**：是否计划未来 Python 版本调用 Rust？
   - 建议：Phase 8（未来）可选支持 PyO3 绑定

## Related Changes

- 无（这是第一个主要架构变更）

## References

- Python 实现：`src/datongzi_rules/`（3831 行代码）
- 测试套件：270+ 测试用例，88.66% 覆盖率
- 性能基准：`tests/benchmark/test_performance.py`
- 架构文档：`CLAUDE.md`, `ARCHITECTURE.md`, `GAME_RULE.md`
