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
- 格式: `lowercase_with_underscores.rs`
- 示例:
  - `card.rs` - 卡牌数据模型
  - `recognizer.rs` - 牌型识别器
  - `play_generator.rs` - 出牌生成器
  - `hand_pattern_analyzer.rs` - 手牌结构分析器

### 测试文件 (Test Files)
- 单元测试：模块内 `#[cfg(test)]` 模块
- 集成测试：`tests/` 目录下，格式 `test_<module_name>.rs`
- 示例:
  - `tests/basic.rs`
  - `tests/scoring_integration.rs`

### 文档文件 (Documentation Files)
- 格式: `UPPERCASE.md` (顶层文档), `lowercase.md` (子文档)
- 示例:
  - `README.md`
  - `GAME_RULE.md`
  - `ARCHITECTURE.md`
  - `NAME_CONVENTION.md`

---

## 3. Rust 命名规范

### 结构体名 (Struct Names)
- 格式: `PascalCase` (每个单词首字母大写)
- 示例:
  - `Card` - 卡牌结构
  - `PatternRecognizer` - 牌型识别器
  - `PlayGenerator` - 出牌生成器
  - `ScoreComputation` - 计分引擎
  - `HandPatternAnalyzer` - 手牌结构分析器
  - `HandPatterns` - 手牌结构数据类

### 枚举名 (Enum Names)
- 类型名: `PascalCase`
- 变体名: `PascalCase`
- 示例:
  ```rust
  pub enum PlayType {
      Single,
      Pair,
      ConsecutivePairs,
      Triple,
      Bomb,
      Tongzi,
      Dizha,
  }
  ```

### 函数/方法名 (Function/Method Names)
- 格式: `lowercase_with_underscores` (snake_case)
- 动词开头，清晰表达动作
- 示例:
  - `generate_all_plays()` - 生成所有出牌
  - `analyze_cards()` - 分析卡牌
  - `analyze_patterns()` - 分析手牌结构
  - `can_beat_play()` - 能否打过

### 变量名 (Variable Names)
- 格式: `lowercase_with_underscores` (snake_case)
- 名词或形容词+名词
- 示例:
  - `hand` - 手牌
  - `current_pattern` - 当前牌型
  - `primary_rank` - 主要点数
  - `card_count` - 卡牌数量

### 常量 (Constants)
- 格式: `UPPERCASE_WITH_UNDERSCORES` (SCREAMING_SNAKE_CASE)
- 示例:
  - `MAX_COMBINATIONS` - 最大组合数
  - `DEFAULT_NUM_DECKS` - 默认牌副数

### Trait 名 (Trait Names)
- 格式: `PascalCase`
- 通常使用形容词或动词描述行为
- 示例:
  - `Display` - 显示
  - `Clone` - 克隆
  - `PartialOrd` - 部分排序

### 模块名 (Module Names)
- 格式: `lowercase_with_underscores` (snake_case)
- 示例:
  - `models`
  - `patterns`
  - `ai_helpers`

---

## 4. 方法命名模式

### 生成器方法 (Generator Methods)
- 返回集合的方法使用 `generate_*` 或 `create_*`
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
  - `is_scoring_card()` - 是否为计分牌

### 分析/计算方法 (Analysis/Calculation Methods)
- 使用 `analyze_*`, `calculate_*`, `count_*`
- 示例:
  - `analyze_cards()` - 分析卡牌
  - `calculate_total_score()` - 计算总分
  - `count_all_plays()` - 统计出牌数

### 查找/获取方法 (Find/Get Methods)
- 使用 `find_*`, `get_*`
- 示例:
  - `find_scoring_cards()` - 查找计分牌
  - `get_primary_rank()` - 获取主要点数

### 构造方法 (Constructor Methods)
- 使用 `new` 作为主构造函数
- 使用 `from_*` 进行转换构造
- 使用 `with_*` 进行配置构造
- 示例:
  - `Card::new(suit, rank)` - 创建新卡牌
  - `Deck::from_cards(cards)` - 从卡牌列表创建
  - `GameConfig::with_bonus(bonus)` - 带奖励配置

---

## 5. 特殊命名规则

### 王牌相关 (Trump-related)
- `trump` - 王牌（地炸/筒子/炸弹的统称）
- `trump_types` - 王牌类型列表
- `is_current_trump` - 当前是否为王牌
- 示例方法:
  - `generate_beating_plays_with_same_type_or_trump()`
  - `generate_higher_bombs()` - 生成更大的炸弹

### 牌型层级相关 (Pattern Hierarchy)
- `higher_*` - 更大/更高的
- `same_type` - 同类型
- 示例:
  - `generate_higher_singles()` - 生成更大的单张
  - `generate_higher_pairs()` - 生成更大的对子
  - `generate_higher_bombs()` - 生成更大的炸弹

### 计分相关 (Scoring)
- `score` / `points` - 分数
- `bonus` - 奖励分
- `penalty` - 罚分
- 示例:
  - `round_win_bonus` - 回合胜利奖励
  - `tongzi_bonus` - 筒子奖励分
  - `finish_penalty` - 完成罚分

---

## 6. 文档注释 (Documentation Comments)

### 格式
- 使用 `///` 进行文档注释
- 简洁描述 + 参数 + 返回值 + 示例

### 示例
```rust
/// Generate plays that can beat current pattern using same type or trump cards.
///
/// Strategy:
/// - Only use same-type plays with higher rank (no pattern breaking)
/// - Or use trump cards (BOMB/TONGZI/DIZHA) to beat normal plays
/// - Trump hierarchy: DIZHA > TONGZI > BOMB
///
/// This follows the "有牌必打" rule - must play if you can beat.
///
/// # Arguments
///
/// * `hand` - Slice of cards in hand
/// * `current_pattern` - Current play pattern to beat
///
/// # Returns
///
/// Vector of valid beating plays (minimal set, no wasteful combinations)
///
/// # Example
///
/// ```
/// use datongzi_rules::{Card, PlayGenerator, PlayPattern};
///
/// let hand = vec![/* ... */];
/// let pattern = PlayPattern::new(/* ... */);
/// let plays = PlayGenerator::generate_beating_plays_with_same_type_or_trump(&hand, &pattern);
/// ```
pub fn generate_beating_plays_with_same_type_or_trump(
    hand: &[Card],
    current_pattern: &PlayPattern,
) -> Vec<Vec<Card>> {
    // ...
}
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

6. **不遵循 Rust 惯例**
   - ❌ `getCard()` (驼峰式)
   - ✅ `get_card()` (蛇形式)
   - ❌ `card_type` (枚举变体)
   - ✅ `CardType` (枚举变体应为 PascalCase)

---

## 8. 版本历史

| 版本 | 日期 | 说明 |
|-----|------|------|
| 1.0 | 2025-01-17 | 初始版本，定义核心命名规范 |
| 2.0 | 2025-11-26 | 更新为 Rust 命名规范 |

---

## 9. 参考资料

- [Rust API Guidelines - Naming](https://rust-lang.github.io/api-guidelines/naming.html)
- [Rust Style Guide](https://doc.rust-lang.org/nightly/style-guide/)
- [Clean Code by Robert C. Martin](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882)

---

**注意**:
- 所有新代码必须遵循此规范
- 现有代码重构时应逐步向此规范靠拢
- 特殊情况需在代码审查中讨论并记录
