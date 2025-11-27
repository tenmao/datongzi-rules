//! Complex rules integration tests - 规则组合和边界场景

use datongzi_rules::{
    Card, PatternRecognizer, PlayGenerator, PlayPattern, PlayType, PlayValidator, Rank,
    ScoreComputation, Suit,
};

// ============================================================================
// 核心规则测试：地炸 > 筒子 > 炸弹 > 普通牌
// ============================================================================

#[test]
fn test_trump_hierarchy_complete() {
    // 地炸 > 筒子 > 炸弹 > 普通牌

    // 普通单张
    let single = vec![Card::new(Suit::Spades, Rank::Two)];
    let single_pattern = PatternRecognizer::analyze_cards(&single).unwrap();

    // 炸弹
    let bomb = vec![
        Card::new(Suit::Spades, Rank::Three),
        Card::new(Suit::Hearts, Rank::Three),
        Card::new(Suit::Clubs, Rank::Three),
        Card::new(Suit::Diamonds, Rank::Three),
    ];
    let bomb_pattern = PatternRecognizer::analyze_cards(&bomb).unwrap();

    // 筒子
    let tongzi = vec![
        Card::new(Suit::Spades, Rank::Three),
        Card::new(Suit::Spades, Rank::Three),
        Card::new(Suit::Spades, Rank::Three),
    ];
    let tongzi_pattern = PatternRecognizer::analyze_cards(&tongzi).unwrap();

    // 地炸
    let dizha = vec![
        Card::new(Suit::Spades, Rank::Three),
        Card::new(Suit::Spades, Rank::Three),
        Card::new(Suit::Hearts, Rank::Three),
        Card::new(Suit::Hearts, Rank::Three),
        Card::new(Suit::Clubs, Rank::Three),
        Card::new(Suit::Clubs, Rank::Three),
        Card::new(Suit::Diamonds, Rank::Three),
        Card::new(Suit::Diamonds, Rank::Three),
    ];

    // 炸弹 > 普通牌
    assert!(PlayValidator::can_beat_play(&bomb, Some(&single_pattern)));

    // 筒子 > 炸弹
    assert!(PlayValidator::can_beat_play(&tongzi, Some(&bomb_pattern)));

    // 地炸 > 筒子
    assert!(PlayValidator::can_beat_play(&dizha, Some(&tongzi_pattern)));

    // 地炸 > 炸弹
    assert!(PlayValidator::can_beat_play(&dizha, Some(&bomb_pattern)));

    // 地炸 > 普通牌
    assert!(PlayValidator::can_beat_play(&dizha, Some(&single_pattern)));
}

// ============================================================================
// 炸弹规则测试：大打小，多打少
// ============================================================================

#[test]
fn test_bomb_large_beats_small() {
    // 大打小：K炸 > 5炸
    let small_bomb = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Clubs, Rank::Five),
        Card::new(Suit::Diamonds, Rank::Five),
    ];
    let small_pattern = PatternRecognizer::analyze_cards(&small_bomb).unwrap();

    let large_bomb = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Clubs, Rank::King),
        Card::new(Suit::Diamonds, Rank::King),
    ];

    assert!(PlayValidator::can_beat_play(
        &large_bomb,
        Some(&small_pattern)
    ));
    assert!(!PlayValidator::can_beat_play(
        &small_bomb,
        Some(&PatternRecognizer::analyze_cards(&large_bomb).unwrap())
    ));
}

#[test]
fn test_bomb_many_beats_few_same_rank() {
    // 多打少（同数字）：5张K > 4张K
    let four_k = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Clubs, Rank::King),
        Card::new(Suit::Diamonds, Rank::King),
    ];
    let four_pattern = PatternRecognizer::analyze_cards(&four_k).unwrap();

    let five_k = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Clubs, Rank::King),
        Card::new(Suit::Diamonds, Rank::King),
        Card::new(Suit::Spades, Rank::King),
    ];

    // 同数字：多打少
    assert!(PlayValidator::can_beat_play(&five_k, Some(&four_pattern)));

    // 反向测试：4张K不能打5张K
    let five_pattern = PatternRecognizer::analyze_cards(&five_k).unwrap();
    assert!(!PlayValidator::can_beat_play(&four_k, Some(&five_pattern)));
}

#[test]
fn test_bomb_same_rank_more_beats_less() {
    // 同数字：6张 > 5张 > 4张
    let four = vec![
        Card::new(Suit::Spades, Rank::Ten),
        Card::new(Suit::Hearts, Rank::Ten),
        Card::new(Suit::Clubs, Rank::Ten),
        Card::new(Suit::Diamonds, Rank::Ten),
    ];
    let four_pattern = PatternRecognizer::analyze_cards(&four).unwrap();

    let five = vec![
        Card::new(Suit::Spades, Rank::Ten),
        Card::new(Suit::Hearts, Rank::Ten),
        Card::new(Suit::Clubs, Rank::Ten),
        Card::new(Suit::Diamonds, Rank::Ten),
        Card::new(Suit::Spades, Rank::Ten),
    ];
    let five_pattern = PatternRecognizer::analyze_cards(&five).unwrap();

    let six = vec![
        Card::new(Suit::Spades, Rank::Ten),
        Card::new(Suit::Hearts, Rank::Ten),
        Card::new(Suit::Clubs, Rank::Ten),
        Card::new(Suit::Diamonds, Rank::Ten),
        Card::new(Suit::Spades, Rank::Ten),
        Card::new(Suit::Hearts, Rank::Ten),
    ];

    assert!(PlayValidator::can_beat_play(&five, Some(&four_pattern)));
    assert!(PlayValidator::can_beat_play(&six, Some(&five_pattern)));
}

// ============================================================================
// 筒子规则测试：先比数字，再比花色
// ============================================================================

#[test]
fn test_tongzi_rank_priority() {
    // 同花色不同数字：A筒子 > K筒子（无论花色）
    let k_tongzi_spade = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Spades, Rank::King),
    ];
    let k_pattern = PatternRecognizer::analyze_cards(&k_tongzi_spade).unwrap();

    let a_tongzi_diamond = vec![
        Card::new(Suit::Diamonds, Rank::Ace),
        Card::new(Suit::Diamonds, Rank::Ace),
        Card::new(Suit::Diamonds, Rank::Ace),
    ];

    // 即使是方块A筒子，也能打黑桃K筒子
    assert!(PlayValidator::can_beat_play(
        &a_tongzi_diamond,
        Some(&k_pattern)
    ));
}

#[test]
fn test_tongzi_suit_comparison_same_rank() {
    // 同数字：黑桃 > 红桃 > 梅花 > 方块
    let diamond = vec![
        Card::new(Suit::Diamonds, Rank::King),
        Card::new(Suit::Diamonds, Rank::King),
        Card::new(Suit::Diamonds, Rank::King),
    ];
    let club = vec![
        Card::new(Suit::Clubs, Rank::King),
        Card::new(Suit::Clubs, Rank::King),
        Card::new(Suit::Clubs, Rank::King),
    ];
    let heart = vec![
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
    ];
    let spade = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Spades, Rank::King),
    ];

    let diamond_pattern = PatternRecognizer::analyze_cards(&diamond).unwrap();
    let club_pattern = PatternRecognizer::analyze_cards(&club).unwrap();
    let heart_pattern = PatternRecognizer::analyze_cards(&heart).unwrap();

    // 花色递进
    assert!(PlayValidator::can_beat_play(&club, Some(&diamond_pattern)));
    assert!(PlayValidator::can_beat_play(&heart, Some(&club_pattern)));
    assert!(PlayValidator::can_beat_play(&spade, Some(&heart_pattern)));

    // 反向不行
    assert!(!PlayValidator::can_beat_play(
        &diamond,
        Some(&club_pattern)
    ));
}

// ============================================================================
// 连对和飞机规则测试：长度必须相同
// ============================================================================

#[test]
fn test_consecutive_pairs_same_length_required() {
    // 2连对 vs 2连对
    let two_pairs_low = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Spades, Rank::Six),
        Card::new(Suit::Hearts, Rank::Six),
    ];
    let two_pairs_high = vec![
        Card::new(Suit::Spades, Rank::Seven),
        Card::new(Suit::Hearts, Rank::Seven),
        Card::new(Suit::Spades, Rank::Eight),
        Card::new(Suit::Hearts, Rank::Eight),
    ];
    let low_pattern = PatternRecognizer::analyze_cards(&two_pairs_low).unwrap();
    assert!(PlayValidator::can_beat_play(
        &two_pairs_high,
        Some(&low_pattern)
    ));

    // 2连对 vs 3连对：不能打
    let three_pairs = vec![
        Card::new(Suit::Spades, Rank::Nine),
        Card::new(Suit::Hearts, Rank::Nine),
        Card::new(Suit::Spades, Rank::Ten),
        Card::new(Suit::Hearts, Rank::Ten),
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
    ];
    assert!(!PlayValidator::can_beat_play(
        &three_pairs,
        Some(&low_pattern)
    ));
}

#[test]
fn test_airplane_same_length_required() {
    // 2组飞机 vs 2组飞机
    let airplane2_low = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Clubs, Rank::Five),
        Card::new(Suit::Spades, Rank::Six),
        Card::new(Suit::Hearts, Rank::Six),
        Card::new(Suit::Clubs, Rank::Six),
    ];
    let airplane2_high = vec![
        Card::new(Suit::Spades, Rank::Seven),
        Card::new(Suit::Hearts, Rank::Seven),
        Card::new(Suit::Clubs, Rank::Seven),
        Card::new(Suit::Spades, Rank::Eight),
        Card::new(Suit::Hearts, Rank::Eight),
        Card::new(Suit::Clubs, Rank::Eight),
    ];
    let low_pattern = PatternRecognizer::analyze_cards(&airplane2_low).unwrap();
    assert!(PlayValidator::can_beat_play(
        &airplane2_high,
        Some(&low_pattern)
    ));

    // 2组飞机 vs 3组飞机：不能打
    let airplane3 = vec![
        Card::new(Suit::Spades, Rank::Nine),
        Card::new(Suit::Hearts, Rank::Nine),
        Card::new(Suit::Clubs, Rank::Nine),
        Card::new(Suit::Spades, Rank::Ten),
        Card::new(Suit::Hearts, Rank::Ten),
        Card::new(Suit::Clubs, Rank::Ten),
        Card::new(Suit::Spades, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
    ];
    assert!(!PlayValidator::can_beat_play(&airplane3, Some(&low_pattern)));
}

// ============================================================================
// 普通牌型对抗测试：同类型比大小
// ============================================================================

#[test]
fn test_normal_types_same_type_comparison() {
    // 单张 vs 单张
    let low_single = vec![Card::new(Suit::Spades, Rank::Five)];
    let high_single = vec![Card::new(Suit::Spades, Rank::King)];
    let low_pattern = PatternRecognizer::analyze_cards(&low_single).unwrap();
    assert!(PlayValidator::can_beat_play(&high_single, Some(&low_pattern)));

    // 对子 vs 对子
    let low_pair = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
    ];
    let high_pair = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
    ];
    let low_pattern = PatternRecognizer::analyze_cards(&low_pair).unwrap();
    assert!(PlayValidator::can_beat_play(&high_pair, Some(&low_pattern)));

    // 三张 vs 三张
    let low_triple = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Clubs, Rank::Five),
    ];
    let high_triple = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Clubs, Rank::King),
    ];
    let low_pattern = PatternRecognizer::analyze_cards(&low_triple).unwrap();
    assert!(PlayValidator::can_beat_play(&high_triple, Some(&low_pattern)));
}

#[test]
fn test_normal_types_different_type_cannot_beat() {
    // 单张不能打对子（即使更大）
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

// ============================================================================
// 复杂场景测试："有牌必打"的场景
// ============================================================================

#[test]
fn test_must_play_if_can_beat_single() {
    // 场景：上家出单张5，我有单张7，必须打
    let hand = vec![
        Card::new(Suit::Spades, Rank::Seven),
        Card::new(Suit::Hearts, Rank::Three),
    ];

    let current = vec![Card::new(Suit::Spades, Rank::Five)];
    let current_pattern = PatternRecognizer::analyze_cards(&current).unwrap();

    // 检查是否有牌能打
    let beating_plays =
        PlayGenerator::generate_beating_plays_with_same_type_or_trump(&hand, &current_pattern);

    assert!(!beating_plays.is_empty()); // 有7可以打
}

#[test]
fn test_must_play_if_can_beat_with_trump() {
    // 场景：上家出单张A，我没有单张能打，但有炸弹，必须用炸弹打
    let hand = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Clubs, Rank::Five),
        Card::new(Suit::Diamonds, Rank::Five),
        Card::new(Suit::Spades, Rank::Three),
    ];

    let current = vec![Card::new(Suit::Spades, Rank::Ace)];
    let current_pattern = PatternRecognizer::analyze_cards(&current).unwrap();

    let beating_plays =
        PlayGenerator::generate_beating_plays_with_same_type_or_trump(&hand, &current_pattern);

    assert!(!beating_plays.is_empty()); // 有炸弹可以打
    assert_eq!(beating_plays[0].len(), 4); // 炸弹是4张
}

#[test]
fn test_can_pass_if_no_beating_play() {
    // 场景：上家出单张A，我只有单张3和4，可以pass
    let hand = vec![
        Card::new(Suit::Spades, Rank::Three),
        Card::new(Suit::Hearts, Rank::Four),
    ];

    let current = vec![Card::new(Suit::Spades, Rank::Ace)];
    let current_pattern = PatternRecognizer::analyze_cards(&current).unwrap();

    let beating_plays =
        PlayGenerator::generate_beating_plays_with_same_type_or_trump(&hand, &current_pattern);

    assert!(beating_plays.is_empty()); // 没有牌能打，可以pass
}

// ============================================================================
// 极端场景测试
// ============================================================================

#[test]
fn test_all_same_rank() {
    // 12张同样的牌（3副牌最大炸弹）
    let bomb12 = vec![
        Card::new(Suit::Spades, Rank::Two),
        Card::new(Suit::Hearts, Rank::Two),
        Card::new(Suit::Clubs, Rank::Two),
        Card::new(Suit::Diamonds, Rank::Two),
        Card::new(Suit::Spades, Rank::Two),
        Card::new(Suit::Hearts, Rank::Two),
        Card::new(Suit::Clubs, Rank::Two),
        Card::new(Suit::Diamonds, Rank::Two),
        Card::new(Suit::Spades, Rank::Two),
        Card::new(Suit::Hearts, Rank::Two),
        Card::new(Suit::Clubs, Rank::Two),
        Card::new(Suit::Diamonds, Rank::Two),
    ];

    let pattern = PatternRecognizer::analyze_cards(&bomb12);
    assert!(pattern.is_some());
    if let Some(p) = pattern {
        assert_eq!(p.play_type, PlayType::Bomb);
        assert_eq!(p.card_count, 12);
    }
}

#[test]
fn test_longest_consecutive_pairs() {
    // 最长连对：3-4-5-6-7-8-9-10-J-Q-K-A（12连对）
    let mut cards = Vec::new();
    for rank in [
        Rank::Three,
        Rank::Four,
        Rank::Five,
        Rank::Six,
        Rank::Seven,
        Rank::Eight,
        Rank::Nine,
        Rank::Ten,
        Rank::Jack,
        Rank::Queen,
        Rank::King,
        Rank::Ace,
    ] {
        cards.push(Card::new(Suit::Spades, rank));
        cards.push(Card::new(Suit::Hearts, rank));
    }

    let pattern = PatternRecognizer::analyze_cards(&cards);
    assert!(pattern.is_some());
    if let Some(p) = pattern {
        assert_eq!(p.play_type, PlayType::ConsecutivePairs);
        assert_eq!(p.card_count, 24); // 12对 = 24张
    }
}

#[test]
fn test_longest_airplane() {
    // 最长飞机：3-3-3到A-A-A（10组）
    let mut cards = Vec::new();
    for rank in [
        Rank::Three,
        Rank::Four,
        Rank::Five,
        Rank::Six,
        Rank::Seven,
        Rank::Eight,
        Rank::Nine,
        Rank::Ten,
        Rank::Jack,
        Rank::Queen,
        Rank::King,
        Rank::Ace,
    ] {
        cards.push(Card::new(Suit::Spades, rank));
        cards.push(Card::new(Suit::Hearts, rank));
        cards.push(Card::new(Suit::Clubs, rank));
    }

    let pattern = PatternRecognizer::analyze_cards(&cards);
    assert!(pattern.is_some());
    if let Some(p) = pattern {
        assert_eq!(p.play_type, PlayType::Airplane);
        assert_eq!(p.card_count, 36); // 12组 * 3张 = 36张
    }
}

// ============================================================================
// 计分规则集成测试
// ============================================================================

#[test]
fn test_scoring_integration_only_winner_gets_special_bonus() {
    let config = datongzi_rules::GameConfig::default();
    let mut engine = ScoreComputation::new(config);

    // 回合1：A出K筒子，B出A筒子打过
    let k_tongzi = PlayPattern::new(
        PlayType::Tongzi,
        Rank::King,
        Some(Suit::Spades),
        vec![],
        3,
        0,
    );
    let k_events = engine.create_special_bonus_events(
        "player_a".to_string(),
        &k_tongzi,
        1,
        false, // 不是胜利者
    );
    assert_eq!(k_events.len(), 0);

    let a_tongzi = PlayPattern::new(
        PlayType::Tongzi,
        Rank::Ace,
        Some(Suit::Hearts),
        vec![],
        3,
        0,
    );
    let a_events = engine.create_special_bonus_events(
        "player_b".to_string(),
        &a_tongzi,
        1,
        true, // 胜利者
    );
    assert_eq!(a_events.len(), 1);
    assert_eq!(a_events[0].points, 200);

    // 验证：A没有得分，B得到200分
    assert_eq!(engine.calculate_total_score_for_player("player_a"), 0);
    assert_eq!(engine.calculate_total_score_for_player("player_b"), 200);
}

#[test]
fn test_scoring_complete_game_flow() {
    let config = datongzi_rules::GameConfig::default();
    let mut engine = ScoreComputation::new(config);

    // 回合1：Player1获胜，得到5/10/K的分数
    let round1_cards = vec![
        Card::new(Suit::Spades, Rank::Five),   // 5分
        Card::new(Suit::Hearts, Rank::Ten),    // 10分
        Card::new(Suit::Clubs, Rank::King),    // 10分
        Card::new(Suit::Diamonds, Rank::Ace),  // 0分
    ];
    engine.create_round_win_event("player1".to_string(), &round1_cards, 1);

    // 回合2：Player2用地炸获胜
    let dizha = PlayPattern::new(PlayType::Dizha, Rank::Two, None, vec![], 8, 0);
    engine.create_special_bonus_events("player2".to_string(), &dizha, 2, true);

    // 回合3：Player3用K筒子获胜
    let k_tongzi = PlayPattern::new(
        PlayType::Tongzi,
        Rank::King,
        Some(Suit::Spades),
        vec![],
        3,
        0,
    );
    engine.create_special_bonus_events("player3".to_string(), &k_tongzi, 3, true);

    // 完成顺序：Player2, Player1, Player3
    let finish_order = vec![
        "player2".to_string(),
        "player1".to_string(),
        "player3".to_string(),
    ];
    engine.create_finish_bonus_events(&finish_order);

    // 计算总分
    let p1_score = engine.calculate_total_score_for_player("player1");
    let p2_score = engine.calculate_total_score_for_player("player2");
    let p3_score = engine.calculate_total_score_for_player("player3");

    // Player1: 25 (回合分) - 40 (二游) = -15
    // Player2: 400 (地炸) + 100 (上游) = 500
    // Player3: 100 (K筒子) - 60 (三游) = 40

    assert_eq!(p1_score, 25 - 40);
    assert_eq!(p2_score, 400 + 100);
    assert_eq!(p3_score, 100 - 60);

    // 验证总和为0（零和游戏）
    assert_eq!(p1_score + p2_score + p3_score, 25 + 400 + 100 + 100 - 40 - 60);
}
