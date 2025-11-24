# Cross-Language Consistency Tests

这个目录包含用于验证 Python 和 Rust 实现一致性的测试框架。

## 架构

```
tests/cross-language/
├── test_cases.json      # 统一的测试用例定义
├── run_tests.py         # Python 测试运行器
├── results_python.json  # Python 测试结果（自动生成）
├── results_rust.json    # Rust 测试结果（自动生成）
└── README.md            # 本文件
```

## 运行测试

### 本地运行

```bash
# 运行所有跨语言测试
python tests/cross-language/run_tests.py

# 查看测试结果
cat tests/cross-language/results_python.json
```

### CI/CD 自动运行

每次推送到 GitHub 时，`.github/workflows/cross-language-tests.yml` 会自动：

1. 运行 Python 测试
2. 运行 Rust 测试（Phase 2+ 实现后）
3. 对比结果
4. 生成报告

## 测试用例格式

```json
{
  "test_suites": {
    "suite_name": [
      {
        "name": "test_group_name",
        "description": "Test description",
        "tests": [
          {
            "id": "test_001",
            "input": { "param": "value" },
            "expected": { "result": "value" }
          }
        ]
      }
    ]
  }
}
```

## 添加新测试

1. 编辑 `test_cases.json`
2. 添加新的测试用例到相应的 test suite
3. 运行 `python tests/cross-language/run_tests.py` 验证

## 当前测试覆盖

- ✅ Card 基础操作（创建、属性、排序）
- ✅ Deck 操作（创建、洗牌、发牌）
- ✅ GameConfig 验证
- 🚧 Pattern 识别（Phase 3）
- 🚧 Play 验证（Phase 3）
- 🚧 Scoring 计算（Phase 4）
- 🚧 AI Helpers（Phase 5）

## 状态码

- 0: 所有测试通过
- 1: 有测试失败或发生错误
