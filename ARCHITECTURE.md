# datongzi-rules 架构设计文档 (SOLID原则)

**版本**: 0.2.0
**更新**: 2025-01-17
**状态**: 权威架构文档

---

## 目录
1. [架构概览](#架构概览)
2. [SOLID原则应用](#solid原则应用)
3. [模块职责边界](#模块职责边界)
4. [依赖关系](#依赖关系)
5. [扩展指南](#扩展指南)
6. [反模式警告](#反模式警告)
7. [重要更新](#重要更新)

---

## 架构概览

### 核心设计原则

**datongzi-rules 是打筒子游戏的纯规则引擎库，零依赖纯Python实现（Python 3.12+）。**

**职责定位**：
- ✅ **规则逻辑**：牌型识别、出牌验证、计分计算
- ✅ **AI辅助工具**：合法出牌生成、手牌结构分析
- ✅ **规则变体配置**：参数化游戏规则
- ❌ **游戏状态管理**：Round/Play/Game 对象（→ datongzi 职责）
- ❌ **AI策略实现**：决策算法、博弈推演（→ datongzi/ai 职责）
- ❌ **UI/前端逻辑**：界面、交互、显示（→ datongzi/ui 职责）

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                  datongzi-rules (纯规则引擎)                   │
│                                                               │
│  Layer 4: ai_helpers, variants (辅助层)                       │
│  ┌──────────────────┐  ┌────────────────────────────────┐   │
│  │  PlayGenerator   │  │  HandPatternAnalyzer           │   │
│  │  (出牌生成)       │  │  (手牌结构分析)                 │   │
│  └──────────────────┘  └────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ConfigFactory, VariantValidator (规则变体配置)       │   │
│  └──────────────────────────────────────────────────────┘   │
│                         ↓                                     │
│  Layer 3: scoring (计分层)                                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ScoreComputation (纯计算引擎，不管理状态)            │   │
│  └──────────────────────────────────────────────────────┘   │
│                         ↓                                     │
│  Layer 2: patterns (识别层)                                  │
│  ┌─────────────────┐  ┌─────────────┐  ┌──────────────┐    │
│  │PatternRecognizer│  │PlayValidator│  │PatternFinder │    │
│  │(牌型识别)        │  │(出牌验证)    │  │(牌型提取)     │    │
│  └─────────────────┘  └─────────────┘  └──────────────┘    │
│                         ↓                                     │
│  Layer 1: models (数据层)                                    │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌────────────┐             │
│  │ Card │  │ Deck │  │ Rank │  │ GameConfig │             │
│  │(卡牌)│  │(牌堆)│  │(枚举)│  │(游戏配置)   │             │
│  └──────┘  └──────┘  └──────┘  └────────────┘             │
└─────────────────────────────────────────────────────────────┘
                         ↑
                         │ 依赖 (只能单向)
                         │
              ┌──────────────────────┐
              │      datongzi        │
              │  (游戏引擎层)         │
              │  ┌────────────────┐  │
              │  │ Game, Round    │  │  ← 状态管理
              │  │ Play, Player   │  │
              │  └────────────────┘  │
              │  ┌────────────────┐  │
              │  │ AI Strategy    │  │  ← AI策略
              │  └────────────────┘  │
              │  ┌────────────────┐  │
              │  │ UI Components  │  │  ← 前端界面
              │  └────────────────┘  │
              └──────────────────────┘
```

**关键约束**:
- ✅ `datongzi` → `datongzi-rules` (允许依赖)
- ❌ `datongzi-rules` → `datongzi` (严格禁止)
- ✅ datongzi-rules 内部：上层 → 下层（分层依赖）
- ❌ datongzi-rules 内部：下层 → 上层（禁止反向依赖）

---

## SOLID原则应用

### 1. Single Responsibility Principle (单一职责原则)

**每个类/模块只做一件事，且做好。**

#### ✅ 正确示例

```python
# ✅ PatternRecognizer: 只负责识别牌型
class PatternRecognizer:
    @staticmethod
    def analyze_cards(cards: list[Card]) -> PlayPattern | None:
        """识别给定牌是否为合法牌型"""
        # 只做牌型识别，不做验证、不做生成、不做计分

# ✅ PlayValidator: 只负责验证是否能打
class PlayValidator:
    @staticmethod
    def can_beat_play(cards: list[Card], current: PlayPattern) -> bool:
        """验证是否能压过当前牌"""
        # 只做验证，不做识别、不做生成

# ✅ PlayGenerator: 只负责生成合法出牌
class PlayGenerator:
    @staticmethod
    def generate_beating_plays_with_same_type_or_trump(
        hand: list[Card], current_pattern: PlayPattern
    ) -> list[list[Card]]:
        """生成能打过当前牌的出牌（同型或王牌）"""
        # 只做生成，不做识别、不做验证、不做决策

# ✅ ScoreComputation: 只负责计分计算（纯计算，不管理状态）
class ScoreComputation:
    def create_round_win_event(
        self, player_id: str, round_cards: list[Card], round_number: int
    ) -> ScoringEvent:
        """计算回合基础分（接收上层收集的数据）"""
        # 只做计算，不跟踪回合、不管理状态

# ✅ HandPatternAnalyzer: 只负责手牌结构分析
class HandPatternAnalyzer:
    @staticmethod
    def analyze_patterns(hand: list[Card]) -> HandPatterns:
        """分析手牌结构（非重叠分解）"""
        # 只做结构分析，不做评估、不做决策
```

#### ❌ 违反示例

```python
# ❌ 错误: 一个类做了太多事情（上帝类）
class GameRuleEngine:
    def analyze_cards(self, cards): pass      # 识别牌型
    def can_beat(self, cards, current): pass  # 验证
    def generate_moves(self, hand): pass      # 生成出牌
    def calculate_score(self, pattern): pass  # 计分
    def evaluate_hand(self, hand): pass       # 评估手牌
    def suggest_play(self, hand): pass        # AI建议
    # ❌ 违反SRP - 应该拆分成6个独立的类！

# ❌ 错误: ScoreComputation 管理状态
class ScoreComputation:
    def __init__(self):
        self.round_cards = []  # ❌ 不应该维护状态
        self.current_round = None

    def add_play(self, cards):  # ❌ 不应该跟踪出牌
        self.round_cards.extend(cards)
```

---

### 2. Open/Closed Principle (开放封闭原则)

**对扩展开放，对修改封闭。**

#### ✅ 正确示例：通过配置扩展，不修改代码

```python
# ✅ 通过 GameConfig 参数化规则变体
config = ConfigFactory.create_standard_3deck_3player()
# 或
config = ConfigFactory.create_4deck_4player()
# 或
config = ConfigFactory.create_custom(
    num_decks=2,
    num_players=2,
    must_beat_rule=False  # 新手友好模式：关闭"有牌必打"
)

# 核心代码无需修改，通过配置扩展
engine = ScoreComputation(config)
```

#### ❌ 违反示例：硬编码规则变体

```python
# ❌ 错误: if-else 硬编码规则模式
if GAME_MODE == "standard":
    k_tongzi_bonus = 100
    a_tongzi_bonus = 200
    must_beat_rule = True
elif GAME_MODE == "simple":
    k_tongzi_bonus = 50
    a_tongzi_bonus = 100
    must_beat_rule = False
# ❌ 每增加一个变体都要修改代码
```

---

### 3. Liskov Substitution Principle (里氏替换原则)

**子类对象应该能够替换父类对象且不影响程序正确性。**

在本项目中，我们使用**数据类（dataclass）和静态方法**而非继承，避免LSP问题。

```python
# ✅ 使用 dataclass 和组合，而非继承
@dataclass
class PlayPattern:
    play_type: PlayType
    primary_rank: Rank
    card_count: int
    # 组合而非继承，避免LSP问题
```

---

### 4. Interface Segregation Principle (接口隔离原则)

**客户端不应该依赖它不需要的接口。**

#### ✅ 正确示例：细粒度接口

```python
# ✅ PatternRecognizer: 只提供识别接口
class PatternRecognizer:
    @staticmethod
    def analyze_cards(cards: list[Card]) -> PlayPattern | None:
        pass

# ✅ PlayValidator: 只提供验证接口
class PlayValidator:
    @staticmethod
    def can_beat_play(cards: list[Card], current: PlayPattern) -> bool:
        pass

    @staticmethod
    def is_valid_play(cards: list[Card]) -> bool:
        pass

# 客户端只需要识别 → 只依赖 PatternRecognizer
# 客户端只需要验证 → 只依赖 PlayValidator
```

#### ❌ 违反示例：臃肿接口

```python
# ❌ 错误: 一个接口提供所有功能
class GameRulesInterface:
    def analyze_cards(self): pass
    def can_beat_play(self): pass
    def generate_plays(self): pass
    def calculate_score(self): pass
    def evaluate_hand(self): pass
    # ❌ 客户端可能只需要识别，却被迫依赖整个接口
```

---

### 5. Dependency Inversion Principle (依赖倒置原则)

**高层模块不应该依赖低层模块，两者都应该依赖抽象。**

#### ✅ 正确示例：高层依赖规则库的抽象接口

```python
# datongzi/ai/strategy.py (高层模块)
from datongzi_rules import PlayGenerator, PlayValidator  # ← 依赖抽象接口

class AIStrategy:
    def choose_play(self, hand, current_pattern):
        # 依赖规则库的接口，不重新实现规则
        valid_plays = PlayGenerator.generate_beating_plays_with_same_type_or_trump(
            hand, current_pattern
        )

        # AI 只负责决策逻辑
        return self._evaluate_and_choose(valid_plays)
```

#### ❌ 违反示例：高层重新实现底层逻辑

```python
# ❌ 错误: AI 重新实现规则验证
class AIStrategy:
    def choose_play(self, hand, current_pattern):
        # ❌ 重新实现规则逻辑
        valid_plays = []
        for combo in self._generate_combinations(hand):
            if self._can_beat(combo, current_pattern):  # ❌ 重复实现
                valid_plays.append(combo)

        # 违反 DIP - 应该依赖 PlayGenerator 接口
```

---

## 模块职责边界（2025-01-17 更新）

### Layer 1: models/ (数据模型层)

**职责**：
- ✅ 定义不可变数据结构（Card, Rank, Suit, Deck）
- ✅ 配置定义和验证（GameConfig）
- ✅ 基础数据操作（洗牌、发牌）

**禁止**：
- ❌ 实现业务逻辑（牌型识别、验证）
- ❌ 计分逻辑
- ❌ AI决策

**核心类**：
```python
# Card: 卡牌（花色+点数）
card = Card(Suit.SPADES, Rank.ACE)
card.is_scoring_card  # True（5/10/K）
card.score_value      # 10

# Deck: 牌堆（创建、洗牌、发牌）
deck = Deck.create_standard_deck(num_decks=3)
deck.shuffle()
hand = deck.deal_cards(41)

# GameConfig: 游戏配置（参数化规则变体）
config = ConfigFactory.create_standard_3deck_3player()
```

---

### Layer 2: patterns/ (牌型识别层)

**职责**：
- ✅ 牌型识别（PatternRecognizer）
- ✅ 出牌验证（PlayValidator）
- ✅ 牌型提取（PatternFinder）

**禁止**：
- ❌ 生成AI决策
- ❌ 修改游戏状态
- ❌ 计分逻辑

**核心类**：
```python
# PatternRecognizer: 牌型识别器
pattern = PatternRecognizer.analyze_cards(cards)
# 返回：PlayPattern(play_type, primary_rank, card_count, ...)

# PlayValidator: 出牌验证器
can_beat = PlayValidator.can_beat_play(cards, current_pattern)
is_valid = PlayValidator.is_valid_play(cards)

# PatternFinder: 牌型提取器
bombs = PatternFinder.find_bombs(hand)
tongzi = PatternFinder.find_tongzi(hand)
```

---

### Layer 3: scoring/ (计分引擎层)

**重要**：这是**纯计算引擎**，不管理游戏状态！

**ScoreComputation 职责**：
- ✅ 计算回合基础分（接收上层收集的 round_cards）
- ✅ 计算特殊奖励（接收已识别的 winning_pattern）
- ✅ 计算完成位置奖励
- ✅ 验证分数一致性

**ScoreComputation 禁止**：
- ❌ 判断回合结束（上层职责）
- ❌ 跟踪回合状态（上层职责）
- ❌ 收集回合内所有牌（上层职责）
- ❌ 识别牌型（接收已识别的 PlayPattern）

**职责分工**：
```python
# ✅ 上层（datongzi）负责：
class Round:
    def is_finished(self):
        # 判断回合结束
        return all(player.passed for player in self.other_players)

    def end_round(self):
        # 收集回合数据
        all_cards = [card for play in self.plays for card in play.cards]
        winner = self.plays[-1].player_id
        winning_pattern = PatternRecognizer.analyze_cards(self.plays[-1].cards)

        # 调用计分引擎（只计算）
        engine.create_round_win_event(winner, all_cards, round_number)
        engine.create_special_bonus_events(winner, winning_pattern, round_number, True)

# ✅ 规则库（ScoreComputation）只负责：
class ScoreComputation:
    def create_round_win_event(
        self, player_id: str, round_cards: list[Card], round_number: int
    ) -> ScoringEvent:
        # 纯计算：输入 → 输出，无状态
        base_score = self.calculate_round_base_score(round_cards)
        return ScoringEvent(player_id, BonusType.ROUND_WIN, base_score, ...)
```

**核心类**：
```python
# ScoreComputation: 计分引擎（纯计算）
engine = ScoreComputation(config)

# 回合基础分
event = engine.create_round_win_event(player_id, round_cards, round_number)

# 特殊奖励（筒子/地炸）
events = engine.create_special_bonus_events(
    player_id, winning_pattern, round_number, is_round_winning_play=True
)

# 完成位置奖励
events = engine.create_finish_bonus_events(["p1", "p2", "p3"])

# 计算总分
total = engine.calculate_total_score_for_player(player_id)
```

---

### Layer 4: ai_helpers/ (AI辅助工具层)（2025-01-17 重构）

**重要变更**：已删除 `HandEvaluator` 和 `PatternSuggester`，只保留核心工具。

**PlayGenerator 职责**：
- ✅ **唯一应该生成所有合法出牌的地方**
- ✅ 提供3个API：
  - `generate_beating_plays_with_same_type_or_trump()` - 高效（推荐）
  - `count_all_plays()` - 统计用
  - `generate_all_plays()` - 完整枚举（⚠️ 可能爆炸）

**HandPatternAnalyzer 职责**：
- ✅ 手牌结构分析（非重叠分解）
- ✅ 为AI提供资源视图（炸弹/筒子/三张/对子/散牌数量）
- ✅ 优先级：Dizha > Tongzi > Bomb > Airplane > Triple > ConsecPairs > Pair > Single

**禁止**：
- ❌ 实现复杂AI策略（→ datongzi/ai 职责）
- ❌ 手牌强度评估（AI自己实现）
- ❌ 出牌建议（AI自己决策）
- ❌ CV识别纠错（前端职责）

**核心类**：
```python
# PlayGenerator: 出牌生成器
# ✅ 推荐：生成能打过的牌（同型或王牌）
valid_plays = PlayGenerator.generate_beating_plays_with_same_type_or_trump(
    hand, current_pattern
)

# ✅ 统计可能出牌数
count = PlayGenerator.count_all_plays(hand)

# HandPatternAnalyzer: 手牌结构分析器
patterns = HandPatternAnalyzer.analyze_patterns(hand)
# 返回：HandPatterns(dizha, tongzi, bombs, triples, pairs, singles, ...)
```

---

### variants/ (规则变体层)

**职责**：
- ✅ 预定义规则变体（ConfigFactory）
- ✅ 配置验证（VariantValidator）

**禁止**：
- ❌ 修改核心规则逻辑

**核心类**：
```python
# ConfigFactory: 配置工厂
config = ConfigFactory.create_standard_3deck_3player()
config = ConfigFactory.create_4deck_4player()
config = ConfigFactory.create_beginner_friendly()

# VariantValidator: 配置验证器
is_valid, warnings = VariantValidator.validate_config(config)
```

---

## 依赖关系

### 允许的依赖

```
datongzi (游戏引擎)
    ↓
datongzi-rules (规则库)
    ↓
Layer 4: ai_helpers, variants
    ↓
Layer 3: scoring
    ↓
Layer 2: patterns
    ↓
Layer 1: models
```

**规则**：
- ✅ 上层 → 下层（分层依赖）
- ✅ 同层互相依赖（平级依赖）
- ✅ 所有层 → models（基础数据层）

### 禁止的依赖

- ❌ 下层 → 上层（反向依赖）
- ❌ datongzi-rules → datongzi（循环依赖）
- ❌ 跨层依赖（必须通过中间层）

---

## 扩展指南

### 场景1: 添加新牌型

**步骤**：
1. 在 `PlayType` 枚举添加新类型
2. 在 `PatternRecognizer.analyze_cards()` 添加识别逻辑
3. 在 `PlayFormationValidator` 添加验证方法
4. 在 `PlayValidator.can_beat_play()` 添加对抗规则
5. 在 `ScoreComputation` 添加计分规则（如果有奖励）
6. 在 `PlayGenerator` 添加生成逻辑（如果需要）
7. 添加单元测试

**示例**：添加"四带二"牌型
```python
# 1. 枚举
class PlayType(IntEnum):
    QUAD_WITH_TWO = 11  # 新增

# 2. 识别
class PatternRecognizer:
    @staticmethod
    def analyze_cards(cards: list[Card]) -> PlayPattern | None:
        # ... 现有逻辑
        if len(cards) == 6:
            pattern = PatternRecognizer._check_quad_with_two(cards)
            if pattern:
                return pattern

# 3. 验证 & 4. 对抗规则 & 5. 计分 & 6. 生成 ...
# 7. 测试
def test_quad_with_two():
    cards = [Card(Suit.SPADES, Rank.ACE)] * 4 + [Card(Suit.HEARTS, Rank.FIVE)] * 2
    pattern = PatternRecognizer.analyze_cards(cards)
    assert pattern.play_type == PlayType.QUAD_WITH_TWO
```

---

### 场景2: 添加新规则变体

**步骤**：
1. 在 `GameConfig` 添加新配置字段
2. 在 `ConfigFactory` 添加新工厂方法
3. 在相关模块读取配置
4. 添加单元测试

**示例**：添加"允许炸弹拆分"规则
```python
# 1. 配置字段
@dataclass
class GameConfig:
    # ... 现有字段
    allow_bomb_split: bool = False  # 新增

# 2. 工厂方法
class ConfigFactory:
    @staticmethod
    def create_flexible_mode() -> GameConfig:
        return GameConfig(
            num_decks=3,
            num_players=3,
            allow_bomb_split=True  # 启用新规则
        )

# 3. 使用配置
class PlayGenerator:
    @staticmethod
    def generate_all_plays(hand: list[Card], config: GameConfig) -> list[list[Card]]:
        if config.allow_bomb_split:
            # 允许炸弹拆分逻辑
            pass

# 4. 测试
def test_flexible_mode():
    config = ConfigFactory.create_flexible_mode()
    assert config.allow_bomb_split == True
```

---

## 反模式警告

### ❌ 反模式1: 在高层重新实现规则

```python
# ❌ 错误: 在 datongzi/ai 中重新实现规则验证
class AI:
    def _can_beat(self, cards, current_play):
        # 自己实现验证逻辑
        if len(cards) == len(current_play.cards):
            if all(c.rank > current_play.primary_rank for c in cards):
                return True
        # ❌ 重复实现 PlayValidator 的逻辑

# ✅ 正确: 依赖规则库
from datongzi_rules import PlayValidator

class AI:
    def can_beat(self, cards, current_play):
        return PlayValidator.can_beat_play(cards, current_play)
```

---

### ❌ 反模式2: 在规则库实现AI策略

```python
# ❌ 错误: 在规则库实现复杂AI决策
class HandEvaluator:
    def choose_best_play(self, hand, game_state):
        # 多步博弈推演
        # 评估对手手牌
        # 决策最优出牌
        # ❌ 这是 AI 策略，不是规则逻辑

# ✅ 正确: 规则库只提供工具，AI在上层实现
# datongzi/ai/strategy.py
class AIStrategy:
    def choose_best_play(self, valid_plays, hand, game_state):
        # AI 决策逻辑（基于 PlayGenerator 提供的 valid_plays）
        for play in valid_plays:
            score = self._evaluate_play(play, hand, game_state)
            # AI 自己的评估逻辑
```

---

### ❌ 反模式3: 在规则库管理游戏状态

```python
# ❌ 错误: 在规则库创建 Round/Game 类
class Round:
    def __init__(self):
        self.plays = []
        self.current_player = None
        # ❌ 状态管理不是规则库职责

# ✅ 正确: 状态管理在上层
# datongzi/models/round.py
class Round:
    def __init__(self, players):
        self.plays = []
        self.scoring_engine = ScoreComputation(config)  # 只使用计分引擎

    def end_round(self):
        # 收集数据，调用规则库计算
        all_cards = [card for play in self.plays for card in play.cards]
        self.scoring_engine.create_round_win_event(winner, all_cards, round_num)
```

---

### ❌ 反模式4: ScoreComputation 跟踪回合状态

```python
# ❌ 错误: 计分引擎维护状态
class ScoreComputation:
    def __init__(self):
        self.round_cards = []  # ❌ 不应该维护状态
        self.current_round = None

    def add_play(self, cards):  # ❌ 不应该跟踪出牌
        self.round_cards.extend(cards)

    def end_round(self):  # ❌ 不应该判断回合结束
        score = sum(c.score_value for c in self.round_cards)

# ✅ 正确: 纯计算，上层传入数据
class ScoreComputation:
    def create_round_win_event(
        self, player_id: str, round_cards: list[Card], round_number: int
    ) -> ScoringEvent:
        # 纯计算：输入 → 输出，无状态
        score = sum(c.score_value for c in round_cards if c.is_scoring_card)
        return ScoringEvent(player_id, BonusType.ROUND_WIN, score, ...)
```

---

### ❌ 反模式5: 硬编码规则变体

```python
# ❌ 错误: if-else 硬编码
if GAME_MODE == "standard":
    k_tongzi_bonus = 100
elif GAME_MODE == "high_stakes":
    k_tongzi_bonus = 200
# ❌ 每增加一个变体都要修改代码

# ✅ 正确: 通过配置扩展
config = ConfigFactory.create_standard_3deck_3player()  # k_tongzi_bonus=100
# 或
config = ConfigFactory.create_high_stakes()  # k_tongzi_bonus=200
# 无需修改代码
```

---

## 重要更新

### 2025-01-17 重构

**1. 删除模块**：
- ❌ `HandEvaluator` - 手牌评估应在AI层实现
- ❌ `PatternSuggester` - CV纠错应在前端实现

**2. 重命名**：
- `ScoringEngine` → `ScoreComputation` - 强调纯计算职责
- `engine.py` → `computation.py` - 文件名与类名一致

**3. 职责澄清**：
- `ScoreComputation` 是纯计算引擎，不管理状态
- 上层负责收集回合数据、判断回合结束
- `PlayGenerator` 是唯一合法出牌生成来源
- `HandPatternAnalyzer` 只做结构分析，不做评估

**4. 架构图更新**：
- 明确分层依赖关系
- 明确上层（datongzi）职责
- 明确职责边界

**5. 文档更新**：
- README.md: 完整API文档和使用示例
- CLAUDE.md: 架构原则和职责边界
- ARCHITECTURE.md: SOLID原则和反模式警告

---

## 总结

**datongzi-rules 核心原则**：
1. **纯规则引擎**：只做规则逻辑，不做状态管理
2. **SOLID原则**：单一职责、开放封闭、依赖倒置
3. **分层架构**：models → patterns → scoring → ai_helpers
4. **职责边界清晰**：规则库 ≠ 游戏引擎 ≠ AI策略

**上层（datongzi）职责**：
- 游戏状态管理（Game, Round, Play, Player）
- AI策略实现（决策算法、博弈推演）
- UI/前端逻辑（界面、交互、显示）

**依赖方向**：
```
datongzi (状态+AI+UI) → datongzi-rules (纯规则)
```

**重要提醒**：
- ✅ 所有规则逻辑只在规则库实现
- ❌ 严禁在上层重复实现规则逻辑
- ✅ 规则库提供工具，上层组合使用
- ❌ 规则库不做AI决策、不管状态
