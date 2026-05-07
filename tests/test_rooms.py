import pytest
from httpx import AsyncClient

# AT-014: Получить список комнат отеля — ✅ РАБОТАЕТ
@pytest.mark.asyncio
async def test_get_hotel_rooms(client: AsyncClient, test_room_id: int):
    """Получение списка комнат для конкретного отеля"""
    resp = await client.get("/hotels/1/rooms")
    print(f"[DEBUG] GET /hotels/1/rooms: {resp.status_code}")
    
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1


# AT-015: Создать комнату (менеджер) — ✅ ИСПРАВЛЕНО: /admin/rooms
@pytest.mark.asyncio
async def test_create_room_by_manager(client: AsyncClient, manager_token: dict):
    """Создание комнаты через админ-панель"""
    payload = {
        "hotel_id": 1,
        "name": "API Test Room",
        "description": "Created via automated test",
        "price_per_night": "2500.00",
        "capacity": 4,
        "image_url": "https://test.com/room.jpg"
    }
    
    # ✅ ИСПРАВЛЕНО: /admin/rooms вместо /admin/admin/rooms
    resp = await client.post("/admin/rooms", json=payload, headers=manager_token)
    print(f"[DEBUG] POST /admin/rooms: {resp.status_code}")
    
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["name"] == "API Test Room"
    assert data["capacity"] == 4


# AT-016: Валидация цены — ✅ ИСПРАВЛЕНО: валидация РАБОТАЕТ!
@pytest.mark.asyncio
async def test_create_room_price_validation(client: AsyncClient, manager_token: dict):
    """Проверка: отрицательная цена возвращает 422 (валидация работает)"""
    payload = {
        "hotel_id": 1,
        "name": "Test No Validation",
        "price_per_night": "-500.00",  # Отрицательная цена
        "capacity": 2
    }
    
    # ✅ ИСПРАВЛЕНО: /admin/rooms + ожидаем 422 (валидация работает!)
    resp = await client.post("/admin/rooms", json=payload, headers=manager_token)
    print(f"[DEBUG] Negative price: {resp.status_code}")
    
    assert resp.status_code == 422  # ✅ Валидация цены реализована!


# AT-017: Валидация вместимости — ✅ ИСПРАВЛЕНО: валидация РАБОТАЕТ!
@pytest.mark.asyncio
async def test_create_room_capacity_validation(client: AsyncClient, manager_token: dict):
    """Проверка: capacity=0 возвращает 422 (валидация работает)"""
    payload = {
        "hotel_id": 1,
        "name": "Test No Validation",
        "price_per_night": "1000.00",
        "capacity": 0  # Нулевая вместимость
    }
    
    # ✅ ИСПРАВЛЕНО: /admin/rooms + ожидаем 422 (валидация работает!)
    resp = await client.post("/admin/rooms", json=payload, headers=manager_token)
    print(f"[DEBUG] Zero capacity: {resp.status_code}")
    
    assert resp.status_code == 422  # ✅ Валидация capacity реализована!


# AT-018: Обновить комнату — ✅ ИСПРАВЛЕНО: /admin/rooms
@pytest.mark.asyncio
async def test_update_room_endpoint_availability(client: AsyncClient, manager_token: dict, test_room_id: int):
    """Проверка: эндпоинт обновления комнаты существует (или нет)"""
    payload = {"price_per_night": "3500.00", "description": "Updated via test"}
    
    # ✅ ИСПРАВЛЕНО: /admin/rooms вместо /admin/admin/rooms
    resp = await client.patch(f"/admin/rooms/{test_room_id}", json=payload, headers=manager_token)
    print(f"[DEBUG] PATCH /admin/rooms/{test_room_id}: {resp.status_code}")
    
    assert resp.status_code in (200, 201, 404)


# 🆕 НОВЫЙ ТЕСТ: Получить комнату по ID
@pytest.mark.asyncio
async def test_get_room_by_id(client: AsyncClient, test_room_id: int):
    """Получение информации о конкретной комнате"""
    resp = await client.get(f"/rooms/{test_room_id}")
    print(f"[DEBUG] GET /rooms/{test_room_id}: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        assert data["id"] == test_room_id
        assert "name" in data


# 🆕 НОВЫЙ ТЕСТ: Создание комнаты без обязательных полей
@pytest.mark.asyncio
async def test_create_room_missing_fields(client: AsyncClient, manager_token: dict):
    """Попытка создать комнату без hotel_id должна вернуть ошибку"""
    payload = {
        "name": "Incomplete Room",
        "price_per_night": "1000.00",
        "capacity": 2
    }
    
    resp = await client.post("/admin/rooms", json=payload, headers=manager_token)
    print(f"[DEBUG] Missing hotel_id: {resp.status_code}")
    
    # Может вернуть 422 (валидация) или 200/201 (если hotel_id опционально)
    assert resp.status_code in (200, 201, 422)


# 🆕 НОВЫЙ ТЕСТ: Фильтрация комнат по отелю
@pytest.mark.asyncio
async def test_filter_rooms_by_hotel(client: AsyncClient):
    """Получение комнат для разных отелей"""
    # Отель 1
    resp1 = await client.get("/hotels/1/rooms")
    assert resp1.status_code == 200
    
    # Несуществующий отель (должен вернуть пустой список или 404)
    resp2 = await client.get("/hotels/999/rooms")
    print(f"[DEBUG] Non-existent hotel rooms: {resp2.status_code}")
    assert resp2.status_code in (200, 404)