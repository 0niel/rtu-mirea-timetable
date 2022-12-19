from fastapi.testclient import TestClient

from tests.mock.db import MockDBFacade


class TestCampuses:
    def test_get_campuses(self, client: TestClient, db_facade: MockDBFacade):
        response = client.get("/api/campuses")
        assert response.status_code == 200

        response_data = response.json()
        assert isinstance(response_data, list)
        assert len(response_data) == 2

    def test_get_campus_rooms(self, client: TestClient, db_facade: MockDBFacade):
        response = client.get("/api/campuses/1/rooms")
        assert response.status_code == 200

        response_data = response.json()
        assert isinstance(response_data, list)
        assert len(response_data) == 3
