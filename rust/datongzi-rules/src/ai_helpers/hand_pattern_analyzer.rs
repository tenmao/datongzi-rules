//! Hand pattern analysis for AI decision making.
//!
//! This module provides structured analysis of hand resources grouped by pattern types.
//! It is the recommended way for AI to analyze hands, instead of generating all possible plays.

use std::collections::HashMap;
use std::fmt;

use crate::models::{Card, Rank, Suit};
use crate::patterns::{PatternRecognizer, PlayType};

/// Structured representation of hand resources grouped by pattern types.
///
/// ## Design Principles
/// - Each resource is a valid playable pattern
/// - Resources are non-overlapping (a card only appears in its "best" category)
/// - Sorted by strength (descending) within each category
/// - Priority: Dizha > Tongzi > Bomb > Airplane > Triple > ConsecPairs > Pair > Single
///
/// ## Examples
///
/// ```
/// use datongzi_rules::{Card, Rank, Suit, HandPatternAnalyzer};
///
/// let hand = vec![
///     Card::new(Suit::Spades, Rank::Ten),
///     Card::new(Suit::Hearts, Rank::Ten),
///     Card::new(Suit::Clubs, Rank::Ten),
///     Card::new(Suit::Diamonds, Rank::Ten),
/// ];
///
/// let patterns = HandPatternAnalyzer::analyze_patterns(&hand);
/// assert_eq!(patterns.bombs.len(), 1);
/// assert_eq!(patterns.trump_count, 1);
/// ```
#[derive(Debug, Clone, Default)]
pub struct HandPatterns {
    // Trump cards (highest priority resources)
    /// Dizha (地炸) - 8 cards of same rank (2 of each suit)
    pub dizha: Vec<Vec<Card>>,
    /// Tongzi (筒子) - 3 same suit, same rank
    pub tongzi: Vec<Vec<Card>>,
    /// Bombs (炸弹) - 4+ same rank
    pub bombs: Vec<Vec<Card>>,

    // Composite patterns (multi-card combinations)
    /// Airplane chains (飞机) - consecutive triples
    pub airplane_chains: Vec<Vec<Card>>,

    // Basic patterns (triple has higher priority than consecutive pairs)
    /// Triples (三张) - 3 same rank
    pub triples: Vec<Vec<Card>>,
    /// Consecutive pair chains (连对) - 2+ consecutive pairs
    pub consecutive_pair_chains: Vec<Vec<Card>>,
    /// Pairs (对子) - 2 same rank
    pub pairs: Vec<Vec<Card>>,
    /// Singles (单张) - individual cards
    pub singles: Vec<Card>,

    // Metadata
    /// Total number of cards
    pub total_cards: usize,
    /// Number of trump cards (dizha + tongzi + bombs)
    pub trump_count: usize,
    /// Has control cards (2s, As, or Ks)
    pub has_control_cards: bool,
}

impl fmt::Display for HandPatterns {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        writeln!(f, "HandPatterns({} cards):", self.total_cards)?;
        writeln!(
            f,
            "  Trump: {} (Dizha:{}, Tongzi:{}, Bombs:{})",
            self.trump_count,
            self.dizha.len(),
            self.tongzi.len(),
            self.bombs.len()
        )?;
        writeln!(
            f,
            "  Chains: Airplanes:{}, ConsecPairs:{})",
            self.airplane_chains.len(),
            self.consecutive_pair_chains.len()
        )?;
        write!(
            f,
            "  Basic: Triples:{}, Pairs:{}, Singles:{}",
            self.triples.len(),
            self.pairs.len(),
            self.singles.len()
        )
    }
}

/// Analyze hand patterns for AI decision making.
///
/// This is the recommended way for AI to analyze hands, instead of generating
/// all possible plays which causes combinatorial explosion.
///
/// ## Key Differences from PlayGenerator
/// - Returns structured data (`HandPatterns`) not list of plays
/// - Non-overlapping decomposition (each card assigned to best category)
/// - Focuses on "what resources do I have" not "what plays can I make"
/// - Much more efficient for AI strategy planning
///
/// ## Priority Order (Non-overlapping Extraction)
/// 1. Dizha (地炸)
/// 2. Tongzi (筒子)
/// 3. Bomb (炸弹)
/// 4. Airplane chains (飞机)
/// 5. Triples (三张) ← Higher priority than consecutive pairs
/// 6. Consecutive pair chains (连对) ← Lower priority, extracted after triples
/// 7. Pairs (对子)
/// 8. Singles (单张)
///
/// ## Example Usage
///
/// ```
/// use datongzi_rules::{Card, Rank, Suit, HandPatternAnalyzer};
///
/// let hand = vec![
///     Card::new(Suit::Spades, Rank::Ace),
///     Card::new(Suit::Hearts, Rank::Ace),
///     Card::new(Suit::Clubs, Rank::Ace),
/// ];
///
/// let patterns = HandPatternAnalyzer::analyze_patterns(&hand);
///
/// // AI can now decide:
/// if !patterns.dizha.is_empty() {
///     // I have dizha, can control the game
/// } else if !patterns.bombs.is_empty() {
///     // I have bombs, can beat most plays
/// } else if !patterns.triples.is_empty() {
///     // I have triples, strong basic patterns
/// }
/// ```
pub struct HandPatternAnalyzer;

impl HandPatternAnalyzer {
    /// Analyze hand and extract non-overlapping patterns.
    ///
    /// ## Strategy
    /// 1. Extract trump cards first (dizha, tongzi, bombs)
    /// 2. Extract airplane chains (consecutive triples)
    /// 3. Extract standalone triples (higher priority than consecutive pairs)
    /// 4. Re-scan remaining cards for consecutive pair chains
    /// 5. Extract pairs from remaining cards
    /// 6. Extract singles from remaining cards
    ///
    /// # Arguments
    ///
    /// * `hand` - Slice of cards in hand
    ///
    /// # Returns
    ///
    /// `HandPatterns` with structured decomposition
    #[must_use]
    pub fn analyze_patterns(hand: &[Card]) -> HandPatterns {
        if hand.is_empty() {
            return HandPatterns::default();
        }

        let mut patterns = HandPatterns {
            total_cards: hand.len(),
            ..Default::default()
        };

        let mut remaining_cards = hand.to_vec();

        // Step 1: Extract trump cards (highest priority)
        Self::_extract_trump_cards(&mut remaining_cards, &mut patterns);

        // Step 2: Extract airplane chains (consecutive triples)
        Self::_extract_airplane_chains(&mut remaining_cards, &mut patterns);

        // Step 3: Extract standalone triples (higher priority than consecutive pairs)
        Self::_extract_triples(&mut remaining_cards, &mut patterns);

        // Step 4: Re-scan for consecutive pair chains (after triples extracted)
        Self::_extract_consecutive_pair_chains(&mut remaining_cards, &mut patterns);

        // Step 5: Extract pairs from remaining cards
        Self::_extract_pairs(&mut remaining_cards, &mut patterns);

        // Step 6: Extract singles from remaining cards
        Self::_extract_singles(&mut remaining_cards, &mut patterns);

        // Step 7: Calculate metadata
        patterns.trump_count = patterns.dizha.len() + patterns.tongzi.len() + patterns.bombs.len();
        patterns.has_control_cards = hand
            .iter()
            .any(|c| matches!(c.rank, Rank::Two | Rank::Ace | Rank::King));

        // Debug logging removed for zero-dependency implementation

        patterns
    }

    // ========== Private Extraction Methods ==========

    /// Extract dizha, tongzi, and bombs.
    fn _extract_trump_cards(remaining_cards: &mut Vec<Card>, patterns: &mut HandPatterns) {
        // Extract dizha (highest priority trump)
        let dizha_list = Self::_find_dizha(remaining_cards);
        for dizha in dizha_list {
            patterns.dizha.push(dizha.clone());
            for card in &dizha {
                if let Some(pos) = remaining_cards.iter().position(|c| c == card) {
                    remaining_cards.remove(pos);
                }
            }
        }

        // Extract tongzi
        let tongzi_list = Self::_find_tongzi(remaining_cards);
        for tongzi in tongzi_list {
            patterns.tongzi.push(tongzi.clone());
            for card in &tongzi {
                if let Some(pos) = remaining_cards.iter().position(|c| c == card) {
                    remaining_cards.remove(pos);
                }
            }
        }

        // Extract bombs (4+ same rank)
        let bombs_list = Self::_find_bombs(remaining_cards);
        for bomb in bombs_list {
            patterns.bombs.push(bomb.clone());
            for card in &bomb {
                if let Some(pos) = remaining_cards.iter().position(|c| c == card) {
                    remaining_cards.remove(pos);
                }
            }
        }

        // Sort by strength (descending)
        patterns
            .dizha
            .sort_by(|a, b| b[0].rank.value().cmp(&a[0].rank.value()));
        patterns.tongzi.sort_by(|a, b| {
            b[0].suit
                .value()
                .cmp(&a[0].suit.value())
                .then(b[0].rank.value().cmp(&a[0].rank.value()))
        });
        patterns.bombs.sort_by(|a, b| {
            b.len()
                .cmp(&a.len())
                .then(b[0].rank.value().cmp(&a[0].rank.value()))
        });
    }

    /// Extract airplane chains (consecutive triples).
    fn _extract_airplane_chains(remaining_cards: &mut Vec<Card>, patterns: &mut HandPatterns) {
        let airplane_chains = Self::_find_airplane_chains(remaining_cards);
        for chain in airplane_chains {
            patterns.airplane_chains.push(chain.clone());
            for card in &chain {
                if let Some(pos) = remaining_cards.iter().position(|c| c == card) {
                    remaining_cards.remove(pos);
                }
            }
        }

        // Sort by length (descending), then by rank
        patterns.airplane_chains.sort_by(|a, b| {
            b.len()
                .cmp(&a.len())
                .then(b[0].rank.value().cmp(&a[0].rank.value()))
        });
    }

    /// Extract standalone triples.
    fn _extract_triples(remaining_cards: &mut Vec<Card>, patterns: &mut HandPatterns) {
        let triples_list = Self::_find_triples(remaining_cards);
        for triple in triples_list {
            patterns.triples.push(triple.clone());
            for card in &triple {
                if let Some(pos) = remaining_cards.iter().position(|c| c == card) {
                    remaining_cards.remove(pos);
                }
            }
        }

        // Sort by rank (descending)
        patterns
            .triples
            .sort_by(|a, b| b[0].rank.value().cmp(&a[0].rank.value()));
    }

    /// Extract consecutive pair chains (after triples extracted).
    fn _extract_consecutive_pair_chains(
        remaining_cards: &mut Vec<Card>,
        patterns: &mut HandPatterns,
    ) {
        let consec_pair_chains = Self::_find_consecutive_pair_chains(remaining_cards);
        for chain in consec_pair_chains {
            patterns.consecutive_pair_chains.push(chain.clone());
            for card in &chain {
                if let Some(pos) = remaining_cards.iter().position(|c| c == card) {
                    remaining_cards.remove(pos);
                }
            }
        }

        // Sort by length (descending), then by rank
        patterns.consecutive_pair_chains.sort_by(|a, b| {
            b.len()
                .cmp(&a.len())
                .then(b[0].rank.value().cmp(&a[0].rank.value()))
        });
    }

    /// Extract pairs from remaining cards.
    fn _extract_pairs(remaining_cards: &mut Vec<Card>, patterns: &mut HandPatterns) {
        let mut rank_groups: HashMap<Rank, Vec<Card>> = HashMap::new();
        for card in remaining_cards.iter() {
            rank_groups.entry(card.rank).or_default().push(*card);
        }

        // Extract pairs
        let mut ranks: Vec<Rank> = rank_groups.keys().copied().collect();
        ranks.sort_by_key(|b| std::cmp::Reverse(b.value()));

        for rank in ranks {
            let mut cards = rank_groups[&rank].clone();
            while cards.len() >= 2 {
                let pair = vec![cards[0], cards[1]];
                patterns.pairs.push(pair.clone());
                for card in &pair {
                    if let Some(pos) = remaining_cards.iter().position(|c| c == card) {
                        remaining_cards.remove(pos);
                    }
                }
                cards.drain(0..2);
            }
        }
    }

    /// Extract singles from remaining cards.
    fn _extract_singles(remaining_cards: &mut Vec<Card>, patterns: &mut HandPatterns) {
        // All remaining cards are singles
        patterns.singles = remaining_cards.clone();
        patterns
            .singles
            .sort_by(|a, b| b.rank.value().cmp(&a.rank.value()));
        remaining_cards.clear();
    }

    // ========== Private Finding Methods ==========

    /// Find all dizha (2 of each suit for same rank).
    fn _find_dizha(cards: &[Card]) -> Vec<Vec<Card>> {
        let mut rank_groups: HashMap<Rank, Vec<Card>> = HashMap::new();
        for card in cards {
            rank_groups.entry(card.rank).or_default().push(*card);
        }

        let mut dizha_list = Vec::new();
        for (_rank, rank_cards) in rank_groups {
            if rank_cards.len() < 8 {
                continue;
            }

            // Group by suit
            let mut suit_groups: HashMap<Suit, Vec<Card>> = HashMap::new();
            for card in &rank_cards {
                suit_groups.entry(card.suit).or_default().push(*card);
            }

            // Check if all 4 suits have at least 2 cards
            let all_suits = [Suit::Spades, Suit::Hearts, Suit::Clubs, Suit::Diamonds];
            if all_suits
                .iter()
                .all(|suit| suit_groups.get(suit).map_or(0, |v| v.len()) >= 2)
            {
                let mut dizha = Vec::new();
                for suit in &all_suits {
                    dizha.extend(&suit_groups[suit][0..2]);
                }

                // Validate
                if let Some(pattern) = PatternRecognizer::analyze_cards(&dizha) {
                    if pattern.play_type == PlayType::Dizha {
                        dizha_list.push(dizha);
                    }
                }
            }
        }

        dizha_list
    }

    /// Find all tongzi (3 same suit, same rank).
    fn _find_tongzi(cards: &[Card]) -> Vec<Vec<Card>> {
        let mut suit_rank_groups: HashMap<(Suit, Rank), Vec<Card>> = HashMap::new();
        for card in cards {
            suit_rank_groups
                .entry((card.suit, card.rank))
                .or_default()
                .push(*card);
        }

        let mut tongzi_list = Vec::new();
        for ((_suit, _rank), group_cards) in suit_rank_groups {
            if group_cards.len() >= 3 {
                let tongzi = group_cards[0..3].to_vec();
                if let Some(pattern) = PatternRecognizer::analyze_cards(&tongzi) {
                    if pattern.play_type == PlayType::Tongzi {
                        tongzi_list.push(tongzi);
                    }
                }
            }
        }

        tongzi_list
    }

    /// Find all bombs (4+ same rank).
    fn _find_bombs(cards: &[Card]) -> Vec<Vec<Card>> {
        let mut rank_groups: HashMap<Rank, Vec<Card>> = HashMap::new();
        for card in cards {
            rank_groups.entry(card.rank).or_default().push(*card);
        }

        let mut bombs_list = Vec::new();
        for (_rank, rank_cards) in rank_groups {
            if rank_cards.len() >= 4 {
                // Take the largest possible bomb
                let bomb = rank_cards.clone();
                if let Some(pattern) = PatternRecognizer::analyze_cards(&bomb) {
                    if pattern.play_type == PlayType::Bomb {
                        bombs_list.push(bomb);
                    }
                }
            }
        }

        bombs_list
    }

    /// Find all triples (3 same rank).
    fn _find_triples(cards: &[Card]) -> Vec<Vec<Card>> {
        let mut rank_groups: HashMap<Rank, Vec<Card>> = HashMap::new();
        for card in cards {
            rank_groups.entry(card.rank).or_default().push(*card);
        }

        let mut triples_list = Vec::new();
        for (_rank, rank_cards) in rank_groups {
            if rank_cards.len() >= 3 {
                let triple = rank_cards[0..3].to_vec();
                if let Some(pattern) = PatternRecognizer::analyze_cards(&triple) {
                    if pattern.play_type == PlayType::Triple {
                        triples_list.push(triple);
                    }
                }
            }
        }

        triples_list
    }

    /// Find longest airplane chains (consecutive triples).
    fn _find_airplane_chains(cards: &[Card]) -> Vec<Vec<Card>> {
        let mut rank_groups: HashMap<Rank, Vec<Card>> = HashMap::new();
        for card in cards {
            rank_groups.entry(card.rank).or_default().push(*card);
        }

        // Get ranks with at least 3 cards
        let mut valid_ranks: Vec<Rank> = rank_groups
            .iter()
            .filter(|(_r, cards)| cards.len() >= 3)
            .map(|(r, _cards)| *r)
            .collect();
        valid_ranks.sort();

        let mut chains = Vec::new();
        let mut i = 0;
        while i < valid_ranks.len() {
            // Try to build longest chain starting from valid_ranks[i]
            let mut chain_ranks = vec![valid_ranks[i]];
            let mut j = i + 1;

            while j < valid_ranks.len() {
                if valid_ranks[j].value() == chain_ranks.last().unwrap().value() + 1 {
                    chain_ranks.push(valid_ranks[j]);
                    j += 1;
                } else {
                    break;
                }
            }

            // Only keep chains of length >= 2
            if chain_ranks.len() >= 2 {
                let mut chain_cards = Vec::new();
                for rank in &chain_ranks {
                    chain_cards.extend(&rank_groups[rank][0..3]);
                }

                // Validate
                if let Some(pattern) = PatternRecognizer::analyze_cards(&chain_cards) {
                    if pattern.play_type == PlayType::Airplane {
                        chains.push(chain_cards);
                        i = j; // Skip to next unprocessed rank
                    } else {
                        i += 1;
                    }
                } else {
                    i += 1;
                }
            } else {
                i += 1;
            }
        }

        chains
    }

    /// Find longest consecutive pair chains.
    fn _find_consecutive_pair_chains(cards: &[Card]) -> Vec<Vec<Card>> {
        let mut rank_groups: HashMap<Rank, Vec<Card>> = HashMap::new();
        for card in cards {
            rank_groups.entry(card.rank).or_default().push(*card);
        }

        // Get ranks with at least 2 cards
        let mut valid_ranks: Vec<Rank> = rank_groups
            .iter()
            .filter(|(_r, cards)| cards.len() >= 2)
            .map(|(r, _cards)| *r)
            .collect();
        valid_ranks.sort();

        let mut chains = Vec::new();
        let mut i = 0;
        while i < valid_ranks.len() {
            // Try to build longest chain starting from valid_ranks[i]
            let mut chain_ranks = vec![valid_ranks[i]];
            let mut j = i + 1;

            while j < valid_ranks.len() {
                if valid_ranks[j].value() == chain_ranks.last().unwrap().value() + 1 {
                    chain_ranks.push(valid_ranks[j]);
                    j += 1;
                } else {
                    break;
                }
            }

            // Only keep chains of length >= 2
            if chain_ranks.len() >= 2 {
                let mut chain_cards = Vec::new();
                for rank in &chain_ranks {
                    chain_cards.extend(&rank_groups[rank][0..2]);
                }

                // Validate
                if let Some(pattern) = PatternRecognizer::analyze_cards(&chain_cards) {
                    if pattern.play_type == PlayType::ConsecutivePairs {
                        chains.push(chain_cards);
                        i = j; // Skip to next unprocessed rank
                    } else {
                        i += 1;
                    }
                } else {
                    i += 1;
                }
            } else {
                i += 1;
            }
        }

        chains
    }
}
