# 命名规范 (Naming Convention)

本文档定义 `datongzi-rules` 项目的命名规范，确保代码一致性和可读性。

---

## 核心原则

1. **英文优先**: 所有代码、变量、函数、类名使用英文（游戏术语除外）
2. **语义化命名**: 名称应清晰表达意图，避免缩写（除非是业界公认缩写）
3. **一致性**: 同类型实体使用统一命名模式
4. **领域术语**: 游戏规则相关术语使用中文音译或业界通用术语

---

## 1. 游戏术语翻译对照表

| 中文术语 | 英文翻译 | 说明 |
|---------|---------|------|
| 打筒子 | Datongzi | 游戏名称（拼音） |
| 筒子 | Tongzi | 特殊牌型（3张同花色同数字），音译 |
| 地炸 | Dizha | 最强牌型（8张同数字4花色各2张），音译 |
| 炸弹 | Bomb | 4张及以上同数字 |
| 王牌 | Trump | 地炸/筒子/炸弹的统称 |
| 飞机 | Airplane | 连续数字的三张 |
| 连对 | Consecutive Pairs | 两连对及以上 |
| 三张 | Triple | 3张同数字 |
| 对子 | Pair | 2张同数字 |
| 单张 | Single | 1张牌 |
| 有牌必打 | Must Play If Can Beat | 核心规则 |
| 回合 | Round | 从出牌到无人应答的完整循环 |
| 上游/二游/三游 | First/Second/Third Finisher | 完成顺序 |

---

## 2. 文件命名

### 模块文件 (Module Files)
- 格式: `lowercase_with_underscores.py`
- 示例:
  - `card.py` - 卡牌数据模型
  - `pattern_recognizer.py` - 牌型识别器
  - `play_generator.py` - 出牌生成器
  - `hand_pattern_analyzer.py` - 手牌结构分析器

### 测试文件 (Test Files)
- 格式: `test_<module_name>.py`
- 示例:
  - `test_card.py`
  - `test_pattern_recognizer.py`

### 文档文件 (Documentation Files)
- 格式: `UPPERCASE.md` (顶层文档), `lowercase.md` (子文档)
- 示例:
  - `README.md`
  - `GAME_RULE.md`
  - `ARCHITECTURE.md`
  - `NAME_CONVENTION.md`

---

## 3. Python 命名规范

### 类名 (Class Names)
- 格式: `PascalCase` (每个单词首字母大写)
- 示例:
  - `Card` - 卡牌类
  - `PatternRecognizer` - 牌型识别器
  - `PlayGenerator` - 出牌生成器
  - `ScoreComputation` - 计分引擎
  - `HandEvaluator` - 手牌评估器
  - `HandPatternAnalyzer` - 手牌结构分析器
  - `HandPatterns` - 手牌结构数据类

### 函数/方法名 (Function/Method Names)
- 格式: `lowercase_with_underscores`
- 动词开头，清晰表达动作
- 示例:
  - `generate_all_plays()` - 生成所有出牌
  - `analyze_cards()` - 分析卡牌
  - `analyze_patterns()` - 分析手牌结构
  - `can_beat_play()` - 能否打过
  - `evaluate_hand()` - 评估手牌

### 变量名 (Variable Names)
- 格式: `lowercase_with_underscores`
- 名词或形容词+名词
- 示例:
  - `hand` - 手牌
  - `current_pattern` - 当前牌型
  - `primary_rank` - 主要点数
  - `card_count` - 卡牌数量

### 常量 (Constants)
- 格式: `UPPERCASE_WITH_UNDERSCORES`
- 示例:
  - `MAX_COMBINATIONS` - 最大组合数
  - `DEFAULT_NUM_DECKS` - 默认牌副数

### 枚举 (Enums)
- 类名: `PascalCase`
- 枚举值: `UPPERCASE` (单个词) 或 `UPPERCASE_WITH_UNDERSCORES` (多词)
- 示例:
  ```python
  class PlayType(IntEnum):
      SINGLE = 1
      PAIR = 2
      CONSECUTIVE_PAIRS = 3
      TRIPLE = 4
      BOMB = 8
      TONGZI = 9
      DIZHA = 10
  ```

### 私有方法/属性 (Private Methods/Attributes)
- 格式: `_leading_underscore`
- 示例:
  - `_generate_pairs()` - 内部使用的辅助方法
  - `_group_by_rank()` - 内部分组逻辑

---

## 4. 方法命名模式

### 生成器方法 (Generator Methods)
- 返回列表/集合的方法使用 `generate_*` 或 `create_*`
- 示例:
  - `generate_all_plays()` - 生成所有出牌
  - `generate_beating_plays_with_same_type_or_trump()` - 生成打牌（同型或王牌）
  - `create_standard_deck()` - 创建标准牌组

### 验证/检查方法 (Validation/Check Methods)
- 返回布尔值的方法使用 `is_*`, `can_*`, `has_*`, `should_*`
- 示例:
  - `can_beat_play()` - 能否打过
  - `is_consecutive()` - 是否连续
  - `has_must_play_violation()` - 是否违反有牌必打

### 分析/计算方法 (Analysis/Calculation Methods)
- 使用 `analyze_*`, `calculate_*`, `evaluate_*`, `count_*`
- 示例:
  - `analyze_cards()` - 分析卡牌
  - `calculate_total_score()` - 计算总分
  - `evaluate_hand()` - 评估手牌
  - `count_all_plays()` - 统计出牌数

### 查找/过滤方法 (Find/Filter Methods)
- 使用 `find_*`, `get_*`, `filter_*`
- 示例:
  - `find_scoring_cards()` - 查找计分牌
  - `get_primary_rank()` - 获取主要点数

---

## 5. 特殊命名规则

### 王牌相关 (Trump-related)
- `trump` - 王牌（地炸/筒子/炸弹的统称）
- `trump_types` - 王牌类型列表
- `is_current_trump` - 当前是否为王牌
- 示例方法:
  - `generate_beating_plays_with_same_type_or_trump()`
  - `_generate_higher_bombs()` - 生成更大的炸弹

### 牌型层级相关 (Pattern Hierarchy)
- `higher_*` - 更大/更高的
- `same_type` - 同类型
- 示例:
  - `_generate_higher_singles()` - 生成更大的单张
  - `_generate_higher_pairs()` - 生成更大的对子
  - `_generate_higher_bombs()` - 生成更大的炸弹

### 计分相关 (Scoring)
- `score` / `points` - 分数
- `bonus` - 奖励分
- `penalty` - 罚分
- 示例:
  - `round_win_bonus` - 回合胜利奖励
  - `tongzi_bonus` - 筒子奖励分
  - `finish_penalty` - 完成罚分

---

## 6. 文档字符串 (Docstrings)

### 格式
- 使用 Google 风格 docstring
- 简洁描述 + Args + Returns + (可选) Raises/Examples

### 示例
```python
def generate_beating_plays_with_same_type_or_trump(
    hand: list[Card], current_pattern: PlayPattern
) -> list[list[Card]]:
    """
    Generate plays that can beat current pattern using same type or trump cards.

    Strategy:
    - Only use same-type plays with higher rank (no pattern breaking)
    - Or use trump cards (BOMB/TONGZI/DIZHA) to beat normal plays
    - Trump hierarchy: DIZHA > TONGZI > BOMB

    This follows the "有牌必打" rule - must play if you can beat.

    Args:
        hand: List of cards in hand
        current_pattern: Current play pattern to beat

    Returns:
        List of valid beating plays (minimal set, no wasteful combinations)
    """
```

---

## 7. 反模式 (Anti-Patterns)

### ❌ 避免的命名

1. **拼音缩写**
   - ❌ `dtz` (打筒子)
   - ✅ `datongzi`

2. **不清晰的缩写**
   - ❌ `gen_plays()`
   - ✅ `generate_plays()`

3. **模糊的动词**
   - ❌ `process_cards()`
   - ✅ `analyze_cards()` 或 `validate_cards()`

4. **混合中英文**
   - ❌ `tongziPattern`
   - ✅ `tongzi_pattern`

5. **过长的名称** (超过50字符需要重新考虑)
   - ❌ `generate_all_possible_valid_beating_plays_using_same_type_or_higher_trump_cards()`
   - ✅ `generate_beating_plays_with_same_type_or_trump()`

---

## 8. 版本历史

| 版本 | 日期 | 说明 |
|-----|------|------|
| 1.0 | 2025-01-17 | 初始版本，定义核心命名规范 |

---

## 9. 参考资料

- [PEP 8 - Style Guide for Python Code](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Clean Code by Robert C. Martin](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882)

---

**注意**:
- 所有新代码必须遵循此规范
- 现有代码重构时应逐步向此规范靠拢
- 特殊情况需在代码审查中讨论并记录
