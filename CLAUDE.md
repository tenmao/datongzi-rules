<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目定位

`datongzi-rules` 是"打筒子"游戏的权威规则引擎库，零依赖 Rust 实现。

**核心职责**: 提供牌型识别、出牌验证、计分逻辑、AI辅助工具等核心规则API，供上层游戏引擎(datongzi)调用。

**关键约束**:
- ✅ `datongzi` → `datongzi-rules` (游戏引擎依赖规则库)
- ❌ `datongzi-rules` → `datongzi` (规则库永不依赖游戏引擎)
- 所有规则逻辑只在此库实现，避免在上层重复实现

**职责边界**：
- ✅ 牌型识别、出牌验证、计分逻辑
- ✅ 生成合法出牌、手牌结构分析
- ✅ 规则变体配置
- ❌ 游戏状态管理（Round/Play/Game 对象 → datongzi 职责）
- ❌ AI 策略实现（→ datongzi/ai 职责）
- ❌ UI/前端逻辑（→ datongzi/ui 职责）

## 开发命令

```bash
# 构建项目
cd rust && cargo build

# 运行所有测试
cd rust && cargo test

# 运行特定测试
cd rust && cargo test test_name

# 运行特定测试文件
cd rust && cargo test --test test_file_name

# 代码格式化
cd rust && cargo fmt

# 代码检查
cd rust && cargo clippy

# 运行性能基准测试
cd rust && cargo bench

# 生成文档
cd rust && cargo doc --open
```

## 架构原则(SOLID)

**分层架构**(从下到上):
```
Layer 1: models (数据层) - Card, Rank, Suit, Deck, GameConfig
         ↓
Layer 2: patterns (识别层) - PatternRecognizer, PlayValidator, PatternFinder
         ↓
Layer 3: scoring (计分层) - ScoreComputation
         ↓
Layer 4: ai_helpers, variants (辅助层) - PlayGenerator, HandPatternAnalyzer, ConfigFactory
```

**依赖规则**:
- 允许: 上层 → 下层, 同层互相依赖, 所有层 → models
- 禁止: 下层 → 上层, datongzi-rules → datongzi

**单一职责原则 (SRP)**:
- `PatternRecognizer`: 只负责识别牌型
- `PlayValidator`: 只负责验证出牌是否合法
- `PlayGenerator`: 只负责生成所有合法出牌 (AI的唯一合法出牌来源)
- `ScoreComputation`: 只负责计分逻辑（纯计算，不管理状态）
- `HandPatternAnalyzer`: 只负责手牌结构分析（非重叠分解）
- 严禁创建"上帝类"(God Class)合并多个职责

**开放封闭原则 (OCP)**:
- 通过`GameConfig`参数化规则变体，不修改核心代码
- 添加新牌型/规则变体时，遵循扩展而非修改

**依赖倒置原则 (DIP)**:
- 高层模块(AI/UI)依赖此规则库的抽象接口
- 严禁在高层重新实现规则逻辑

## 核心游戏规则

**关键规则** (修改代码前必读 GAME_RULE.md):
1. **回合制**: 出牌后无人能打，回合结束，最后出牌者胜利
2. **有牌必打**: 上家出牌后，如果手牌有大过的牌，则必须出
3. **牌型优先级**: 地炸 > 筒子 > 炸弹 > 普通牌(单张/对子/连对/三张/飞机)
4. **计分**:
   - 回合获胜者得该回合所有5/10/K的分数
   - 筒子/地炸奖励分: K筒子100分, A筒子200分, 2筒子300分, 地炸400分
   - 完成位置奖励: 上游+100分, 二游-40分, 三游-60分
   - **只有回合最后出牌者得分，中间出的特殊牌不得分**

**牌型定义**:
- 炸弹: 4张及以上相同数字，讲究大打小、多打少
- 筒子: 3张相同花色相同数字(同花三张)，压炸弹，花色也分大小(黑桃>红桃>梅花>方块)
- 地炸: 8张同数字(4种花色各2张)，最强牌型
- 连对: 两连对及以上，没有单牌顺子
- 三张: 可以带0-2张
- 飞机: 连续数字的三张，可以带翅膀(每组带0-2张)

## 模块职责边界

### models/ (数据模型层)
- **允许**: 定义不可变数据结构、配置验证
- **禁止**: 实现业务逻辑、牌型识别、计分

**核心类**:
- `Card`: 卡牌（花色+点数）
- `Rank`, `Suit`: 枚举（点数/花色）
- `Deck`: 牌堆（创建、洗牌、发牌）
- `GameConfig`: 游戏配置（参数化规则变体）

### patterns/ (牌型识别层)
- **PatternRecognizer**: 识别给定牌是否为合法牌型
- **PlayValidator**: 验证出牌是否能打、是否违反"有牌必打"
- **PatternFinder**: 从手牌中提取特定牌型组合
- **禁止**: 生成AI决策、修改游戏状态

**核心类**:
- `PatternRecognizer`: 牌型识别器（analyze_cards）
- `PlayValidator`: 出牌验证器（can_beat_play, is_valid_play）
- `PlayPattern`: 牌型数据类（play_type, primary_rank, etc.）
- `PlayType`: 牌型枚举（Single, Pair, Bomb, Tongzi, Dizha, etc.）

### scoring/ (计分引擎层)
**重要**: 这是**纯计算引擎**，不管理游戏状态！

**ScoreComputation 职责**:
- ✅ 计算回合得分（接收上层收集的 round_cards）
- ✅ 计算筒子/地炸奖励（接收已识别的 winning_pattern）
- ✅ 计算完成位置奖励
- ❌ 判断回合结束（上层职责）
- ❌ 跟踪回合状态（上层职责）
- ❌ 收集回合内所有牌（上层职责）

**上层调用方职责**（datongzi 游戏引擎）:
```rust
// 1. 判断回合结束
impl Round {
    fn is_finished(&self) -> bool {
        self.other_players.iter().all(|p| p.passed)
    }
}

// 2. 收集回合数据
let all_cards: Vec<Card> = round.plays.iter()
    .flat_map(|p| p.cards.iter().cloned())
    .collect();
let winner = &round.plays.last().unwrap().player_id;
let winning_pattern = PatternRecognizer::analyze_cards(&round.plays.last().unwrap().cards);

// 3. 调用计分引擎
engine.create_round_win_event(winner, &all_cards, round_number);
engine.create_special_bonus_events(winner, &winning_pattern, round_number, true);
```

**核心类**:
- `ScoreComputation`: 计分引擎（纯计算）
- `ScoringEvent`: 计分事件数据类
- `BonusType`: 奖励类型枚举

### ai_helpers/ (AI辅助工具层)

**PlayGenerator 职责**:
- ✅ **唯一应该生成所有合法出牌的地方**
- ✅ 所有AI/UI必须调用此类，严禁重复实现
- ✅ 提供3个API：
  - `generate_beating_plays_with_same_type_or_trump()` - 高效（推荐）
  - `count_all_plays()` - 统计用
  - `generate_all_plays()` - 完整枚举（⚠️ 可能爆炸）

**HandPatternAnalyzer 职责**:
- ✅ 手牌结构分析（非重叠分解）
- ✅ 为AI提供资源视图（炸弹/筒子/三张/对子/散牌数量）
- ✅ 优先级：Dizha > Tongzi > Bomb > Airplane > Triple > ConsecPairs > Pair > Single

**禁止**:
- ❌ 实现复杂AI策略（那是 datongzi/ai 的职责）
- ❌ 手牌强度评估（AI自己实现）
- ❌ 出牌建议（AI自己决策）
- ❌ CV识别纠错（前端职责）

**核心类**:
- `PlayGenerator`: 出牌生成器
- `HandPatternAnalyzer`: 手牌结构分析器
- `HandPatterns`: 手牌结构数据类

### variants/ (规则变体层)
- **ConfigFactory**: 预定义规则变体(标准3副牌、简化规则、2人对战等)
- **VariantValidator**: 配置验证器
- **允许**: 创建配置对象、验证配置合法性
- **禁止**: 修改核心规则逻辑

**核心类**:
- `ConfigFactory`: 配置工厂（7种预设变体）
- `VariantValidator`: 配置验证器

## 反模式警告

### ❌ 禁止在高层重新实现规则
```rust
// ❌ 错误: 在datongzi/ai中重新实现规则
impl AI {
    fn can_beat(&self, cards: &[Card], current_play: &PlayPattern) -> bool {
        // 自己实现验证逻辑...
    }
}

// ✅ 正确: 依赖规则库
use datongzi_rules::PlayValidator;
let can_beat = PlayValidator::can_beat_play(&cards, &current_play);
```

### ❌ 禁止多处生成合法出牌
```rust
// ❌ 错误: 在AI中重复实现PlayGenerator
impl AI {
    fn get_legal_moves(&self, hand: &[Card]) -> Vec<Vec<Card>> {
        // 重新实现生成逻辑...
    }
}

// ✅ 正确: 使用PlayGenerator
use datongzi_rules::PlayGenerator;
let moves = PlayGenerator::generate_beating_plays_with_same_type_or_trump(&hand, &current_pattern);
```

### ❌ 禁止在规则库实现AI策略
```rust
// ❌ 错误: 在规则库实现复杂AI
impl HandEvaluator {
    fn choose_best_play(&self, hand: &[Card], game_state: &GameState) -> Vec<Card> {
        // 多步博弈推演...
    }
}

// ✅ 正确: 规则库只提供工具，AI在上层实现
// datongzi/ai/strategy.rs
impl AIStrategy {
    fn choose_best_play(&self, valid_plays: &[Vec<Card>], hand: &[Card], game_state: &GameState) -> Vec<Card> {
        // AI策略逻辑（基于 PlayGenerator 提供的 valid_plays）
    }
}
```

### ❌ 禁止在规则库管理游戏状态
```rust
// ❌ 错误: 在规则库创建 Round/Game 类
struct Round {
    plays: Vec<Play>,
    current_player: Option<Player>,
}

// ✅ 正确: 状态管理在上层
// datongzi/models/round.rs
struct Round {
    plays: Vec<Play>,
    scoring_engine: ScoreComputation,  // 只使用计分引擎
}
```

### ❌ 禁止硬编码规则变体
```rust
// ❌ 错误: if-else判断规则模式
let bonus = match game_mode {
    "standard" => 100,
    "simple" => 50,
    _ => panic!(),
};

// ✅ 正确: 使用GameConfig参数化
let config = ConfigFactory::create_standard_3deck_3player();
```

### ❌ 禁止创建上帝类
```rust
// ❌ 错误: 一个类做所有事情
struct GameRules;
impl GameRules {
    fn recognize_pattern(&self) {}
    fn validate_play(&self) {}
    fn generate_moves(&self) {}
    fn calculate_score(&self) {}
}

// ✅ 正确: 拆分成专职类
// PatternRecognizer, PlayValidator, PlayGenerator, ScoreComputation
```

## 代码修改检查清单

**添加新牌型**:
1. 在`PlayType`枚举添加新类型
2. 在`PatternRecognizer::analyze_cards()`添加识别逻辑
3. 在`PlayFormationValidator`添加验证方法
4. 在`PlayValidator::can_beat_play()`添加对抗规则
5. 在`ScoreComputation`添加计分规则(如果有奖励)
6. 添加单元测试

**添加新规则变体**:
1. 在`GameConfig`添加新配置字段
2. 在`ConfigFactory`添加新工厂方法
3. 在相关模块读取配置
4. 添加单元测试

**性能优化**:
1. 添加缓存/索引，不改变接口
2. 保持方法签名不变
3. 确保所有单元测试通过

**SOLID自检**:
- [ ] SRP: 是否只做一件事?
- [ ] OCP: 是否可以通过配置/组合扩展，而非修改现有代码?
- [ ] DIP: 是否依赖抽象而非具体实现?
- [ ] 是否违反了依赖方向(上→下)?
- [ ] 是否在高层重复实现了底层规则逻辑?
- [ ] 是否在规则库实现了状态管理或AI策略?（应在上层）

## 测试要求

- 所有新功能必须包含单元测试
- 修改现有功能必须通过所有现有测试
- 性能敏感路径需要benchmark测试
- 使用`cargo test`验证所有测试通过

## 常见开发场景

### 场景1: 上层需要判断回合结束

**错误做法**:
```rust
// ❌ 在规则库添加 Round 类
struct Round {
    fn is_finished(&self) -> bool { ... }
}
```

**正确做法**:
```rust
// ✅ 在上层 datongzi 实现
// datongzi/models/round.rs
impl Round {
    fn is_finished(&self) -> bool {
        // 判断逻辑...
    }
}
```

### 场景2: 上层需要AI出牌建议

**错误做法**:
```rust
// ❌ 在规则库实现AI策略
impl HandEvaluator {
    fn suggest_best_play(&self, hand: &[Card], game_state: &GameState) -> Vec<Card> {
        // AI决策...
    }
}
```

**正确做法**:
```rust
// ✅ 规则库只提供工具
let valid_plays = PlayGenerator::generate_beating_plays_with_same_type_or_trump(&hand, &current_pattern);

// ✅ AI策略在上层实现
// datongzi/ai/strategy.rs
impl AIStrategy {
    fn choose_best_play(&self, valid_plays: &[Vec<Card>], hand: &[Card], game_state: &GameState) -> Vec<Card> {
        // AI决策逻辑...
    }
}
```

### 场景3: 上层需要计分

**错误做法**:
```rust
// ❌ 规则库自动跟踪回合状态
struct ScoreComputation {
    round_cards: Vec<Card>,  // ❌ 不应该维护状态
}
```

**正确做法**:
```rust
// ✅ 上层收集数据，规则库只计算
// datongzi/models/round.rs
impl Round {
    fn end_round(&mut self) {
        let all_cards: Vec<Card> = self.plays.iter()
            .flat_map(|p| p.cards.iter().cloned())
            .collect();
        let winner_pattern = PatternRecognizer::analyze_cards(&self.plays.last().unwrap().cards);

        // 调用计分引擎
        engine.create_round_win_event(&winner, &all_cards, round_number);
        engine.create_special_bonus_events(&winner, &winner_pattern, round_number, true);
    }
}
```

## 参考文档

- **GAME_RULE.md**: 游戏规则详细定义(修改规则逻辑前必读)
- **ARCHITECTURE.md**: SOLID原则详细说明、模块职责、反模式警告
- **README.md**: 完整API文档、使用示例、常见问题
- **NAME_CONVENTION.md**: 命名规范
