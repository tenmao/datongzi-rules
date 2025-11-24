"""Basic usage examples for datongzi-rules library."""

from datongzi_rules import (
    Card,
    Rank,
    Suit,
    Deck,
    PatternRecognizer,
    PlayValidator,
    PlayType,
    ConfigFactory,
)


def example_1_card_basics():
    """Example 1: Creating and working with cards."""
    print("\n" + "=" * 50)
    print("示例 1: 创建和使用卡牌")
    print("=" * 50)
    
    # 创建单张牌
    card = Card(Suit.SPADES, Rank.ACE)
    print(f"创建卡牌: {card}")  # 输出: ♠A
    
    # 检查计分牌
    five = Card(Suit.HEARTS, Rank.FIVE)
    print(f"{five} 是计分牌吗? {five.is_scoring_card}")  # True
    print(f"{five} 分值: {five.score_value}")  # 5
    
    # 从字符串创建牌
    card_from_str = Card.from_string("♦K")
    print(f"从字符串创建: {card_from_str}")


def example_2_pattern_recognition():
    """Example 2: Recognizing card patterns."""
    print("\n" + "=" * 50)
    print("示例 2: 识别牌型")
    print("=" * 50)
    
    # 对子
    pair = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
    ]
    pattern = PatternRecognizer.analyze_cards(pair)
    print(f"牌型: {[str(c) for c in pair]}")
    print(f"识别结果: {pattern.play_type.name}")  # PAIR
    
    # 炸弹
    bomb = [
        Card(Suit.SPADES, Rank.TEN),
        Card(Suit.HEARTS, Rank.TEN),
        Card(Suit.CLUBS, Rank.TEN),
        Card(Suit.DIAMONDS, Rank.TEN),
    ]
    pattern = PatternRecognizer.analyze_cards(bomb)
    print(f"\n牌型: {[str(c) for c in bomb]}")
    print(f"识别结果: {pattern.play_type.name}")  # BOMB
    
    # 筒子（3张相同花色相同点数）
    tongzi = [
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.SPADES, Rank.ACE),
    ]
    pattern = PatternRecognizer.analyze_cards(tongzi)
    print(f"\n牌型: {[str(c) for c in tongzi]}")
    print(f"识别结果: {pattern.play_type.name}")  # TONGZI


def example_3_play_validation():
    """Example 3: Validating plays."""
    print("\n" + "=" * 50)
    print("示例 3: 验证出牌")
    print("=" * 50)
    
    # 当前牌面：一对5
    current_cards = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
    ]
    current_pattern = PatternRecognizer.analyze_cards(current_cards)
    print(f"当前牌面: {[str(c) for c in current_cards]}")
    
    # 尝试用一对K跟牌
    new_cards = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
    ]
    can_beat = PlayValidator.can_beat_play(new_cards, current_pattern)
    print(f"\n{[str(c) for c in new_cards]} 能否跟牌? {can_beat}")  # True
    
    # 尝试用单牌跟对子
    single_card = [Card(Suit.SPADES, Rank.ACE)]
    can_beat = PlayValidator.can_beat_play(single_card, current_pattern)
    print(f"{[str(c) for c in single_card]} 能否跟牌? {can_beat}")  # False
    
    # 用炸弹可以打任何牌
    bomb = [
        Card(Suit.SPADES, Rank.SIX),
        Card(Suit.HEARTS, Rank.SIX),
        Card(Suit.CLUBS, Rank.SIX),
        Card(Suit.DIAMONDS, Rank.SIX),
    ]
    can_beat = PlayValidator.can_beat_play(bomb, current_pattern)
    print(f"\n炸弹 {[str(c) for c in bomb]} 能否跟牌? {can_beat}")  # True


def example_4_deck_and_dealing():
    """Example 4: Creating deck and dealing cards."""
    print("\n" + "=" * 50)
    print("示例 4: 创建牌堆并发牌")
    print("=" * 50)
    
    # 创建3副牌
    deck = Deck.create_standard_deck(num_decks=3)
    print(f"创建 3 副牌，总计: {len(deck)} 张")
    
    # 洗牌
    deck.shuffle()
    print("洗牌完成")
    
    # 发牌
    hand = deck.deal_cards(13)
    print(f"\n发牌 13 张:")
    print(f"手牌: {[str(c) for c in hand[:5]]}... (显示前5张)")
    print(f"剩余牌数: {len(deck)}")


def example_5_game_variants():
    """Example 5: Using different game variants."""
    print("\n" + "=" * 50)
    print("示例 5: 使用不同游戏变体")
    print("=" * 50)
    
    # 标准3副牌3人游戏
    config = ConfigFactory.create_standard_3deck_3player()
    print(f"标准配置:")
    print(f"  - 牌数: {config.num_decks} 副")
    print(f"  - 玩家: {config.num_players} 人")
    print(f"  - 每人牌数: {config.cards_per_player} 张")
    
    # 4人游戏
    config = ConfigFactory.create_4deck_4player()
    print(f"\n4人游戏配置:")
    print(f"  - 牌数: {config.num_decks} 副")
    print(f"  - 玩家: {config.num_players} 人")
    print(f"  - 每人牌数: {config.cards_per_player} 张")
    
    # 快速游戏
    config = ConfigFactory.create_quick_game()
    print(f"\n快速游戏配置:")
    print(f"  - 牌数: {config.num_decks} 副")
    print(f"  - 每人牌数: {config.cards_per_player} 张")
    
    # 自定义配置
    config = ConfigFactory.create_custom(
        num_decks=2,
        num_players=2,
        must_beat_rule=False
    )
    print(f"\n自定义配置:")
    print(f"  - 牌数: {config.num_decks} 副")
    print(f"  - 玩家: {config.num_players} 人")
    print(f"  - 有牌必打: {config.must_beat_rule}")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "打筒子规则引擎 - 基础示例" + " " * 21 + "║")
    print("╚" + "=" * 58 + "╝")
    
    example_1_card_basics()
    example_2_pattern_recognition()
    example_3_play_validation()
    example_4_deck_and_dealing()
    example_5_game_variants()
    
    print("\n" + "=" * 50)
    print("所有示例完成！")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
