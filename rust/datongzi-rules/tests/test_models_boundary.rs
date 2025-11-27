//! Boundary tests for models layer

use datongzi_rules::{Card, Deck, GameConfig, Rank, Suit};

// ============================================================================
// Card 边界测试
// ============================================================================

#[test]
fn test_card_equality() {
    let card1 = Card::new(Suit::Spades, Rank::Ace);
    let card2 = Card::new(Suit::Spades, Rank::Ace);
    let card3 = Card::new(Suit::Hearts, Rank::Ace);

    assert_eq!(card1, card2);
    assert_ne!(card1, card3);
}

#[test]
fn test_card_ordering() {
    // 同花色：2 > A > K > ... > 5
    let two = Card::new(Suit::Spades, Rank::Two);
    let ace = Card::new(Suit::Spades, Rank::Ace);
    let king = Card::new(Suit::Spades, Rank::King);
    let five = Card::new(Suit::Spades, Rank::Five);

    assert!(two > ace);
    assert!(ace > king);
    assert!(king > five);
}

#[test]
fn test_all_scoring_cards() {
    // 测试所有计分牌
    let five_spades = Card::new(Suit::Spades, Rank::Five);
    let five_hearts = Card::new(Suit::Hearts, Rank::Five);
    let ten_clubs = Card::new(Suit::Clubs, Rank::Ten);
    let ten_diamonds = Card::new(Suit::Diamonds, Rank::Ten);
    let king_spades = Card::new(Suit::Spades, Rank::King);
    let king_hearts = Card::new(Suit::Hearts, Rank::King);

    // 5分
    assert!(five_spades.is_scoring_card());
    assert_eq!(five_spades.score_value(), 5);
    assert!(five_hearts.is_scoring_card());
    assert_eq!(five_hearts.score_value(), 5);

    // 10分
    assert!(ten_clubs.is_scoring_card());
    assert_eq!(ten_clubs.score_value(), 10);
    assert!(ten_diamonds.is_scoring_card());
    assert_eq!(ten_diamonds.score_value(), 10);

    // K = 10分
    assert!(king_spades.is_scoring_card());
    assert_eq!(king_spades.score_value(), 10);
    assert!(king_hearts.is_scoring_card());
    assert_eq!(king_hearts.score_value(), 10);
}

#[test]
fn test_all_non_scoring_cards() {
    // 测试所有非计分牌
    for rank in [
        Rank::Six,
        Rank::Seven,
        Rank::Eight,
        Rank::Nine,
        Rank::Jack,
        Rank::Queen,
        Rank::Ace,
        Rank::Two,
    ] {
        let card = Card::new(Suit::Spades, rank);
        assert!(!card.is_scoring_card());
        assert_eq!(card.score_value(), 0);
    }
}

// ============================================================================
// Rank 边界测试
// ============================================================================

#[test]
fn test_rank_values() {
    // 测试所有牌面值: Two=15最大
    assert_eq!(Rank::Two.value(), 15);
    assert_eq!(Rank::Ace.value(), 14);
    assert_eq!(Rank::King.value(), 13);
    assert_eq!(Rank::Queen.value(), 12);
    assert_eq!(Rank::Jack.value(), 11);
    assert_eq!(Rank::Ten.value(), 10);
    assert_eq!(Rank::Nine.value(), 9);
    assert_eq!(Rank::Eight.value(), 8);
    assert_eq!(Rank::Seven.value(), 7);
    assert_eq!(Rank::Six.value(), 6);
    assert_eq!(Rank::Five.value(), 5);
    assert_eq!(Rank::Four.value(), 4);
    assert_eq!(Rank::Three.value(), 3);
}

#[test]
fn test_rank_ordering() {
    // 2 > A > K > Q > J > 10 > 9 > 8 > 7 > 6 > 5 > 4 > 3
    assert!(Rank::Two > Rank::Ace);
    assert!(Rank::Ace > Rank::King);
    assert!(Rank::King > Rank::Queen);
    assert!(Rank::Queen > Rank::Jack);
    assert!(Rank::Jack > Rank::Ten);
    assert!(Rank::Ten > Rank::Nine);
    assert!(Rank::Nine > Rank::Eight);
    assert!(Rank::Eight > Rank::Seven);
    assert!(Rank::Seven > Rank::Six);
    assert!(Rank::Six > Rank::Five);
    assert!(Rank::Five > Rank::Four);
    assert!(Rank::Four > Rank::Three);
}

// ============================================================================
// Suit 边界测试
// ============================================================================

#[test]
fn test_suit_values() {
    // 黑桃 > 红桃 > 梅花 > 方块
    assert_eq!(Suit::Spades.value(), 4);
    assert_eq!(Suit::Hearts.value(), 3);
    assert_eq!(Suit::Clubs.value(), 2);
    assert_eq!(Suit::Diamonds.value(), 1);
}

#[test]
fn test_suit_ordering() {
    // 黑桃 > 红桃 > 梅花 > 方块
    assert!(Suit::Spades > Suit::Hearts);
    assert!(Suit::Hearts > Suit::Clubs);
    assert!(Suit::Clubs > Suit::Diamonds);
}

// ============================================================================
// Deck 边界测试
// ============================================================================

#[test]
fn test_deck_single_deck() {
    let deck = Deck::new(1, &[]);
    assert_eq!(deck.remaining(), 52);
}

#[test]
fn test_deck_multiple_decks() {
    // 1副牌
    let deck1 = Deck::new(1, &[]);
    assert_eq!(deck1.remaining(), 52);

    // 2副牌
    let deck2 = Deck::new(2, &[]);
    assert_eq!(deck2.remaining(), 104);

    // 3副牌
    let deck3 = Deck::new(3, &[]);
    assert_eq!(deck3.remaining(), 156);

    // 8副牌（极限）
    let deck8 = Deck::new(8, &[]);
    assert_eq!(deck8.remaining(), 416);
}

#[test]
fn test_deck_remove_ranks() {
    // 标准3副牌去掉3、4
    let deck = Deck::new(3, &[Rank::Three, Rank::Four]);
    // 3副牌 = 156张，去掉3、4 = 去掉24张（每副牌各4张，共8张）
    assert_eq!(deck.remaining(), 156 - 24);

    // 去掉3、4、5、6
    let deck2 = Deck::new(3, &[Rank::Three, Rank::Four, Rank::Five, Rank::Six]);
    assert_eq!(deck2.remaining(), 156 - 48);

    // 去掉所有牌（极端情况）
    let all_ranks = [
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
        Rank::Two,
    ];
    let empty_deck = Deck::new(1, &all_ranks);
    assert_eq!(empty_deck.remaining(), 0);
}

#[test]
fn test_deck_deal_exact() {
    let mut deck = Deck::new(1, &[]);

    // 发13张
    let hand1 = deck.deal(13);
    assert_eq!(hand1.len(), 13);
    assert_eq!(deck.remaining(), 39);

    // 再发13张
    let hand2 = deck.deal(13);
    assert_eq!(hand2.len(), 13);
    assert_eq!(deck.remaining(), 26);

    // 发完所有牌
    let hand3 = deck.deal(26);
    assert_eq!(hand3.len(), 26);
    assert_eq!(deck.remaining(), 0);
}

#[test]
fn test_deck_deal_exact_amount() {
    let mut deck = Deck::new(1, &[]);

    // 发50张（还剩2张）
    let hand1 = deck.deal(50);
    assert_eq!(hand1.len(), 50);
    assert_eq!(deck.remaining(), 2);

    // 再发2张（正好发完）
    let hand2 = deck.deal(2);
    assert_eq!(hand2.len(), 2);
    assert_eq!(deck.remaining(), 0);
}

#[test]
fn test_deck_deal_zero() {
    let mut deck = Deck::new(1, &[]);

    let hand = deck.deal(0);
    assert_eq!(hand.len(), 0);
    assert_eq!(deck.remaining(), 52);
}

#[test]
fn test_deck_deal_exactly_all() {
    let mut deck = Deck::new(1, &[]);

    // 正好发完所有牌
    let hand = deck.deal(52);
    assert_eq!(hand.len(), 52);
    assert_eq!(deck.remaining(), 0);
}

#[test]
fn test_deck_shuffle_changes_order() {
    let mut deck1 = Deck::new(1, &[]);
    let mut deck2 = Deck::new(1, &[]);

    // 不洗牌，发牌顺序应该相同
    let hand1_before = deck1.deal(10);
    let hand2_before = deck2.deal(10);
    assert_eq!(hand1_before, hand2_before);

    // 洗牌后，发牌顺序大概率不同（注意：理论上有极小概率相同）
    let mut deck3 = Deck::new(1, &[]);
    let mut deck4 = Deck::new(1, &[]);
    deck3.shuffle();
    deck4.shuffle();

    let hand3 = deck3.deal(10);
    let hand4 = deck4.deal(10);

    // 两次洗牌结果大概率不同
    // 注意：这个测试有极小概率失败（概率约为 1/52!)
    assert_ne!(hand3, hand4);
}

// ============================================================================
// GameConfig 边界测试
// ============================================================================

#[test]
fn test_game_config_default() {
    let config = GameConfig::default();

    // 默认配置：3副牌，3人，41张手牌，9张铺底
    assert_eq!(config.num_decks(), 3);
    assert_eq!(config.num_players(), 3);
    assert_eq!(config.cards_per_player(), 41);
    assert_eq!(config.cards_dealt_aside(), 9);

    // 验证默认去掉的牌：3和4
    assert_eq!(config.removed_ranks(), &[Rank::Three, Rank::Four]);

    // 验证默认奖励分
    assert_eq!(config.k_tongzi_bonus(), 100);
    assert_eq!(config.a_tongzi_bonus(), 200);
    assert_eq!(config.two_tongzi_bonus(), 300);
    assert_eq!(config.dizha_bonus(), 400);

    // 默认配置应该有效
    assert!(config.validate().is_ok());
}

#[test]
fn test_game_config_custom_valid() {
    // 2人对战
    let config2p = GameConfig::new(
        2,                   // 2副牌
        2,                   // 2人
        47,                  // 每人47张
        10,                  // 铺底10张
        vec![50, -50],       // 完成奖励
        150, 250, 350, 500,  // 特殊奖励
    );
    assert!(config2p.validate().is_ok());

    // 4副牌4人
    let config4p = GameConfig::new(
        4,                         // 4副牌
        4,                         // 4人
        46,                        // 每人46张
        16,                        // 铺底16张
        vec![100, -30, -50, -70],  // 完成奖励
        100, 200, 300, 400,        // 特殊奖励
    );
    assert!(config4p.validate().is_ok());
}

#[test]
fn test_game_config_invalid_num_decks() {
    // 0副牌（无效）
    let config = GameConfig::new(
        0,
        3,
        44,
        9,
        vec![100, -40, -60],
        100, 200, 300, 400,
    );
    assert!(config.validate().is_err());

    // 负数副牌（无效）
    // 注意：由于 num_decks 是 usize，不能为负数，这里不需要测试
}

#[test]
fn test_game_config_invalid_num_players() {
    // 1人游戏（无效，至少2人）
    let config = GameConfig::new(
        3,
        1,
        44,
        9,
        vec![100],
        100, 200, 300, 400,
    );
    assert!(config.validate().is_err());

    // 0人游戏（无效）
    let config2 = GameConfig::new(
        3,
        0,
        44,
        9,
        vec![],
        100, 200, 300, 400,
    );
    assert!(config2.validate().is_err());
}

#[test]
fn test_game_config_invalid_card_distribution() {
    // 手牌数超过总牌数
    let config = GameConfig::new(
        1,  // 1副牌 = 52张
        3,  // 3人
        20, // 每人20张 = 60张 > 52张
        0,
        vec![100, -40, -60],
        100, 200, 300, 400,
    );
    assert!(config.validate().is_err());

    // 手牌数 + 铺底 > 总牌数
    let config2 = GameConfig::new(
        1,   // 1副牌 = 52张
        2,   // 2人
        20,  // 每人20张 = 40张
        20,  // 铺底20张，总共60张 > 52张
        vec![100, -100],
        100, 200, 300, 400,
    );
    assert!(config2.validate().is_err());
}

#[test]
fn test_game_config_finish_bonus_length_mismatch() {
    // finish_bonus 长度必须与玩家数匹配

    // 长度不足：2个奖励但有3人
    let config = GameConfig::new(
        3,
        3,  // 3人
        41,
        9,
        vec![100, -40], // 只有2个奖励
        100, 200, 300, 400,
    );
    assert!(config.validate().is_err());

    // 空奖励列表
    let config2 = GameConfig::new(
        3,
        3,
        41,
        9,
        vec![], // 空列表
        100, 200, 300, 400,
    );
    assert!(config2.validate().is_err());

    // 长度过多：4个奖励但只有3人
    let config3 = GameConfig::new(
        3,
        3,
        41,
        9,
        vec![100, -40, -60, -100], // 4个奖励
        100, 200, 300, 400,
    );
    assert!(config3.validate().is_err());

    // 正确长度：3个奖励，3人
    let config4 = GameConfig::new(
        3,
        3,
        41,
        9,
        vec![100, -40, -60], // 3个奖励
        100, 200, 300, 400,
    );
    assert!(config4.validate().is_ok());
}

#[test]
fn test_game_config_edge_cases() {
    // 最小有效配置：2人，1副牌，每人26张，0张铺底
    let min_config = GameConfig::new(
        1,
        2,
        26,
        0,
        vec![50, -50],
        100, 200, 300, 400,
    );
    assert!(min_config.validate().is_ok());

    // 大型游戏：4副牌，4人（最多4人）
    let large_config = GameConfig::new(
        4,
        4,  // 最多4人
        48,
        16,
        vec![100, -20, -40, -80],
        100, 200, 300, 400,
    );
    assert!(large_config.validate().is_ok());
}

#[test]
fn test_game_config_zero_bonuses() {
    // 所有奖励分为0（有效，但不常见）
    let config = GameConfig::new(
        3,
        3,
        44,
        9,
        vec![0, 0, 0],
        0, 0, 0, 0,
    );
    assert!(config.validate().is_ok());
}

#[test]
fn test_game_config_negative_bonuses() {
    // 所有完成奖励为负（罕见但有效）
    let config = GameConfig::new(
        3,
        3,
        44,
        9,
        vec![-100, -200, -300],
        100, 200, 300, 400,
    );
    assert!(config.validate().is_ok());
}

#[test]
fn test_game_config_removed_ranks_default() {
    // 测试默认配置去掉3和4
    let config = GameConfig::new(
        3,
        3,
        41,
        9,
        vec![100, -40, -60],
        100, 200, 300, 400,
    );
    // new()默认去掉3和4
    assert_eq!(config.removed_ranks(), &[Rank::Three, Rank::Four]);
}

#[test]
fn test_game_config_removed_ranks_custom() {
    // 测试自定义去掉的牌
    let config = GameConfig::new_with_removed_ranks(
        2,
        2,
        40,
        8,
        vec![Rank::Three, Rank::Four, Rank::Five, Rank::Six], // 去掉3、4、5、6
        vec![100, -100],
        100, 200, 300, 400,
    );
    assert_eq!(
        config.removed_ranks(),
        &[Rank::Three, Rank::Four, Rank::Five, Rank::Six]
    );
}

#[test]
fn test_game_config_removed_ranks_empty() {
    // 测试不去掉任何牌（使用全部52张）
    let config = GameConfig::new_with_removed_ranks(
        1,
        2,
        26,
        0,
        vec![], // 不去掉任何牌
        vec![50, -50],
        100, 200, 300, 400,
    );
    assert_eq!(config.removed_ranks(), &[]);
}

#[test]
fn test_game_config_removed_ranks_integration_with_deck() {
    // 验证removed_ranks与Deck配合使用
    let config = GameConfig::default();

    // 使用config创建Deck
    let deck = Deck::new(config.num_decks(), config.removed_ranks());

    // 3副牌 = 156张，去掉3和4 = 去掉24张（每副牌8张，共24张）
    assert_eq!(deck.remaining(), 156 - 24);
}
