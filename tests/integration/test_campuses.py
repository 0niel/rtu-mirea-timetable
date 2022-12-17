import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient


class TestCampuses:
    @pytest.mark.asyncio
    async def test_get_campuses(self, client: AsyncClient, mocker):
        response = await client.get("/api/campuses")
        assert response.status_code == 200
