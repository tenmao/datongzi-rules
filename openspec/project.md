# Project Context

## Purpose

`datongzi-rules` 是"打筒子"游戏的权威规则引擎库，零依赖纯 Python 实现。

**核心职责**：
- 提供牌型识别、出牌验证、计分逻辑、AI 辅助工具等核心规则 API
- 供上层游戏引擎 `datongzi` 调用
- 作为独立子模块，不包含游戏状态管理、UI、AI 策略

**设计目标**：
- 零依赖（仅使用 Python 3.12+ 标准库）
- 高性能（牌型识别 ~150K ops/sec）
- 类型安全（完整类型提示，支持静态类型检查）
- 高测试覆盖率（270+ 测试用例，88.66% 覆盖率）

## Tech Stack

### Core Technologies
- **Python 3.12+**：仅使用标准库，零第三方依赖
- **Type Hints**：完整类型标注，支持 mypy 静态检查

### Development Tools
- **pytest** 8.0.0+：单元测试、集成测试、性能基准测试
- **pytest-cov** 4.1.0+：代码覆盖率报告
- **mypy** 1.8.0+：静态类型检查（strict 模式）
- **black** 24.0.0+：代码格式化（88 字符行宽）
- **ruff** 0.2.0+：快速 linter（替代 flake8/isort）

### Build System
- **setuptools** 68.0+：包管理和分发
- **wheel**：二进制分发格式

## Project Conventions

### Code Style

#### Naming Conventions
遵循 `NAME_CONVENTION.md`：

- **文件名**：`lowercase_with_underscores.py`
  - `card.py`, `pattern_recognizer.py`, `play_generator.py`
- **类名**：`PascalCase`
  - `Card`, `PatternRecognizer`, `PlayGenerator`, `ScoreComputation`
- **函数/方法**：`lowercase_with_underscores`
  - `generate_all_plays()`, `analyze_cards()`, `can_beat_play()`
- **常量**：`UPPERCASE_WITH_UNDERSCORES`
  - `MAX_COMBINATIONS`, `DEFAULT_NUM_DECKS`
- **枚举值**：`UPPERCASE`
  - `PlayType.SINGLE`, `BonusType.ROUND_WIN`
- **私有成员**：`_leading_underscore`
  - `_generate_pairs()`, `_group_by_rank()`

#### 游戏术语翻译
| 中文 | 英文 | 说明 |
|-----|------|------|
| 筒子 | Tongzi | 同花三张（音译）|
| 地炸 | Dizha | 8 张同数字（音译）|
| 炸弹 | Bomb | 4 张及以上同数字 |
| 王牌 | Trump | 地炸/筒子/炸弹统称 |
| 飞机 | Airplane | 连续数字的三张 |
| 连对 | Consecutive Pairs | 两连对及以上 |
| 有牌必打 | Must Play If Can Beat | 核心规则 |

#### 方法命名模式
- **生成器**：`generate_*`, `create_*`
  - `generate_all_plays()`, `create_standard_deck()`
- **验证/检查**：`is_*`, `can_*`, `has_*`
  - `can_beat_play()`, `is_consecutive()`, `has_must_play_violation()`
- **分析/计算**：`analyze_*`, `calculate_*`, `count_*`
  - `analyze_cards()`, `calculate_total_score()`, `count_all_plays()`

#### 格式化规则
- **行宽**：88 字符（black 默认）
- **缩进**：4 空格
- **引号**：双引号优先
- **尾随逗号**：多行集合末尾保留逗号
- **导入顺序**：标准库 → 第三方库 → 本地模块（ruff 自动排序）

### Architecture Patterns

#### 分层架构（SOLID 原则）
```
Layer 1: models (数据层)
  ├── Card, Rank, Suit, Deck, GameConfig
  └── 不可变数据结构、配置验证
         ↓
Layer 2: patterns (识别层)
  ├── PatternRecognizer (牌型识别)
  ├── PlayValidator (出牌验证)
  └── PatternFinder (牌型查找)
         ↓
Layer 3: scoring (计分层)
  └── ScoreComputation (纯计算引擎，不管理状态)
         ↓
Layer 4: ai_helpers, variants (辅助层)
  ├── PlayGenerator (唯一合法出牌生成)
  ├── HandPatternAnalyzer (手牌结构分析)
  └── ConfigFactory (规则变体配置)
```

#### 依赖规则
- ✅ **允许**：上层 → 下层，同层互相依赖，所有层 → models
- ❌ **禁止**：下层 → 上层，`datongzi-rules` → `datongzi`

#### 单一职责原则 (SRP)
- `PatternRecognizer`：只负责识别牌型
- `PlayValidator`：只负责验证出牌是否合法
- `PlayGenerator`：只负责生成所有合法出牌（AI 的唯一出牌来源）
- `ScoreComputation`：只负责计分逻辑（纯计算，不管理状态）
- `HandPatternAnalyzer`：只负责手牌结构分析（非重叠分解）
- **严禁创建"上帝类"合并多个职责**

#### 开放封闭原则 (OCP)
- 通过 `GameConfig` 参数化规则变体，不修改核心代码
- 添加新牌型/规则变体时，遵循扩展而非修改

#### 依赖倒置原则 (DIP)
- 高层模块（AI/UI）依赖此规则库的抽象接口
- 严禁在高层重新实现规则逻辑

### Testing Strategy

#### 测试结构
```
tests/
├── unit/           # 单元测试（258 个）
│   ├── test_models.py
│   ├── test_patterns.py
│   ├── test_scoring.py
│   ├── test_ai_helpers.py
│   └── test_variants.py
├── integration/    # 集成测试（12 个）
│   ├── test_full_game_flow.py
│   └── test_game_simulation.py
└── benchmark/      # 性能基准测试
    └── test_performance.py
```

#### 测试要求
- **覆盖率目标**：>85%（当前 88.66%）
- **必须测试**：所有新功能必须包含单元测试
- **回归测试**：修改现有功能必须通过所有现有测试
- **性能测试**：性能敏感路径需要 benchmark 测试

#### 测试命令
```bash
# 运行所有测试（含覆盖率）
python run.py test

# 仅运行单元测试
python run.py unit

# 仅运行集成测试
python run.py integration

# 运行性能基准测试
python run.py benchmark

# 直接使用 pytest（单个测试文件）
pytest tests/unit/test_basic.py -v

# 直接使用 pytest（单个测试函数）
pytest tests/unit/test_basic.py::test_function_name -v
```

#### 测试标记
- `@pytest.mark.unit`：单元测试
- `@pytest.mark.integration`：集成测试
- `@pytest.mark.performance`：性能基准测试

### Git Workflow

#### Branching Strategy
- **main**：稳定分支，所有测试通过
- **feature/**：功能分支
- **fix/**：修复分支
- **refactor/**：重构分支

#### Commit Conventions
- **格式**：`<type>: <description>`
- **类型**：
  - `feat`: 新功能
  - `fix`: 修复 bug
  - `refactor`: 重构（不改变功能）
  - `test`: 添加/修改测试
  - `docs`: 文档更新
  - `perf`: 性能优化
  - `chore`: 构建/工具配置

#### 示例
```
feat: 添加飞机带翅膀牌型识别
fix: 修复筒子花色比较逻辑
refactor: 重构 PlayGenerator 提升性能
test: 添加地炸计分单元测试
docs: 更新 README API 文档
```

## Domain Context

### 打筒子游戏核心规则

#### 关键规则（修改代码前必读 GAME_RULE.md）
1. **回合制**：出牌后无人能打，回合结束，最后出牌者胜利
2. **有牌必打**：上家出牌后，如果手牌有大过的牌，则必须出
3. **牌型优先级**：地炸 > 筒子 > 炸弹 > 普通牌（单张/对子/连对/三张/飞机）
4. **计分规则**：
   - 回合获胜者得该回合所有 5/10/K 的分数
   - 筒子/地炸奖励分：K 筒子 100 分，A 筒子 200 分，2 筒子 300 分，地炸 400 分
   - 完成位置奖励：上游 +100 分，二游 -40 分，三游 -60 分
   - **只有回合最后出牌者得分，中间出的特殊牌不得分**

#### 牌型定义
- **炸弹**：4 张及以上相同数字，讲究大打小、多打少
- **筒子**：3 张相同花色相同数字（同花三张），压炸弹，花色也分大小（黑桃>红桃>梅花>方块）
- **地炸**：8 张同数字（4 种花色各 2 张），最强牌型
- **连对**：两连对及以上，没有单牌顺子
- **三张**：可以带 0-2 张
- **飞机**：连续数字的三张，可以带翅膀（每组带 0-2 张）

### 模块职责边界（关键约束）

#### ✅ 规则库职责（datongzi-rules）
- 牌型识别、出牌验证、计分逻辑
- 生成合法出牌、手牌结构分析
- 规则变体配置

#### ❌ 非规则库职责（由上层 datongzi 实现）
- 游戏状态管理（Round/Play/Game 对象）
- AI 策略实现（应在 `datongzi/ai` 实现）
- UI/前端逻辑（应在 `datongzi/ui` 实现）

#### 计分引擎职责（ScoreComputation）
**重要**：这是纯计算引擎，不管理游戏状态！

- ✅ 计算回合得分（接收上层收集的 round_cards）
- ✅ 计算筒子/地炸奖励（接收已识别的 winning_pattern）
- ✅ 计算完成位置奖励
- ❌ 判断回合结束（上层职责）
- ❌ 跟踪回合状态（上层职责）
- ❌ 收集回合内所有牌（上层职责）

## Important Constraints

### 技术约束
1. **零依赖原则**：
   - ✅ 只能使用 Python 3.12+ 标准库
   - ❌ 禁止引入任何第三方运行时依赖（开发依赖除外）

2. **依赖方向约束**：
   - ✅ `datongzi` → `datongzi-rules`（游戏引擎依赖规则库）
   - ❌ `datongzi-rules` → `datongzi`（规则库永不依赖游戏引擎）

3. **职责边界约束**：
   - 所有规则逻辑只在此库实现，避免在上层重复实现
   - 规则库不实现状态管理、AI 策略、UI 逻辑

### 架构约束（反模式警告）

#### ❌ 禁止在高层重新实现规则
```python
# ❌ 错误：在 datongzi/ai 中重新实现规则
class AI:
    def _can_beat(self, cards, current_play):
        # 自己实现验证逻辑...

# ✅ 正确：依赖规则库
from datongzi_rules import PlayValidator
can_beat = PlayValidator.can_beat_play(cards, current_play)
```

#### ❌ 禁止多处生成合法出牌
```python
# ❌ 错误：在 AI 中重复实现 PlayGenerator
class AI:
    def _get_legal_moves(self, hand):
        # 重新实现生成逻辑...

# ✅ 正确：使用 PlayGenerator
from datongzi_rules import PlayGenerator
moves = PlayGenerator.generate_beating_plays_with_same_type_or_trump(hand, current_pattern)
```

#### ❌ 禁止在规则库实现 AI 策略
```python
# ❌ 错误：在规则库实现复杂 AI
class HandEvaluator:
    def choose_best_play(self, hand, game_state):
        # 多步博弈推演...

# ✅ 正确：规则库只提供工具，AI 在上层实现
# datongzi/ai/strategy.py
class AIStrategy:
    def choose_best_play(self, valid_plays, hand, game_state):
        # AI 策略逻辑（基于 PlayGenerator 提供的 valid_plays）
```

#### ❌ 禁止在规则库管理游戏状态
```python
# ❌ 错误：在规则库创建 Round/Game 类
class Round:
    plays: list[Play]
    current_player: Player

# ✅ 正确：状态管理在上层
# datongzi/models/round.py
class Round:
    def __init__(self, players):
        self.plays = []
        self.scoring_engine = ScoreComputation(config)  # 只使用计分引擎
```

### 性能约束
- **牌型识别**：~150K ops/sec (0.006ms/op)
- **游戏设置**：~5K games/sec (0.19ms/op)
- **出牌生成（满手牌 41 张）**：6.38ms/op
- **计分计算**：~140K ops/sec (0.007ms/op)

### 代码质量约束
- **测试覆盖率**：>85%（当前 88.66%）
- **类型检查**：mypy strict 模式，0 错误
- **代码格式化**：black + ruff，0 警告
- **文档完整性**：所有公共 API 必须有 docstring

## External Dependencies

### 无运行时依赖
该项目是零依赖库，不依赖任何外部服务或第三方库。

### 上层依赖方（Consumers）
- **datongzi**：主游戏引擎，依赖此规则库
  - 游戏状态管理（Round/Play/Game）
  - AI 策略实现（基于此库的工具）
  - UI/前端逻辑

### 开发依赖（仅开发时使用）
- pytest：测试框架
- pytest-cov：覆盖率报告
- mypy：类型检查
- black：代码格式化
- ruff：代码质量检查

### 构建工具
- setuptools：包构建
- wheel：二进制分发

## 重要文档

- **CLAUDE.md**：AI 助手开发指南（本文件）
- **GAME_RULE.md**：游戏规则详细定义（修改规则逻辑前必读）
- **NAME_CONVENTION.md**：命名规范
- **ARCHITECTURE.md**：SOLID 原则详细说明、模块职责、反模式警告
- **README.md**：完整 API 文档、使用示例、常见问题

## 代码修改检查清单

### 添加新牌型
1. 在 `PlayType` 枚举添加新类型
2. 在 `PatternRecognizer.analyze_cards()` 添加识别逻辑
3. 在 `PlayFormationValidator` 添加验证方法
4. 在 `PlayValidator.can_beat_play()` 添加对抗规则
5. 在 `ScoreComputation` 添加计分规则（如果有奖励）
6. 添加单元测试

### 添加新规则变体
1. 在 `GameConfig` 添加新配置字段
2. 在 `ConfigFactory` 添加新工厂方法
3. 在相关模块读取配置
4. 添加单元测试

### SOLID 自检
- [ ] SRP：是否只做一件事？
- [ ] OCP：是否可以通过配置/组合扩展，而非修改现有代码？
- [ ] DIP：是否依赖抽象而非具体实现？
- [ ] 是否违反了依赖方向（上→下）？
- [ ] 是否在高层重复实现了底层规则逻辑？
- [ ] 是否在规则库实现了状态管理或 AI 策略？（应在上层）
