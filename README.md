# Da Tong Zi Rules Engine

零依赖的打筒子游戏规则引擎库，作为独立子模块供 `datongzi` 游戏引擎使用。

## 项目定位

**这是一个纯规则引擎库**，只负责游戏规则逻辑，不包含游戏状态管理、UI、AI策略等上层功能。

**职责边界**：
- ✅ 牌型识别、出牌验证、计分逻辑
- ✅ 生成合法出牌、手牌结构分析
- ✅ 规则变体配置
- ❌ 游戏状态管理（Round/Play/Game 对象）
- ❌ AI 策略实现（应在上层 `datongzi/ai` 实现）
- ❌ UI/前端逻辑

**依赖方向**：
```
datongzi (游戏引擎) → datongzi-rules (规则库)
```

## 特性

- ✅ **零依赖**：仅使用 Python 3.12+ 标准库
- ✅ **高性能**：牌型识别 ~150K ops/sec，游戏设置 ~5K games/sec
- ✅ **完整规则**：支持所有打筒子牌型和规则
  - 10 种牌型：单牌、对子、连对、三张、飞机、炸弹、筒子、地炸等
  - 回合制计分：回合基础分、特殊奖励、完成位置奖励
- ✅ **类型安全**：完整类型提示，支持静态类型检查
- ✅ **测试驱动**：270+ 测试用例，覆盖率 88.66%

## 安装

```bash
# 从源码安装
pip install -e .

# 开发模式（包含测试依赖）
pip install -e ".[dev]"
```

## 核心 API 文档

### 1. 数据模型（models）

#### Card - 卡牌类

```python
from datongzi_rules import Card, Rank, Suit

# 创建卡牌
card = Card(Suit.SPADES, Rank.ACE)

# 属性
card.suit        # Suit.SPADES
card.rank        # Rank.ACE
card.is_scoring_card  # True（5/10/K 为计分牌）
card.score_value      # 10（5=5分，10=10分，K=10分）

# 比较
card1 > card2    # 按点数比较
card1 == card2   # 花色和点数都相同
```

**枚举定义**：
```python
class Suit(Enum):
    SPADES = 4    # 黑桃（最大）
    HEARTS = 3    # 红桃
    CLUBS = 2     # 梅花
    DIAMONDS = 1  # 方块（最小）

class Rank(Enum):
    TWO = 15      # 2（最大）
    ACE = 14      # A
    KING = 13     # K
    QUEEN = 12    # Q
    JACK = 11     # J
    TEN = 10      # 10
    NINE = 9      # 9
    EIGHT = 8     # 8
    SEVEN = 7     # 7
    SIX = 6       # 6
    FIVE = 5      # 5
    FOUR = 4      # 4
    THREE = 3     # 3（最小）
```

#### Deck - 牌堆类

```python
from datongzi_rules import Deck

# 创建标准牌堆
deck = Deck.create_standard_deck(num_decks=3)  # 3副牌 = 132张

# 洗牌
deck.shuffle()

# 发牌
hand1 = deck.deal_cards(41)  # 发41张
hand2 = deck.deal_cards(41)

# 属性
len(deck.cards)  # 剩余牌数
```

#### GameConfig - 游戏配置

```python
from datongzi_rules import GameConfig, ConfigFactory

# 使用预设配置
config = ConfigFactory.create_standard_3deck_3player()

# 配置属性
config.num_decks           # 3（牌副数）
config.num_players         # 3（玩家数）
config.cards_per_player    # 41（每人牌数）
config.cards_dealt_aside   # 9（底牌数）
config.finish_bonus        # [100, -40, -60]（上游/二游/三游奖励）
config.k_tongzi_bonus      # 100（K筒子奖励）
config.a_tongzi_bonus      # 200（A筒子奖励）
config.two_tongzi_bonus    # 300（2筒子奖励）
config.dizha_bonus         # 400（地炸奖励）
config.must_beat_rule      # True（有牌必打规则）

# 自定义配置
config = ConfigFactory.create_custom(
    num_decks=2,
    num_players=2,
    must_beat_rule=False
)
```

**预设配置**：
- `create_standard_3deck_3player()` - 标准 3 副牌 3 人
- `create_4deck_4player()` - 4 副牌 4 人
- `create_2player()` - 2 人对战
- `create_quick_game()` - 快速游戏（2 副牌）
- `create_high_stakes()` - 高额赌注（奖励翻倍）
- `create_beginner_friendly()` - 新手友好（无有牌必打）

---

### 2. 牌型识别（patterns）

#### PatternRecognizer - 牌型识别器

```python
from datongzi_rules import PatternRecognizer

cards = [Card(Suit.SPADES, Rank.ACE)] * 3

# 识别牌型
pattern = PatternRecognizer.analyze_cards(cards)

# 返回 PlayPattern 对象
pattern.play_type       # PlayType.TRIPLE
pattern.primary_rank    # Rank.ACE
pattern.card_count      # 3
pattern.is_tongzi       # False
pattern.is_dizha        # False
```

**PlayType 枚举**：
```python
class PlayType(IntEnum):
    SINGLE = 1               # 单牌
    PAIR = 2                 # 对子
    CONSECUTIVE_PAIRS = 3    # 连对（2连对及以上）
    TRIPLE = 4               # 三张
    TRIPLE_WITH_TWO = 5      # 三带二
    AIRPLANE = 6             # 飞机（连续三张）
    AIRPLANE_WITH_WINGS = 7  # 飞机带翅膀
    BOMB = 8                 # 炸弹（4张及以上）
    TONGZI = 9               # 筒子（同花三张）
    DIZHA = 10               # 地炸（8张同数字）
```

#### PlayValidator - 出牌验证器

```python
from datongzi_rules import PlayValidator

# 验证是否可以打过
low_pair = [Card(Suit.SPADES, Rank.FIVE)] * 2
high_pair = [Card(Suit.HEARTS, Rank.KING)] * 2

current_pattern = PatternRecognizer.analyze_cards(low_pair)
can_beat = PlayValidator.can_beat_play(high_pair, current_pattern)
# True（K对 > 5对）

# 验证是否为合法牌型
is_valid = PlayValidator.is_valid_play(cards)
```

**打牌规则**：
1. **同牌型打法**：同类型且点数更大
   - 单牌 > 单牌，对子 > 对子，三张 > 三张
   - 连对必须长度相同
   - 飞机必须长度相同

2. **王牌打法**：地炸 > 筒子 > 炸弹
   - 炸弹可以打任何普通牌型（单/对/三张/连对/飞机）
   - 筒子可以打炸弹和普通牌型
   - 地炸可以打所有牌型
   - 炸弹之间：张数多 > 张数少，张数相同比点数
   - 筒子之间：先比点数，再比花色

3. **不能打过的情况**：
   - 牌型不同且不是王牌
   - 点数/张数/长度不够

---

### 3. 出牌生成（ai_helpers）

#### PlayGenerator - 出牌生成器

**核心API**（推荐使用）：

```python
from datongzi_rules import PlayGenerator

# ✅ 生成能打过的牌（同型或王牌，高效）
valid_plays = PlayGenerator.generate_beating_plays_with_same_type_or_trump(
    hand, current_pattern
)
# 返回：5-20 个有效出牌（只生成同型更大的牌或王牌）
# 策略：不破坏牌型，只用同类型或王牌打过

# ✅ 统计可能出牌数（高效，仅返回数量）
count = PlayGenerator.count_all_plays(hand)
# 返回：整数（用于评估手牌灵活性）

# ⚠️ 生成所有可能出牌（可能组合爆炸，仅测试/调试用）
all_plays = PlayGenerator.generate_all_plays(hand, max_combinations=1000)
# 返回：所有可能的合法出牌（13张牌可能500+组合）
# 警告：超过阈值会抛出异常
```

**使用场景**：
```python
# AI 决策示例
if current_pattern is None:
    # 开局出牌 - AI 自行决策策略
    play = ai_strategy.choose_opening_play(hand)
else:
    # 必须打过当前牌
    valid_plays = PlayGenerator.generate_beating_plays_with_same_type_or_trump(
        hand, current_pattern
    )

    if not valid_plays:
        return None  # 过牌

    # AI 从 valid_plays 中选择最优出牌
    play = ai_strategy.choose_best_play(valid_plays, hand, game_state)
```

#### HandPatternAnalyzer - 手牌结构分析器

```python
from datongzi_rules import HandPatternAnalyzer

# 分析手牌结构（非重叠分解）
patterns = HandPatternAnalyzer.analyze_patterns(hand)

# HandPatterns 数据类
patterns.dizha                  # list[list[Card]] - 地炸
patterns.tongzi                 # list[list[Card]] - 筒子
patterns.bombs                  # list[list[Card]] - 炸弹
patterns.airplane_chains        # list[list[Card]] - 飞机链
patterns.triples                # list[list[Card]] - 三张
patterns.consecutive_pair_chains # list[list[Card]] - 连对链
patterns.pairs                  # list[list[Card]] - 对子
patterns.singles                # list[Card] - 单张

# 元数据
patterns.trump_count            # int - 王牌总数（地炸+筒子+炸弹）
patterns.has_control_cards      # bool - 是否有控场牌

# 优先级：Dizha > Tongzi > Bomb > Airplane > Triple > ConsecPairs > Pair > Single
```

**使用场景**：
```python
# AI 决策基础
patterns = HandPatternAnalyzer.analyze_patterns(hand)

if patterns.dizha:
    # 我有地炸，可以控场
    strategy = "aggressive"
elif patterns.bombs:
    # 我有炸弹，强势打法
    strategy = "moderate"
else:
    # 普通牌型，保守打法
    strategy = "conservative"

# 快速获取资源信息
print(f"王牌: {patterns.trump_count}")
print(f"三张: {len(patterns.triples)}")
print(f"散牌: {len(patterns.singles)}")
```

---

### 4. 计分系统（scoring）

#### ScoreComputation - 计分引擎

**重要**：这是一个纯计算引擎，不管理游戏状态。上层游戏引擎负责：
1. 判断回合结束
2. 收集回合内所有牌
3. 识别回合胜利者和牌型
4. 调用计分接口

```python
from datongzi_rules import ScoreComputation, BonusType

# 创建计分引擎
config = ConfigFactory.create_standard_3deck_3player()
engine = ScoreComputation(config)

# 1. 回合基础计分（回合结束时调用）
event = engine.create_round_win_event(
    player_id="player1",
    round_cards=all_cards_in_round,  # 回合内所有牌（上层收集）
    round_number=1
)
# 返回：ScoringEvent（包含5/10/K的总分）

# 2. 特殊奖励（筒子/地炸，回合结束时调用）
events = engine.create_special_bonus_events(
    player_id="player1",
    winning_pattern=pattern,           # 回合胜利牌型（上层识别）
    round_number=1,
    is_round_winning_play=True         # ⚠️ 必须是回合胜利出牌才有奖励
)
# 返回：list[ScoringEvent]（筒子/地炸奖励，可能为空）

# 3. 完成位置奖励（游戏结束时调用）
events = engine.create_finish_bonus_events(
    player_ids_in_finish_order=["player1", "player2", "player3"]  # 完成顺序
)
# 返回：list[ScoringEvent]（上游+100，二游-40，三游-60）

# 4. 计算玩家总分
total = engine.calculate_total_score_for_player("player1")

# 5. 验证分数一致性（调试用）
is_valid = engine.validate_scores({
    "player1": 120,
    "player2": -40,
    "player3": -60
})
```

**ScoringEvent 数据类**：
```python
@dataclass
class ScoringEvent:
    player_id: str           # 玩家ID
    bonus_type: BonusType    # 奖励类型
    points: int              # 分数
    reason: str              # 原因描述
    round_number: int | None # 回合号（可选）
    cards_involved: list[str] # 涉及的牌（可选）
```

**BonusType 枚举**：
```python
class BonusType(Enum):
    ROUND_WIN = "round_win"         # 回合获胜
    K_TONGZI = "k_tongzi"           # K筒子（+100）
    A_TONGZI = "a_tongzi"           # A筒子（+200）
    TWO_TONGZI = "two_tongzi"       # 2筒子（+300）
    DIZHA = "dizha"                 # 地炸（+400）
    FINISH_FIRST = "finish_first"   # 上游（+100）
    FINISH_SECOND = "finish_second" # 二游（-40）
    FINISH_THIRD = "finish_third"   # 三游（-60）
```

**关键规则**：
1. **回合制计分**：只有回合最后出牌者得分，中间出的牌不得分
2. **特殊奖励规则**：
   - 只有回合胜利出牌才有筒子/地炸奖励
   - 如果 A 出 K 筒子，B 用 A 筒子打过并赢得回合，只有 B 得 200 分，A 得 0 分
   - `is_round_winning_play=False` 时不给奖励

---

### 5. 规则变体（variants）

#### VariantValidator - 配置验证器

```python
from datongzi_rules import VariantValidator

# 验证配置合法性
is_valid, warnings = VariantValidator.validate_config(config)

if not is_valid:
    print("配置非法！")

for warning in warnings:
    print(f"警告: {warning}")
```

**验证规则**：
- 牌数必须足够分配
- 玩家数必须在 2-4 人
- 完成奖励必须和为零（零和游戏）
- 奖励分数合理性检查

---

## 完整使用示例

### 示例 1: 基础牌型识别和验证

```python
from datongzi_rules import Card, Rank, Suit, PatternRecognizer, PlayValidator

# 创建牌
cards = [
    Card(Suit.SPADES, Rank.ACE),
    Card(Suit.HEARTS, Rank.ACE),
    Card(Suit.CLUBS, Rank.ACE),
]

# 识别牌型
pattern = PatternRecognizer.analyze_cards(cards)
print(f"牌型: {pattern.play_type.name}")      # TRIPLE
print(f"点数: {pattern.primary_rank.name}")   # ACE
print(f"牌数: {pattern.card_count}")          # 3

# 验证出牌
opponent_cards = [Card(Suit.SPADES, Rank.KING)] * 3
current_pattern = PatternRecognizer.analyze_cards(opponent_cards)

can_beat = PlayValidator.can_beat_play(cards, current_pattern)
print(f"能否打过: {can_beat}")  # True（A三张 > K三张）
```

### 示例 2: 游戏设置和发牌

```python
from datongzi_rules import Deck, ConfigFactory

# 创建标准配置
config = ConfigFactory.create_standard_3deck_3player()

# 创建并洗牌
deck = Deck.create_standard_deck(num_decks=config.num_decks)
deck.shuffle()

# 发牌给玩家
player_hands = {}
for i in range(config.num_players):
    player_id = f"player{i+1}"
    hand = deck.deal_cards(config.cards_per_player)
    player_hands[player_id] = hand

# 发底牌
aside_cards = deck.deal_cards(config.cards_dealt_aside)

print(f"玩家1: {len(player_hands['player1'])} 张")
print(f"玩家2: {len(player_hands['player2'])} 张")
print(f"玩家3: {len(player_hands['player3'])} 张")
print(f"底牌: {len(aside_cards)} 张")
```

### 示例 3: AI 出牌决策

```python
from datongzi_rules import PlayGenerator, HandPatternAnalyzer, PatternRecognizer

def ai_decide_play(hand, current_pattern):
    """简单 AI 出牌逻辑"""

    if current_pattern is None:
        # 开局出牌 - 出最小单张
        smallest = min(hand, key=lambda c: c.rank.value)
        return [smallest]

    # 生成能打过的牌
    valid_plays = PlayGenerator.generate_beating_plays_with_same_type_or_trump(
        hand, current_pattern
    )

    if not valid_plays:
        return None  # 过牌

    # 简单策略：选第一个有效出牌
    return valid_plays[0]

# 使用示例
hand = [...]  # 玩家手牌
current_pattern = None  # 当前牌型

play = ai_decide_play(hand, current_pattern)
if play:
    pattern = PatternRecognizer.analyze_cards(play)
    print(f"出牌: {pattern.play_type.name}")
else:
    print("过牌")
```

### 示例 4: 手牌结构分析

```python
from datongzi_rules import HandPatternAnalyzer

# 分析手牌
patterns = HandPatternAnalyzer.analyze_patterns(hand)

# 显示手牌资源
print(f"王牌总数: {patterns.trump_count}")
print(f"地炸: {len(patterns.dizha)}")
print(f"筒子: {len(patterns.tongzi)}")
print(f"炸弹: {len(patterns.bombs)}")
print(f"三张: {len(patterns.triples)}")
print(f"对子: {len(patterns.pairs)}")
print(f"散牌: {len(patterns.singles)}")

# AI 决策参考
if patterns.has_control_cards:
    print("有控场牌，可以主动出击")
else:
    print("无控场牌，保守跟牌")
```

### 示例 5: 回合计分

```python
from datongzi_rules import ScoreComputation, ConfigFactory, PatternRecognizer

# 初始化计分引擎
config = ConfigFactory.create_standard_3deck_3player()
engine = ScoreComputation(config)

# 回合结束，玩家1 获胜
round_cards = [...]  # 回合内所有出过的牌（上层收集）
winning_play = [...]  # 玩家1 的最后出牌
winning_pattern = PatternRecognizer.analyze_cards(winning_play)

# 1. 基础分（5/10/K）
base_event = engine.create_round_win_event(
    player_id="player1",
    round_cards=round_cards,
    round_number=1
)

# 2. 特殊奖励（如果是筒子/地炸）
bonus_events = engine.create_special_bonus_events(
    player_id="player1",
    winning_pattern=winning_pattern,
    round_number=1,
    is_round_winning_play=True  # 回合胜利出牌
)

# 查看得分
total_score = engine.calculate_total_score_for_player("player1")
print(f"玩家1总分: {total_score}")
```

---

## 性能基准

在 M1 MacBook Air 上的测试结果：

| 操作 | 性能 |
|-----|------|
| 牌型识别 | ~150K ops/sec（0.006ms/op）|
| 游戏设置 | ~5K games/sec（0.19ms/op）|
| 出牌生成（小手牌5张）| 0.02ms/op |
| 出牌生成（满手牌41张）| 6.38ms/op |
| 计分计算 | ~140K ops/sec（0.007ms/op）|

运行基准测试：
```bash
python run.py benchmark
```

---

## 开发

### 开发脚本

```bash
# 运行所有测试（含覆盖率）
python run.py test

# 仅运行单元测试
python run.py unit

# 仅运行集成测试
python run.py integration

# 运行性能基准测试
python run.py benchmark

# 运行所有示例
python run.py examples

# 清理缓存
python run.py clean
```

### 测试

- **单元测试**：258 个测试，覆盖所有核心模块
- **集成测试**：12 个测试，覆盖完整游戏流程
- **覆盖率**：88.66%

```bash
# 运行所有测试
pytest tests/ -v

# 带覆盖率报告
pytest tests/ -v --cov=src/datongzi_rules --cov-report=term-missing
```

---

## 项目结构

```
datongzi-rules/
├── src/
│   └── datongzi_rules/
│       ├── models/          # 数据模型
│       │   ├── card.py      # Card, Rank, Suit, Deck
│       │   └── config.py    # GameConfig
│       ├── patterns/        # 牌型识别
│       │   ├── recognizer.py # PatternRecognizer, PlayPattern
│       │   ├── validators.py # PlayValidator
│       │   └── finders.py    # PatternFinder
│       ├── scoring/         # 计分系统
│       │   └── computation.py # ScoreComputation
│       ├── ai_helpers/      # AI 辅助
│       │   ├── play_generator.py        # PlayGenerator
│       │   └── hand_pattern_analyzer.py # HandPatternAnalyzer
│       ├── variants/        # 规则变体
│       │   └── config_factory.py # ConfigFactory, VariantValidator
│       └── __init__.py
├── tests/
│   ├── unit/              # 单元测试
│   ├── integration/       # 集成测试
│   └── benchmark/         # 性能测试
├── examples/              # 示例代码
│   ├── basic_usage.py
│   ├── complete_game_simulation.py
│   └── ai_player_demo.py
└── README.md
```

---

## 设计原则

1. **零依赖**：仅使用 Python 标准库
2. **高性能**：优化关键路径
3. **类型安全**：完整类型提示
4. **测试驱动**：高测试覆盖率
5. **职责单一**：只做规则引擎，不做状态管理

---

## 常见问题

### Q: 为什么没有 Game/Round/Play 等状态管理类？

A: 这是一个**纯规则引擎库**，只提供规则计算接口。游戏状态管理应该在上层 `datongzi` 游戏引擎中实现。

### Q: 为什么没有 AI 策略实现？

A: 规则库只提供 AI 需要的**基础工具**（`PlayGenerator`, `HandPatternAnalyzer`），具体策略应该在上层 `datongzi/ai` 中实现。

### Q: 如何判断回合结束？

A: 规则库不管理回合状态。上层游戏引擎负责：
```python
class Round:
    def is_finished(self):
        # 其他玩家都 pass 或无法打过
        return all(player.passed for player in self.other_players)
```

### Q: ScoreComputation 为什么需要传入 round_cards？

A: 因为计分引擎是纯计算，不跟踪回合状态。上层需要收集回合内所有牌后传入。

---

## 许可证

MIT License
