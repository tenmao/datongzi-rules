# DaTongZi-Rules AI 辅助算法设计文档

> 版本: 1.0
> 日期: 2025-11-26
> 适用: datongzi-rules Rust crate

## 概述

本文档描述 `datongzi-rules` crate 中的 AI 辅助算法，为上层 MCTS 引擎提供高效的底层支持。
这些算法专注于牌型分析、动作生成和策略评估的基础能力。

## 现有数据结构

### 核心类型 (已存在)
```rust
// models/card.rs
pub struct Card { pub rank: Rank, pub suit: Suit }

// models/rank.rs
pub enum Rank { Three=3, ..., Ace=14, Two=15 }

// models/suit.rs
pub enum Suit { Diamonds=1, Clubs=2, Hearts=3, Spades=4 }

// patterns/pattern.rs
pub enum PlayType { Single, Pair, ConsecutivePairs, Triple, TripleWithTwo,
                    Airplane, AirplaneWithWings, Bomb, Tongzi, Dizha }
pub struct PlayPattern { pub play_type: PlayType, pub cards: Vec<Card>, pub strength: u32 }

// patterns/recognizer.rs
impl PatternRecognizer {
    pub fn analyze_cards(cards: &[Card]) -> Option<PlayPattern>;
}

// ai_helpers/play_generator.rs
impl PlayGenerator {
    pub fn generate_all_plays(hand: &[Card], max: usize) -> Result<Vec<Vec<Card>>, _>;
    pub fn generate_beating_plays_with_same_type_or_trump(hand: &[Card], pattern: &PlayPattern) -> Vec<Vec<Card>>;
}

// ai_helpers/hand_pattern_analyzer.rs
impl HandPatternAnalyzer {
    pub fn analyze_hand_patterns(hand: &[Card]) -> HandAnalysis;
}
```

---

## 1. Boss Card 检测器

### 1.1 概念

**Boss Card (大牌)** 是指在当前花色中，没有任何剩余牌能击败它的牌。

示例:
- 如果红桃 A 和红桃 2 都已打出，那么红桃 K 就是 Boss Card
- Boss Card 在单牌出牌时非常有价值，可以稳定获得控制权

### 1.2 数据结构

```rust
// ai_helpers/boss_card.rs

/// Boss Card 检测器 - 用于快速判断单牌是否为大牌
///
/// 使用 O(1) 查询复杂度，通过记录每个花色剩余的最大 rank 实现。
pub struct BossCardDetector {
    /// 每个花色剩余的最大 rank
    /// 索引: Suit as usize - 1 (Diamonds=0, Clubs=1, Hearts=2, Spades=3)
    /// 值: rank.value() (5-15), 0 表示该花色无牌
    max_remaining_ranks: [u8; 4],
}
```

### 1.3 API 设计

```rust
impl BossCardDetector {
    /// 从剩余牌堆创建检测器
    ///
    /// # Arguments
    /// * `remaining_cards` - 所有未打出的牌（包括所有玩家手牌和弃牌堆以外的牌）
    ///
    /// # Example
    /// ```rust
    /// let all_remaining: Vec<Card> = players.iter()
    ///     .flat_map(|p| p.hand.iter())
    ///     .cloned()
    ///     .collect();
    /// let detector = BossCardDetector::new(&all_remaining);
    /// ```
    pub fn new(remaining_cards: &[Card]) -> Self {
        let mut max_remaining_ranks = [0u8; 4];

        for card in remaining_cards {
            let suit_idx = card.suit as usize - 1;
            let rank_val = card.rank.value() as u8;

            if rank_val > max_remaining_ranks[suit_idx] {
                max_remaining_ranks[suit_idx] = rank_val;
            }
        }

        Self { max_remaining_ranks }
    }

    /// O(1) 检测是否为 Boss Card
    ///
    /// 当该牌的 rank 等于其花色中剩余的最大 rank 时，它就是 Boss Card。
    ///
    /// # Arguments
    /// * `card` - 要检测的牌
    ///
    /// # Returns
    /// `true` 如果该牌是 Boss Card
    #[inline]
    pub fn is_boss(&self, card: &Card) -> bool {
        let suit_idx = card.suit as usize - 1;
        card.rank.value() as u8 >= self.max_remaining_ranks[suit_idx]
    }

    /// 统计手牌中的 Boss Card 数量
    ///
    /// # Arguments
    /// * `hand` - 玩家手牌
    ///
    /// # Returns
    /// Boss Card 的数量
    pub fn count_boss_cards(&self, hand: &[Card]) -> usize {
        hand.iter().filter(|c| self.is_boss(c)).count()
    }

    /// 获取手牌中所有 Boss Card
    pub fn get_boss_cards<'a>(&self, hand: &'a [Card]) -> Vec<&'a Card> {
        hand.iter().filter(|c| self.is_boss(c)).collect()
    }

    /// 增量更新（出牌后调用）
    ///
    /// 当牌被打出后，需要重新计算剩余牌的最大 rank。
    ///
    /// # Arguments
    /// * `remaining_cards` - 更新后的剩余牌
    pub fn update(&mut self, remaining_cards: &[Card]) {
        self.max_remaining_ranks = [0u8; 4];

        for card in remaining_cards {
            let suit_idx = card.suit as usize - 1;
            let rank_val = card.rank.value() as u8;

            if rank_val > self.max_remaining_ranks[suit_idx] {
                self.max_remaining_ranks[suit_idx] = rank_val;
            }
        }
    }
}
```

### 1.4 使用场景

1. **MCTS Rollout 评估**: 在模拟中评估手牌质量
2. **单牌策略**: 决定是否保留高价值单牌
3. **Soft Policy 评分**: 作为启发式评分的因子之一

---

## 2. 贪婪 Kicker 选择

### 2.1 问题描述

飞机(Airplane)、飞机带翅膀(AirplaneWithWings)和三带二(TripleWithTwo)需要选择 kicker 牌。
朴素的选择方法会拆散有价值的结构（如炸弹、筒子、对子）。

### 2.2 选择策略优先级

从高到低：
1. **孤张**: 不属于任何有价值结构的单牌
2. **多余对子**: 从非关键对子中选取
3. **三张中取一**: 尽量避免，只在必要时使用
4. **永不拆除**: 炸弹(Bomb)、筒子(Tongzi)、地炸(Dizha)

### 2.3 数据结构

```rust
// ai_helpers/kicker.rs

/// Kicker 类型
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum KickerType {
    /// 单张 kicker (三带一、飞机带单)
    Single,
    /// 对子 kicker (三带二、飞机带对)
    Pair,
}

/// Kicker 选择器
pub struct KickerSelector;
```

### 2.4 API 设计

```rust
impl KickerSelector {
    /// 为主牌选择最优 kicker
    ///
    /// 使用贪婪策略选择对手牌结构破坏最小的 kicker。
    ///
    /// # Arguments
    /// * `hand` - 完整手牌
    /// * `main_cards` - 已选定的主牌（如三张、飞机主体）
    /// * `kicker_count` - 需要的 kicker 数量
    /// * `kicker_type` - kicker 类型（单张或对子）
    ///
    /// # Returns
    /// 选中的 kicker 牌，如果无法满足返回 None
    ///
    /// # Example
    /// ```rust
    /// // 三带二：选择2张作为对子kicker
    /// let triple = vec![card_7h, card_7d, card_7c];
    /// let kickers = KickerSelector::select_optimal_kickers(
    ///     &hand,
    ///     &triple,
    ///     1,  // 1对
    ///     KickerType::Pair,
    /// );
    /// ```
    pub fn select_optimal_kickers(
        hand: &[Card],
        main_cards: &[Card],
        kicker_count: usize,
        kicker_type: KickerType,
    ) -> Option<Vec<Card>> {
        // 1. 排除主牌，获取可用牌
        let available: Vec<Card> = hand.iter()
            .filter(|c| !main_cards.contains(c))
            .cloned()
            .collect();

        if available.is_empty() {
            return None;
        }

        // 2. 分析剩余牌的结构
        let analysis = HandPatternAnalyzer::analyze_hand_patterns(&available);

        // 3. 收集候选 kicker
        let candidates = Self::collect_candidates(&available, &analysis, kicker_type);

        // 4. 按优先级排序并选取
        Self::select_from_candidates(candidates, kicker_count, kicker_type)
    }

    /// 收集候选 kicker（按优先级标记）
    fn collect_candidates(
        available: &[Card],
        analysis: &HandAnalysis,
        kicker_type: KickerType,
    ) -> Vec<(Card, u8)> {  // (card, priority: 低=优先)
        let mut candidates = Vec::new();

        // 标记受保护的牌（炸弹、筒子、地炸中的牌）
        let protected_cards = Self::get_protected_cards(analysis);

        match kicker_type {
            KickerType::Single => {
                for card in available {
                    if protected_cards.contains(card) {
                        continue;  // 跳过受保护的牌
                    }

                    let priority = Self::card_priority(card, analysis);
                    candidates.push((*card, priority));
                }
            }
            KickerType::Pair => {
                // 找出可用的对子
                let pairs = Self::find_available_pairs(available, &protected_cards);
                for pair in pairs {
                    let priority = Self::pair_priority(&pair, analysis);
                    candidates.push((pair[0], priority));
                    candidates.push((pair[1], priority));
                }
            }
        }

        // 按优先级排序（低优先级数字 = 更优先选择）
        candidates.sort_by_key(|(card, priority)| (*priority, card.rank.value()));
        candidates
    }

    /// 获取受保护的牌（在炸弹、筒子、地炸中的牌）
    fn get_protected_cards(analysis: &HandAnalysis) -> HashSet<Card> {
        let mut protected = HashSet::new();

        // 炸弹中的牌
        for bomb in &analysis.bombs {
            protected.extend(bomb.iter().cloned());
        }

        // 筒子中的牌
        for tongzi in &analysis.tongzi {
            protected.extend(tongzi.iter().cloned());
        }

        // 地炸中的牌
        for dizha in &analysis.dizha {
            protected.extend(dizha.iter().cloned());
        }

        protected
    }

    /// 单牌优先级（数字越小越优先）
    fn card_priority(card: &Card, analysis: &HandAnalysis) -> u8 {
        // 孤张最优先
        if analysis.singles.contains(card) {
            return 0;
        }

        // 对子中的牌次优先
        for pair in &analysis.pairs {
            if pair.contains(card) {
                return 1;
            }
        }

        // 三张中的牌最后
        for triple in &analysis.triples {
            if triple.contains(card) {
                return 2;
            }
        }

        3  // 其他情况
    }

    /// 对子优先级
    fn pair_priority(pair: &[Card], analysis: &HandAnalysis) -> u8 {
        // 独立对子最优先
        for p in &analysis.pairs {
            if p[0].rank == pair[0].rank {
                return 0;
            }
        }

        // 从三张中拆出的对子次优先
        1
    }

    /// 从候选中选取指定数量的 kicker
    fn select_from_candidates(
        candidates: Vec<(Card, u8)>,
        count: usize,
        kicker_type: KickerType,
    ) -> Option<Vec<Card>> {
        let needed = match kicker_type {
            KickerType::Single => count,
            KickerType::Pair => count * 2,
        };

        if candidates.len() < needed {
            return None;
        }

        Some(candidates.into_iter().take(needed).map(|(c, _)| c).collect())
    }

    /// 查找可用的对子
    fn find_available_pairs(available: &[Card], protected: &HashSet<Card>) -> Vec<Vec<Card>> {
        let mut rank_groups: HashMap<Rank, Vec<Card>> = HashMap::new();

        for card in available {
            if !protected.contains(card) {
                rank_groups.entry(card.rank).or_default().push(*card);
            }
        }

        rank_groups.into_iter()
            .filter(|(_, cards)| cards.len() >= 2)
            .map(|(_, mut cards)| {
                cards.truncate(2);
                cards
            })
            .collect()
    }
}
```

---

## 3. Goal-Driven Move Generation

### 3.1 概念

根据不同的游戏场景，生成符合特定目标的动作集合：
- **首发 (Leading)**: 争夺控制权，选择中等强度牌型
- **跟牌 (Following)**: 最小代价压制
- **王牌决策 (Trump)**: 评估是否使用炸弹/筒子/地炸

### 3.2 数据结构

```rust
// ai_helpers/goal_driven.rs

/// 出牌目标类型
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PlayGoal {
    /// 首发：争夺控制权
    /// 倾向出中等强度牌型，保留高价值结构
    LeadControl,

    /// 跟牌：最小代价压制
    /// 选择刚好能赢的最弱牌型
    BeatMinimal,

    /// 仅考虑王牌
    /// 用于评估是否使用炸弹/筒子/地炸翻本
    TrumpOnly,
}

/// 带目标的动作生成器
pub struct GoalDrivenGenerator;
```

### 3.3 API 设计

```rust
impl GoalDrivenGenerator {
    /// 根据目标生成动作
    ///
    /// # Arguments
    /// * `hand` - 玩家手牌
    /// * `current_play` - 当前需要压制的牌型（首发时为 None）
    /// * `goal` - 出牌目标
    ///
    /// # Returns
    /// 符合目标的动作列表，已按相关性排序
    pub fn generate_plays_with_goal(
        hand: &[Card],
        current_play: Option<&PlayPattern>,
        goal: PlayGoal,
    ) -> Vec<Vec<Card>> {
        match goal {
            PlayGoal::LeadControl => Self::generate_lead_control(hand),
            PlayGoal::BeatMinimal => Self::generate_beat_minimal(hand, current_play),
            PlayGoal::TrumpOnly => Self::generate_trump_only(hand),
        }
    }

    /// LeadControl: 首发策略
    ///
    /// 生成中等强度牌型，按控制力排序
    fn generate_lead_control(hand: &[Card]) -> Vec<Vec<Card>> {
        let all_plays = PlayGenerator::generate_all_plays(hand, 200)
            .unwrap_or_default();

        let mut scored_plays: Vec<(Vec<Card>, i32)> = all_plays
            .into_iter()
            .filter_map(|play| {
                let pattern = PatternRecognizer::analyze_cards(&play)?;
                let score = Self::lead_control_score(&pattern, hand);
                Some((play, score))
            })
            .collect();

        // 按分数降序排列
        scored_plays.sort_by(|a, b| b.1.cmp(&a.1));

        scored_plays.into_iter().map(|(play, _)| play).collect()
    }

    /// 首发控制力评分
    fn lead_control_score(pattern: &PlayPattern, hand: &[Card]) -> i32 {
        let mut score = 0i32;

        // 牌型权重（倾向出多张牌型）
        score += match pattern.play_type {
            PlayType::Single => -10,        // 单牌不太好
            PlayType::Pair => 10,           // 对子中等
            PlayType::Triple => 15,         // 三张中等
            PlayType::TripleWithTwo => 20,  // 三带二好
            PlayType::ConsecutivePairs => 25, // 连对好
            PlayType::Airplane => 30,       // 飞机很好
            PlayType::AirplaneWithWings => 35, // 飞机带翅膀最好
            PlayType::Bomb => -20,          // 首发不出炸弹
            PlayType::Tongzi => -30,        // 首发不出筒子
            PlayType::Dizha => -40,         // 首发不出地炸
        };

        // 出牌数量奖励（出多少得多少分）
        score += pattern.cards.len() as i32 * 2;

        // 强度惩罚（太强的牌留着）
        // 假设 strength 范围 0-1000
        if pattern.strength > 500 {
            score -= (pattern.strength as i32 - 500) / 10;
        }

        score
    }

    /// BeatMinimal: 最小代价压制
    fn generate_beat_minimal(
        hand: &[Card],
        current_play: Option<&PlayPattern>,
    ) -> Vec<Vec<Card>> {
        let Some(pattern) = current_play else {
            return Vec::new();
        };

        let beating_plays = PlayGenerator::generate_beating_plays_with_same_type_or_trump(
            hand, pattern
        );

        // 按强度升序排列（最弱的能赢的牌在前）
        let mut scored: Vec<(Vec<Card>, u32)> = beating_plays
            .into_iter()
            .filter_map(|play| {
                let p = PatternRecognizer::analyze_cards(&play)?;
                Some((play, p.strength))
            })
            .collect();

        scored.sort_by_key(|(_, strength)| *strength);
        scored.into_iter().map(|(play, _)| play).collect()
    }

    /// TrumpOnly: 仅生成王牌
    fn generate_trump_only(hand: &[Card]) -> Vec<Vec<Card>> {
        let analysis = HandPatternAnalyzer::analyze_hand_patterns(hand);
        let mut trumps = Vec::new();

        // 收集所有炸弹
        trumps.extend(analysis.bombs.clone());

        // 收集所有筒子
        trumps.extend(analysis.tongzi.clone());

        // 收集所有地炸
        trumps.extend(analysis.dizha.clone());

        // 按强度排序（弱的王牌优先使用）
        trumps.sort_by(|a, b| {
            let pa = PatternRecognizer::analyze_cards(a);
            let pb = PatternRecognizer::analyze_cards(b);
            match (pa, pb) {
                (Some(pa), Some(pb)) => pa.strength.cmp(&pb.strength),
                _ => std::cmp::Ordering::Equal,
            }
        });

        trumps
    }
}
```

---

## 4. 文件结构

### 4.1 新增文件

```
rust/datongzi-rules/src/ai_helpers/
├── mod.rs              # 模块导出 (修改)
├── boss_card.rs        # Boss Card 检测器 (新建)
├── kicker.rs           # Kicker 选择器 (新建)
├── goal_driven.rs      # Goal-Driven 生成器 (新建)
├── play_generator.rs   # 已存在
└── hand_pattern_analyzer.rs  # 已存在
```

### 4.2 mod.rs 更新

```rust
// ai_helpers/mod.rs

mod play_generator;
mod hand_pattern_analyzer;
mod boss_card;        // 新增
mod kicker;           // 新增
mod goal_driven;      // 新增

pub use play_generator::*;
pub use hand_pattern_analyzer::*;
pub use boss_card::*;   // 新增
pub use kicker::*;      // 新增
pub use goal_driven::*; // 新增
```

---

## 5. 测试计划

### 5.1 Boss Card 测试

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_boss_card_detection() {
        // 假设红桃 A, 2 已打出，红桃 K 应为 Boss
        let remaining = vec![
            Card::new(Suit::Hearts, Rank::King),
            Card::new(Suit::Hearts, Rank::Queen),
            Card::new(Suit::Spades, Rank::Ace),
        ];

        let detector = BossCardDetector::new(&remaining);

        assert!(detector.is_boss(&Card::new(Suit::Hearts, Rank::King)));
        assert!(!detector.is_boss(&Card::new(Suit::Hearts, Rank::Queen)));
        assert!(detector.is_boss(&Card::new(Suit::Spades, Rank::Ace)));
    }

    #[test]
    fn test_boss_card_count() {
        let remaining = vec![
            Card::new(Suit::Hearts, Rank::Ace),
            Card::new(Suit::Spades, Rank::Two),
        ];

        let detector = BossCardDetector::new(&remaining);
        let hand = vec![
            Card::new(Suit::Hearts, Rank::Ace),  // Boss
            Card::new(Suit::Hearts, Rank::King), // Not boss
            Card::new(Suit::Spades, Rank::Two),  // Boss
        ];

        assert_eq!(detector.count_boss_cards(&hand), 2);
    }
}
```

### 5.2 Kicker 选择测试

```rust
#[test]
fn test_kicker_prefers_singles() {
    // 手牌: 777 + 88 + 5(孤张)
    let hand = vec![
        Card::new(Suit::Hearts, Rank::Seven),
        Card::new(Suit::Spades, Rank::Seven),
        Card::new(Suit::Diamonds, Rank::Seven),
        Card::new(Suit::Hearts, Rank::Eight),
        Card::new(Suit::Spades, Rank::Eight),
        Card::new(Suit::Hearts, Rank::Five),  // 孤张
    ];

    let main_cards = vec![
        Card::new(Suit::Hearts, Rank::Seven),
        Card::new(Suit::Spades, Rank::Seven),
        Card::new(Suit::Diamonds, Rank::Seven),
    ];

    let kickers = KickerSelector::select_optimal_kickers(
        &hand, &main_cards, 1, KickerType::Single
    ).unwrap();

    // 应该选择孤张 5
    assert_eq!(kickers[0].rank, Rank::Five);
}

#[test]
fn test_kicker_protects_bombs() {
    // 手牌: 777 + 8888(炸弹) + 5
    let hand = vec![
        Card::new(Suit::Hearts, Rank::Seven),
        Card::new(Suit::Spades, Rank::Seven),
        Card::new(Suit::Diamonds, Rank::Seven),
        Card::new(Suit::Hearts, Rank::Eight),
        Card::new(Suit::Spades, Rank::Eight),
        Card::new(Suit::Diamonds, Rank::Eight),
        Card::new(Suit::Clubs, Rank::Eight),
        Card::new(Suit::Hearts, Rank::Five),
    ];

    let main_cards = vec![
        Card::new(Suit::Hearts, Rank::Seven),
        Card::new(Suit::Spades, Rank::Seven),
        Card::new(Suit::Diamonds, Rank::Seven),
    ];

    let kickers = KickerSelector::select_optimal_kickers(
        &hand, &main_cards, 1, KickerType::Single
    ).unwrap();

    // 不应该拆炸弹，应该选 5
    assert_eq!(kickers[0].rank, Rank::Five);
}
```

---

## 6. 性能考虑

| 操作 | 复杂度 | 说明 |
|------|--------|------|
| `BossCardDetector::new()` | O(n) | n = 剩余牌数量 |
| `BossCardDetector::is_boss()` | O(1) | 数组查表 |
| `KickerSelector::select_optimal_kickers()` | O(n log n) | 主要是排序开销 |
| `GoalDrivenGenerator::generate_plays_with_goal()` | O(m log m) | m = 生成的动作数 |

---

## 7. 后续优化方向

1. **HandMatrix 表示**: 如果性能成为瓶颈，可以考虑 11×4 矩阵表示手牌
2. **增量更新**: BossCardDetector 可优化为增量更新而非完全重建
3. **缓存**: 对于相同手牌的多次查询，可以缓存分析结果
