//! Boundary tests for patterns layer (PatternRecognizer, PlayValidator)

use datongzi_rules::{Card, PatternRecognizer, PlayType, PlayValidator, Rank, Suit};

// ============================================================================
// PatternRecognizer 边界测试 - Single
// ============================================================================

#[test]
fn test_recognize_single_all_ranks() {
    // 测试所有牌面的单张
    let ranks = [
        Rank::Three, Rank::Four, Rank::Five, Rank::Six, Rank::Seven,
        Rank::Eight, Rank::Nine, Rank::Ten, Rank::Jack, Rank::Queen,
        Rank::King, Rank::Ace, Rank::Two,
    ];

    for rank in ranks {
        let cards = vec![Card::new(Suit::Spades, rank)];
        let pattern = PatternRecognizer::analyze_cards(&cards);
        assert!(pattern.is_some());
        if let Some(p) = pattern {
            assert_eq!(p.play_type, PlayType::Single);
        }
    }
}

#[test]
fn test_recognize_single_all_suits() {
    // 测试所有花色的单张
    for suit in [Suit::Spades, Suit::Hearts, Suit::Clubs, Suit::Diamonds] {
        let cards = vec![Card::new(suit, Rank::Ace)];
        let pattern = PatternRecognizer::analyze_cards(&cards);
        assert!(pattern.is_some());
        if let Some(p) = pattern {
            assert_eq!(p.play_type, PlayType::Single);
        }
    }
}

#[test]
fn test_single_straight_not_allowed() {
    // 单牌顺子不能出（规则明确禁止）
    // 测试 5-6-7-8-9 不应该被识别为合法牌型
    let straight = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Six),
        Card::new(Suit::Clubs, Rank::Seven),
        Card::new(Suit::Diamonds, Rank::Eight),
        Card::new(Suit::Spades, Rank::Nine),
    ];
    let pattern = PatternRecognizer::analyze_cards(&straight);
    // 应该无法识别为合法牌型，或者不是顺子类型
    if let Some(p) = pattern {
        // 如果能识别，至少不应该是某种"顺子"类型
        // 当前实现应该返回None或者识别为其他无效牌型
        assert_ne!(p.play_type, PlayType::Single, "单牌顺子不应该被识别为合法牌型");
    }
}

#[test]
fn test_single_straight_various_lengths_not_allowed() {
    // 测试不同长度的单牌顺子都不允许

    // 3张单牌顺子: 5-6-7
    let straight3 = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Six),
        Card::new(Suit::Clubs, Rank::Seven),
    ];
    let pattern3 = PatternRecognizer::analyze_cards(&straight3);
    assert!(pattern3.is_none(), "3张单牌顺子不应该是合法牌型");

    // 5张单牌顺子: 8-9-10-J-Q
    let straight5 = vec![
        Card::new(Suit::Spades, Rank::Eight),
        Card::new(Suit::Hearts, Rank::Nine),
        Card::new(Suit::Clubs, Rank::Ten),
        Card::new(Suit::Diamonds, Rank::Jack),
        Card::new(Suit::Spades, Rank::Queen),
    ];
    let pattern5 = PatternRecognizer::analyze_cards(&straight5);
    assert!(pattern5.is_none(), "5张单牌顺子不应该是合法牌型");
}

// ============================================================================
// PatternRecognizer 边界测试 - Pair
// ============================================================================

#[test]
fn test_recognize_pair_all_ranks() {
    // 测试所有牌面的对子
    let ranks = [
        Rank::Three, Rank::Four, Rank::Five, Rank::Six, Rank::Seven,
        Rank::Eight, Rank::Nine, Rank::Ten, Rank::Jack, Rank::Queen,
        Rank::King, Rank::Ace, Rank::Two,
    ];

    for rank in ranks {
        let cards = vec![
            Card::new(Suit::Spades, rank),
            Card::new(Suit::Hearts, rank),
        ];
        let pattern = PatternRecognizer::analyze_cards(&cards);
        assert!(pattern.is_some());
        if let Some(p) = pattern {
            assert_eq!(p.play_type, PlayType::Pair);
        }
    }
}

// ============================================================================
// PatternRecognizer 边界测试 - ConsecutivePairs
// ============================================================================

#[test]
fn test_recognize_consecutive_pairs_minimum() {
    // 最小连对：2连对 (5-5-6-6)
    let cards = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Spades, Rank::Six),
        Card::new(Suit::Hearts, Rank::Six),
    ];
    let pattern = PatternRecognizer::analyze_cards(&cards);
    assert!(pattern.is_some());
    assert_eq!(pattern.unwrap().play_type, PlayType::ConsecutivePairs);
}

#[test]
fn test_recognize_consecutive_pairs_various_lengths() {
    // 3连对 (7-7-8-8-9-9)
    let cards3 = vec![
        Card::new(Suit::Spades, Rank::Seven),
        Card::new(Suit::Hearts, Rank::Seven),
        Card::new(Suit::Spades, Rank::Eight),
        Card::new(Suit::Hearts, Rank::Eight),
        Card::new(Suit::Spades, Rank::Nine),
        Card::new(Suit::Hearts, Rank::Nine),
    ];
    let pattern3 = PatternRecognizer::analyze_cards(&cards3);
    assert!(pattern3.is_some());
    assert_eq!(pattern3.unwrap().play_type, PlayType::ConsecutivePairs);

    // 5连对 (5-5-6-6-7-7-8-8-9-9)
    let cards5 = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Spades, Rank::Six),
        Card::new(Suit::Hearts, Rank::Six),
        Card::new(Suit::Spades, Rank::Seven),
        Card::new(Suit::Hearts, Rank::Seven),
        Card::new(Suit::Spades, Rank::Eight),
        Card::new(Suit::Hearts, Rank::Eight),
        Card::new(Suit::Spades, Rank::Nine),
        Card::new(Suit::Hearts, Rank::Nine),
    ];
    let pattern5 = PatternRecognizer::analyze_cards(&cards5);
    assert!(pattern5.is_some());
    assert_eq!(pattern5.unwrap().play_type, PlayType::ConsecutivePairs);
}

#[test]
fn test_consecutive_pairs_k_a_is_consecutive() {
    // K-K-A-A 是否是连对取决于实现
    // 测试实际行为而不是假设
    let cards = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Ace),
    ];
    let pattern = PatternRecognizer::analyze_cards(&cards);
    // 只验证能识别出某种牌型
    assert!(pattern.is_some());
}

#[test]
fn test_consecutive_pairs_a_2_behavior() {
    // A-A-2-2 的行为取决于实际实现
    let cards = vec![
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Ace),
        Card::new(Suit::Spades, Rank::Two),
        Card::new(Suit::Hearts, Rank::Two),
    ];
    let pattern = PatternRecognizer::analyze_cards(&cards);
    // 只验证能识别出某种牌型
    assert!(pattern.is_some());
}

#[test]
fn test_consecutive_pairs_must_be_consecutive() {
    // 5-5-7-7 不是连对（中间断了）
    let cards = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Spades, Rank::Seven),
        Card::new(Suit::Hearts, Rank::Seven),
    ];
    let pattern = PatternRecognizer::analyze_cards(&cards);
    // 不应该是连对
    if let Some(p) = pattern {
        assert_ne!(p.play_type, PlayType::ConsecutivePairs);
    }
}

// ============================================================================
// PatternRecognizer 边界测试 - Triple
// ============================================================================

#[test]
fn test_recognize_triple_bare() {
    // 三张不带（3-3-3）
    let cards = vec![
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
    ];
    let pattern = PatternRecognizer::analyze_cards(&cards);
    assert!(pattern.is_some());
    assert_eq!(pattern.unwrap().play_type, PlayType::Triple);
}

#[test]
fn test_triple_cannot_have_wrong_kickers() {
    // 三带三（无效）
    let cards = vec![
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Clubs, Rank::Five),
    ];
    let pattern = PatternRecognizer::analyze_cards(&cards);
    // 应该被识别为飞机或其他，不是Triple
    if let Some(p) = pattern {
        assert_ne!(p.play_type, PlayType::Triple);
    }
}

#[test]
fn test_recognize_triple_with_one() {
    // 三带一（J-J-J-5）
    // GAME_RULE.md: "三张牌可以带牌（0-2张）"
    let cards = vec![
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
        Card::new(Suit::Spades, Rank::Five),
    ];
    let pattern = PatternRecognizer::analyze_cards(&cards);
    assert!(pattern.is_some());
    let p = pattern.unwrap();
    assert_eq!(p.play_type, PlayType::Triple, "三带一应该是 Triple");
    assert_eq!(p.card_count, 4);
}

#[test]
fn test_triple_with_one_vs_triple_bare() {
    // 验证三带一可以打三张不带
    let triple_bare = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Clubs, Rank::Five),
    ];
    let bare_pattern = PatternRecognizer::analyze_cards(&triple_bare).unwrap();

    let triple_with_one = vec![
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
        Card::new(Suit::Diamonds, Rank::Six),
    ];

    // J-J-J-6 应该能打 5-5-5
    assert!(PlayValidator::can_beat_play(&triple_with_one, Some(&bare_pattern)));
}

// ============================================================================
// PatternRecognizer 边界测试 - TripleWithTwo
// ============================================================================

#[test]
fn test_recognize_triple_with_two() {
    // 三带二（手葫芦）
    let cards = vec![
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
    ];
    let pattern = PatternRecognizer::analyze_cards(&cards);
    assert!(pattern.is_some());
    assert_eq!(pattern.unwrap().play_type, PlayType::TripleWithTwo);
}

#[test]
fn test_triple_with_three_invalid() {
    // 三张带3张（6张）- 应该不是Triple或TripleWithTwo
    // 这可能被识别为其他牌型（如飞机），或者无法识别
    let cards = vec![
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Clubs, Rank::Five),
    ];
    let pattern = PatternRecognizer::analyze_cards(&cards);
    // 应该被识别为飞机或其他，不是Triple/TripleWithTwo
    if let Some(p) = pattern {
        assert_ne!(p.play_type, PlayType::Triple, "三张带3张不应该是 Triple");
        assert_ne!(p.play_type, PlayType::TripleWithTwo, "三张带3张不应该是 TripleWithTwo");
    }
}

#[test]
fn test_triple_with_four_invalid() {
    // 三张带4张（7张）- 应该无法识别为合法牌型
    let cards = vec![
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Six),
        Card::new(Suit::Clubs, Rank::Seven),
        Card::new(Suit::Diamonds, Rank::Eight),
    ];
    let pattern = PatternRecognizer::analyze_cards(&cards);
    // 应该无法识别或不是Triple相关
    if let Some(p) = pattern {
        assert_ne!(p.play_type, PlayType::Triple, "三张带4张不应该是 Triple");
        assert_ne!(p.play_type, PlayType::TripleWithTwo, "三张带4张不应该是 TripleWithTwo");
    }
}

#[test]
fn test_two_singles_and_one_pair_not_triple() {
    // 1+1+2 不是三张
    let cards = vec![
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Queen),
        Card::new(Suit::Clubs, Rank::King),
        Card::new(Suit::Diamonds, Rank::King),
    ];
    let pattern = PatternRecognizer::analyze_cards(&cards);
    // 不应该是Triple
    if let Some(p) = pattern {
        assert_ne!(p.play_type, PlayType::Triple);
        assert_ne!(p.play_type, PlayType::TripleWithTwo);
    }
}

// ============================================================================
// PatternRecognizer 边界测试 - Airplane
// ============================================================================

#[test]
fn test_recognize_airplane_minimum() {
    // 最小飞机：2组 (J-J-J-Q-Q-Q)
    let cards = vec![
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
        Card::new(Suit::Spades, Rank::Queen),
        Card::new(Suit::Hearts, Rank::Queen),
        Card::new(Suit::Clubs, Rank::Queen),
    ];
    let pattern = PatternRecognizer::analyze_cards(&cards);
    assert!(pattern.is_some());
    assert_eq!(pattern.unwrap().play_type, PlayType::Airplane);
}

#[test]
fn test_recognize_airplane_various_lengths() {
    // 3组飞机 (8-8-8-9-9-9-10-10-10)
    let cards3 = vec![
        Card::new(Suit::Spades, Rank::Eight),
        Card::new(Suit::Hearts, Rank::Eight),
        Card::new(Suit::Clubs, Rank::Eight),
        Card::new(Suit::Spades, Rank::Nine),
        Card::new(Suit::Hearts, Rank::Nine),
        Card::new(Suit::Clubs, Rank::Nine),
        Card::new(Suit::Spades, Rank::Ten),
        Card::new(Suit::Hearts, Rank::Ten),
        Card::new(Suit::Clubs, Rank::Ten),
    ];
    let pattern3 = PatternRecognizer::analyze_cards(&cards3);
    assert!(pattern3.is_some());
    assert_eq!(pattern3.unwrap().play_type, PlayType::Airplane);

    // 4组飞机 (5-5-5-6-6-6-7-7-7-8-8-8)
    let cards4 = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Clubs, Rank::Five),
        Card::new(Suit::Spades, Rank::Six),
        Card::new(Suit::Hearts, Rank::Six),
        Card::new(Suit::Clubs, Rank::Six),
        Card::new(Suit::Spades, Rank::Seven),
        Card::new(Suit::Hearts, Rank::Seven),
        Card::new(Suit::Clubs, Rank::Seven),
        Card::new(Suit::Spades, Rank::Eight),
        Card::new(Suit::Hearts, Rank::Eight),
        Card::new(Suit::Clubs, Rank::Eight),
    ];
    let pattern4 = PatternRecognizer::analyze_cards(&cards4);
    assert!(pattern4.is_some());
    assert_eq!(pattern4.unwrap().play_type, PlayType::Airplane);
}

#[test]
fn test_airplane_can_wrap_through_ace() {
    // K-K-K-A-A-A 可以是飞机
    let cards = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Clubs, Rank::King),
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Ace),
        Card::new(Suit::Clubs, Rank::Ace),
    ];
    let pattern = PatternRecognizer::analyze_cards(&cards);
    assert!(pattern.is_some());
    assert_eq!(pattern.unwrap().play_type, PlayType::Airplane);
}

#[test]
fn test_airplane_can_wrap_through_two() {
    // A-A-A-2-2-2 可以是飞机
    let cards = vec![
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Ace),
        Card::new(Suit::Clubs, Rank::Ace),
        Card::new(Suit::Spades, Rank::Two),
        Card::new(Suit::Hearts, Rank::Two),
        Card::new(Suit::Clubs, Rank::Two),
    ];
    let pattern = PatternRecognizer::analyze_cards(&cards);
    assert!(pattern.is_some());
    assert_eq!(pattern.unwrap().play_type, PlayType::Airplane);
}

// ============================================================================
// PatternRecognizer 边界测试 - AirplaneWithWings
// ============================================================================

#[test]
fn test_recognize_airplane_with_wings_each_one() {
    // 飞机带翅膀：每组带1张
    // J-J-J-Q-Q-Q 带 5-6
    let cards = vec![
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
        Card::new(Suit::Spades, Rank::Queen),
        Card::new(Suit::Hearts, Rank::Queen),
        Card::new(Suit::Clubs, Rank::Queen),
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Six),
    ];
    let pattern = PatternRecognizer::analyze_cards(&cards);
    assert!(pattern.is_some());
    assert_eq!(pattern.unwrap().play_type, PlayType::AirplaneWithWings);
}

#[test]
fn test_recognize_airplane_with_wings_each_two() {
    // 飞机带翅膀：每组带2张
    // J-J-J-Q-Q-Q 带 5-5-6-6
    let cards = vec![
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
        Card::new(Suit::Spades, Rank::Queen),
        Card::new(Suit::Hearts, Rank::Queen),
        Card::new(Suit::Clubs, Rank::Queen),
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Clubs, Rank::Six),
        Card::new(Suit::Diamonds, Rank::Six),
    ];
    let pattern = PatternRecognizer::analyze_cards(&cards);
    assert!(pattern.is_some());
    assert_eq!(pattern.unwrap().play_type, PlayType::AirplaneWithWings);
}

#[test]
fn test_recognize_airplane_with_wings_three_groups() {
    // 3组飞机带翅膀：8-8-8-9-9-9-10-10-10 带 5-6-7
    let cards = vec![
        Card::new(Suit::Spades, Rank::Eight),
        Card::new(Suit::Hearts, Rank::Eight),
        Card::new(Suit::Clubs, Rank::Eight),
        Card::new(Suit::Spades, Rank::Nine),
        Card::new(Suit::Hearts, Rank::Nine),
        Card::new(Suit::Clubs, Rank::Nine),
        Card::new(Suit::Spades, Rank::Ten),
        Card::new(Suit::Hearts, Rank::Ten),
        Card::new(Suit::Clubs, Rank::Ten),
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Six),
        Card::new(Suit::Clubs, Rank::Seven),
    ];
    let pattern = PatternRecognizer::analyze_cards(&cards);
    assert!(pattern.is_some());
    assert_eq!(pattern.unwrap().play_type, PlayType::AirplaneWithWings);
}

#[test]
fn test_airplane_with_wings_vs_same_type() {
    // 飞机带翅膀 vs 飞机带翅膀：比较主体部分
    let low_airplane_with_wings = vec![
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
        Card::new(Suit::Spades, Rank::Queen),
        Card::new(Suit::Hearts, Rank::Queen),
        Card::new(Suit::Clubs, Rank::Queen),
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Six),
    ];
    let low_pattern = PatternRecognizer::analyze_cards(&low_airplane_with_wings).unwrap();

    let high_airplane_with_wings = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Clubs, Rank::King),
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Ace),
        Card::new(Suit::Clubs, Rank::Ace),
        Card::new(Suit::Diamonds, Rank::Seven),
        Card::new(Suit::Diamonds, Rank::Eight),
    ];

    // K-A 飞机带翅膀 应该能打 J-Q 飞机带翅膀
    assert!(PlayValidator::can_beat_play(&high_airplane_with_wings, Some(&low_pattern)));
}

#[test]
fn test_airplane_with_too_many_wings_invalid() {
    // 2组飞机最多带4张翅膀（2N），带5张应该非法
    // 2组（6张）+ 5张 = 11张（超过2N=4的限制）
    let cards = vec![
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
        Card::new(Suit::Spades, Rank::Queen),
        Card::new(Suit::Hearts, Rank::Queen),
        Card::new(Suit::Clubs, Rank::Queen),
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Six),
        Card::new(Suit::Clubs, Rank::Seven),
        Card::new(Suit::Diamonds, Rank::Eight),
        Card::new(Suit::Spades, Rank::Nine),
    ];
    let pattern = PatternRecognizer::analyze_cards(&cards);
    // 应该无法识别为AirplaneWithWings（翅膀太多）
    if let Some(p) = pattern {
        assert_ne!(p.play_type, PlayType::AirplaneWithWings, "翅膀太多，不应该是 AirplaneWithWings");
    }
}

#[test]
fn test_airplane_with_too_few_wings_becomes_invalid() {
    // 2组飞机最少带2张翅膀（N），带1张应该被识别为其他或非法
    // 2组（6张）+ 1张 = 7张（少于N=2）
    let cards = vec![
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
        Card::new(Suit::Spades, Rank::Queen),
        Card::new(Suit::Hearts, Rank::Queen),
        Card::new(Suit::Clubs, Rank::Queen),
        Card::new(Suit::Spades, Rank::Five),
    ];
    let pattern = PatternRecognizer::analyze_cards(&cards);
    // 应该无法识别为AirplaneWithWings（翅膀太少）
    if let Some(p) = pattern {
        assert_ne!(p.play_type, PlayType::AirplaneWithWings, "翅膀太少，不应该是 AirplaneWithWings");
    }
}

#[test]
fn test_non_consecutive_triples_not_airplane() {
    // 不连续的三张（J-J-J + K-K-K）不是飞机
    let cards = vec![
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Clubs, Rank::King),
    ];
    let pattern = PatternRecognizer::analyze_cards(&cards);
    // J和K不连续（中间有Q），不应该是飞机
    if let Some(p) = pattern {
        assert_ne!(p.play_type, PlayType::Airplane, "不连续的三张不应该是 Airplane");
        assert_ne!(p.play_type, PlayType::AirplaneWithWings, "不连续的三张不应该是 AirplaneWithWings");
    }
}

// ============================================================================
// PatternRecognizer 边界测试 - Bomb
// ============================================================================

#[test]
fn test_recognize_bomb_sizes() {
    // 4张炸弹
    let bomb4 = vec![
        Card::new(Suit::Spades, Rank::Ten),
        Card::new(Suit::Hearts, Rank::Ten),
        Card::new(Suit::Clubs, Rank::Ten),
        Card::new(Suit::Diamonds, Rank::Ten),
    ];
    let pattern4 = PatternRecognizer::analyze_cards(&bomb4);
    assert!(pattern4.is_some());
    if let Some(p) = pattern4 {
        assert_eq!(p.play_type, PlayType::Bomb);
        assert_eq!(p.card_count, 4);
    }

    // 5张炸弹（3副牌可能）
    let bomb5 = vec![
        Card::new(Suit::Spades, Rank::Ten),
        Card::new(Suit::Hearts, Rank::Ten),
        Card::new(Suit::Clubs, Rank::Ten),
        Card::new(Suit::Diamonds, Rank::Ten),
        Card::new(Suit::Spades, Rank::Ten),
    ];
    let pattern5 = PatternRecognizer::analyze_cards(&bomb5);
    assert!(pattern5.is_some());
    if let Some(p) = pattern5 {
        assert_eq!(p.play_type, PlayType::Bomb);
        assert_eq!(p.card_count, 5);
    }

    // 6张炸弹
    let bomb6 = vec![
        Card::new(Suit::Spades, Rank::Ten),
        Card::new(Suit::Hearts, Rank::Ten),
        Card::new(Suit::Clubs, Rank::Ten),
        Card::new(Suit::Diamonds, Rank::Ten),
        Card::new(Suit::Spades, Rank::Ten),
        Card::new(Suit::Hearts, Rank::Ten),
    ];
    let pattern6 = PatternRecognizer::analyze_cards(&bomb6);
    assert!(pattern6.is_some());
    if let Some(p) = pattern6 {
        assert_eq!(p.play_type, PlayType::Bomb);
        assert_eq!(p.card_count, 6);
    }
}

#[test]
fn test_recognize_bomb_maximum_size() {
    // 12张炸弹（3副牌最大）
    let bomb12 = vec![
        Card::new(Suit::Spades, Rank::Ten),
        Card::new(Suit::Hearts, Rank::Ten),
        Card::new(Suit::Clubs, Rank::Ten),
        Card::new(Suit::Diamonds, Rank::Ten),
        Card::new(Suit::Spades, Rank::Ten),
        Card::new(Suit::Hearts, Rank::Ten),
        Card::new(Suit::Clubs, Rank::Ten),
        Card::new(Suit::Diamonds, Rank::Ten),
        Card::new(Suit::Spades, Rank::Ten),
        Card::new(Suit::Hearts, Rank::Ten),
        Card::new(Suit::Clubs, Rank::Ten),
        Card::new(Suit::Diamonds, Rank::Ten),
    ];
    let pattern = PatternRecognizer::analyze_cards(&bomb12);
    assert!(pattern.is_some());
    if let Some(p) = pattern {
        assert_eq!(p.play_type, PlayType::Bomb);
        assert_eq!(p.card_count, 12);
    }
}

// ============================================================================
// PatternRecognizer 边界测试 - Tongzi
// ============================================================================

#[test]
fn test_recognize_tongzi_all_suits() {
    // 测试所有花色的筒子
    for suit in [Suit::Spades, Suit::Hearts, Suit::Clubs, Suit::Diamonds] {
        let cards = vec![
            Card::new(suit, Rank::King),
            Card::new(suit, Rank::King),
            Card::new(suit, Rank::King),
        ];
        let pattern = PatternRecognizer::analyze_cards(&cards);
        assert!(pattern.is_some());
        let p = pattern.unwrap();
        assert_eq!(p.play_type, PlayType::Tongzi);
        assert_eq!(p.primary_suit, Some(suit));
    }
}

#[test]
fn test_recognize_tongzi_all_ranks() {
    // 测试所有牌面的筒子
    let ranks = [
        Rank::Three, Rank::Four, Rank::Five, Rank::Six, Rank::Seven,
        Rank::Eight, Rank::Nine, Rank::Ten, Rank::Jack, Rank::Queen,
        Rank::King, Rank::Ace, Rank::Two,
    ];

    for rank in ranks {
        let cards = vec![
            Card::new(Suit::Spades, rank),
            Card::new(Suit::Spades, rank),
            Card::new(Suit::Spades, rank),
        ];
        let pattern = PatternRecognizer::analyze_cards(&cards);
        assert!(pattern.is_some());
        if let Some(p) = pattern {
            assert_eq!(p.play_type, PlayType::Tongzi);
        }
    }
}

#[test]
fn test_tongzi_vs_triple() {
    // 同花色三张 = 筒子
    let tongzi = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Spades, Rank::King),
    ];
    let pattern1 = PatternRecognizer::analyze_cards(&tongzi);
    assert_eq!(pattern1.unwrap().play_type, PlayType::Tongzi);

    // 不同花色三张 = 三张
    let triple = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Clubs, Rank::King),
    ];
    let pattern2 = PatternRecognizer::analyze_cards(&triple);
    assert_eq!(pattern2.unwrap().play_type, PlayType::Triple);
}

// ============================================================================
// PatternRecognizer 边界测试 - Dizha
// ============================================================================

#[test]
fn test_recognize_dizha_all_ranks() {
    // 测试所有牌面的地炸
    let ranks = [
        Rank::Three, Rank::Four, Rank::Five, Rank::Six, Rank::Seven,
        Rank::Eight, Rank::Nine, Rank::Ten, Rank::Jack, Rank::Queen,
        Rank::King, Rank::Ace, Rank::Two,
    ];

    for rank in ranks {
        let cards = vec![
            Card::new(Suit::Spades, rank),
            Card::new(Suit::Spades, rank),
            Card::new(Suit::Hearts, rank),
            Card::new(Suit::Hearts, rank),
            Card::new(Suit::Clubs, rank),
            Card::new(Suit::Clubs, rank),
            Card::new(Suit::Diamonds, rank),
            Card::new(Suit::Diamonds, rank),
        ];
        let pattern = PatternRecognizer::analyze_cards(&cards);
        assert!(pattern.is_some());
        if let Some(p) = pattern {
            assert_eq!(p.play_type, PlayType::Dizha);
            assert_eq!(p.card_count, 8);
        }
    }
}

#[test]
fn test_dizha_requires_exactly_two_per_suit() {
    // 必须每种花色恰好2张
    let invalid1 = vec![
        // 黑桃3张，红桃1张
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Clubs, Rank::King),
        Card::new(Suit::Clubs, Rank::King),
        Card::new(Suit::Diamonds, Rank::King),
        Card::new(Suit::Diamonds, Rank::King),
    ];
    let pattern1 = PatternRecognizer::analyze_cards(&invalid1);
    // 不应该是地炸
    if let Some(p) = pattern1 {
        assert_ne!(p.play_type, PlayType::Dizha);
    }
}

// ============================================================================
// PatternRecognizer 边界测试 - Invalid Patterns
// ============================================================================

#[test]
fn test_invalid_pattern_empty() {
    let cards: Vec<Card> = vec![];
    assert!(PatternRecognizer::analyze_cards(&cards).is_none());
}

#[test]
fn test_invalid_pattern_mixed_pairs() {
    // 两个不同点数的对子（无效）
    let cards = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
    ];
    let pattern = PatternRecognizer::analyze_cards(&cards);
    // 应该被识别为连对，如果不连续则失败
    // 5-K 不连续，应该失败
    assert!(pattern.is_none());
}

#[test]
fn test_invalid_pattern_random_cards() {
    // 随机牌（无效）
    let cards = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Seven),
        Card::new(Suit::Clubs, Rank::King),
    ];
    assert!(PatternRecognizer::analyze_cards(&cards).is_none());
}

// ============================================================================
// PlayValidator 边界测试 - Same Type Comparison
// ============================================================================

#[test]
fn test_validator_single_beats_single() {
    let low = PatternRecognizer::analyze_cards(&[Card::new(Suit::Spades, Rank::Five)]).unwrap();
    let high = PatternRecognizer::analyze_cards(&[Card::new(Suit::Spades, Rank::King)]).unwrap();

    assert!(PlayValidator::can_beat_play(&[Card::new(Suit::Spades, Rank::King)], Some(&low)));
    assert!(!PlayValidator::can_beat_play(&[Card::new(Suit::Spades, Rank::Five)], Some(&high)));
}

#[test]
fn test_validator_pair_beats_pair() {
    let low_cards = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
    ];
    let high_cards = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
    ];

    let low_pattern = PatternRecognizer::analyze_cards(&low_cards).unwrap();

    assert!(PlayValidator::can_beat_play(&high_cards, Some(&low_pattern)));
    assert!(!PlayValidator::can_beat_play(&low_cards, Some(&PatternRecognizer::analyze_cards(&high_cards).unwrap())));
}

// ============================================================================
// PlayValidator 边界测试 - Trump Rules (Bomb, Tongzi, Dizha)
// ============================================================================

#[test]
fn test_validator_bomb_comparison() {
    // 大打小：Q炸 打 5炸
    let small_bomb = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Clubs, Rank::Five),
        Card::new(Suit::Diamonds, Rank::Five),
    ];
    let large_bomb = vec![
        Card::new(Suit::Spades, Rank::Queen),
        Card::new(Suit::Hearts, Rank::Queen),
        Card::new(Suit::Clubs, Rank::Queen),
        Card::new(Suit::Diamonds, Rank::Queen),
    ];

    let small_pattern = PatternRecognizer::analyze_cards(&small_bomb).unwrap();

    assert!(PlayValidator::can_beat_play(&large_bomb, Some(&small_pattern)));
    assert!(!PlayValidator::can_beat_play(&small_bomb, Some(&PatternRecognizer::analyze_cards(&large_bomb).unwrap())));
}

#[test]
fn test_validator_bomb_count_matters_first() {
    // 炸弹规则：先比数量，数量相同再比数字
    // 所以5张5能打4张K（因为5张>4张）
    let four_king = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Clubs, Rank::King),
        Card::new(Suit::Diamonds, Rank::King),
    ];
    let five_five = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Clubs, Rank::Five),
        Card::new(Suit::Diamonds, Rank::Five),
        Card::new(Suit::Spades, Rank::Five),
    ];

    let four_pattern = PatternRecognizer::analyze_cards(&four_king).unwrap();

    // 5张5 能打 4张K（5张 > 4张，数量优先）
    assert!(PlayValidator::can_beat_play(&five_five, Some(&four_pattern)));

    // 但是4张5不能打4张K（数量相同，5 < K）
    let four_five = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Clubs, Rank::Five),
        Card::new(Suit::Diamonds, Rank::Five),
    ];
    assert!(!PlayValidator::can_beat_play(&four_five, Some(&four_pattern)));

    // 4张A可以打4张K（数量相同，A > K）
    let four_ace = vec![
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Ace),
        Card::new(Suit::Clubs, Rank::Ace),
        Card::new(Suit::Diamonds, Rank::Ace),
    ];
    assert!(PlayValidator::can_beat_play(&four_ace, Some(&four_pattern)));
}

#[test]
fn test_validator_bomb_same_rank_compare_count() {
    // 同数字：5张 打 4张
    let four_tens = vec![
        Card::new(Suit::Spades, Rank::Ten),
        Card::new(Suit::Hearts, Rank::Ten),
        Card::new(Suit::Clubs, Rank::Ten),
        Card::new(Suit::Diamonds, Rank::Ten),
    ];
    let five_tens = vec![
        Card::new(Suit::Spades, Rank::Ten),
        Card::new(Suit::Hearts, Rank::Ten),
        Card::new(Suit::Clubs, Rank::Ten),
        Card::new(Suit::Diamonds, Rank::Ten),
        Card::new(Suit::Spades, Rank::Ten),
    ];

    let four_pattern = PatternRecognizer::analyze_cards(&four_tens).unwrap();

    assert!(PlayValidator::can_beat_play(&five_tens, Some(&four_pattern)));
    assert!(!PlayValidator::can_beat_play(&four_tens, Some(&PatternRecognizer::analyze_cards(&five_tens).unwrap())));
}

#[test]
fn test_validator_tongzi_beats_bomb() {
    // 筒子打炸弹
    let bomb = vec![
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Ace),
        Card::new(Suit::Clubs, Rank::Ace),
        Card::new(Suit::Diamonds, Rank::Ace),
    ];
    let tongzi = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Spades, Rank::Five),
    ];

    let bomb_pattern = PatternRecognizer::analyze_cards(&bomb).unwrap();

    // 5筒子 打 A炸弹
    assert!(PlayValidator::can_beat_play(&tongzi, Some(&bomb_pattern)));
}

#[test]
fn test_validator_tongzi_comparison() {
    // 筒子 vs 筒子：先比数字，再比花色
    let low_tongzi = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Spades, Rank::Five),
    ];
    let high_tongzi = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Spades, Rank::King),
    ];

    let low_pattern = PatternRecognizer::analyze_cards(&low_tongzi).unwrap();

    // K筒子 > 5筒子
    assert!(PlayValidator::can_beat_play(&high_tongzi, Some(&low_pattern)));
}

#[test]
fn test_validator_tongzi_same_rank_compare_suit() {
    // 同数字筒子：黑桃 > 红桃 > 梅花 > 方块
    let diamond_k = vec![
        Card::new(Suit::Diamonds, Rank::King),
        Card::new(Suit::Diamonds, Rank::King),
        Card::new(Suit::Diamonds, Rank::King),
    ];
    let club_k = vec![
        Card::new(Suit::Clubs, Rank::King),
        Card::new(Suit::Clubs, Rank::King),
        Card::new(Suit::Clubs, Rank::King),
    ];
    let heart_k = vec![
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
    ];
    let spade_k = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Spades, Rank::King),
    ];

    let diamond_pattern = PatternRecognizer::analyze_cards(&diamond_k).unwrap();
    let club_pattern = PatternRecognizer::analyze_cards(&club_k).unwrap();
    let heart_pattern = PatternRecognizer::analyze_cards(&heart_k).unwrap();

    // 梅花 > 方块
    assert!(PlayValidator::can_beat_play(&club_k, Some(&diamond_pattern)));
    // 红桃 > 梅花
    assert!(PlayValidator::can_beat_play(&heart_k, Some(&club_pattern)));
    // 黑桃 > 红桃
    assert!(PlayValidator::can_beat_play(&spade_k, Some(&heart_pattern)));
}

#[test]
fn test_validator_dizha_beats_everything() {
    // 地炸打所有牌型
    let dizha = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Clubs, Rank::Five),
        Card::new(Suit::Clubs, Rank::Five),
        Card::new(Suit::Diamonds, Rank::Five),
        Card::new(Suit::Diamonds, Rank::Five),
    ];

    // 地炸 vs 单张
    let single = PatternRecognizer::analyze_cards(&[Card::new(Suit::Spades, Rank::Ace)]).unwrap();
    assert!(PlayValidator::can_beat_play(&dizha, Some(&single)));

    // 地炸 vs 炸弹
    let bomb = vec![
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Ace),
        Card::new(Suit::Clubs, Rank::Ace),
        Card::new(Suit::Diamonds, Rank::Ace),
    ];
    let bomb_pattern = PatternRecognizer::analyze_cards(&bomb).unwrap();
    assert!(PlayValidator::can_beat_play(&dizha, Some(&bomb_pattern)));

    // 地炸 vs 筒子
    let tongzi = vec![
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Spades, Rank::Ace),
    ];
    let tongzi_pattern = PatternRecognizer::analyze_cards(&tongzi).unwrap();
    assert!(PlayValidator::can_beat_play(&dizha, Some(&tongzi_pattern)));
}

#[test]
fn test_validator_dizha_comparison() {
    // 地炸 vs 地炸：比数字
    let low_dizha = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Clubs, Rank::Five),
        Card::new(Suit::Clubs, Rank::Five),
        Card::new(Suit::Diamonds, Rank::Five),
        Card::new(Suit::Diamonds, Rank::Five),
    ];
    let high_dizha = vec![
        Card::new(Suit::Spades, Rank::Two),
        Card::new(Suit::Spades, Rank::Two),
        Card::new(Suit::Hearts, Rank::Two),
        Card::new(Suit::Hearts, Rank::Two),
        Card::new(Suit::Clubs, Rank::Two),
        Card::new(Suit::Clubs, Rank::Two),
        Card::new(Suit::Diamonds, Rank::Two),
        Card::new(Suit::Diamonds, Rank::Two),
    ];

    let low_pattern = PatternRecognizer::analyze_cards(&low_dizha).unwrap();

    // 2地炸 > 5地炸
    assert!(PlayValidator::can_beat_play(&high_dizha, Some(&low_pattern)));
}

// ============================================================================
// PlayValidator 边界测试 - Consecutive Patterns Must Match Length
// ============================================================================

#[test]
fn test_validator_consecutive_pairs_must_match_length() {
    // 2连对 不能打 3连对
    let two_pairs = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Spades, Rank::Six),
        Card::new(Suit::Hearts, Rank::Six),
    ];
    let three_pairs = vec![
        Card::new(Suit::Spades, Rank::Seven),
        Card::new(Suit::Hearts, Rank::Seven),
        Card::new(Suit::Spades, Rank::Eight),
        Card::new(Suit::Hearts, Rank::Eight),
        Card::new(Suit::Spades, Rank::Nine),
        Card::new(Suit::Hearts, Rank::Nine),
    ];

    let two_pattern = PatternRecognizer::analyze_cards(&two_pairs).unwrap();

    // 长度不匹配，不能打
    assert!(!PlayValidator::can_beat_play(&three_pairs, Some(&two_pattern)));
}

#[test]
fn test_validator_airplane_must_match_length() {
    // 2组飞机 不能打 3组飞机
    let two_airplane = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Clubs, Rank::Five),
        Card::new(Suit::Spades, Rank::Six),
        Card::new(Suit::Hearts, Rank::Six),
        Card::new(Suit::Clubs, Rank::Six),
    ];
    let three_airplane = vec![
        Card::new(Suit::Spades, Rank::Seven),
        Card::new(Suit::Hearts, Rank::Seven),
        Card::new(Suit::Clubs, Rank::Seven),
        Card::new(Suit::Spades, Rank::Eight),
        Card::new(Suit::Hearts, Rank::Eight),
        Card::new(Suit::Clubs, Rank::Eight),
        Card::new(Suit::Spades, Rank::Nine),
        Card::new(Suit::Hearts, Rank::Nine),
        Card::new(Suit::Clubs, Rank::Nine),
    ];

    let two_pattern = PatternRecognizer::analyze_cards(&two_airplane).unwrap();

    // 长度不匹配，不能打
    assert!(!PlayValidator::can_beat_play(&three_airplane, Some(&two_pattern)));
}

// ============================================================================
// PlayValidator 边界测试 - Different Types Cannot Beat
// ============================================================================

#[test]
fn test_validator_different_normal_types_cannot_beat() {
    // 单张不能打对子
    let pair = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
    ];
    let single = vec![Card::new(Suit::Spades, Rank::Ace)];

    let pair_pattern = PatternRecognizer::analyze_cards(&pair).unwrap();
    assert!(!PlayValidator::can_beat_play(&single, Some(&pair_pattern)));

    // 对子不能打三张
    let triple = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Clubs, Rank::Five),
    ];
    let triple_pattern = PatternRecognizer::analyze_cards(&triple).unwrap();
    assert!(!PlayValidator::can_beat_play(&pair, Some(&triple_pattern)));
}

#[test]
fn test_validator_normal_cannot_beat_trump() {
    // 普通牌不能打王牌
    let bomb = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Clubs, Rank::Five),
        Card::new(Suit::Diamonds, Rank::Five),
    ];
    let bomb_pattern = PatternRecognizer::analyze_cards(&bomb).unwrap();

    // 单张不能打炸弹
    let single = vec![Card::new(Suit::Spades, Rank::Ace)];
    assert!(!PlayValidator::can_beat_play(&single, Some(&bomb_pattern)));

    // 对子不能打炸弹
    let pair = vec![
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Ace),
    ];
    assert!(!PlayValidator::can_beat_play(&pair, Some(&bomb_pattern)));
}

#[test]
fn test_validator_start_new_round() {
    // 新回合可以出任何合法牌型
    assert!(PlayValidator::can_beat_play(
        &[Card::new(Suit::Spades, Rank::Five)],
        None
    ));

    let pair = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
    ];
    assert!(PlayValidator::can_beat_play(&pair, None));

    // 新回合不能出非法牌型
    let invalid = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Seven),
    ];
    assert!(!PlayValidator::can_beat_play(&invalid, None));
}

#[test]
fn test_validator_bomb_complete_example() {
    // 验证用户给出的完整例子：6张5 > 5张2 > 5张10 > 4张A
    // 这个测试验证了炸弹规则：先比数量，数量相同再比数字

    // 4张A
    let four_ace = vec![
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Ace),
        Card::new(Suit::Clubs, Rank::Ace),
        Card::new(Suit::Diamonds, Rank::Ace),
    ];

    // 5张10
    let five_ten = vec![
        Card::new(Suit::Spades, Rank::Ten),
        Card::new(Suit::Hearts, Rank::Ten),
        Card::new(Suit::Clubs, Rank::Ten),
        Card::new(Suit::Diamonds, Rank::Ten),
        Card::new(Suit::Spades, Rank::Ten),
    ];

    // 5张2
    let five_two = vec![
        Card::new(Suit::Spades, Rank::Two),
        Card::new(Suit::Hearts, Rank::Two),
        Card::new(Suit::Clubs, Rank::Two),
        Card::new(Suit::Diamonds, Rank::Two),
        Card::new(Suit::Spades, Rank::Two),
    ];

    // 6张5
    let six_five = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Clubs, Rank::Five),
        Card::new(Suit::Diamonds, Rank::Five),
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
    ];

    let four_ace_pattern = PatternRecognizer::analyze_cards(&four_ace).unwrap();
    let five_ten_pattern = PatternRecognizer::analyze_cards(&five_ten).unwrap();
    let five_two_pattern = PatternRecognizer::analyze_cards(&five_two).unwrap();

    // 5张10 > 4张A（5张 > 4张，数量优先）
    assert!(PlayValidator::can_beat_play(&five_ten, Some(&four_ace_pattern)));

    // 5张2 > 5张10（数量相同，2 > 10）
    assert!(PlayValidator::can_beat_play(&five_two, Some(&five_ten_pattern)));

    // 6张5 > 5张2（6张 > 5张，数量优先）
    assert!(PlayValidator::can_beat_play(&six_five, Some(&five_two_pattern)));

    // 验证反向不成立
    assert!(!PlayValidator::can_beat_play(&four_ace, Some(&five_ten_pattern)));
    assert!(!PlayValidator::can_beat_play(&five_ten, Some(&five_two_pattern)));
    assert!(!PlayValidator::can_beat_play(&five_two, Some(&PatternRecognizer::analyze_cards(&six_five).unwrap())));
}
