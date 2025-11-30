//! Play generation for AI assistance.
//!
//! This module provides utilities to generate valid plays from a hand of cards.
//! It is the **only** place that should generate legal plays for AI/UI.

use std::collections::HashMap;

use crate::ai_helpers::{filter_consecutive_pairs, filter_pairs, filter_singles, filter_triples};
use crate::models::{Card, Rank, Suit};
use crate::patterns::{PatternRecognizer, PlayPattern, PlayType, PlayValidator};

/// Generate valid plays from a hand of cards.
///
/// **IMPORTANT**: This is a pure utility struct for AI assistance. It does not maintain state
/// and can be used by AI players, auto-play features, or hint systems.
///
/// ## API Hierarchy
///
/// 1. **Recommended**: [`generate_beating_plays_with_same_type_or_trump`](Self::generate_beating_plays_with_same_type_or_trump)
///    - High-performance, generates minimal beating plays
///    - Only same-type higher plays or trump cards
///
/// 2. **For Statistics**: [`count_all_plays`](Self::count_all_plays)
///    - Counts valid plays without generating them
///    - Useful for hand evaluation metrics
///
/// 3. **⚠️ Use With Caution**: [`generate_all_plays`](Self::generate_all_plays)
///    - May cause combinatorial explosion with large hands
///    - Only use for testing, debugging, or small hands (<10 cards)
pub struct PlayGenerator;

impl PlayGenerator {
    /// Generate all possible valid plays from hand.
    ///
    /// ## ⚠️ WARNING: Combinatorial Explosion
    ///
    /// This method can cause combinatorial explosion with large hands.
    ///
    /// ### Valid Use Cases
    /// 1. Unit tests - Verify pattern recognition completeness
    /// 2. Debug tools - Developer inspection of all possibilities
    /// 3. Small hands - When hand size < 10 cards
    ///
    /// ### ❌ DO NOT Use
    /// - AI decision making or production code
    ///
    /// ### ✅ Prefer Instead
    /// - For AI: Use [`generate_beating_plays_with_same_type_or_trump`](Self::generate_beating_plays_with_same_type_or_trump)
    /// - For statistics: Use [`count_all_plays`](Self::count_all_plays)
    ///
    /// # Arguments
    ///
    /// * `hand` - Slice of cards in hand
    /// * `max_combinations` - Safety threshold (default 1000)
    ///
    /// # Returns
    ///
    /// `Ok(Vec<Vec<Card>>)` - All valid play combinations
    /// `Err(String)` - If combinations exceed `max_combinations`
    ///
    /// # Examples
    ///
    /// ```
    /// use datongzi_rules::{Card, Rank, Suit, PlayGenerator};
    ///
    /// let hand = vec![
    ///     Card::new(Suit::Spades, Rank::Five),
    ///     Card::new(Suit::Hearts, Rank::Five),
    /// ];
    ///
    /// let plays = PlayGenerator::generate_all_plays(&hand, 1000).unwrap();
    /// // Returns: singles, pairs
    /// ```
    pub fn generate_all_plays(
        hand: &[Card],
        max_combinations: usize,
    ) -> Result<Vec<Vec<Card>>, String> {
        if hand.is_empty() {
            return Ok(Vec::new());
        }

        // Warn about potential combinatorial explosion (in debug builds)
        #[cfg(debug_assertions)]
        if hand.len() > 15 {
            eprintln!(
                "WARNING: generate_all_plays called with {} cards - may cause combinatorial explosion",
                hand.len()
            );
        }

        let mut all_plays = Vec::new();

        // Generate singles (with identical play filtering)
        all_plays.extend(filter_singles(hand));

        // Generate pairs (with identical play filtering)
        all_plays.extend(filter_pairs(hand));

        // Generate consecutive pairs (with identical play filtering)
        all_plays.extend(filter_consecutive_pairs(hand));

        // Generate triples (with identical play filtering)
        all_plays.extend(filter_triples(hand));

        // Generate triple with kickers (1-2 cards)
        all_plays.extend(Self::_generate_triple_with_kickers(hand));

        // Generate airplanes
        all_plays.extend(Self::_generate_airplanes(hand));

        // Generate airplane with wings
        all_plays.extend(Self::_generate_airplane_with_wings(hand));

        // Generate bombs
        all_plays.extend(Self::_generate_bombs(hand));

        // Generate tongzi
        all_plays.extend(Self::_generate_tongzi(hand));

        // Generate dizha
        all_plays.extend(Self::_generate_dizha(hand));

        if all_plays.len() > max_combinations {
            return Err(format!(
                "Generated {} combinations exceeds limit {}. Use generate_beating_plays_with_same_type_or_trump or count_all_plays instead.",
                all_plays.len(),
                max_combinations
            ));
        }

        // Debug logging removed for zero-dependency implementation

        Ok(all_plays)
    }

    /// Generate plays that can beat current pattern using same type or trump cards.
    ///
    /// ## Strategy
    /// - Only use same-type plays with higher rank (no pattern breaking)
    /// - Or use trump cards (BOMB/TONGZI/DIZHA) to beat normal plays
    /// - Trump hierarchy: DIZHA > TONGZI > BOMB
    ///
    /// This follows the "有牌必打" rule - must play if you can beat.
    ///
    /// # Arguments
    ///
    /// * `hand` - Slice of cards in hand
    /// * `current_pattern` - Current play pattern to beat
    ///
    /// # Returns
    ///
    /// `Vec<Vec<Card>>` - Valid beating plays (minimal set, no wasteful combinations)
    ///
    /// # Examples
    ///
    /// ```
    /// use datongzi_rules::{Card, Rank, Suit, PlayGenerator, PatternRecognizer};
    ///
    /// let hand = vec![
    ///     Card::new(Suit::Spades, Rank::Seven),
    ///     Card::new(Suit::Hearts, Rank::Seven),
    /// ];
    ///
    /// let current_play = vec![Card::new(Suit::Spades, Rank::Five)];
    /// let current_pattern = PatternRecognizer::analyze_cards(&current_play).unwrap();
    ///
    /// let beating_plays = PlayGenerator::generate_beating_plays_with_same_type_or_trump(&hand, &current_pattern);
    /// // Returns single 7s that can beat single 5
    /// ```
    #[must_use]
    pub fn generate_beating_plays_with_same_type_or_trump(
        hand: &[Card],
        current_pattern: &PlayPattern,
    ) -> Vec<Vec<Card>> {
        if hand.is_empty() {
            return Vec::new();
        }

        let mut beating_plays = Vec::new();
        let current_type = current_pattern.play_type;

        // Trump cards (can beat any normal play)
        let trump_types = [PlayType::Dizha, PlayType::Tongzi, PlayType::Bomb];
        let is_current_trump = trump_types.contains(&current_type);

        // 1. Generate same-type plays with higher rank
        match current_type {
            PlayType::Single => {
                beating_plays.extend(Self::_generate_higher_singles(hand, current_pattern));
            }
            PlayType::Pair => {
                beating_plays.extend(Self::_generate_higher_pairs(hand, current_pattern));
            }
            PlayType::ConsecutivePairs => {
                beating_plays.extend(Self::_generate_higher_consecutive_pairs(
                    hand,
                    current_pattern,
                ));
            }
            PlayType::Triple => {
                // Triple can have 0-2 kickers, generate matching patterns
                beating_plays.extend(Self::_generate_higher_triples(hand, current_pattern));
            }
            PlayType::Airplane => {
                beating_plays.extend(Self::_generate_higher_airplanes(hand, current_pattern));
            }
            PlayType::AirplaneWithWings => {
                beating_plays.extend(Self::_generate_higher_airplane_with_wings(
                    hand,
                    current_pattern,
                ));
            }
            _ => {}
        }

        // 2. Generate trump plays (if current is not trump, or higher trump)
        if !is_current_trump {
            // Any trump beats normal play
            beating_plays.extend(Self::_generate_bombs(hand));
            beating_plays.extend(Self::_generate_tongzi(hand));
            beating_plays.extend(Self::_generate_dizha(hand));
        } else {
            // Trump vs trump - must follow hierarchy
            match current_type {
                PlayType::Bomb => {
                    // Higher bombs, or tongzi/dizha
                    beating_plays.extend(Self::_generate_higher_bombs(hand, current_pattern));
                    beating_plays.extend(Self::_generate_tongzi(hand));
                    beating_plays.extend(Self::_generate_dizha(hand));
                }
                PlayType::Tongzi => {
                    // Higher tongzi, or dizha
                    beating_plays.extend(Self::_generate_higher_tongzi(hand, current_pattern));
                    beating_plays.extend(Self::_generate_dizha(hand));
                }
                PlayType::Dizha => {
                    // Only higher dizha
                    beating_plays.extend(Self::_generate_higher_dizha(hand, current_pattern));
                }
                _ => {}
            }
        }

        // 3. Validate all plays can actually beat current pattern
        let valid_plays: Vec<Vec<Card>> = beating_plays
            .into_iter()
            .filter(|play| PlayValidator::can_beat_play(play, Some(current_pattern)))
            .collect();

        valid_plays
    }

    /// Count total number of valid plays without generating them.
    ///
    /// This is much more efficient than [`generate_all_plays`](Self::generate_all_plays) when you only
    /// need the count (e.g., for hand evaluation metrics).
    ///
    /// # Arguments
    ///
    /// * `hand` - Slice of cards in hand
    ///
    /// # Returns
    ///
    /// Total count of valid plays
    ///
    /// # Examples
    ///
    /// ```
    /// use datongzi_rules::{Card, Rank, Suit, PlayGenerator};
    ///
    /// let hand = vec![
    ///     Card::new(Suit::Spades, Rank::Five),
    ///     Card::new(Suit::Hearts, Rank::Five),
    /// ];
    ///
    /// let count = PlayGenerator::count_all_plays(&hand);
    /// // Returns: 3 (two singles + one pair)
    /// ```
    #[must_use]
    pub fn count_all_plays(hand: &[Card]) -> usize {
        if hand.is_empty() {
            return 0;
        }

        let mut count = 0;

        // Count singles
        count += hand.len();

        // Count pairs
        count += Self::_generate_pairs(hand).len();

        // Count consecutive pairs
        count += Self::_generate_consecutive_pairs(hand).len();

        // Count triples
        count += Self::_generate_triples(hand).len();

        // Count triple with kickers
        count += Self::_generate_triple_with_kickers(hand).len();

        // Count airplanes
        count += Self::_generate_airplanes(hand).len();

        // Count airplane with wings
        count += Self::_generate_airplane_with_wings(hand).len();

        // Count bombs
        count += Self::_generate_bombs(hand).len();

        // Count tongzi
        count += Self::_generate_tongzi(hand).len();

        // Count dizha
        count += Self::_generate_dizha(hand).len();

        // Debug logging removed for zero-dependency implementation

        count
    }

    // ========== Private Helper Methods ==========
    // Basic pattern generation methods

    /// Group cards by rank.
    fn _group_by_rank(cards: &[Card]) -> HashMap<Rank, Vec<Card>> {
        let mut groups: HashMap<Rank, Vec<Card>> = HashMap::new();
        for card in cards {
            groups.entry(card.rank).or_default().push(*card);
        }
        groups
    }

    /// Check if ranks are consecutive.
    fn _is_consecutive(ranks: &[Rank]) -> bool {
        if ranks.len() <= 1 {
            return true;
        }

        let values: Vec<u8> = ranks.iter().map(|r| r.value()).collect();
        for i in 1..values.len() {
            if values[i] != values[i - 1] + 1 {
                return false;
            }
        }
        true
    }

    /// Generate all valid pairs from hand.
    fn _generate_pairs(hand: &[Card]) -> Vec<Vec<Card>> {
        let mut pairs = Vec::new();
        let rank_groups = Self::_group_by_rank(hand);

        for (_rank, cards) in rank_groups {
            if cards.len() >= 2 {
                // Generate all 2-card combinations
                for i in 0..cards.len() {
                    for j in i + 1..cards.len() {
                        let pair = vec![cards[i], cards[j]];
                        if let Some(pattern) = PatternRecognizer::analyze_cards(&pair) {
                            if pattern.play_type == PlayType::Pair {
                                pairs.push(pair);
                            }
                        }
                    }
                }
            }
        }

        pairs
    }

    /// Generate all valid consecutive pairs from hand.
    fn _generate_consecutive_pairs(hand: &[Card]) -> Vec<Vec<Card>> {
        let mut consecutive_pairs = Vec::new();
        let rank_groups = Self::_group_by_rank(hand);

        // Get ranks that have at least 2 cards
        let mut valid_ranks: Vec<Rank> = rank_groups
            .iter()
            .filter(|(_r, cards)| cards.len() >= 2)
            .map(|(r, _cards)| *r)
            .collect();
        valid_ranks.sort();

        // Try all consecutive sequences of length 2+
        for length in 2..=valid_ranks.len() {
            for i in 0..=valid_ranks.len().saturating_sub(length) {
                let ranks = &valid_ranks[i..i + length];

                // Check if consecutive
                if Self::_is_consecutive(ranks) {
                    // Take 2 cards from each rank
                    let mut cards_list = Vec::new();
                    for rank in ranks {
                        cards_list.extend(&rank_groups[rank][0..2]);
                    }

                    if let Some(pattern) = PatternRecognizer::analyze_cards(&cards_list) {
                        if pattern.play_type == PlayType::ConsecutivePairs {
                            consecutive_pairs.push(cards_list);
                        }
                    }
                }
            }
        }

        consecutive_pairs
    }

    /// Generate all valid triples from hand.
    fn _generate_triples(hand: &[Card]) -> Vec<Vec<Card>> {
        let mut triples = Vec::new();
        let rank_groups = Self::_group_by_rank(hand);

        for (_rank, cards) in rank_groups {
            if cards.len() >= 3 {
                // Generate all 3-card combinations
                for i in 0..cards.len() {
                    for j in i + 1..cards.len() {
                        for k in j + 1..cards.len() {
                            let triple = vec![cards[i], cards[j], cards[k]];
                            if let Some(pattern) = PatternRecognizer::analyze_cards(&triple) {
                                if pattern.play_type == PlayType::Triple {
                                    triples.push(triple);
                                }
                            }
                        }
                    }
                }
            }
        }

        triples
    }

    /// Generate all valid triple with kicker combinations (1-2 kickers).
    ///
    /// According to GAME_RULE.md: 三张牌可以带牌（0-2张）
    /// This generates Triple with 1 or 2 kickers (any cards, not just pairs).
    fn _generate_triple_with_kickers(hand: &[Card]) -> Vec<Vec<Card>> {
        let mut results = Vec::new();
        let rank_groups = Self::_group_by_rank(hand);

        // Find all ranks with at least 3 cards (can form triple)
        let triple_ranks: Vec<Rank> = rank_groups
            .iter()
            .filter(|(_r, cards)| cards.len() >= 3)
            .map(|(r, _cards)| *r)
            .collect();

        for triple_rank in &triple_ranks {
            // Get the first 3 cards of this rank as the triple
            let triple_cards: Vec<Card> = rank_groups[triple_rank][0..3].to_vec();

            // Get all available kicker cards (excluding the triple cards)
            let available_kickers: Vec<Card> = hand
                .iter()
                .copied()
                .filter(|c| !triple_cards.contains(c))
                .collect();

            // Generate triple with 1 kicker
            for kicker in &available_kickers {
                let mut combo = triple_cards.clone();
                combo.push(*kicker);

                if let Some(pattern) = PatternRecognizer::analyze_cards(&combo) {
                    if pattern.play_type == PlayType::Triple && pattern.card_count == 4 {
                        results.push(combo);
                    }
                }
            }

            // Generate triple with 2 kickers
            for i in 0..available_kickers.len() {
                for j in i + 1..available_kickers.len() {
                    let mut combo = triple_cards.clone();
                    combo.push(available_kickers[i]);
                    combo.push(available_kickers[j]);

                    if let Some(pattern) = PatternRecognizer::analyze_cards(&combo) {
                        if pattern.play_type == PlayType::Triple && pattern.card_count == 5 {
                            results.push(combo);
                        }
                    }
                }
            }
        }

        results
    }

    /// Generate all valid airplane patterns (consecutive triples).
    fn _generate_airplanes(hand: &[Card]) -> Vec<Vec<Card>> {
        let mut airplanes = Vec::new();
        let rank_groups = Self::_group_by_rank(hand);

        // Get ranks with at least 3 cards
        let mut valid_ranks: Vec<Rank> = rank_groups
            .iter()
            .filter(|(_r, cards)| cards.len() >= 3)
            .map(|(r, _cards)| *r)
            .collect();
        valid_ranks.sort();

        // Try all consecutive sequences of length 2+
        for length in 2..=valid_ranks.len() {
            for i in 0..=valid_ranks.len().saturating_sub(length) {
                let ranks = &valid_ranks[i..i + length];

                // Check if consecutive
                if Self::_is_consecutive(ranks) {
                    // Take 3 cards from each rank
                    let mut cards_list = Vec::new();
                    for rank in ranks {
                        cards_list.extend(&rank_groups[rank][0..3]);
                    }

                    if let Some(pattern) = PatternRecognizer::analyze_cards(&cards_list) {
                        if pattern.play_type == PlayType::Airplane {
                            airplanes.push(cards_list);
                        }
                    }
                }
            }
        }

        airplanes
    }

    /// Generate all valid airplane with wings patterns.
    fn _generate_airplane_with_wings(hand: &[Card]) -> Vec<Vec<Card>> {
        let mut results = Vec::new();
        let rank_groups = Self::_group_by_rank(hand);

        // Get consecutive triples (airplanes)
        let mut valid_ranks: Vec<Rank> = rank_groups
            .iter()
            .filter(|(_r, cards)| cards.len() >= 3)
            .map(|(r, _cards)| *r)
            .collect();
        valid_ranks.sort();

        for length in 2..=valid_ranks.len() {
            for i in 0..=valid_ranks.len().saturating_sub(length) {
                let ranks = &valid_ranks[i..i + length];

                if !Self::_is_consecutive(ranks) {
                    continue;
                }

                // Get airplane cards
                let mut airplane_cards = Vec::new();
                for rank in ranks {
                    airplane_cards.extend(&rank_groups[rank][0..3]);
                }

                // Find available pairs for wings
                let remaining_cards: Vec<Card> = hand
                    .iter()
                    .copied()
                    .filter(|c| !airplane_cards.contains(c))
                    .collect();
                let remaining_groups = Self::_group_by_rank(&remaining_cards);

                let pair_ranks: Vec<Rank> = remaining_groups
                    .iter()
                    .filter(|(_r, cards)| cards.len() >= 2)
                    .map(|(r, _cards)| *r)
                    .collect();

                // Need same number of pairs as triples
                if pair_ranks.len() >= length {
                    // Try combinations of pairs
                    Self::_generate_pair_combinations(&pair_ranks, length, &remaining_groups)
                        .iter()
                        .for_each(|wing_cards| {
                            let mut combo = airplane_cards.clone();
                            combo.extend(wing_cards);

                            if let Some(pattern) = PatternRecognizer::analyze_cards(&combo) {
                                if pattern.play_type == PlayType::AirplaneWithWings {
                                    results.push(combo);
                                }
                            }
                        });
                }
            }
        }

        results
    }

    /// Generate pair combinations for airplane wings.
    fn _generate_pair_combinations(
        pair_ranks: &[Rank],
        count: usize,
        rank_groups: &HashMap<Rank, Vec<Card>>,
    ) -> Vec<Vec<Card>> {
        let mut results = Vec::new();

        // Generate all combinations of `count` ranks from `pair_ranks`
        Self::_combinations_of_ranks(pair_ranks, count)
            .iter()
            .for_each(|ranks_combo| {
                let mut wing_cards = Vec::new();
                for rank in ranks_combo {
                    wing_cards.extend(&rank_groups[rank][0..2]);
                }
                results.push(wing_cards);
            });

        results
    }

    /// Generate all combinations of ranks.
    fn _combinations_of_ranks(ranks: &[Rank], k: usize) -> Vec<Vec<Rank>> {
        if k == 0 {
            return vec![Vec::new()];
        }
        if ranks.is_empty() || k > ranks.len() {
            return Vec::new();
        }

        let mut results = Vec::new();

        // Include first element
        for sub_combo in Self::_combinations_of_ranks(&ranks[1..], k - 1) {
            let mut combo = vec![ranks[0]];
            combo.extend(sub_combo);
            results.push(combo);
        }

        // Exclude first element
        results.extend(Self::_combinations_of_ranks(&ranks[1..], k));

        results
    }

    /// Generate all valid bombs from hand.
    fn _generate_bombs(hand: &[Card]) -> Vec<Vec<Card>> {
        let mut bombs = Vec::new();
        let rank_groups = Self::_group_by_rank(hand);

        for (_rank, cards) in rank_groups {
            if cards.len() >= 4 {
                // Generate bombs of all possible sizes (4, 5, 6, etc.)
                for size in 4..=cards.len() {
                    // Generate all combinations of `size` cards
                    Self::_combinations_of_cards(&cards, size)
                        .iter()
                        .for_each(|bomb| {
                            if let Some(pattern) = PatternRecognizer::analyze_cards(bomb) {
                                if pattern.play_type == PlayType::Bomb {
                                    bombs.push(bomb.clone());
                                }
                            }
                        });
                }
            }
        }

        bombs
    }

    /// Generate all combinations of cards.
    fn _combinations_of_cards(cards: &[Card], k: usize) -> Vec<Vec<Card>> {
        if k == 0 {
            return vec![Vec::new()];
        }
        if cards.is_empty() || k > cards.len() {
            return Vec::new();
        }

        let mut results = Vec::new();

        // Include first element
        for sub_combo in Self::_combinations_of_cards(&cards[1..], k - 1) {
            let mut combo = vec![cards[0]];
            combo.extend(sub_combo);
            results.push(combo);
        }

        // Exclude first element
        results.extend(Self::_combinations_of_cards(&cards[1..], k));

        results
    }

    /// Generate all valid tongzi patterns (3 same suit, same rank).
    fn _generate_tongzi(hand: &[Card]) -> Vec<Vec<Card>> {
        let mut tongzi = Vec::new();

        // Group by (suit, rank)
        let mut suit_rank_groups: HashMap<(Suit, Rank), Vec<Card>> = HashMap::new();
        for card in hand {
            suit_rank_groups
                .entry((card.suit, card.rank))
                .or_default()
                .push(*card);
        }

        // Find suit-rank combinations with 3+ cards
        for ((_suit, _rank), cards) in suit_rank_groups {
            if cards.len() >= 3 {
                // Generate all 3-card combinations
                for i in 0..cards.len() {
                    for j in i + 1..cards.len() {
                        for k in j + 1..cards.len() {
                            let triple = vec![cards[i], cards[j], cards[k]];
                            if let Some(pattern) = PatternRecognizer::analyze_cards(&triple) {
                                if pattern.play_type == PlayType::Tongzi {
                                    tongzi.push(triple);
                                }
                            }
                        }
                    }
                }
            }
        }

        tongzi
    }

    /// Generate all valid dizha patterns (2 of each suit for same rank).
    fn _generate_dizha(hand: &[Card]) -> Vec<Vec<Card>> {
        let mut dizha = Vec::new();
        let rank_groups = Self::_group_by_rank(hand);

        for (_rank, cards) in rank_groups {
            if cards.len() >= 8 {
                // Group by suit
                let mut suit_groups: HashMap<Suit, Vec<Card>> = HashMap::new();
                for card in cards {
                    suit_groups.entry(card.suit).or_default().push(card);
                }

                // Check if all 4 suits have at least 2 cards
                let all_suits = [Suit::Spades, Suit::Hearts, Suit::Clubs, Suit::Diamonds];
                if all_suits
                    .iter()
                    .all(|suit| suit_groups.get(suit).map_or(0, |v| v.len()) >= 2)
                {
                    // Take 2 cards from each suit
                    let mut dizha_cards = Vec::new();
                    for suit in &all_suits {
                        dizha_cards.extend(&suit_groups[suit][0..2]);
                    }

                    if let Some(pattern) = PatternRecognizer::analyze_cards(&dizha_cards) {
                        if pattern.play_type == PlayType::Dizha {
                            dizha.push(dizha_cards);
                        }
                    }
                }
            }
        }

        dizha
    }

    // ========== Helper Methods for generate_beating_plays_with_same_type_or_trump ==========

    /// Generate single cards higher than current single.
    fn _generate_higher_singles(hand: &[Card], current_pattern: &PlayPattern) -> Vec<Vec<Card>> {
        let mut higher_singles = Vec::new();
        let current_rank = current_pattern.primary_rank;

        for card in hand {
            if card.rank.value() > current_rank.value() {
                higher_singles.push(vec![*card]);
            }
        }

        higher_singles
    }

    /// Generate pairs higher than current pair.
    fn _generate_higher_pairs(hand: &[Card], current_pattern: &PlayPattern) -> Vec<Vec<Card>> {
        let all_pairs = Self::_generate_pairs(hand);
        let current_rank = current_pattern.primary_rank;

        all_pairs
            .into_iter()
            .filter(|pair| {
                PatternRecognizer::analyze_cards(pair)
                    .map_or(false, |p| p.primary_rank.value() > current_rank.value())
            })
            .collect()
    }

    /// Generate consecutive pairs higher than current consecutive pairs.
    fn _generate_higher_consecutive_pairs(
        hand: &[Card],
        current_pattern: &PlayPattern,
    ) -> Vec<Vec<Card>> {
        let all_consecutive = Self::_generate_consecutive_pairs(hand);
        let current_rank = current_pattern.primary_rank;
        let current_count = current_pattern.card_count;

        all_consecutive
            .into_iter()
            .filter(|consecutive| {
                PatternRecognizer::analyze_cards(consecutive).map_or(false, |p| {
                    consecutive.len() == current_count
                        && p.primary_rank.value() > current_rank.value()
                })
            })
            .collect()
    }

    /// Generate triples higher than current triple.
    fn _generate_higher_triples(hand: &[Card], current_pattern: &PlayPattern) -> Vec<Vec<Card>> {
        let all_triples = Self::_generate_triples(hand);
        let current_rank = current_pattern.primary_rank;

        all_triples
            .into_iter()
            .filter(|triple| {
                PatternRecognizer::analyze_cards(triple)
                    .map_or(false, |p| p.primary_rank.value() > current_rank.value())
            })
            .collect()
    }

    /// Generate airplanes higher than current airplane.
    fn _generate_higher_airplanes(hand: &[Card], current_pattern: &PlayPattern) -> Vec<Vec<Card>> {
        let all_airplanes = Self::_generate_airplanes(hand);
        let current_rank = current_pattern.primary_rank;
        let current_count = current_pattern.card_count;

        all_airplanes
            .into_iter()
            .filter(|airplane| {
                PatternRecognizer::analyze_cards(airplane).map_or(false, |p| {
                    airplane.len() == current_count && p.primary_rank.value() > current_rank.value()
                })
            })
            .collect()
    }

    /// Generate airplane-with-wings higher than current airplane-with-wings.
    fn _generate_higher_airplane_with_wings(
        hand: &[Card],
        current_pattern: &PlayPattern,
    ) -> Vec<Vec<Card>> {
        let all_airplane_wings = Self::_generate_airplane_with_wings(hand);
        let current_rank = current_pattern.primary_rank;
        let current_count = current_pattern.card_count;

        all_airplane_wings
            .into_iter()
            .filter(|combo| {
                PatternRecognizer::analyze_cards(combo).map_or(false, |p| {
                    combo.len() == current_count && p.primary_rank.value() > current_rank.value()
                })
            })
            .collect()
    }

    /// Generate bombs higher than current bomb.
    fn _generate_higher_bombs(hand: &[Card], current_pattern: &PlayPattern) -> Vec<Vec<Card>> {
        let all_bombs = Self::_generate_bombs(hand);
        let current_rank = current_pattern.primary_rank;
        let current_size = current_pattern.card_count;

        all_bombs
            .into_iter()
            .filter(|bomb| {
                PatternRecognizer::analyze_cards(bomb).map_or(false, |p| {
                    // Higher rank with same size, or more cards with any rank
                    bomb.len() > current_size
                        || (bomb.len() == current_size
                            && p.primary_rank.value() > current_rank.value())
                })
            })
            .collect()
    }

    /// Generate tongzi higher than current tongzi.
    fn _generate_higher_tongzi(hand: &[Card], current_pattern: &PlayPattern) -> Vec<Vec<Card>> {
        let all_tongzi = Self::_generate_tongzi(hand);

        all_tongzi
            .into_iter()
            .filter(|tongzi| PlayValidator::can_beat_play(tongzi, Some(current_pattern)))
            .collect()
    }

    /// Generate dizha higher than current dizha.
    fn _generate_higher_dizha(hand: &[Card], current_pattern: &PlayPattern) -> Vec<Vec<Card>> {
        let all_dizha = Self::_generate_dizha(hand);
        let current_rank = current_pattern.primary_rank;

        all_dizha
            .into_iter()
            .filter(|dizha| {
                PatternRecognizer::analyze_cards(dizha)
                    .map_or(false, |p| p.primary_rank.value() > current_rank.value())
            })
            .collect()
    }
}
