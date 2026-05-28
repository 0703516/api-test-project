"""断言辅助函数，让测试用例更语义化"""


def assert_status(response, expected_code: int):
    assert response.status_code == expected_code, (
        f"期望状态码 {expected_code}，实际为 {response.status_code}，"
        f"响应体：{response.text[:200]}"
    )


def assert_field(data: dict, field: str, expected_value=None):
    assert field in data, f"响应体中缺少字段：{field}"
    if expected_value is not None:
        assert data[field] == expected_value, (
            f"字段 '{field}' 期望值 {expected_value!r}，实际值 {data[field]!r}"
        )


def assert_response_time(response, max_seconds: float = 3.0):
    elapsed = response.elapsed.total_seconds()
    assert elapsed <= max_seconds, f"响应时间 {elapsed:.2f}s 超过阈值 {max_seconds}s"
