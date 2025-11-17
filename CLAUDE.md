# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目定位

`datongzi-rules` 是"打筒子"游戏的权威规则引擎库，零依赖纯Python实现(Python 3.12+)。

**核心职责**: 提供牌型识别、出牌验证、计分逻辑、AI辅助工具等核心规则API，供上层游戏引擎(datongzi)调用。

**关键约束**:
- ✅ `datongzi` → `datongzi-rules` (游戏引擎依赖规则库)
- ❌ `datongzi-rules` → `datongzi` (规则库永不依赖游戏引擎)
- 所有规则逻辑只在此库实现，避免在上层重复实现

**职责边界**（2025-01-17 更新）：
- ✅ 牌型识别、出牌验证、计分逻辑
- ✅ 生成合法出牌、手牌结构分析
- ✅ 规则变体配置
- ❌ 游戏状态管理（Round/Play/Game 对象 → datongzi 职责）
- ❌ AI 策略实现（→ datongzi/ai 职责）
- ❌ UI/前端逻辑（→ datongzi/ui 职责）

## 开发命令

```bash
# 运行所有测试(含覆盖率)
python run.py test

# 仅运行单元测试
python run.py unit

# 仅运行集成测试
python run.py integration

# 运行性能基准测试
python run.py benchmark

# 运行所有示例
python run.py examples

# 运行所有检查(测试 + 示例)
python run.py check

# 清理缓存
python run.py clean

# 直接使用pytest(单个测试文件)
pytest tests/unit/test_basic.py -v

# 直接使用pytest(单个测试函数)
pytest tests/unit/test_basic.py::test_function_name -v
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

## 模块职责边界（2025-01-17 更新）

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
- `PlayType`: 牌型枚举（SINGLE, PAIR, BOMB, TONGZI, DIZHA, etc.）

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
```python
# 1. 判断回合结束
class Round:
    def is_finished(self):
        return all(player.passed for player in self.other_players)

# 2. 收集回合数据
all_cards_in_round = [card for play in round.plays for card in play.cards]
winner = round.plays[-1].player_id
winning_pattern = PatternRecognizer.analyze_cards(round.plays[-1].cards)

# 3. 调用计分引擎
engine.create_round_win_event(winner, all_cards_in_round, round_number)
engine.create_special_bonus_events(winner, winning_pattern, round_number, is_round_winning_play=True)
```

**核心类**:
- `ScoreComputation`: 计分引擎（纯计算）
- `ScoringEvent`: 计分事件数据类
- `BonusType`: 奖励类型枚举

### ai_helpers/ (AI辅助工具层)（2025-01-17 重构）

**重要变更**: 已删除 `HandEvaluator` 和 `PatternSuggester`，只保留核心工具。

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
```python
# ❌ 错误: 在datongzi/ai中重新实现规则
class AI:
    def _can_beat(self, cards, current_play):
        # 自己实现验证逻辑...

# ✅ 正确: 依赖规则库
from datongzi_rules import PlayValidator
can_beat = PlayValidator.can_beat_play(cards, current_play)
```

### ❌ 禁止多处生成合法出牌
```python
# ❌ 错误: 在AI中重复实现PlayGenerator
class AI:
    def _get_legal_moves(self, hand):
        # 重新实现生成逻辑...

# ✅ 正确: 使用PlayGenerator
from datongzi_rules import PlayGenerator
moves = PlayGenerator.generate_beating_plays_with_same_type_or_trump(hand, current_pattern)
```

### ❌ 禁止在规则库实现AI策略
```python
# ❌ 错误: 在规则库实现复杂AI
class HandEvaluator:
    def choose_best_play(self, hand, game_state):
        # 多步博弈推演...

# ✅ 正确: 规则库只提供工具，AI在上层实现
# datongzi/ai/strategy.py
class AIStrategy:
    def choose_best_play(self, valid_plays, hand, game_state):
        # AI策略逻辑（基于 PlayGenerator 提供的 valid_plays）
```

### ❌ 禁止在规则库管理游戏状态
```python
# ❌ 错误: 在规则库创建 Round/Game 类
class Round:
    plays: list[Play]
    current_player: Player

# ✅ 正确: 状态管理在上层
# datongzi/models/round.py
class Round:
    def __init__(self, players):
        self.plays = []
        self.scoring_engine = ScoreComputation(config)  # 只使用计分引擎
```

### ❌ 禁止硬编码规则变体
```python
# ❌ 错误: if-else判断规则模式
if GAME_MODE == "standard":
    # 标准规则...
elif GAME_MODE == "simple":
    # 简化规则...

# ✅ 正确: 使用GameConfig参数化
config = ConfigFactory.create_standard_3deck_3player()
```

### ❌ 禁止创建上帝类
```python
# ❌ 错误: 一个类做所有事情
class GameRules:
    def recognize_pattern(self): pass
    def validate_play(self): pass
    def generate_moves(self): pass
    def calculate_score(self): pass

# ✅ 正确: 拆分成专职类
PatternRecognizer, PlayValidator, PlayGenerator, ScoreComputation
```

## 代码修改检查清单

**添加新牌型**:
1. 在`PlayType`枚举添加新类型
2. 在`PatternRecognizer.analyze_cards()`添加识别逻辑
3. 在`PlayFormationValidator`添加验证方法
4. 在`PlayValidator.can_beat_play()`添加对抗规则
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

- 单元测试覆盖率目标: >85%（当前 88.66%）
- 所有新功能必须包含单元测试
- 修改现有功能必须通过所有现有测试
- 性能敏感路径需要benchmark测试
- 使用`python run.py check`验证所有测试和示例通过

**测试统计**（2025-01-17）:
- 单元测试: 258 个
- 集成测试: 12 个
- 总计: 270 个测试
- 覆盖率: 88.66%

## 常见开发场景

### 场景1: 上层需要判断回合结束

**错误做法**:
```python
# ❌ 在规则库添加 Round 类
class Round:
    def is_finished(self): ...
```

**正确做法**:
```python
# ✅ 在上层 datongzi 实现
# datongzi/models/round.py
class Round:
    def is_finished(self):
        # 判断逻辑...
```

### 场景2: 上层需要AI出牌建议

**错误做法**:
```python
# ❌ 在规则库实现AI策略
class HandEvaluator:
    def suggest_best_play(self, hand, game_state):
        # AI决策...
```

**正确做法**:
```python
# ✅ 规则库只提供工具
valid_plays = PlayGenerator.generate_beating_plays_with_same_type_or_trump(hand, current_pattern)

# ✅ AI策略在上层实现
# datongzi/ai/strategy.py
class AIStrategy:
    def choose_best_play(self, valid_plays, hand, game_state):
        # AI决策逻辑...
```

### 场景3: 上层需要计分

**错误做法**:
```python
# ❌ 规则库自动跟踪回合状态
class ScoreComputation:
    def __init__(self):
        self.round_cards = []  # ❌ 不应该维护状态
```

**正确做法**:
```python
# ✅ 上层收集数据，规则库只计算
# datongzi/models/round.py
class Round:
    def end_round(self):
        all_cards = [card for play in self.plays for card in play.cards]
        winner_pattern = PatternRecognizer.analyze_cards(self.plays[-1].cards)

        # 调用计分引擎
        engine.create_round_win_event(winner, all_cards, round_number)
        engine.create_special_bonus_events(winner, winner_pattern, round_number, True)
```

## 重要更新日志

### 2025-01-17 重构
1. **删除模块**:
   - `HandEvaluator` - 手牌评估应在AI层实现
   - `PatternSuggester` - CV纠错应在前端实现

2. **重命名**:
   - `ScoringEngine` → `ScoreComputation` - 强调纯计算职责
   - `engine.py` → `computation.py` - 文件名与类名一致

3. **职责澄清**:
   - `ScoreComputation` 是纯计算引擎，不管理状态
   - 上层负责收集回合数据、判断回合结束

4. **文档更新**:
   - README.md: 完整API文档和使用示例
   - CLAUDE.md: 架构原则和职责边界

## 参考文档

- **GAME_RULE.md**: 游戏规则详细定义(修改规则逻辑前必读)
- **ARCHITECTURE.md**: SOLID原则详细说明、模块职责、反模式警告
- **README.md**: 完整API文档、使用示例、常见问题
- **NAME_CONVENTION.md**: 命名规范
