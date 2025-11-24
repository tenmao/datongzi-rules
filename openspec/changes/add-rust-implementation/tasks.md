# Tasks: Add Rust Implementation

## Phase 1: 基础设施搭建 (P0)

### 1.1 创建 Cargo Workspace 结构
- [ ] 创建 `rust/` 顶层目录
- [ ] 创建 workspace `Cargo.toml` 配置
- [ ] 创建 `datongzi-rules` 核心库 crate
- [ ] 配置 `rust-toolchain.toml`（固定 Rust 版本 1.75+）
- [ ] 添加基础依赖：serde, thiserror, rand
- [ ] 验证：`cargo build` 成功

### 1.2 重组项目结构
- [ ] 将现有 Python 代码移动到 `python/` 目录
- [ ] 保持所有路径引用正常工作
- [ ] 更新 `pyproject.toml` 路径配置
- [ ] 更新 `run.py` 脚本路径
- [ ] 验证：`python run.py test` 全部通过

### 1.3 设置 CI/CD (GitHub Actions)
- [ ] 创建 `.github/workflows/rust-ci.yml`
- [ ] 添加任务：格式检查（rustfmt）
- [ ] 添加任务：Lint 检查（clippy --all-targets --all-features -- -D warnings）
- [ ] 添加任务：单元测试（cargo nextest run）
- [ ] 添加任务：代码覆盖率（cargo tarpaulin）
- [ ] 添加任务：安全审计（cargo audit）
- [ ] 添加任务：性能基准测试（criterion）
- [ ] 验证：所有 CI 任务通过

### 1.4 创建跨语言测试框架
- [ ] 创建 `tests/cross-language/` 目录
- [ ] 设计测试用例 JSON 格式（输入/预期输出）
- [ ] 编写 Python 测试运行器
- [ ] 编写 Rust 测试运行器
- [ ] 添加初始测试用例（牌型识别、计分）
- [ ] 验证：两种语言输出完全一致

---

## Phase 2: 核心数据模型 (P0)

### 2.1 实现 Card 相关类型
**文件**: `rust/datongzi-rules/src/models/card.rs`

- [ ] 实现 `Suit` 枚举（SPADES=4, HEARTS=3, CLUBS=2, DIAMONDS=1）
- [ ] 实现 `Rank` 枚举（TWO=15, ACE=14, ..., THREE=3）
- [ ] 实现 `Card` 结构体（suit, rank）
- [ ] 实现 `Card` 特性：
  - [ ] `PartialOrd`, `Ord`（按 rank 比较）
  - [ ] `Display`（如 "A♠"）
  - [ ] `is_scoring_card()`, `score_value()`
- [ ] 编写单元测试（迁移 `tests/unit/test_models.py` 中 Card 相关测试）
- [ ] 验证：覆盖率 >95%，所有测试通过

### 2.2 实现 Deck
**文件**: `rust/datongzi-rules/src/models/card.rs`

- [ ] 实现 `Deck` 结构体（cards: Vec<Card>）
- [ ] 实现 `Deck::create_standard_deck(num_decks: u8)` 工厂方法
- [ ] 实现 `shuffle(&mut self)`（使用 `rand::thread_rng`）
- [ ] 实现 `deal_cards(&mut self, count: usize) -> Vec<Card>`
- [ ] 编写单元测试（迁移 Deck 相关测试）
- [ ] 验证：覆盖率 >95%，所有测试通过

### 2.3 实现 GameConfig
**文件**: `rust/datongzi-rules/src/models/config.rs`

- [ ] 实现 `GameConfig` 结构体（17 个字段）
- [ ] 实现 `Default` trait（标准 3 副牌 3 人配置）
- [ ] 实现 `validate(&self) -> Result<(), ConfigError>`
- [ ] 编写单元测试（迁移配置验证测试）
- [ ] 验证：覆盖率 >95%，所有测试通过

### 2.4 模块导出与文档
- [ ] 创建 `rust/datongzi-rules/src/models/mod.rs`
- [ ] 公开导出所有类型
- [ ] 为所有公开 API 添加文档注释（rustdoc）
- [ ] 验证：`cargo doc --no-deps` 生成完整文档

---

## Phase 3: 牌型识别 (P0)

### 3.1 实现 PlayType 和 PlayPattern
**文件**: `rust/datongzi-rules/src/patterns/recognizer.rs`

- [ ] 实现 `PlayType` 枚举（10 种牌型）
- [ ] 实现 `PlayPattern` 结构体（frozen, 9 个字段）
- [ ] 实现 `PlayPattern::new()` 构造函数
- [ ] 实现 `is_trump()`, `is_special_bonus()` 辅助方法
- [ ] 编写单元测试
- [ ] 验证：覆盖率 >95%，所有测试通过

### 3.2 实现 PatternRecognizer
**文件**: `rust/datongzi-rules/src/patterns/recognizer.rs`（509 行 Python 代码）

- [ ] 实现 `PatternRecognizer` 结构体（无状态，全静态方法）
- [ ] 实现 `analyze_cards(cards: &[Card]) -> Result<PlayPattern, PatternError>`
- [ ] 实现单牌识别逻辑
- [ ] 实现对子识别逻辑
- [ ] 实现连对识别逻辑
- [ ] 实现三张识别逻辑（含三带一、三带二）
- [ ] 实现飞机识别逻辑（含飞机带翅膀）
- [ ] 实现炸弹识别逻辑
- [ ] 实现筒子识别逻辑（同花三张）
- [ ] 实现地炸识别逻辑（8 张同数字）
- [ ] 编写单元测试（迁移 `tests/unit/test_patterns.py` 全部测试）
- [ ] 验证：覆盖率 >95%，所有测试通过

### 3.3 实现 PlayValidator
**文件**: `rust/datongzi-rules/src/patterns/validators.rs`（173 行 Python 代码）

- [ ] 实现 `PlayFormationValidator`（牌型合法性验证）
- [ ] 实现 `PlayValidator::is_valid_play(cards: &[Card]) -> bool`
- [ ] 实现 `PlayValidator::can_beat_play(cards: &[Card], current: &PlayPattern) -> bool`
- [ ] 实现同类型比较逻辑
- [ ] 实现王牌比较逻辑（地炸 > 筒子 > 炸弹）
- [ ] 实现 `has_must_play_violation()`（有牌必打检查）
- [ ] 编写单元测试（迁移 `tests/unit/test_pattern_validators.py`）
- [ ] 验证：覆盖率 >95%，所有测试通过

### 3.4 实现 PatternFinder
**文件**: `rust/datongzi-rules/src/patterns/finders.rs`（548 行 Python 代码）

- [ ] 实现 `PatternFinder` 结构体
- [ ] 实现 `find_all_singles(hand: &[Card]) -> Vec<Card>`
- [ ] 实现 `find_all_pairs(hand: &[Card]) -> Vec<Vec<Card>>`
- [ ] 实现 `find_all_consecutive_pairs(hand: &[Card]) -> Vec<Vec<Card>>`
- [ ] 实现 `find_all_triples(hand: &[Card]) -> Vec<Vec<Card>>`
- [ ] 实现 `find_all_airplanes(hand: &[Card]) -> Vec<Vec<Card>>`
- [ ] 实现 `find_all_bombs(hand: &[Card]) -> Vec<Vec<Card>>`
- [ ] 实现 `find_all_tongzi(hand: &[Card]) -> Vec<Vec<Card>>`
- [ ] 实现 `find_all_dizha(hand: &[Card]) -> Vec<Vec<Card>>`
- [ ] 编写单元测试（迁移 `tests/unit/test_pattern_finders.py`）
- [ ] 验证：覆盖率 >95%，所有测试通过

---

## Phase 4: 计分引擎 (P0)

### 4.1 实现 BonusType 和 ScoringEvent
**文件**: `rust/datongzi-rules/src/scoring/computation.rs`

- [ ] 实现 `BonusType` 枚举（8 种奖励类型）
- [ ] 实现 `ScoringEvent` 结构体（6 个字段）
- [ ] 实现 `Display` trait（格式化输出）
- [ ] 编写单元测试
- [ ] 验证：覆盖率 >95%，所有测试通过

### 4.2 实现 ScoreComputation
**文件**: `rust/datongzi-rules/src/scoring/computation.rs`（375 行 Python 代码）

- [ ] 实现 `ScoreComputation` 结构体（持有 GameConfig 和事件列表）
- [ ] 实现 `new(config: GameConfig) -> Self`
- [ ] 实现 `create_round_win_event(player_id, round_cards, round_number) -> ScoringEvent`
- [ ] 实现 `create_special_bonus_events(player_id, winning_pattern, round_number, is_round_winning_play) -> Vec<ScoringEvent>`
- [ ] 实现 `create_finish_bonus_events(player_ids_in_finish_order) -> Vec<ScoringEvent>`
- [ ] 实现 `calculate_total_score_for_player(player_id) -> i32`
- [ ] 实现 `validate_scores(player_scores: HashMap<String, i32>) -> bool`（零和检查）
- [ ] 编写单元测试（迁移 `tests/unit/test_scoring.py` 全部测试）
- [ ] 编写规则一致性测试（迁移 `tests/unit/test_scoring_rule_compliance.py`）
- [ ] 编写回合制测试（迁移 `tests/unit/test_scoring_round_based.py`）
- [ ] 验证：覆盖率 >95%，所有测试通过

---

## Phase 5: AI 辅助工具 (P1)

### 5.1 实现 PlayGenerator
**文件**: `rust/datongzi-rules/src/ai_helpers/play_generator.rs`（699 行 Python 代码）

- [ ] 实现 `PlayGenerator` 结构体
- [ ] 实现 `generate_beating_plays_with_same_type_or_trump(hand, current_pattern) -> Vec<Vec<Card>>`
- [ ] 实现 `count_all_plays(hand: &[Card]) -> usize`
- [ ] 实现 `generate_all_plays(hand, max_combinations) -> Result<Vec<Vec<Card>>, GeneratorError>`
- [ ] 优化组合生成算法（使用迭代器避免克隆）
- [ ] 编写单元测试（迁移 `tests/unit/test_ai_helpers.py` 中 PlayGenerator 测试）
- [ ] 验证：覆盖率 >90%，所有测试通过

### 5.2 实现 HandPatternAnalyzer
**文件**: `rust/datongzi-rules/src/ai_helpers/hand_pattern_analyzer.rs`（411 行 Python 代码）

- [ ] 实现 `HandPatterns` 结构体（10 个字段）
- [ ] 实现 `HandPatternAnalyzer::analyze_patterns(hand: &[Card]) -> HandPatterns`
- [ ] 实现非重叠分解逻辑（优先级：Dizha > Tongzi > Bomb > ...）
- [ ] 实现 `trump_count()`, `has_control_cards()` 元数据计算
- [ ] 编写单元测试（迁移 `tests/unit/test_hand_pattern_analyzer.py`）
- [ ] 验证：覆盖率 >90%，所有测试通过

---

## Phase 6: 规则变体 (P1)

### 6.1 实现 ConfigFactory
**文件**: `rust/datongzi-rules/src/variants/config_factory.rs`（300 行 Python 代码）

- [ ] 实现 `ConfigFactory` 结构体（全静态方法）
- [ ] 实现 `create_standard_3deck_3player() -> GameConfig`
- [ ] 实现 `create_4deck_4player() -> GameConfig`
- [ ] 实现 `create_2player() -> GameConfig`
- [ ] 实现 `create_quick_game() -> GameConfig`
- [ ] 实现 `create_high_stakes() -> GameConfig`
- [ ] 实现 `create_beginner_friendly() -> GameConfig`
- [ ] 实现 `create_custom(...) -> GameConfig`
- [ ] 编写单元测试（迁移 `tests/unit/test_variants.py`）
- [ ] 验证：覆盖率 >90%，所有测试通过

### 6.2 实现 VariantValidator
**文件**: `rust/datongzi-rules/src/variants/config_factory.rs`

- [ ] 实现 `VariantValidator::validate_config(config: &GameConfig) -> (bool, Vec<String>)`
- [ ] 实现牌数合法性检查
- [ ] 实现玩家数检查（2-4 人）
- [ ] 实现完成奖励零和检查
- [ ] 实现奖励分数合理性检查
- [ ] 编写单元测试
- [ ] 验证：覆盖率 >90%，所有测试通过

---

## Phase 7: 性能优化与集成测试 (P2)

### 7.1 性能基准测试
**文件**: `rust/benches/benchmarks.rs`

- [ ] 创建 Criterion 基准测试框架
- [ ] 迁移牌型识别基准测试（目标 >1M ops/sec）
- [ ] 迁移出牌生成基准测试（目标满手牌 <1ms）
- [ ] 迁移游戏设置基准测试（目标 >50K games/sec）
- [ ] 迁移计分基准测试（目标 >1M ops/sec）
- [ ] 创建性能对比报告脚本（Python vs Rust）
- [ ] 验证：所有性能目标达成

### 7.2 集成测试
**文件**: `rust/datongzi-rules/tests/integration_tests.rs`

- [ ] 迁移 `tests/integration/test_full_game_flow.py`（完整游戏流程）
- [ ] 迁移 `tests/integration/test_game_simulation.py`（游戏模拟）
- [ ] 创建跨语言一致性测试（JSON 驱动）
- [ ] 验证：所有集成测试通过

### 7.3 性能优化
- [ ] Profile 识别性能瓶颈（使用 `cargo flamegraph`）
- [ ] 优化热路径代码（避免不必要的克隆/分配）
- [ ] 使用 SIMD 加速关键算法（可选）
- [ ] 添加性能回归检测到 CI
- [ ] 验证：达到性能目标

---

## Phase 8: 文档与示例 (P2)

### 8.1 API 文档
- [ ] 为所有公开 API 添加详细 rustdoc 注释
- [ ] 添加模块级文档（module-level docs）
- [ ] 添加使用示例到文档中（doc tests）
- [ ] 验证：`cargo doc --open` 文档完整

### 8.2 用户指南
- [ ] 创建 `docs/RUST_MIGRATION.md`（迁移指南）
- [ ] 创建 `rust/README.md`（快速开始）
- [ ] 创建 Python vs Rust API 对照表
- [ ] 添加常见问题解答

### 8.3 示例代码
- [ ] 创建 `rust/examples/basic_usage.rs`（基础用法）
- [ ] 创建 `rust/examples/game_simulation.rs`（游戏模拟）
- [ ] 创建 `rust/examples/benchmark.rs`（性能测试）
- [ ] 验证：所有示例可运行

### 8.4 更新根文档
- [ ] 更新根 `README.md`（添加 Rust 说明）
- [ ] 更新 `CLAUDE.md`（添加 Rust 开发指南）
- [ ] 创建 `CONTRIBUTING.md`（双语言贡献指南）

---

## 验收标准

### 功能完整性
- [ ] 18 个公开 API 全部实现
- [ ] 270+ 测试用例全部通过（Python: 270, Rust: 270+）
- [ ] 跨语言一致性测试 100% 通过

### 性能指标
- [ ] 牌型识别：>1M ops/sec（vs Python 150K）
- [ ] 满手牌出牌生成：<1ms/op（vs Python 6.38ms）
- [ ] 游戏设置：>50K games/sec（vs Python 5K）
- [ ] 计分计算：>1M ops/sec（vs Python 140K）

### 代码质量
- [ ] Rust 测试覆盖率 >90%
- [ ] Clippy 无警告（`clippy::all`, `clippy::pedantic`）
- [ ] `cargo fmt --check` 通过
- [ ] `cargo audit` 无安全漏洞
- [ ] 所有 CI 任务绿灯

### 文档完整性
- [ ] 所有公开 API 有 rustdoc 文档
- [ ] 迁移指南完整
- [ ] 至少 3 个示例程序
- [ ] 性能对比报告

---

## 并行工作机会

以下任务可以并行执行：

**阶段 1**：
- 1.1, 1.2 可以并行（不同目录）
- 1.3, 1.4 可以在 1.1 完成后并行

**阶段 2-3**：
- Phase 2 和 Phase 3 部分独立（models 先行，patterns 依赖 models）

**阶段 4-6**：
- Phase 4（scoring）和 Phase 5（ai_helpers）可以部分并行
- Phase 6（variants）依赖 Phase 2（models）

**阶段 7-8**：
- 7.1（性能测试）和 7.2（集成测试）并行
- 8.1（API 文档）和 8.3（示例代码）并行

---

## 估算工作量

| Phase | 任务数 | 估计工时 | 优先级 |
|-------|--------|----------|--------|
| Phase 1 | 15 | 16h | P0 |
| Phase 2 | 12 | 20h | P0 |
| Phase 3 | 16 | 40h | P0 |
| Phase 4 | 10 | 24h | P0 |
| Phase 5 | 8 | 20h | P1 |
| Phase 6 | 8 | 16h | P1 |
| Phase 7 | 10 | 24h | P2 |
| Phase 8 | 12 | 16h | P2 |
| **总计** | **91** | **~176h** | - |

**关键路径**：Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 7（性能优化）

**最小可行版本（MVP）**：Phase 1-4（~100h），实现核心功能和测试。
