import allure
import pytest
from utils.assertions import assert_status, assert_field, assert_response_time


@allure.feature("DummyJSON - 用户鉴权接口")
class TestAuth:

    @allure.story("用户登录")
    @allure.title("POST /auth/login 有效凭据返回 token")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_login_success(self, dummyjson, test_data):
        with allure.step("发送有效登录请求"):
            resp = dummyjson.post("/auth/login", json=test_data["login_valid"])
        with allure.step("断言状态码 200 并包含 accessToken 和 refreshToken"):
            assert_status(resp, 200)
            data = resp.json()
            assert_field(data, "accessToken")
            assert_field(data, "refreshToken")
            assert len(data["accessToken"]) > 0, "accessToken 不应为空"

    @allure.story("用户登录")
    @allure.title("POST /auth/login 无效凭据返回 400")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_fail(self, dummyjson, test_data):
        with allure.step("发送无效登录请求"):
            resp = dummyjson.post("/auth/login", json=test_data["login_invalid"])
        with allure.step("断言状态码 400 并包含 message 字段"):
            assert_status(resp, 400)
            assert_field(resp.json(), "message")

    @allure.story("用户信息")
    @allure.title("GET /auth/me 使用 token 获取当前用户信息")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_current_user(self, dummyjson_with_token):
        with allure.step("发送带 token 的 GET /auth/me"):
            resp = dummyjson_with_token.get("/auth/me")
        with allure.step("断言状态码 200 并包含 username 和 email"):
            assert_status(resp, 200)
            data = resp.json()
            assert_field(data, "username")
            assert_field(data, "email")


@allure.feature("DummyJSON - 用户 CRUD 接口")
class TestUsers:

    @allure.story("获取用户列表")
    @allure.title("GET /users 返回用户列表，total>0")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_users(self, dummyjson):
        with allure.step("发送 GET /users"):
            resp = dummyjson.get("/users")
        with allure.step("断言状态码 200，含 users 数组和 total"):
            assert_status(resp, 200)
            assert_response_time(resp)
            data = resp.json()
            assert_field(data, "users")
            assert_field(data, "total")
            assert data["total"] > 0

    @allure.story("获取单个用户")
    @allure.title("GET /users/1 返回 id=1 的用户信息")
    def test_get_user_by_id(self, dummyjson):
        with allure.step("发送 GET /users/1"):
            resp = dummyjson.get("/users/1")
        with allure.step("断言状态码 200 并校验 id、email、firstName"):
            assert_status(resp, 200)
            user = resp.json()
            assert_field(user, "id", 1)
            assert_field(user, "email")
            assert_field(user, "firstName")

    @allure.story("获取不存在的用户")
    @allure.title("GET /users/9999 应返回 404")
    def test_get_user_not_found(self, dummyjson):
        with allure.step("发送 GET /users/9999"):
            resp = dummyjson.get("/users/9999")
        with allure.step("断言状态码 404"):
            assert_status(resp, 404)

    @allure.story("创建用户")
    @allure.title("POST /users/add 创建新用户并返回 id")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_user(self, dummyjson):
        payload = {"firstName": "张三", "lastName": "测试", "age": 28}
        with allure.step(f"发送 POST /users/add，数据：{payload}"):
            resp = dummyjson.post("/users/add", json=payload)
        with allure.step("断言状态码 201 并含 id、firstName"):
            assert_status(resp, 201)
            data = resp.json()
            assert_field(data, "id")
            assert_field(data, "firstName", "张三")

    @allure.story("更新用户")
    @allure.title("PUT /users/1 全量更新用户信息")
    def test_update_user_put(self, dummyjson):
        payload = {"firstName": "李四", "age": 30}
        with allure.step("发送 PUT /users/1"):
            resp = dummyjson.put("/users/1", json=payload)
        with allure.step("断言状态码 200 并校验 firstName"):
            assert_status(resp, 200)
            data = resp.json()
            assert_field(data, "firstName", "李四")

    @allure.story("删除用户")
    @allure.title("DELETE /users/1 删除用户返回 200 且含 isDeleted 字段")
    def test_delete_user(self, dummyjson):
        with allure.step("发送 DELETE /users/1"):
            resp = dummyjson.delete("/users/1")
        with allure.step("断言状态码 200 并含 isDeleted=True"):
            assert_status(resp, 200)
            data = resp.json()
            assert_field(data, "isDeleted", True)

    @allure.story("搜索用户")
    @allure.title("GET /users/search?q=Emily 搜索用户返回结果")
    def test_search_users(self, dummyjson):
        with allure.step("发送 GET /users/search?q=Emily"):
            resp = dummyjson.get("/users/search", params={"q": "Emily"})
        with allure.step("断言状态码 200 并含 users 数组"):
            assert_status(resp, 200)
            data = resp.json()
            assert_field(data, "users")

    @allure.story("数据驱动 - 查询多个用户")
    @allure.title("参数化：查询用户 id={user_id}")
    @pytest.mark.parametrize("user_id", [1, 2, 5, 10])
    def test_get_users_parametrize(self, dummyjson, user_id):
        with allure.step(f"发送 GET /users/{user_id}"):
            resp = dummyjson.get(f"/users/{user_id}")
        with allure.step("断言状态码 200 并包含 id 字段"):
            assert_status(resp, 200)
            assert_field(resp.json(), "id", user_id)
