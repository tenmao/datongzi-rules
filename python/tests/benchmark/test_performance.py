"""Performance benchmark tests for datongzi-rules."""

import time

from datongzi_rules import (
    Card,
    ConfigFactory,
    Deck,
    PatternRecognizer,
    PlayGenerator,
    Rank,
    ScoreComputation,
    Suit,
)


def benchmark_pattern_recognition():
    """Benchmark pattern recognition performance."""
    print("\n" + "=" * 60)
    print("Pattern Recognition Benchmark")
    print("=" * 60)

    # Test data
    test_cases = [
        # Singles
        ([Card(Suit.SPADES, Rank.ACE)], "Single"),
        # Pairs
        ([Card(Suit.SPADES, Rank.KING), Card(Suit.HEARTS, Rank.KING)], "Pair"),
        # Triples
        (
            [
                Card(Suit.SPADES, Rank.QUEEN),
                Card(Suit.HEARTS, Rank.QUEEN),
                Card(Suit.CLUBS, Rank.QUEEN),
            ],
            "Triple",
        ),
        # Bombs
        (
            [
                Card(Suit.SPADES, Rank.TEN),
                Card(Suit.HEARTS, Rank.TEN),
                Card(Suit.CLUBS, Rank.TEN),
                Card(Suit.DIAMONDS, Rank.TEN),
            ],
            "Bomb",
        ),
        # Tongzi
        (
            [
                Card(Suit.SPADES, Rank.ACE),
                Card(Suit.SPADES, Rank.ACE),
                Card(Suit.SPADES, Rank.ACE),
            ],
            "Tongzi",
        ),
    ]

    iterations = 10000

    for cards, name in test_cases:
        start_time = time.time()

        for _ in range(iterations):
            PatternRecognizer.analyze_cards(cards)

        elapsed = time.time() - start_time
        avg_time = (elapsed / iterations) * 1000  # ms

        print(f"{name:15s}: {avg_time:.4f} ms/op ({iterations/elapsed:.0f} ops/sec)")

    print("✓ Pattern recognition benchmark complete")


def benchmark_play_generation():
    """Benchmark play generation performance."""
    print("\n" + "=" * 60)
    print("Play Generation Benchmark")
    print("=" * 60)

    # Create test hands of different sizes
    test_hands = [
        (5, "Small hand"),
        (13, "Medium hand"),
        (25, "Large hand"),
        (41, "Full hand"),
    ]

    deck = Deck.create_standard_deck(num_decks=3)
    deck.shuffle()

    for size, name in test_hands:
        hand = deck.cards[:size]

        start_time = time.time()
        iterations = 100

        for _ in range(iterations):
            # Use max_combinations=2000 for benchmark tests
            # (We're testing performance, not production safety)
            PlayGenerator.generate_all_plays(hand, max_combinations=2000)

        elapsed = time.time() - start_time
        avg_time = (elapsed / iterations) * 1000  # ms

        print(f"{name:15s} ({size:2d} cards): {avg_time:.2f} ms/op")

    print("✓ Play generation benchmark complete")


def benchmark_full_game_setup():
    """Benchmark full game setup performance."""
    print("\n" + "=" * 60)
    print("Full Game Setup Benchmark")
    print("=" * 60)

    iterations = 100

    start_time = time.time()

    for _ in range(iterations):
        # Create config
        config = ConfigFactory.create_standard_3deck_3player()

        # Create and shuffle deck
        deck = Deck.create_standard_deck(num_decks=config.num_decks)
        deck.shuffle()

        # Deal cards
        hands = []
        for _ in range(config.num_players):
            hand = deck.deal_cards(config.cards_per_player)
            hands.append(hand)

        # Create scoring engine
        ScoreComputation(config)

    elapsed = time.time() - start_time
    avg_time = (elapsed / iterations) * 1000  # ms

    print(f"Full game setup: {avg_time:.2f} ms/op ({iterations/elapsed:.0f} games/sec)")
    print("✓ Full game setup benchmark complete")


def benchmark_scoring():
    """Benchmark scoring performance."""
    print("\n" + "=" * 60)
    print("Scoring Benchmark")
    print("=" * 60)

    config = ConfigFactory.create_standard_3deck_3player()

    # Create test cards
    round_cards = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.TEN),
        Card(Suit.CLUBS, Rank.KING),
    ]

    iterations = 10000

    # Benchmark round scoring
    start_time = time.time()

    for i in range(iterations):
        engine = ScoreComputation(config)
        engine.create_round_win_event("player1", round_cards, round_number=i)

    elapsed = time.time() - start_time
    avg_time = (elapsed / iterations) * 1000  # ms

    print(f"Round scoring: {avg_time:.4f} ms/op ({iterations/elapsed:.0f} ops/sec)")

    # Benchmark finish bonuses
    start_time = time.time()

    for _ in range(iterations):
        engine = ScoreComputation(config)
        engine.create_finish_bonus_events(["player1", "player2", "player3"])

    elapsed = time.time() - start_time
    avg_time = (elapsed / iterations) * 1000  # ms

    print(f"Finish bonuses: {avg_time:.4f} ms/op ({iterations/elapsed:.0f} ops/sec)")
    print("✓ Scoring benchmark complete")


def test_run_all_benchmarks():
    """Run all performance benchmarks."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "Performance Benchmarks" + " " * 21 + "║")
    print("╚" + "=" * 58 + "╝")

    benchmark_pattern_recognition()
    benchmark_play_generation()
    benchmark_full_game_setup()
    benchmark_scoring()

    print("\n" + "=" * 60)
    print("All benchmarks complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    test_run_all_benchmarks()
