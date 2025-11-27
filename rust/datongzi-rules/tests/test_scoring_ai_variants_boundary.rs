//! Boundary tests for scoring, ai_helpers, and variants layers

use datongzi_rules::{
    Card, ConfigFactory, GameConfig, HandPatternAnalyzer, PlayGenerator, PlayPattern, PlayType,
    Rank, ScoreComputation, Suit, VariantValidator,
};

// ============================================================================
// Scoring 边界测试 - 关键规则：只有回合胜利者得分
// ============================================================================

#[test]
fn test_scoring_only_round_winner_gets_bonus() {
    let config = GameConfig::default();
    let mut engine = ScoreComputation::new(config);

    // 场景：A出K筒子，B出A筒子打过，C无牌可打
    // 结果：只有B（回合胜利者）得分，A不得分

    // A出K筒子（不是胜利者，不应得分）
    let k_tongzi = PlayPattern::new(
        PlayType::Tongzi,
        Rank::King,
        Some(Suit::Spades),
        vec![],
        3,
        0,
    );
    let events_a = engine.create_special_bonus_events(
        "player_a".to_string(),
        &k_tongzi,
        1,
        false, // 不是回合胜利者
    );
    assert_eq!(events_a.len(), 0); // 不得分

    // B出A筒子（回合胜利者，应得分）
    let a_tongzi = PlayPattern::new(
        PlayType::Tongzi,
        Rank::Ace,
        Some(Suit::Hearts),
        vec![],
        3,
        0,
    );
    let events_b = engine.create_special_bonus_events(
        "player_b".to_string(),
        &a_tongzi,
        1,
        true, // 回合胜利者
    );
    assert_eq!(events_b.len(), 1);
    assert_eq!(events_b[0].points, 200); // A筒子200分

    // 验证总分
    assert_eq!(engine.calculate_total_score_for_player("player_a"), 0);
    assert_eq!(engine.calculate_total_score_for_player("player_b"), 200);
}

#[test]
fn test_scoring_round_win_only_scores_5_10_k() {
    let config = GameConfig::default();
    let mut engine = ScoreComputation::new(config);

    // 回合中有5、10、K和其他牌
    let cards = vec![
        Card::new(Suit::Spades, Rank::Five),   // 5分
        Card::new(Suit::Hearts, Rank::Ten),    // 10分
        Card::new(Suit::Clubs, Rank::King),    // 10分
        Card::new(Suit::Diamonds, Rank::Ace),  // 0分
        Card::new(Suit::Spades, Rank::Two),    // 0分
        Card::new(Suit::Hearts, Rank::Jack),   // 0分
    ];

    let event = engine.create_round_win_event("player1".to_string(), &cards, 1);
    assert!(event.is_some());
    assert_eq!(event.unwrap().points, 25); // 5 + 10 + 10 = 25分
}

#[test]
fn test_scoring_multiple_special_bonuses_in_game() {
    let config = GameConfig::default();
    let mut engine = ScoreComputation::new(config);

    // 玩家A: K筒子
    let k_tongzi = PlayPattern::new(
        PlayType::Tongzi,
        Rank::King,
        Some(Suit::Spades),
        vec![],
        3,
        0,
    );
    engine.create_special_bonus_events("player_a".to_string(), &k_tongzi, 1, true);

    // 玩家B: A筒子
    let a_tongzi = PlayPattern::new(
        PlayType::Tongzi,
        Rank::Ace,
        Some(Suit::Hearts),
        vec![],
        3,
        0,
    );
    engine.create_special_bonus_events("player_b".to_string(), &a_tongzi, 2, true);

    // 玩家C: 地炸
    let dizha = PlayPattern::new(PlayType::Dizha, Rank::Two, None, vec![], 8, 0);
    engine.create_special_bonus_events("player_c".to_string(), &dizha, 3, true);

    // 验证分数
    assert_eq!(engine.calculate_total_score_for_player("player_a"), 100); // K筒子
    assert_eq!(engine.calculate_total_score_for_player("player_b"), 200); // A筒子
    assert_eq!(engine.calculate_total_score_for_player("player_c"), 400); // 地炸
}

#[test]
fn test_scoring_finish_bonuses() {
    let config = GameConfig::default();
    let mut engine = ScoreComputation::new(config);

    // 完成顺序：P1, P2, P3
    let finish_order = vec![
        "player1".to_string(),
        "player2".to_string(),
        "player3".to_string(),
    ];
    let events = engine.create_finish_bonus_events(&finish_order);

    assert_eq!(events.len(), 3);
    assert_eq!(events[0].points, 100);  // 上游 +100
    assert_eq!(events[1].points, -40);  // 二游 -40
    assert_eq!(events[2].points, -60);  // 三游 -60
}

#[test]
fn test_scoring_custom_config_bonuses() {
    // 自定义配置：不同的奖励分
    let config = GameConfig::new(
        3,
        3,
        41,
        9,
        vec![200, -100, -200],
        150, 250, 350, 500, // K=150, A=250, 2=350, Dizha=500
    );
    let mut engine = ScoreComputation::new(config);

    // K筒子
    let k_tongzi = PlayPattern::new(
        PlayType::Tongzi,
        Rank::King,
        Some(Suit::Spades),
        vec![],
        3,
        0,
    );
    let events = engine.create_special_bonus_events("player1".to_string(), &k_tongzi, 1, true);
    assert_eq!(events[0].points, 150);

    // 完成顺序
    let finish_order = vec!["p1".to_string(), "p2".to_string(), "p3".to_string()];
    let finish_events = engine.create_finish_bonus_events(&finish_order);
    assert_eq!(finish_events[0].points, 200);
    assert_eq!(finish_events[1].points, -100);
    assert_eq!(finish_events[2].points, -200);
}

#[test]
fn test_scoring_game_summary() {
    let config = GameConfig::default();
    let mut engine = ScoreComputation::new(config);

    // 回合得分
    let cards = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Ten),
    ];
    engine.create_round_win_event("player1".to_string(), &cards, 1);

    // 特殊奖励
    let tongzi = PlayPattern::new(
        PlayType::Tongzi,
        Rank::King,
        Some(Suit::Spades),
        vec![],
        3,
        0,
    );
    engine.create_special_bonus_events("player1".to_string(), &tongzi, 1, true);

    // 完成顺序
    let finish_order = vec!["player1".to_string(), "player2".to_string()];
    engine.create_finish_bonus_events(&finish_order);

    // 获取总结
    let summary = engine.get_game_summary(&finish_order);
    // 验证事件数量（实际数量取决于实现）
    assert!(summary.total_events >= 3); // 至少有3个事件
    assert!(summary.final_scores.contains_key("player1"));
    assert!(summary.final_scores.contains_key("player2"));
}

#[test]
fn test_scoring_negative_total_allowed() {
    let config = GameConfig::default();
    let mut engine = ScoreComputation::new(config);

    // 只有完成惩罚，没有得分
    let finish_order = vec!["player1".to_string(), "player2".to_string()];
    engine.create_finish_bonus_events(&finish_order);

    let score = engine.calculate_total_score_for_player("player2");
    assert!(score < 0); // 二游惩罚
}

// ============================================================================
// AI Helpers 边界测试 - PlayGenerator
// ============================================================================

#[test]
fn test_play_generator_single_card_hand() {
    let hand = vec![Card::new(Suit::Spades, Rank::Ace)];
    let count = PlayGenerator::count_all_plays(&hand);
    assert_eq!(count, 1); // 只能出这一张
}

#[test]
fn test_play_generator_no_valid_beating_play() {
    let hand = vec![
        Card::new(Suit::Spades, Rank::Three),
        Card::new(Suit::Hearts, Rank::Four),
    ];

    // 当前出牌：A单张
    let current = vec![Card::new(Suit::Spades, Rank::Ace)];
    let current_pattern = datongzi_rules::PatternRecognizer::analyze_cards(&current).unwrap();

    let beating_plays =
        PlayGenerator::generate_beating_plays_with_same_type_or_trump(&hand, &current_pattern);

    // 3和4都打不过A
    assert_eq!(beating_plays.len(), 0);
}

#[test]
fn test_play_generator_must_use_trump_to_beat() {
    let hand = vec![
        // 有炸弹
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Clubs, Rank::Five),
        Card::new(Suit::Diamonds, Rank::Five),
        // 单张不够大
        Card::new(Suit::Spades, Rank::Six),
    ];

    // 当前出牌：K单张
    let current = vec![Card::new(Suit::Spades, Rank::King)];
    let current_pattern = datongzi_rules::PatternRecognizer::analyze_cards(&current).unwrap();

    let beating_plays =
        PlayGenerator::generate_beating_plays_with_same_type_or_trump(&hand, &current_pattern);

    // 应该只有炸弹能打
    assert_eq!(beating_plays.len(), 1);
    assert_eq!(beating_plays[0].len(), 4);
}

#[test]
fn test_play_generator_count_explosion() {
    // 测试过多组合时的限制
    let mut hand = Vec::new();
    for rank in [Rank::Five, Rank::Six, Rank::Seven, Rank::Eight, Rank::Nine] {
        for _ in 0..3 {
            for suit in [Suit::Spades, Suit::Hearts, Suit::Clubs, Suit::Diamonds] {
                hand.push(Card::new(suit, rank));
            }
        }
    }

    // 组合数会非常大，应该触发限制
    let result = PlayGenerator::generate_all_plays(&hand, 100);
    assert!(result.is_err());
}

// ============================================================================
// AI Helpers 边界测试 - HandPatternAnalyzer
// ============================================================================

#[test]
fn test_hand_analyzer_priority_dizha_first() {
    // 有地炸时，优先识别地炸，不拆分成其他牌型
    let hand = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Hearts, Rank::King),
        Card::new(Suit::Clubs, Rank::King),
        Card::new(Suit::Clubs, Rank::King),
        Card::new(Suit::Diamonds, Rank::King),
        Card::new(Suit::Diamonds, Rank::King),
    ];

    let patterns = HandPatternAnalyzer::analyze_patterns(&hand);

    // 应该识别为地炸，不应该有炸弹或其他
    assert_eq!(patterns.dizha.len(), 1);
    assert_eq!(patterns.bombs.len(), 0);
    assert_eq!(patterns.tongzi.len(), 0);
    assert_eq!(patterns.trump_count, 1);
}

#[test]
fn test_hand_analyzer_priority_tongzi_over_triple() {
    // 同花色三张应该识别为筒子，不是普通三张
    let hand = vec![
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Spades, Rank::King),
        Card::new(Suit::Spades, Rank::King),
    ];

    let patterns = HandPatternAnalyzer::analyze_patterns(&hand);

    assert_eq!(patterns.tongzi.len(), 1);
    assert_eq!(patterns.triples.len(), 0);
    assert_eq!(patterns.trump_count, 1);
}

#[test]
fn test_hand_analyzer_priority_airplane_over_consecutive_pairs() {
    // 连续的三张（飞机）优先于连对
    let hand = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        Card::new(Suit::Clubs, Rank::Five),
        Card::new(Suit::Spades, Rank::Six),
        Card::new(Suit::Hearts, Rank::Six),
        Card::new(Suit::Clubs, Rank::Six),
    ];

    let patterns = HandPatternAnalyzer::analyze_patterns(&hand);

    assert_eq!(patterns.airplane_chains.len(), 1);
    assert_eq!(patterns.consecutive_pair_chains.len(), 0);
}

#[test]
fn test_hand_analyzer_no_overlap() {
    // 确保没有重叠：每张牌只属于一个牌型
    let hand = vec![
        // 炸弹
        Card::new(Suit::Spades, Rank::Ten),
        Card::new(Suit::Hearts, Rank::Ten),
        Card::new(Suit::Clubs, Rank::Ten),
        Card::new(Suit::Diamonds, Rank::Ten),
        // 对子
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Five),
        // 单张
        Card::new(Suit::Spades, Rank::King),
    ];

    let patterns = HandPatternAnalyzer::analyze_patterns(&hand);

    // 计算所有牌型的总卡牌数
    let total_in_patterns = patterns.dizha.iter().map(|d| d.len()).sum::<usize>()
        + patterns.tongzi.iter().map(|t| t.len()).sum::<usize>()
        + patterns.bombs.iter().map(|b| b.len()).sum::<usize>()
        + patterns
            .airplane_chains
            .iter()
            .map(|a| a.len())
            .sum::<usize>()
        + patterns
            .consecutive_pair_chains
            .iter()
            .map(|c| c.len())
            .sum::<usize>()
        + patterns.triples.iter().map(|t| t.len()).sum::<usize>()
        + patterns.pairs.iter().map(|p| p.len()).sum::<usize>()
        + patterns.singles.len();

    assert_eq!(total_in_patterns, patterns.total_cards);
}

#[test]
fn test_hand_analyzer_control_cards() {
    // 测试大牌检测
    let hand_with_two = vec![
        Card::new(Suit::Spades, Rank::Two),
        Card::new(Suit::Hearts, Rank::Five),
    ];
    let patterns1 = HandPatternAnalyzer::analyze_patterns(&hand_with_two);
    assert!(patterns1.has_control_cards);

    let hand_with_ace = vec![
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Five),
    ];
    let patterns2 = HandPatternAnalyzer::analyze_patterns(&hand_with_ace);
    assert!(patterns2.has_control_cards);

    let hand_no_control = vec![
        Card::new(Suit::Spades, Rank::Five),
        Card::new(Suit::Hearts, Rank::Six),
    ];
    let patterns3 = HandPatternAnalyzer::analyze_patterns(&hand_no_control);
    assert!(!patterns3.has_control_cards);
}

// ============================================================================
// Variants 边界测试 - ConfigFactory
// ============================================================================

#[test]
fn test_config_factory_all_variants() {
    // 测试所有预设变体
    let configs = vec![
        ("standard_3deck_3player", ConfigFactory::create_standard_3deck_3player(), true),
        ("4deck_4player", ConfigFactory::create_4deck_4player(), true),
        ("2player", ConfigFactory::create_2player(), true),
        ("quick_game", ConfigFactory::create_quick_game(), false), // 可能有warning（不平均分配）
        ("high_stakes", ConfigFactory::create_high_stakes(), true),
        ("beginner_friendly", ConfigFactory::create_beginner_friendly(), true),
    ];

    for (name, config, should_be_valid) in configs {
        let (is_valid, warnings) = VariantValidator::validate_config(&config);
        if should_be_valid && !is_valid {
            panic!("Config {} failed validation with warnings: {:?}", name, warnings);
        }
        // 所有配置至少应该能通过GameConfig.validate()
        assert!(config.validate().is_ok(), "Config {} failed GameConfig.validate()", name);
    }
}

#[test]
fn test_config_factory_standard_3deck_3player() {
    let config = ConfigFactory::create_standard_3deck_3player();

    assert_eq!(config.num_decks(), 3);
    assert_eq!(config.num_players(), 3);
    assert_eq!(config.cards_per_player(), 41);
    assert_eq!(config.cards_dealt_aside(), 9);
}

#[test]
fn test_config_factory_2player() {
    let config = ConfigFactory::create_2player();

    assert_eq!(config.num_decks(), 3);
    assert_eq!(config.num_players(), 2);
}

#[test]
fn test_config_factory_4deck_4player() {
    let config = ConfigFactory::create_4deck_4player();

    assert_eq!(config.num_decks(), 4);
    assert_eq!(config.num_players(), 4);
}

#[test]
fn test_config_factory_quick_game() {
    let config = ConfigFactory::create_quick_game();

    assert_eq!(config.num_decks(), 2);
    assert_eq!(config.num_players(), 3);
}

#[test]
fn test_config_factory_high_stakes() {
    let config = ConfigFactory::create_high_stakes();

    assert_eq!(config.k_tongzi_bonus(), 200);
    assert_eq!(config.dizha_bonus(), 800);
}

// ============================================================================
// Variants 边界测试 - VariantValidator
// ============================================================================

#[test]
fn test_variant_validator_valid_configs() {
    // 所有预设变体都应该通过验证
    let configs = vec![
        ConfigFactory::create_standard_3deck_3player(),
        ConfigFactory::create_2player(),
        ConfigFactory::create_4deck_4player(),
    ];

    for config in configs {
        let (is_valid, _) = VariantValidator::validate_config(&config);
        assert!(is_valid);
    }
}

#[test]
fn test_variant_validator_invalid_num_players() {
    // 注意：0人会导致除以0错误，所以使用1人（也是无效的）
    let invalid = GameConfig::new(
        3,
        1, // 无效：1人（至少需要2人）
        41,
        9,
        vec![100], // 1人的finish_bonus
        100,
        200,
        300,
        400,
    );

    // GameConfig.validate()会检查玩家数必须在2-4之间
    assert!(invalid.validate().is_err());
}

#[test]
fn test_variant_validator_invalid_card_distribution() {
    let invalid = GameConfig::new(
        1,  // 1副牌 = 52张
        3,  // 3人
        50, // 每人50张 = 150张 > 52张
        0,
        vec![100, -40, -60],
        100,
        200,
        300,
        400,
    );

    let (is_valid, warnings) = VariantValidator::validate_config(&invalid);
    assert!(!is_valid);
    assert!(!warnings.is_empty());
}

#[test]
fn test_variant_validator_finish_bonus_mismatch() {
    let invalid = GameConfig::new(
        3,
        3,  // 3人
        41,
        9,
        vec![100, -40], // 只有2个奖励，但有3人
        100,
        200,
        300,
        400,
    );

    let (is_valid, warnings) = VariantValidator::validate_config(&invalid);
    assert!(!is_valid);
    assert!(!warnings.is_empty());
}

#[test]
fn test_variant_validator_edge_case_valid() {
    // 边界但有效的配置
    let edge = GameConfig::new(
        1,  // 1副牌
        2,  // 2人
        26, // 每人26张
        0,  // 无铺底
        vec![50, -50],
        100,
        200,
        300,
        400,
    );

    let (is_valid, _) = VariantValidator::validate_config(&edge);
    assert!(is_valid);
}
