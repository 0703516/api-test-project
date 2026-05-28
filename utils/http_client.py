import requests


class HttpClient:
    """统一封装 HTTP 请求，支持 session 复用和 header 注入"""

    def __init__(self, base_url: str, headers: dict = None):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        if headers:
            self.session.headers.update(headers)

    def set_token(self, token: str):
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def get(self, path: str, params: dict = None, **kwargs):
        url = f"{self.base_url}{path}"
        return self.session.get(url, params=params, **kwargs)

    def post(self, path: str, json: dict = None, **kwargs):
        url = f"{self.base_url}{path}"
        return self.session.post(url, json=json, **kwargs)

    def put(self, path: str, json: dict = None, **kwargs):
        url = f"{self.base_url}{path}"
        return self.session.put(url, json=json, **kwargs)

    def patch(self, path: str, json: dict = None, **kwargs):
        url = f"{self.base_url}{path}"
        return self.session.patch(url, json=json, **kwargs)

    def delete(self, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        return self.session.delete(url, **kwargs)
