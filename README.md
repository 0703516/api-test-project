# 接口自动化测试项目

> 基于 Python + Pytest + Requests + Allure 的接口自动化测试框架  
> 被测系统：[JSONPlaceholder](https://jsonplaceholder.typicode.com/)（文章接口）+ [DummyJSON](https://dummyjson.com/)（鉴权/用户接口）

## 测试结果

**26 个用例全部通过 ✅**

| 被测系统 | 测试文件 | 用例数 | 覆盖场景 |
|---------|---------|-------|---------|
| JSONPlaceholder | test_posts.py | 12 | GET列表/单条、POST、PUT、PATCH、DELETE、评论、参数化 |
| DummyJSON | test_auth_users.py | 14 | 登录成功/失败、token鉴权、用户CRUD、404、搜索、参数化 |
| **合计** | | **26** | |

## 项目结构

```
api_test_project/
├── tests/
│   ├── test_posts.py         # JSONPlaceholder 文章接口（含参数化）
│   └── test_auth_users.py    # DummyJSON 鉴权 + 用户 CRUD 接口
├── utils/
│   ├── http_client.py        # 请求封装层（Session 复用）
│   └── assertions.py         # 断言辅助函数（语义化断言）
├── data/
│   └── test_data.json        # 测试数据（数据驱动）
├── reports/
│   ├── allure-results/       # Allure 原始数据
│   └── test_report.html      # pytest-html 自包含报告
├── conftest.py               # 全局 fixture（client、token 鉴权）
├── pytest.ini                # Pytest 配置
└── requirements.txt          # 依赖清单
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行全部测试

```bash
pytest
```

### 3. 只运行某个模块

```bash
pytest tests/test_posts.py -v
pytest tests/test_auth_users.py -v
```

### 4. 查看 HTML 报告（无需额外工具）

```bash
# 直接用浏览器打开
start reports/test_report.html   # Windows
open reports/test_report.html    # macOS
```

### 5. 生成并查看 Allure 可视化报告（需安装 allure 命令行）

```bash
allure serve reports/allure-results
```

## 技术亮点

- **Session 复用**：同一测试会话复用 TCP 连接，减少请求开销
- **fixture 分层**：`session` 级 fixture 保证 token 只请求一次，所有用例共享
- **数据驱动**：`@pytest.mark.parametrize` 让一个用例覆盖多组数据
- **Allure 三级标注**：`@allure.feature` / `@allure.story` / `allure.step` 三级组织，报告层次清晰
- **响应时间断言**：对关键接口增加 3s 性能基线校验
- **自定义断言函数**：错误信息友好，字段缺失时精准定位

## 依赖

```
pytest==8.2.0
requests==2.31.0
allure-pytest==2.13.5
pytest-html==4.1.1
```
