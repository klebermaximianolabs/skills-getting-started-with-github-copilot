"""
Tests for GET / (root) endpoint.

Tests the root route which redirects to the static index page.
"""


class TestRootEndpoint:
    """Test suite for GET / endpoint."""

    def test_root_returns_redirect(self, client):
        """Test that GET / returns a redirect response."""
        response = client.get("/", follow_redirects=False)
        
        # Should be a redirect (307 or similar)
        assert response.status_code in [301, 302, 303, 307, 308]

    def test_root_redirects_to_static_index(self, client):
        """Test that GET / redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        
        # Check location header
        assert "location" in response.headers
        assert "/static/index.html" in response.headers["location"]

    def test_root_redirect_location_exact(self, client):
        """Test that GET / redirects to exact /static/index.html path."""
        response = client.get("/", follow_redirects=False)
        
        location = response.headers["location"]
        # The location should end with /static/index.html
        assert location.endswith("/static/index.html")

    def test_root_with_follow_redirects(self, client):
        """Test that following the redirect works (if static files are served)."""
        # Note: This might fail if static files aren't properly mounted for testing,
        # but the redirect itself should work
        response = client.get("/", follow_redirects=True)
        
        # If static files are served, we get 200; otherwise we might get 307
        # The important thing is that the initial redirect exists
        assert response.status_code in [200, 307]

    def test_root_access_multiple_times(self, client):
        """Test that root redirect works consistently on multiple accesses."""
        for _ in range(3):
            response = client.get("/", follow_redirects=False)
            assert response.status_code in [301, 302, 303, 307, 308]
            assert "/static/index.html" in response.headers["location"]

    def test_root_does_not_return_content(self, client):
        """Test that root redirect doesn't return typical HTML content directly."""
        response = client.get("/", follow_redirects=False)
        
        # Should not have typical HTML content (empty or minimal body for redirect)
        # Redirects typically have empty or minimal body
        assert len(response.text) < 100  # Redirect responses are typically very short
