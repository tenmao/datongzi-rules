# Codecov 私有仓库配置指南

## 问题
私有仓库需要 Codecov token 才能上传覆盖率数据到 codecov.io。

## 配置步骤

### 1. 获取 Codecov Token

1. 访问 https://codecov.io/ 并使用 GitHub 账号登录
2. 点击右上角 "+ Add new repository"
3. 找到你的私有仓库 `datongzi-rules`
4. 点击仓库名称进入设置页面
5. 复制显示的 **Repository Upload Token**（格式类似 `a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6`）

### 2. 添加 Token 到 GitHub Secrets

1. 访问 GitHub 仓库设置页面：
   ```
   https://github.com/yourusername/datongzi-rules/settings/secrets/actions
   ```
   （将 `yourusername` 替换为你的 GitHub 用户名）

2. 点击 **"New repository secret"** 按钮

3. 填写 Secret 信息：
   - **Name**: `CODECOV_TOKEN`（必须是这个名称，大小写敏感）
   - **Value**: 粘贴步骤 1 中复制的 token

4. 点击 **"Add secret"** 保存

### 3. 验证配置

配置完成后，有两种方式触发 CI 并验证：

**方式 1: 推送新 commit**
```bash
git add .
git commit -m "chore: 配置 Codecov token"
git push
```

**方式 2: 手动重新运行 Actions**
1. 访问 GitHub Actions 页面：`https://github.com/yourusername/datongzi-rules/actions`
2. 选择一个已完成的工作流（如 "Python CI"）
3. 点击 "Re-run all jobs"

### 4. 查看覆盖率报告

CI 运行成功后：
1. 访问 Codecov 仓库页面：
   ```
   https://codecov.io/gh/yourusername/datongzi-rules
   ```
2. 应该能看到：
   - 总体覆盖率百分比
   - 各文件的详细覆盖率
   - 历史趋势图表
   - Python 和 Rust 的独立覆盖率（通过 flags 区分）

### 5. 添加 Codecov Badge（可选）

在 Codecov 仓库页面：
1. 点击 "Settings" → "Badge"
2. 复制 Markdown 代码（类似下面的格式）：
   ```markdown
   [![codecov](https://codecov.io/gh/yourusername/datongzi-rules/branch/main/graph/badge.svg?token=YOUR_TOKEN)](https://codecov.io/gh/yourusername/datongzi-rules)
   ```
3. 添加到 `README.md` 的徽章区域

## 当前配置状态

### ✅ 已完成

**Python CI 配置** (`.github/workflows/python-ci.yml`):
```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    files: python/coverage.xml      # XML 覆盖率报告
    flags: python                    # 标记为 Python 覆盖率
    fail_ci_if_error: false         # 上传失败不中断 CI
    token: ${{ secrets.CODECOV_TOKEN }}  # 使用 Secret
```

**Rust CI 配置** (`.github/workflows/rust-ci.yml`):
```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    files: rust/cobertura.xml       # XML 覆盖率报告
    flags: rust                      # 标记为 Rust 覆盖率
    fail_ci_if_error: false         # 上传失败不中断 CI
    token: ${{ secrets.CODECOV_TOKEN }}  # 使用 Secret
```

**Python 覆盖率生成** (`python/pyproject.toml`):
```toml
[tool.pytest.ini_options]
addopts = [
    # ... 其他选项 ...
    "--cov-report=xml",  # 生成 coverage.xml
]
```

### ⏳ 待完成

- [ ] 在 Codecov.io 获取 Repository Upload Token
- [ ] 在 GitHub Secrets 添加 `CODECOV_TOKEN`
- [ ] 推送 commit 或重新运行 Actions 验证

## 常见问题

### Q: 为什么私有仓库需要 token？
**A:** Codecov 需要验证你有权限上传数据到私有仓库。公开仓库不需要 token。

### Q: token 安全吗？
**A:** 是的。GitHub Secrets 是加密存储的，只有 GitHub Actions 运行时才能访问，不会在日志中显示明文。

### Q: 上传失败怎么办？
**A:** 检查以下几点：
1. Token 是否正确复制（确保没有多余空格或换行）
2. Secret 名称是否为 `CODECOV_TOKEN`（大小写敏感）
3. CI 是否成功生成了覆盖率文件：
   - Python: `python/coverage.xml`
   - Rust: `rust/cobertura.xml`
4. 查看 GitHub Actions 日志中的 "Upload coverage to Codecov" 步骤

### Q: 如何查看具体的错误信息？
**A:** 在 GitHub Actions 运行页面：
1. 点击失败的工作流
2. 展开 "Upload coverage to Codecov" 步骤
3. 查看详细的错误日志

### Q: 可以使用其他覆盖率服务吗？
**A:** 可以。常见的替代方案：
- **Coveralls**: 类似 Codecov，也支持私有仓库
- **Codecov 自建版本**: 企业可以部署私有实例
- **GitHub Actions 的 artifacts**: 将覆盖率报告作为构建产物保存

## 覆盖率目标

根据项目规划（`openspec/changes/add-rust-implementation/proposal.md`）：

- **Python**: 当前 88.66%，目标保持 >85%
- **Rust**: 当前 Phase 1（基础架构），目标 >90%（Phase 2+ 实现时）

## 下一步

完成 Codecov 配置后，你可以：
1. 在 Pull Request 中看到覆盖率变化
2. 设置覆盖率阈值（不低于某个百分比时才能合并 PR）
3. 跟踪覆盖率历史趋势
4. 对比 Python 和 Rust 的覆盖率差异

## 参考资料

- Codecov 官方文档: https://docs.codecov.com/
- GitHub Actions Secrets: https://docs.github.com/en/actions/security-guides/encrypted-secrets
- Python Coverage.py: https://coverage.readthedocs.io/
- Rust Tarpaulin: https://github.com/xd009642/tarpaulin
