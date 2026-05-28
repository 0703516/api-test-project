import json
import os
import pytest
from utils.http_client import HttpClient

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "test_data.json")


@pytest.fixture(scope="session")
def test_data():
    """加载测试数据"""
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def jsonplaceholder():
    """JSONPlaceholder 客户端，session 级别复用"""
    return HttpClient(base_url="https://jsonplaceholder.typicode.com")


@pytest.fixture(scope="session")
def dummyjson():
    """DummyJSON 客户端，session 级别复用（无需 API Key）"""
    return HttpClient(base_url="https://dummyjson.com")


@pytest.fixture(scope="session")
def dummyjson_with_token(dummyjson, test_data):
    """先登录获取 token，注入到 DummyJSON 客户端"""
    resp = dummyjson.post("/auth/login", json=test_data["login_valid"])
    assert resp.status_code == 200, f"登录失败：{resp.text}"
    token = resp.json().get("accessToken")
    assert token, "未获取到 token"
    client = HttpClient(base_url="https://dummyjson.com")
    client.set_token(token)
    return client
