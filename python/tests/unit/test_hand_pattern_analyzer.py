"""Unit tests for HandPatternAnalyzer."""

from datongzi_rules import Card, HandPatternAnalyzer, Rank, Suit


def test_analyze_empty_hand():
    """Test analyzing empty hand."""
    resources = HandPatternAnalyzer.analyze_patterns([])

    assert resources.total_cards == 0
    assert resources.trump_count == 0
    assert len(resources.singles) == 0


def test_analyze_singles_only():
    """Test hand with only singles."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.SEVEN),
        Card(Suit.CLUBS, Rank.NINE),
    ]

    resources = HandPatternAnalyzer.analyze_patterns(hand)

    assert resources.total_cards == 3
    assert len(resources.singles) == 3
    assert len(resources.pairs) == 0
    assert resources.trump_count == 0


def test_analyze_pairs():
    """Test hand with pairs."""
    hand = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.CLUBS, Rank.FIVE),
        Card(Suit.DIAMONDS, Rank.FIVE),
    ]

    resources = HandPatternAnalyzer.analyze_patterns(hand)

    assert resources.total_cards == 4
    assert len(resources.pairs) == 2
    assert len(resources.singles) == 0


def test_analyze_triples():
    """Test hand with triples."""
    hand = [
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.HEARTS, Rank.ACE),
        Card(Suit.CLUBS, Rank.ACE),
    ]

    resources = HandPatternAnalyzer.analyze_patterns(hand)

    assert resources.total_cards == 3
    assert len(resources.triples) == 1
    assert len(resources.triples[0]) == 3


def test_analyze_bomb():
    """Test hand with bomb."""
    hand = [
        Card(Suit.SPADES, Rank.TEN),
        Card(Suit.HEARTS, Rank.TEN),
        Card(Suit.CLUBS, Rank.TEN),
        Card(Suit.DIAMONDS, Rank.TEN),
    ]

    resources = HandPatternAnalyzer.analyze_patterns(hand)

    assert resources.total_cards == 4
    assert len(resources.bombs) == 1
    assert resources.trump_count == 1
    assert len(resources.bombs[0]) == 4


def test_analyze_tongzi():
    """Test hand with tongzi."""
    hand = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.SPADES, Rank.KING),
    ]

    resources = HandPatternAnalyzer.analyze_patterns(hand)

    assert resources.total_cards == 3
    assert len(resources.tongzi) == 1
    assert resources.trump_count == 1


def test_analyze_consecutive_pairs():
    """Test hand with consecutive pairs."""
    hand = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.SPADES, Rank.SIX),
        Card(Suit.HEARTS, Rank.SIX),
        Card(Suit.SPADES, Rank.SEVEN),
        Card(Suit.HEARTS, Rank.SEVEN),
    ]

    resources = HandPatternAnalyzer.analyze_patterns(hand)

    assert resources.total_cards == 6
    assert len(resources.consecutive_pair_chains) == 1
    assert len(resources.consecutive_pair_chains[0]) == 6


def test_analyze_airplane_chain():
    """Test hand with airplane chain."""
    hand = [
        Card(Suit.SPADES, Rank.JACK),
        Card(Suit.HEARTS, Rank.JACK),
        Card(Suit.CLUBS, Rank.JACK),
        Card(Suit.SPADES, Rank.QUEEN),
        Card(Suit.HEARTS, Rank.QUEEN),
        Card(Suit.CLUBS, Rank.QUEEN),
    ]

    resources = HandPatternAnalyzer.analyze_patterns(hand)

    assert resources.total_cards == 6
    assert len(resources.airplane_chains) == 1
    assert len(resources.airplane_chains[0]) == 6


def test_analyze_complex_hand():
    """Test hand with multiple pattern types."""
    hand = [
        # Bomb
        Card(Suit.SPADES, Rank.TEN),
        Card(Suit.HEARTS, Rank.TEN),
        Card(Suit.CLUBS, Rank.TEN),
        Card(Suit.DIAMONDS, Rank.TEN),
        # Triple
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.HEARTS, Rank.ACE),
        Card(Suit.CLUBS, Rank.ACE),
        # Pair
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        # Singles
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.SEVEN),
    ]

    resources = HandPatternAnalyzer.analyze_patterns(hand)

    assert resources.total_cards == 11
    assert len(resources.bombs) == 1
    assert len(resources.triples) == 1
    assert len(resources.pairs) == 1
    assert len(resources.singles) == 2
    assert resources.trump_count == 1
    assert resources.has_control_cards  # Has ACE and KING


def test_analyze_dizha():
    """Test hand with dizha."""
    hand = [
        # 2 spades
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.SPADES, Rank.KING),
        # 2 hearts
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        # 2 clubs
        Card(Suit.CLUBS, Rank.KING),
        Card(Suit.CLUBS, Rank.KING),
        # 2 diamonds
        Card(Suit.DIAMONDS, Rank.KING),
        Card(Suit.DIAMONDS, Rank.KING),
    ]

    resources = HandPatternAnalyzer.analyze_patterns(hand)

    assert resources.total_cards == 8
    assert len(resources.dizha) == 1
    assert resources.trump_count == 1


def test_non_overlapping_structure_analysis():
    """Test that cards are not duplicated across categories."""
    hand = [
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.HEARTS, Rank.ACE),
        Card(Suit.CLUBS, Rank.ACE),
        Card(Suit.DIAMONDS, Rank.ACE),
    ]

    resources = HandPatternAnalyzer.analyze_patterns(hand)

    # Should be classified as bomb, not triple + single
    assert len(resources.bombs) == 1
    assert len(resources.triples) == 0
    assert len(resources.singles) == 0

    # Verify total cards match
    total_in_resources = (
        sum(len(d) for d in resources.dizha)
        + sum(len(t) for t in resources.tongzi)
        + sum(len(b) for b in resources.bombs)
        + sum(len(a) for a in resources.airplane_chains)
        + sum(len(c) for c in resources.consecutive_pair_chains)
        + sum(len(t) for t in resources.triples)
        + sum(len(p) for p in resources.pairs)
        + len(resources.singles)
    )
    assert total_in_resources == resources.total_cards


def test_resources_sorting():
    """Test that resources are sorted by strength."""
    hand = [
        # Two pairs
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.FIVE),
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.KING),
        # Two singles
        Card(Suit.CLUBS, Rank.SIX),
        Card(Suit.CLUBS, Rank.ACE),
    ]

    resources = HandPatternAnalyzer.analyze_patterns(hand)

    # Pairs should be sorted by rank (descending)
    assert len(resources.pairs) == 2
    assert resources.pairs[0][0].rank == Rank.KING
    assert resources.pairs[1][0].rank == Rank.FIVE

    # Singles should be sorted by rank (descending)
    assert len(resources.singles) == 2
    assert resources.singles[0].rank == Rank.ACE
    assert resources.singles[1].rank == Rank.SIX


def test_hand_structure_str():
    """Test HandPatterns string representation."""
    hand = [
        Card(Suit.SPADES, Rank.TEN),
        Card(Suit.HEARTS, Rank.TEN),
        Card(Suit.CLUBS, Rank.TEN),
        Card(Suit.DIAMONDS, Rank.TEN),
    ]

    resources = HandPatternAnalyzer.analyze_patterns(hand)
    str_repr = str(resources)

    assert "HandPatterns" in str_repr
    assert "4 cards" in str_repr
    assert "Bombs:1" in str_repr


def test_control_cards_detection():
    """Test has_control_cards flag."""
    # Hand with no control cards
    hand1 = [
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.HEARTS, Rank.SIX),
    ]
    resources1 = HandPatternAnalyzer.analyze_patterns(hand1)
    assert not resources1.has_control_cards

    # Hand with 2 (control card)
    hand2 = [
        Card(Suit.SPADES, Rank.TWO),
        Card(Suit.HEARTS, Rank.FIVE),
    ]
    resources2 = HandPatternAnalyzer.analyze_patterns(hand2)
    assert resources2.has_control_cards

    # Hand with ACE (control card)
    hand3 = [
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.HEARTS, Rank.FIVE),
    ]
    resources3 = HandPatternAnalyzer.analyze_patterns(hand3)
    assert resources3.has_control_cards

    # Hand with KING (control card)
    hand4 = [
        Card(Suit.SPADES, Rank.KING),
        Card(Suit.HEARTS, Rank.FIVE),
    ]
    resources4 = HandPatternAnalyzer.analyze_patterns(hand4)
    assert resources4.has_control_cards


if __name__ == "__main__":
    # Run all tests
    test_analyze_empty_hand()
    test_analyze_singles_only()
    test_analyze_pairs()
    test_analyze_triples()
    test_analyze_bomb()
    test_analyze_tongzi()
    test_analyze_consecutive_pairs()
    test_analyze_airplane_chain()
    test_analyze_complex_hand()
    test_analyze_dizha()
    test_non_overlapping_structure_analysis()
    test_resources_sorting()
    test_hand_structure_str()
    test_control_cards_detection()

    print("✓ All HandPatternAnalyzer tests passed!")
