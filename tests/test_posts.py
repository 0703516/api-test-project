import allure
import pytest
from utils.assertions import assert_status, assert_field, assert_response_time


@allure.feature("JSONPlaceholder - 文章接口")
class TestPosts:

    @allure.story("获取文章列表")
    @allure.title("GET /posts 应返回 100 条数据且包含必要字段")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_all_posts(self, jsonplaceholder):
        with allure.step("发送 GET /posts 请求"):
            resp = jsonplaceholder.get("/posts")
        with allure.step("断言状态码为 200"):
            assert_status(resp, 200)
        with allure.step("断言响应时间 < 3s"):
            assert_response_time(resp)
        with allure.step("断言返回 100 条数据且含必要字段"):
            data = resp.json()
            assert len(data) == 100, f"期望 100 条，实际 {len(data)} 条"
            assert_field(data[0], "id")
            assert_field(data[0], "title")
            assert_field(data[0], "userId")

    @allure.story("获取单篇文章")
    @allure.title("GET /posts/1 返回 id=1 的正确数据")
    def test_get_post_by_id(self, jsonplaceholder):
        with allure.step("发送 GET /posts/1"):
            resp = jsonplaceholder.get("/posts/1")
        with allure.step("断言状态码 200 并校验 id 字段"):
            assert_status(resp, 200)
            data = resp.json()
            assert_field(data, "id", 1)
            assert_field(data, "userId", 1)

    @allure.story("创建文章")
    @allure.title("POST /posts 创建新文章返回 201")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_post(self, jsonplaceholder, test_data):
        payload = test_data["create_post"]
        with allure.step(f"发送 POST /posts，数据：{payload}"):
            resp = jsonplaceholder.post("/posts", json=payload)
        with allure.step("断言状态码 201，响应含 id 和 title"):
            assert_status(resp, 201)
            data = resp.json()
            assert_field(data, "id")
            assert_field(data, "title", payload["title"])

    @allure.story("更新文章")
    @allure.title("PUT /posts/1 全量更新文章")
    def test_update_post_put(self, jsonplaceholder, test_data):
        payload = {**test_data["create_post"], "id": 1}
        with allure.step("发送 PUT /posts/1"):
            resp = jsonplaceholder.put("/posts/1", json=payload)
        with allure.step("断言状态码 200 并校验 title"):
            assert_status(resp, 200)
            assert_field(resp.json(), "title", payload["title"])

    @allure.story("更新文章")
    @allure.title("PATCH /posts/1 局部更新文章标题")
    def test_update_post_patch(self, jsonplaceholder):
        with allure.step("发送 PATCH /posts/1，只更新 title"):
            resp = jsonplaceholder.patch("/posts/1", json={"title": "局部更新标题"})
        with allure.step("断言状态码 200 并校验 title"):
            assert_status(resp, 200)
            assert_field(resp.json(), "title", "局部更新标题")

    @allure.story("删除文章")
    @allure.title("DELETE /posts/1 删除文章返回 200")
    def test_delete_post(self, jsonplaceholder):
        with allure.step("发送 DELETE /posts/1"):
            resp = jsonplaceholder.delete("/posts/1")
        with allure.step("断言状态码 200"):
            assert_status(resp, 200)

    @allure.story("获取文章下的评论")
    @allure.title("GET /posts/1/comments 返回属于 postId=1 的评论")
    def test_get_post_comments(self, jsonplaceholder):
        with allure.step("发送 GET /posts/1/comments"):
            resp = jsonplaceholder.get("/posts/1/comments")
        with allure.step("断言状态码 200，评论 postId 均为 1"):
            assert_status(resp, 200)
            data = resp.json()
            assert len(data) > 0
            for comment in data:
                assert comment["postId"] == 1

    @allure.story("数据驱动 - 查询多个文章")
    @allure.title("参数化：批量查询文章 id={post_id}")
    @pytest.mark.parametrize("post_id", [1, 5, 10, 50, 100])
    def test_get_post_parametrize(self, jsonplaceholder, post_id):
        with allure.step(f"发送 GET /posts/{post_id}"):
            resp = jsonplaceholder.get(f"/posts/{post_id}")
        with allure.step("断言状态码 200 并包含 id 字段"):
            assert_status(resp, 200)
            assert_field(resp.json(), "id", post_id)
