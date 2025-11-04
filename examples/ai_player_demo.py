"""AI player demonstration using datongzi-rules library."""

from datongzi_rules import (
    Deck,
    ConfigFactory,
    PatternRecognizer,
    PlayValidator,
    ScoringEngine,
    PlayGenerator,
    HandEvaluator,
)


class SimpleAIPlayer:
    """Simple AI player that uses rule engine utilities."""
    
    def __init__(self, player_id: str):
        self.player_id = player_id
        self.hand = []
    
    def receive_cards(self, cards):
        """Receive dealt cards."""
        self.hand = cards
    
    def decide_play(self, current_pattern=None):
        """Decide what to play based on current situation."""
        if current_pattern is None:
            # Starting round - play weakest cards
            best_play = HandEvaluator.suggest_best_play(self.hand)
        else:
            # Must beat current pattern
            valid_plays = PlayGenerator.generate_valid_responses(
                self.hand, current_pattern
            )
            
            if not valid_plays:
                return None  # Pass
            
            # Choose best play based on strategy
            best_play = HandEvaluator.suggest_best_play(
                self.hand, current_pattern
            )
        
        if best_play:
            # Remove played cards from hand
            for card in best_play:
                self.hand.remove(card)
        
        return best_play


def simulate_ai_game():
    """Simulate a game with AI players."""
    print("\n" + "=" * 60)
    print("AI 玩家对战演示")
    print("=" * 60)
    print()
    
    # Setup
    config = ConfigFactory.create_standard_3deck_3player()
    deck = Deck.create_standard_deck(num_decks=config.num_decks)
    deck.shuffle()
    
    # Create AI players
    players = [
        SimpleAIPlayer("AI-Alice"),
        SimpleAIPlayer("AI-Bob"),
        SimpleAIPlayer("AI-Charlie"),
    ]
    
    print("玩家设置:")
    for player in players:
        print(f"  - {player.player_id}")
    print()
    
    # Deal cards
    print("发牌...")
    for player in players:
        hand = deck.deal_cards(config.cards_per_player)
        player.receive_cards(hand)
        
        # Show initial hand strength
        strength = HandEvaluator.evaluate_hand(player.hand)
        print(f"  {player.player_id}: {len(player.hand)} 张牌, 强度 {strength:.2f}")
    print()
    
    # Simulate several rounds
    print("=" * 60)
    print("游戏开始！")
    print("=" * 60)
    
    scoring_engine = ScoringEngine(config)
    
    for round_num in range(1, 4):
        print(f"\n第 {round_num} 轮:")
        print("-" * 60)
        
        current_pattern = None
        round_winner = None
        round_cards = []
        
        for player in players:
            if len(player.hand) == 0:
                print(f"  {player.player_id}: 已出完牌，跳过")
                continue
            
            print(f"\n  轮到 {player.player_id}:")
            print(f"    剩余牌数: {len(player.hand)}")
            
            play = player.decide_play(current_pattern)
            
            if play is None:
                print(f"    决定: 过牌")
                continue
            
            # Analyze pattern
            pattern = PatternRecognizer.analyze_cards(play)
            print(f"    出牌: {len(play)} 张")
            print(f"    牌型: {pattern.play_type.name}")
            
            # Check if valid
            if PlayValidator.can_beat_play(play, current_pattern):
                current_pattern = pattern
                round_winner = player
                round_cards.extend(play)
                print(f"    状态: ✓ 有效出牌")
            else:
                print(f"    状态: ✗ 无效出牌（不应该发生）")
        
        # Round complete
        if round_winner:
            print(f"\n  回合赢家: {round_winner.player_id}")
            
            # Calculate score
            event = scoring_engine.create_round_win_event(
                round_winner.player_id,
                round_cards,
                round_num
            )
            
            if event:
                print(f"  获得分数: {event.points}")
        
        print()
    
    # Game summary
    print("=" * 60)
    print("游戏结束")
    print("=" * 60)
    
    # Check who finished
    finished_order = []
    for player in players:
        if len(player.hand) == 0:
            finished_order.append(player.player_id)
    
    if finished_order:
        print(f"\n完成顺序:")
        for i, player_id in enumerate(finished_order):
            print(f"  {i+1}. {player_id}")
        
        # Award finish bonuses
        finish_events = scoring_engine.create_finish_bonus_events(finished_order)
        
        print(f"\n完成位置奖励:")
        for event in finish_events:
            print(f"  {event.player_id}: {event.points:+d} 分")
    
    # Final scores
    print(f"\n最终得分:")
    for player in players:
        total = scoring_engine.calculate_total_score_for_player(player.player_id)
        remaining = len(player.hand)
        print(f"  {player.player_id}: {total:+d} 分 (剩余 {remaining} 张牌)")
    
    # Winner
    scores = {
        p.player_id: scoring_engine.calculate_total_score_for_player(p.player_id)
        for p in players
    }
    winner = max(scores.items(), key=lambda x: x[1])
    
    print(f"\n🏆 赢家: {winner[0]} ({winner[1]:+d} 分)")
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    simulate_ai_game()
