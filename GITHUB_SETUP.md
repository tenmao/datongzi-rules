# GitHub 设置指南

## 快速开始

### 1. 在 GitHub 上创建仓库

访问 https://github.com/new 创建新仓库：

- **Repository name**: `datongzi-rules`
- **Description**: `零依赖的打筒子游戏规则引擎库（Python + Rust）`
- **Visibility**: Public 或 Private（根据需要）
- **不要**勾选 "Initialize this repository with..."（已有代码）

### 2. 推送代码到 GitHub

```bash
# 1. 添加远程仓库（替换 yourusername 为你的 GitHub 用户名）
git remote add origin https://github.com/yourusername/datongzi-rules.git

# 2. 查看当前状态
git status

# 3. 添加所有新文件
git add .

# 4. 提交更改
git commit -m "feat: 添加 Rust 实现基础架构和 CI/CD

- 创建 Cargo Workspace 结构
- 实现基础数据模型（Card, Deck, GameConfig）
- 重组项目结构（Python → python/，Rust → rust/）
- 添加 GitHub Actions CI/CD 配置
- 创建跨语言测试框架
- 所有 Python 测试通过（270 个测试，88.60% 覆盖率）"

# 5. 推送到 GitHub
git push -u origin main

# 如果你的默认分支是 master，使用：
# git push -u origin master
```

### 3. 验证 CI/CD 运行

推送成功后，访问你的 GitHub 仓库：

```
https://github.com/yourusername/datongzi-rules/actions
```

你应该看到三个工作流正在运行：

- ✅ **Rust CI**: 检查 Rust 代码格式、测试、文档
- ✅ **Python CI**: 运行 Python 测试、类型检查
- ✅ **Cross-Language Tests**: 验证 Python 和 Rust 一致性

### 4. 添加 Badges（可选）

在 GitHub Actions 页面，点击工作流名称，然后点击"Create status badge"，复制 Markdown 代码到 README.md：

```markdown
![Rust CI](https://github.com/yourusername/datongzi-rules/workflows/Rust%20CI/badge.svg)
![Python CI](https://github.com/yourusername/datongzi-rules/workflows/Python%20CI/badge.svg)
```

---

## 常见问题

### Q: 推送失败，提示 "Updates were rejected"？

```bash
# 先拉取远程更改
git pull origin main --rebase

# 再推送
git push -u origin main
```

### Q: 如何更新远程仓库地址？

```bash
# 查看当前远程仓库
git remote -v

# 更新远程仓库地址
git remote set-url origin https://github.com/yourusername/datongzi-rules.git
```

### Q: CI/CD 运行失败了怎么办？

1. 访问 GitHub Actions 页面查看详细错误
2. 点击失败的工作流查看日志
3. 修复问题后重新推送

常见问题：
- Rust 工具链下载失败：等待几分钟后重试
- Python 依赖安装失败：检查 `pyproject.toml` 配置
- 测试失败：查看具体测试日志

---

## 后续步骤

### 1. 设置分支保护规则（推荐）

在 GitHub 仓库设置中：

```
Settings → Branches → Branch protection rules → Add rule
```

规则建议：
- ✅ Require a pull request before merging
- ✅ Require status checks to pass before merging
  - rust-ci: Check
  - python-ci: Test
  - cross-language-tests: consistency-test
- ✅ Require conversation resolution before merging

### 2. 启用 Codecov（代码覆盖率报告）

1. 访问 https://codecov.io/
2. 使用 GitHub 账号登录
3. 添加你的仓库
4. 复制 Codecov token
5. 在 GitHub 仓库设置中添加 Secret：
   ```
   Settings → Secrets → New repository secret
   Name: CODECOV_TOKEN
   Value: <你的token>
   ```

### 3. 配置自动合并（可选）

如果你想在所有检查通过后自动合并 PR：

1. 安装 GitHub App: Mergify 或 auto-merge
2. 创建 `.github/mergify.yml` 配置文件

---

## CI/CD 工作流说明

### Rust CI (`.github/workflows/rust-ci.yml`)

运行内容：
- ✅ 格式检查（rustfmt）
- ✅ Lint 检查（clippy）
- ✅ 单元测试（cargo test）
- ✅ 代码覆盖率（cargo tarpaulin）
- ✅ 安全审计（cargo audit）
- ✅ 文档生成（cargo doc）

运行条件：
- 修改 `rust/` 目录下的文件
- 修改 `.github/workflows/rust-ci.yml`

### Python CI (`.github/workflows/python-ci.yml`)

运行内容：
- ✅ 单元测试（pytest）
- ✅ 代码覆盖率（pytest-cov）
- ✅ 格式检查（black）
- ✅ Lint 检查（ruff）
- ✅ 类型检查（mypy）

运行条件：
- 修改 `python/` 目录下的文件
- 修改 `.github/workflows/python-ci.yml`

### Cross-Language Tests (`.github/workflows/cross-language-tests.yml`)

运行内容：
- ✅ 运行 Python 测试
- ✅ 运行 Rust 测试（Phase 2+ 实现后）
- ✅ 对比结果确保一致性
- ✅ 生成性能对比报告

运行条件：
- 每次 push 或 pull request
- 每天 00:00 UTC 自动运行

---

## 开发工作流

### 日常开发

```bash
# 1. 创建新分支
git checkout -b feature/my-feature

# 2. 修改代码
# ... 编辑文件 ...

# 3. 本地测试
cd python && python run.py test
cd ../rust && cargo test

# 4. 提交
git add .
git commit -m "feat: 添加新功能"

# 5. 推送
git push origin feature/my-feature

# 6. 在 GitHub 上创建 Pull Request
# GitHub 会自动运行所有 CI 检查
```

### 团队协作

1. **Fork 仓库**（外部贡献者）
2. **创建 PR**
3. **等待 CI 检查通过**
4. **Code Review**
5. **合并到 main**

---

## 监控与维护

### 查看 CI/CD 历史

```
https://github.com/yourusername/datongzi-rules/actions
```

### 查看测试覆盖率

```
https://codecov.io/gh/yourusername/datongzi-rules
```

### 安全漏洞告警

GitHub 会自动检测依赖漏洞：

```
Security → Dependabot alerts
```

---

## 需要帮助？

- 📖 GitHub Actions 文档：https://docs.github.com/actions
- 📖 Rust CI 最佳实践：https://rust-lang.github.io/rustup-components-history/
- 📖 Python 测试指南：https://docs.pytest.org/
