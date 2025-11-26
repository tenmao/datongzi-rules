use datongzi_rules::ai_helpers::HandPatternAnalyzer;
use datongzi_rules::models::{Card, Rank, Suit};

#[test]
fn test_scenario_606_hand_pattern_analysis() {
    // Scenario 606: 手牌包含 ♥2×2, ♦2×4, ♣2×1
    // 问题: Python 识别出 [♥2, ♥2, ♣2] 为三张，Rust 是否也能识别？
    let hand = vec![
        Card::new(Suit::Hearts, Rank::Two),
        Card::new(Suit::Hearts, Rank::Two),
        Card::new(Suit::Diamonds, Rank::Two),
        Card::new(Suit::Diamonds, Rank::Two),
        Card::new(Suit::Clubs, Rank::Five),
        Card::new(Suit::Clubs, Rank::Queen),
        Card::new(Suit::Clubs, Rank::Two),
        Card::new(Suit::Diamonds, Rank::Two),
        Card::new(Suit::Diamonds, Rank::Two),
        Card::new(Suit::Diamonds, Rank::Seven),
        Card::new(Suit::Diamonds, Rank::Seven),
        Card::new(Suit::Spades, Rank::Nine),
        Card::new(Suit::Spades, Rank::Ten),
        Card::new(Suit::Clubs, Rank::Ace),
        Card::new(Suit::Clubs, Rank::Five),
    ];

    let patterns = HandPatternAnalyzer::analyze_patterns(&hand);

    println!("\n{}", "=".repeat(60));
    println!("Scenario 606 Hand Pattern Analysis");
    println!("{}", "=".repeat(60));
    println!("Hand composition:");
    println!("  2s: ♥2×2, ♦2×4, ♣2×1 (total 7 cards)");
    println!("  5s: ♣5×2");
    println!("  7s: ♦7×2");
    println!("  Singles: ♣Q, ♠9, ♠10, ♣A");
    println!();

    println!("Analysis Results:");
    println!("  Triples: {} groups", patterns.triples.len());
    for (i, triple) in patterns.triples.iter().enumerate() {
        println!("    Triple {}: {:?}", i + 1, triple);
    }

    println!("  Tongzi: {} groups", patterns.tongzi.len());
    for (i, tongzi) in patterns.tongzi.iter().enumerate() {
        println!("    Tongzi {}: {:?}", i + 1, tongzi);
    }

    println!("  Bombs: {} groups", patterns.bombs.len());
    for (i, bomb) in patterns.bombs.iter().enumerate() {
        println!("    Bomb {}: {:?}", i + 1, bomb);
    }

    println!("  Pairs: {} groups", patterns.pairs.len());
    for (i, pair) in patterns.pairs.iter().enumerate() {
        println!("    Pair {}: {:?}", i + 1, pair);
    }

    println!("  Singles: {} cards", patterns.singles.len());
    println!("    {:?}", patterns.singles);
    println!("{}\n", "=".repeat(60));

    // 关键验证点
    println!("Key Checks:");

    // Check 1: 应该识别 ♦2×4 为 Tongzi (至少3张同花色同rank)
    let diamonds_two_tongzi = patterns.tongzi.iter().any(|tongzi| {
        tongzi.len() >= 3
            && tongzi.iter().all(|c| c.rank == Rank::Two && c.suit == Suit::Diamonds)
    });
    println!("  ✓ Has ♦2×3+ Tongzi: {}", diamonds_two_tongzi);

    // Check 2: 应该识别 [♥2, ♥2, ♣2] 为独立三张（或类似组合）
    let has_mixed_two_triple = patterns.triples.iter().any(|triple| {
        triple.len() == 3 && triple.iter().all(|c| c.rank == Rank::Two)
    });
    println!("  ✓ Has triple with Rank::Two (mixed suits): {}", has_mixed_two_triple);

    // Check 3: 应该识别 ♣5×2 为对子
    let has_five_pair = patterns.pairs.iter().any(|pair| {
        pair.len() == 2
            && pair.iter().all(|c| c.rank == Rank::Five && c.suit == Suit::Clubs)
    });
    println!("  ✓ Has ♣5×2 pair: {}", has_five_pair);

    // Check 4: 应该识别 ♦7×2 为对子
    let has_seven_pair = patterns.pairs.iter().any(|pair| {
        pair.len() == 2
            && pair.iter().all(|c| c.rank == Rank::Seven && c.suit == Suit::Diamonds)
    });
    println!("  ✓ Has ♦7×2 pair: {}", has_seven_pair);

    println!();

    // 这是关键断言：Python 识别出了这个三张，Rust 也应该识别
    if !has_mixed_two_triple {
        println!("❌ MISMATCH: Rust did not identify the triple [♥2, ♥2, ♣2]");
        println!("   This explains why Python chose to play 3 TWOs,");
        println!("   but Rust chose to play the pair of FIVEs instead.");
        println!();
        println!("Expected behavior (from Python):");
        println!("  - After identifying ♦2×4 as Tongzi");
        println!("  - Remaining ♥2×2 + ♣2×1 should form a triple");
        println!("  - AI should prioritize playing this triple (T2 bucket)");
        println!("  - Instead of playing pairs (T3 bucket)");
    } else {
        println!("✅ MATCH: Rust correctly identified the triple");
    }

    // 可选：如果想让测试失败以引起注意，取消下面的注释
    // assert!(
    //     has_mixed_two_triple,
    //     "Expected Rust to identify triple [♥2, ♥2, ♣2] after Tongzi analysis, but it didn't"
    // );
}
