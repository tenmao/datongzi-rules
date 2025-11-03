"""Unit tests for game variants and configuration factory."""

from datongzi_rules import ConfigFactory, VariantValidator, Rank


def test_standard_3deck_3player():
    """Test standard 3-deck 3-player configuration."""
    config = ConfigFactory.create_standard_3deck_3player()
    
    assert config.num_decks == 3
    assert config.num_players == 3
    assert config.cards_per_player == 41
    assert config.finish_bonus == [100, -40, -60]
    assert config.must_beat_rule is True
    
    print("✓ Standard 3-deck 3-player config test passed")


def test_4deck_4player():
    """Test 4-deck 4-player configuration."""
    config = ConfigFactory.create_4deck_4player()
    
    assert config.num_decks == 4
    assert config.num_players == 4
    assert config.cards_per_player == 42
    assert len(config.finish_bonus) == 4
    
    print("✓ 4-deck 4-player config test passed")


def test_2player():
    """Test 2-player configuration."""
    config = ConfigFactory.create_2player()
    
    assert config.num_decks == 3
    assert config.num_players == 2
    assert config.finish_bonus == [100, -100]
    
    print("✓ 2-player config test passed")


def test_quick_game():
    """Test quick game configuration."""
    config = ConfigFactory.create_quick_game()
    
    assert config.num_decks == 2
    assert config.num_players == 3
    assert config.cards_per_player == 28
    
    print("✓ Quick game config test passed")


def test_high_stakes():
    """Test high-stakes configuration."""
    config = ConfigFactory.create_high_stakes()
    
    assert config.k_tongzi_bonus == 200  # Doubled
    assert config.a_tongzi_bonus == 400  # Doubled
    assert config.two_tongzi_bonus == 600  # Doubled
    assert config.dizha_bonus == 800  # Doubled
    assert config.finish_bonus[0] == 200  # Doubled
    
    print("✓ High-stakes config test passed")


def test_beginner_friendly():
    """Test beginner-friendly configuration."""
    config = ConfigFactory.create_beginner_friendly()
    
    assert config.must_beat_rule is False  # Relaxed rule
    
    print("✓ Beginner-friendly config test passed")


def test_custom_config():
    """Test custom configuration."""
    config = ConfigFactory.create_custom(
        num_decks=2,
        num_players=2,
        cards_dealt_aside=4,
        k_tongzi_bonus=150,
        must_beat_rule=False
    )
    
    assert config.num_decks == 2
    assert config.num_players == 2
    assert config.cards_dealt_aside == 4
    assert config.k_tongzi_bonus == 150
    assert config.must_beat_rule is False
    
    print("✓ Custom config test passed")


def test_variant_validator_valid():
    """Test variant validator with valid configuration."""
    config = ConfigFactory.create_standard_3deck_3player()
    is_valid, warnings = VariantValidator.validate_config(config)
    
    assert is_valid is True
    assert len(warnings) == 0
    
    print("✓ Variant validator (valid) test passed")


def test_variant_validator_warnings():
    """Test variant validator with problematic configuration."""
    # Create config with too few cards
    config = ConfigFactory.create_custom(
        num_decks=1,
        num_players=4,
        cards_dealt_aside=30  # Too many aside
    )
    
    is_valid, warnings = VariantValidator.validate_config(config)
    
    assert is_valid is False
    assert len(warnings) > 0
    
    print("✓ Variant validator (warnings) test passed")


def test_config_excluded_ranks():
    """Test configuration with excluded ranks."""
    excluded = {Rank.FIVE, Rank.SIX}
    config = ConfigFactory.create_custom(
        num_decks=3,
        num_players=3,
        excluded_ranks=excluded
    )
    
    assert config.excluded_ranks == excluded
    # Total cards should be less due to exclusions
    expected_cards = 3 * (11 - 2) * 4  # 3 decks * 9 ranks * 4 suits
    assert config.total_cards == expected_cards
    
    print("✓ Config with excluded ranks test passed")


def test_finish_bonus_sum():
    """Test that finish bonuses sum correctly."""
    config = ConfigFactory.create_standard_3deck_3player()
    
    bonus_sum = sum(config.finish_bonus)
    # Should be zero or negative for fairness
    assert bonus_sum == 0
    
    print("✓ Finish bonus sum test passed")


# All tests can be run with pytest
# pytest will autodiscover all test_* functions
