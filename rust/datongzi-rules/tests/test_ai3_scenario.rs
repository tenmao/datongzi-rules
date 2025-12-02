//! Test AI3 Round 2 scenario from game 5ccd1721
//! Verifies fix: Rank::Two should not participate in consecutive structures

use datongzi_rules::{Card, HandPatternAnalyzer, Rank, Suit};

#[test]
fn test_ai3_round2_hand_analysis() {
    // AI3第2回合手牌 (19张)
    let hand = vec![
        // 8♣×3 (8筒子)
        Card::new(Suit::Clubs, Rank::Eight),
        Card::new(Suit::Clubs, Rank::Eight),
        Card::new(Suit::Clubs, Rank::Eight),
        // 9♣, 9♥, 9♠
        Card::new(Suit::Clubs, Rank::Nine),
        Card::new(Suit::Hearts, Rank::Nine),
        Card::new(Suit::Spades, Rank::Nine),
        // J♦, J♣, J♥
        Card::new(Suit::Diamonds, Rank::Jack),
        Card::new(Suit::Clubs, Rank::Jack),
        Card::new(Suit::Hearts, Rank::Jack),
        // Q♣, Q♥, Q♥
        Card::new(Suit::Clubs, Rank::Queen),
        Card::new(Suit::Hearts, Rank::Queen),
        Card::new(Suit::Hearts, Rank::Queen),
        // A♦, A♥×3, A♠
        Card::new(Suit::Diamonds, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Ace),
        Card::new(Suit::Spades, Rank::Ace),
        // 2♦, 2♠
        Card::new(Suit::Diamonds, Rank::Two),
        Card::new(Suit::Spades, Rank::Two),
    ];

    assert_eq!(hand.len(), 19);

    let patterns = HandPatternAnalyzer::analyze_patterns(&hand);

    println!("\n=== HandPatterns 分析结果 ===");
    println!("Tongzi: {} 个", patterns.tongzi.len());
    for t in &patterns.tongzi {
        println!("  {:?} {:?}", t[0].rank, t[0].suit);
    }

    println!("Triples: {} 个", patterns.triples.len());
    for t in &patterns.triples {
        println!("  {:?}", t[0].rank);
    }

    println!("Airplanes: {} 个", patterns.airplane_chains.len());
    for a in &patterns.airplane_chains {
        let ranks: Vec<_> = a.chunks(3).map(|c| c[0].rank).collect();
        println!("  {:?}", ranks);
    }

    println!("ConsecPairs: {} 个", patterns.consecutive_pair_chains.len());

    println!("Pairs: {} 个", patterns.pairs.len());
    for p in &patterns.pairs {
        println!("  {:?} [{:?}, {:?}]", p[0].rank, p[0].suit, p[1].suit);
    }

    println!("Singles: {} 个", patterns.singles.len());

    // 验证修复后的预期结果:
    // - Tongzi: 8♣筒子, A♥筒子 (2个)
    // - Airplanes: JJJ+QQQ (1个, 6张)
    // - Triples: 999 (1个)
    // - Pairs: AA (A♦A♠), 22 (2♦2♠) (2个)
    // - Singles: 无

    assert_eq!(patterns.tongzi.len(), 2, "应该有2个筒子");
    assert_eq!(patterns.airplane_chains.len(), 1, "应该有1个飞机(JJJ+QQQ)");
    assert_eq!(patterns.triples.len(), 1, "应该有1个三张(999)");
    assert_eq!(patterns.pairs.len(), 2, "应该有2个对子(AA和22)"); // 关键验证点！
    assert_eq!(
        patterns.consecutive_pair_chains.len(),
        0,
        "不应该有连对(AA和22不连续)"
    );

    // 验证22是独立的对子
    let has_22_pair = patterns.pairs.iter().any(|p| p[0].rank == Rank::Two);
    assert!(has_22_pair, "22应该被识别为独立对子，而不是连对");
}

#[test]
fn test_two_not_in_consec_pairs() {
    // 简单测试: AA + 22 不应该形成连对
    let hand = vec![
        Card::new(Suit::Diamonds, Rank::Ace),
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Diamonds, Rank::Two),
        Card::new(Suit::Spades, Rank::Two),
    ];

    let patterns = HandPatternAnalyzer::analyze_patterns(&hand);

    println!("\n=== AA + 22 测试 ===");
    println!("ConsecPairs: {}", patterns.consecutive_pair_chains.len());
    println!("Pairs: {}", patterns.pairs.len());

    assert_eq!(
        patterns.consecutive_pair_chains.len(),
        0,
        "AA+22不应该形成连对"
    );
    assert_eq!(patterns.pairs.len(), 2, "应该是2个独立对子");
}

#[test]
fn test_two_not_in_airplane() {
    // 简单测试: AAA + 222 不应该形成飞机
    let hand = vec![
        Card::new(Suit::Diamonds, Rank::Ace),
        Card::new(Suit::Spades, Rank::Ace),
        Card::new(Suit::Hearts, Rank::Ace),
        Card::new(Suit::Diamonds, Rank::Two),
        Card::new(Suit::Spades, Rank::Two),
        Card::new(Suit::Hearts, Rank::Two),
    ];

    let patterns = HandPatternAnalyzer::analyze_patterns(&hand);

    println!("\n=== AAA + 222 测试 ===");
    println!("Airplanes: {}", patterns.airplane_chains.len());
    println!("Triples: {}", patterns.triples.len());

    assert_eq!(patterns.airplane_chains.len(), 0, "AAA+222不应该形成飞机");
    assert_eq!(patterns.triples.len(), 2, "应该是2个独立三张");
}
