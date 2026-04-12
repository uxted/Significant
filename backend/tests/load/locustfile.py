"""Load tests for API using Locust."""

from locust import HttpUser, task, between


class NewsUser(HttpUser):
    """Simulated user browsing the news feed."""

    wait_time = between(1, 3)

    @task(3)
    def get_news_list(self):
        """Fetch news list with pagination."""
        self.client.get("/api/news/?page=1&page_size=20")

    @task(1)
    def get_news_detail(self):
        """Fetch a single news article."""
        self.client.get("/api/news/1/")

    @task(1)
    def get_sources(self):
        """Fetch sources list."""
        self.client.get("/api/sources/")

    @task(1)
    def get_categories(self):
        """Fetch categories list."""
        self.client.get("/api/categories/")

    @task(1)
    def search_news(self):
        """Search news."""
        self.client.get("/api/news/?search=ставка")

    @task(1)
    def login(self):
        """Login to get JWT tokens."""
        self.client.post(
            "/api/auth/login/",
            {"email": "test@test.com", "password": "testpassword123"},
        )
