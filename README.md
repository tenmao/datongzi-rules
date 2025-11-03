# Da Tong Zi Rules Engine

零依赖的打筒子游戏规则引擎库。

## 特性

- ✅ **零依赖**：仅使用 Python 3.12+ 标准库
- ✅ **高性能**：比 pydantic + structlog 实现快 18-25%
- ✅ **完整规则**：支持所有打筒子牌型和规则
- ✅ **AI 友好**：提供出牌生成、手牌评估等辅助接口
- ✅ **CV 纠错**：基于规则约束的识别纠错算法
- ✅ **规则变体**：支持 3 副牌、4 副牌、多人数配置

## 安装

```bash
# 开发模式安装
pip install -e .
```

## 快速开始

```python
from datongzi_rules import Card, Rank, Suit, PatternRecognizer

# 创建牌
cards = [
    Card(Suit.SPADES, Rank.ACE),
    Card(Suit.HEARTS, Rank.ACE),
    Card(Suit.CLUBS, Rank.ACE),
]

# 识别牌型
pattern = PatternRecognizer.analyze_cards(cards)
print(f"Pattern: {pattern.play_type.name}")  # TRIPLE
print(f"Rank: {pattern.primary_rank.name}")  # ACE
```

## 核心模块

### 模型（models）
- `Card`, `Rank`, `Suit`, `Deck` - 基础牌类
- `GameConfig` - 游戏配置

### 牌型识别（patterns）
- `PatternRecognizer` - 牌型识别器
- `PlayValidator` - 出牌验证器
- `PlayType`, `PlayPattern` - 牌型定义

### 计分（scoring）
- `ScoringEngine` - 计分引擎
- `BonusType` - 奖励类型

### AI 辅助（ai_helpers）
- `PlayGenerator` - 生成所有合法出牌
- `HandEvaluator` - 评估手牌强度
- `PatternSuggester` - CV 识别纠错

## 开发

```bash
# 运行测试
python run.py test

# 代码检查
python run.py lint

# 类型检查
python run.py type

# 完整检查
python run.py check
```

## 许可证

MIT License
