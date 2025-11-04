# Da Tong Zi Rules Engine

零依赖的打筒子游戏规则引擎库。

## 特性

- ✅ **零依赖**：仅使用 Python 3.12+ 标准库
- ✅ **高性能**：比 pydantic + structlog 实现快 18-25%
  - 牌型识别：~150K ops/sec
  - 游戏设置：~5K games/sec
  - 手牌评估：<1ms
- ✅ **完整规则**：支持所有打筒子牌型和规则
  - 10 种牌型：单牌、对子、三张、炸弹、筒子、地炸等
  - 8 种奖励类型：筒子奖励、地炸奖励、完成位置奖励等
- ✅ **AI 友好**：提供出牌生成、手牌评估等辅助接口
- ✅ **CV 纠错**：基于规则约束的识别纠错算法
- ✅ **规则变体**：支持 7 种预配置游戏变体
  - 标准 3 副牌 3 人
  - 4 副牌 4 人
  - 2 人对战
  - 快速游戏
  - 高额赌注
  - 新手友好
  - 自定义配置

## 安装

```bash
# 从源码安装
pip install -e .

# 开发模式（包含测试依赖）
pip install -e ".[dev]"
```

## 快速开始

### 基础用法

```python
from datongzi_rules import Card, Rank, Suit, PatternRecognizer

# 创建牌
cards = [
    Card(Suit.SPADES, Rank.ACE),
    Card(Suit.HEARTS, Rank.ACE),
    Card(Suit.CLUBS, Rank.ACE),
]

# 识别牌型
pattern = PatternRecognizer.analyze_cards(cards)
print(f"Pattern: {pattern.play_type.name}")  # TRIPLE
print(f"Rank: {pattern.primary_rank.name}")  # ACE
```

### 出牌验证

```python
from datongzi_rules import PlayValidator

# 创建两组牌
low_pair = [Card(Suit.SPADES, Rank.FIVE), Card(Suit.HEARTS, Rank.FIVE)]
high_pair = [Card(Suit.SPADES, Rank.KING), Card(Suit.HEARTS, Rank.KING)]

# 识别当前牌型
current = PatternRecognizer.analyze_cards(low_pair)

# 验证是否可以打出
can_beat = PlayValidator.can_beat_play(high_pair, current)
print(f"Can beat: {can_beat}")  # True
```

### 完整游戏设置

```python
from datongzi_rules import Deck, ConfigFactory

# 创建标准配置
config = ConfigFactory.create_standard_3deck_3player()

# 创建并洗牌
deck = Deck.create_standard_deck(num_decks=config.num_decks)
deck.shuffle()

# 发牌
hands = []
for _ in range(config.num_players):
    hand = deck.deal_cards(config.cards_per_player)
    hands.append(hand)
```

### AI 辅助功能

```python
from datongzi_rules import PlayGenerator, HandEvaluator

# 生成所有合法出牌
all_plays = PlayGenerator.generate_all_plays(hand)

# 评估手牌强度
strength = HandEvaluator.evaluate_hand(hand)

# 建议最佳出牌
best_play = HandEvaluator.suggest_best_play(hand, current_pattern)
```

## 示例

项目包含多个完整示例，位于 `examples/` 目录：

1. **basic_usage.py** - 基础用法示例
   - 卡牌创建和属性
   - 牌型识别
   - 出牌验证
   - 牌堆操作
   - 游戏变体

2. **complete_game_simulation.py** - 完整游戏模拟
   - 游戏设置流程
   - 发牌和洗牌
   - 回合出牌
   - 计分系统

3. **ai_player_demo.py** - AI 玩家演示
   - AI 决策逻辑
   - 多轮对战
   - 完整计分

运行示例：

```bash
python examples/basic_usage.py
python examples/complete_game_simulation.py
python examples/ai_player_demo.py
```

## 核心 API

### 模型（models）

- **Card** - 卡牌类
  - `suit: Suit` - 花色
  - `rank: Rank` - 点数
  - `is_scoring_card` - 是否为计分牌（5/10/K）
  - `point_value` - 分值

- **Deck** - 牌堆类
  - `create_standard_deck(num_decks)` - 创建标准牌堆
  - `shuffle()` - 洗牌
  - `deal_cards(count)` - 发牌

- **GameConfig** - 游戏配置
  - `num_decks` - 牌副数
  - `num_players` - 玩家数
  - `cards_per_player` - 每人牌数
  - `finish_bonus` - 完成位置奖励
  - `k_tongzi_bonus/a_tongzi_bonus/two_tongzi_bonus` - 筒子奖励
  - `dizha_bonus` - 地炸奖励
  - `must_beat_rule` - 有牌必打规则

### 牌型识别（patterns）

- **PatternRecognizer** - 牌型识别器
  - `analyze_cards(cards) -> PlayPattern` - 识别牌型

- **PlayValidator** - 出牌验证器
  - `can_beat_play(cards, current_pattern) -> bool` - 验证是否可以打出
  - `is_valid_play(cards) -> bool` - 验证是否为合法牌型

- **PlayType** - 牌型枚举
  - `SINGLE` - 单牌
  - `PAIR` - 对子
  - `TRIPLE` - 三张
  - `BOMB` - 炸弹（4 张）
  - `TONGZI` - 筒子（同花三张）
  - `DIZHA` - 地炸（5 张及以上）
  - `STRAIGHT`, `DOUBLE_STRAIGHT`, `TRIPLE_STRAIGHT` - 顺子类型

- **PlayPattern** - 牌型模式
  - `play_type: PlayType` - 牌型类型
  - `primary_rank: Rank` - 主要点数
  - `card_count: int` - 牌数
  - `is_tongzi: bool` - 是否为筒子
  - `is_dizha: bool` - 是否为地炸

### 计分（scoring）

- **ScoringEngine** - 计分引擎
  - `create_round_win_event(player_id, round_cards, round_number)` - 创建回合获胜事件
  - `create_special_bonus_events(player_id, pattern, round_number)` - 创建特殊奖励事件
  - `create_finish_bonus_events(finish_order)` - 创建完成位置奖励事件
  - `calculate_total_score_for_player(player_id)` - 计算玩家总分
  - `validate_scores(player_scores)` - 验证分数合法性

- **BonusType** - 奖励类型枚举
  - `ROUND_WIN` - 回合获胜
  - `K_TONGZI`, `A_TONGZI`, `TWO_TONGZI` - 筒子奖励
  - `DIZHA` - 地炸奖励
  - `FINISH_FIRST`, `FINISH_SECOND`, `FINISH_THIRD` - 完成位置奖励

### AI 辅助（ai_helpers）

- **PlayGenerator** - 出牌生成器
  - `generate_all_plays(hand)` - 生成所有合法出牌
  - `generate_valid_responses(hand, current_pattern)` - 生成可以打出的牌

- **HandEvaluator** - 手牌评估器
  - `evaluate_hand(hand) -> float` - 评估手牌强度
  - `suggest_best_play(hand, current_pattern)` - 建议最佳出牌

- **PatternSuggester** - 牌型建议器（CV 纠错）
  - `suggest_corrections(recognized_cards, hand)` - 建议识别纠错

### 配置变体（variants）

- **ConfigFactory** - 配置工厂
  - `create_standard_3deck_3player()` - 标准 3 副牌 3 人
  - `create_4deck_4player()` - 4 副牌 4 人
  - `create_2player()` - 2 人对战
  - `create_quick_game()` - 快速游戏（2 副牌）
  - `create_high_stakes()` - 高额赌注（奖励翻倍）
  - `create_beginner_friendly()` - 新手友好（无有牌必打）
  - `create_custom(**kwargs)` - 自定义配置

- **VariantValidator** - 变体验证器
  - `validate_config(config) -> (is_valid, warnings)` - 验证配置合法性

## 性能基准

在 M1 MacBook Air 上的基准测试结果：

### 牌型识别
- 单牌：0.0053 ms/op（189K ops/sec）
- 对子：0.0061 ms/op（163K ops/sec）
- 三张：0.0070 ms/op（144K ops/sec）
- 炸弹：0.0077 ms/op（129K ops/sec）
- 筒子：0.0070 ms/op（142K ops/sec）

### 出牌生成
- 小手牌（5 张）：0.02 ms/op
- 中手牌（13 张）：0.11 ms/op
- 大手牌（25 张）：0.86 ms/op
- 满手牌（41 张）：6.38 ms/op

### 手牌评估
- 10 张：0.0005 ms/op（2M ops/sec）
- 20 张：0.0010 ms/op（1M ops/sec）
- 30 张：0.0015 ms/op（667K ops/sec）
- 41 张：0.0020 ms/op（500K ops/sec）

### 游戏设置
- 完整游戏设置：0.19 ms/op（5,225 games/sec）

### 计分
- 回合计分：0.0071 ms/op（141K ops/sec）
- 完成奖励：0.0071 ms/op（141K ops/sec）

运行基准测试：

```bash
python run.py benchmark
```

## 开发

### 开发脚本

项目提供了统一的开发脚本 `run.py`：

```bash
# 运行所有测试（含覆盖率）
python run.py test

# 仅运行单元测试
python run.py unit

# 仅运行集成测试
python run.py integration

# 运行所有示例
python run.py examples

# 运行性能基准测试
python run.py benchmark

# 运行所有检查（测试 + 示例）
python run.py check

# 清理缓存文件
python run.py clean

# 显示帮助
python run.py help
```

### 测试

项目包含全面的测试套件：

- **单元测试**（`tests/unit/`）：95 个测试
  - 模型测试（card, deck, config）
  - 牌型识别测试
  - 出牌验证测试
  - 计分系统测试
  - AI 辅助测试
  - 配置变体测试

- **集成测试**（`tests/integration/`）：6 个测试
  - 完整游戏流程测试
  - 牌型识别与验证流程测试
  - AI 辅助集成测试
  - 计分流程测试
  - 变体可玩性测试

- **性能测试**（`tests/benchmark/`）：5 个基准测试
  - 牌型识别性能
  - 出牌生成性能
  - 手牌评估性能
  - 游戏设置性能
  - 计分性能

当前测试覆盖率：**79.98%**

运行测试：

```bash
# 所有测试
pytest tests/ -v

# 带覆盖率报告
pytest tests/ -v --cov=src/datongzi_rules --cov-report=term-missing

# 使用开发脚本
python run.py test
```

### 代码质量

```bash
# 代码格式化
black src/ tests/ examples/

# 代码检查
ruff check src/ tests/ examples/ --fix

# 类型检查
mypy src/
```

## 项目结构

```
datongzi-rules/
├── src/
│   └── datongzi_rules/
│       ├── models/          # 数据模型
│       │   ├── card.py      # 卡牌、牌堆
│       │   ├── config.py    # 游戏配置
│       │   └── player.py    # 玩家模型
│       ├── rules/           # 规则引擎
│       │   ├── patterns.py  # 牌型识别
│       │   ├── validator.py # 出牌验证
│       │   └── scoring.py   # 计分系统
│       ├── ai_helpers/      # AI 辅助
│       │   ├── generator.py # 出牌生成
│       │   ├── evaluator.py # 手牌评估
│       │   └── suggester.py # CV 纠错
│       ├── variants/        # 配置变体
│       │   └── config_factory.py
│       └── __init__.py
├── tests/
│   ├── unit/               # 单元测试
│   ├── integration/        # 集成测试
│   └── benchmark/          # 性能测试
├── examples/               # 示例代码
│   ├── basic_usage.py
│   ├── complete_game_simulation.py
│   └── ai_player_demo.py
├── run.py                  # 开发脚本
├── pyproject.toml          # 项目配置
└── README.md
```

## 设计原则

1. **零依赖**：仅使用 Python 标准库，确保最小化依赖
2. **高性能**：优化关键路径，实现高效的牌型识别和验证
3. **类型安全**：全面的类型提示，支持静态类型检查
4. **测试驱动**：高测试覆盖率，确保代码质量
5. **可扩展**：模块化设计，易于扩展新功能

## 许可证

MIT License
