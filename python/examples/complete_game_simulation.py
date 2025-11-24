"""Complete game simulation example using datongzi-rules library."""

from datongzi_rules import (
    Deck,
    ConfigFactory,
    PatternRecognizer,
    PlayValidator,
    ScoreComputation,
    PlayGenerator,
    HandPatternAnalyzer,
)


def simulate_complete_game():
    """Simulate a complete game from setup to finish."""
    
    print("=" * 60)
    print("打筒子规则引擎 - 完整游戏模拟")
    print("=" * 60)
    print()
    
    # 1. 创建游戏配置
    print("1. 创建游戏配置")
    config = ConfigFactory.create_standard_3deck_3player()
    print(f"   - 牌数: {config.num_decks} 副")
    print(f"   - 玩家数: {config.num_players} 人")
    print(f"   - 每人牌数: {config.cards_per_player} 张")
    print(f"   - 完成位置奖励: {config.finish_bonus}")
    print()
    
    # 2. 创建并洗牌
    print("2. 创建牌堆并洗牌")
    deck = Deck.create_standard_deck(num_decks=config.num_decks)
    print(f"   - 总牌数: {len(deck)} 张")
    deck.shuffle()
    print("   - 洗牌完成")
    print()
    
    # 3. 发牌
    print("3. 发牌给玩家")
    player_hands = {}
    for i in range(config.num_players):
        player_id = f"player{i+1}"
        hand = deck.deal_cards(config.cards_per_player)
        player_hands[player_id] = hand
        print(f"   - {player_id}: {len(hand)} 张牌")
    
    # 放置底牌
    aside_cards = deck.deal_cards(config.cards_dealt_aside)
    print(f"   - 底牌: {config.cards_dealt_aside} 张")
    print()
    
    # 4. 分析手牌
    print("4. 分析各玩家手牌")
    for player_id, hand in player_hands.items():
        patterns = HandPatternAnalyzer.analyze_patterns(hand)
        play_count = PlayGenerator.count_all_plays(hand)

        print(f"   - {player_id}:")
        print(f"     * 可能出牌数: {play_count}")
        print(f"     * 炸弹: {len(patterns.bombs)}, 筒子: {len(patterns.tongzi)}, 地炸: {len(patterns.dizha)}")
    print()
    
    # 5. 模拟一轮出牌
    print("5. 模拟第一轮出牌")
    current_pattern = None
    
    for player_id, hand in player_hands.items():
        print(f"\n   轮到 {player_id}:")
        
        if current_pattern is None:
            # 首家出牌 - 简单策略：出最小的单张
            smallest_card = min(hand, key=lambda c: c.rank.value)
            play = [smallest_card]
            pattern = PatternRecognizer.analyze_cards(play)

            print(f"     - 首家出牌: {len(play)} 张")
            print(f"     - 牌型: {pattern.play_type.name}")

            current_pattern = pattern
        else:
            # 跟牌 - 使用新的高效API
            valid_responses = PlayGenerator.generate_beating_plays_with_same_type_or_trump(
                hand, current_pattern
            )
            
            if valid_responses:
                # 选择第一个有效响应（简单策略）
                best_response = valid_responses[0]

                pattern = PatternRecognizer.analyze_cards(best_response)
                print(f"     - 跟牌: {len(best_response)} 张")
                print(f"     - 牌型: {pattern.play_type.name}")
                current_pattern = pattern
            else:
                print("     - 过牌（无法跟）")
    
    print()
    
    # 6. 计分示例
    print("6. 计分示例")
    scoring_engine = ScoreComputation(config)
    
    # 假设 player1 获胜这一轮
    round_cards = []
    for hand in player_hands.values():
        if len(hand) >= 3:
            round_cards.extend(hand[:3])  # 取前3张作为示例
    
    # 创建回合胜利事件
    win_event = scoring_engine.create_round_win_event(
        "player1", round_cards, round_number=1
    )
    
    if win_event:
        print(f"   - player1 获得回合分数: {win_event.points}")
    
    # 模拟游戏结束，计算完成位置奖励
    finish_order = ["player1", "player2", "player3"]
    finish_events = scoring_engine.create_finish_bonus_events(finish_order)
    
    print("\n   完成位置奖励:")
    for event in finish_events:
        print(f"   - {event.player_id}: {event.points} 分 ({event.reason})")
    
    # 最终得分
    print("\n   最终得分:")
    for player_id in player_hands.keys():
        total = scoring_engine.calculate_total_score_for_player(player_id)
        print(f"   - {player_id}: {total} 分")
    
    print()
    print("=" * 60)
    print("游戏模拟完成！")
    print("=" * 60)


if __name__ == "__main__":
    simulate_complete_game()
