import pytest
from app.user_service import UserService

@pytest.fixture
def service():
    return UserService()

def test_add_user(service):
    user = service.add_user("Test@Email.com", "Alice") # returns a single user
    assert user["email"] == "test@email.com"
    assert service.users["test@email.com"]["name"] == "Alice"

def test_add_user_duplicate(service):
    service.add_user("x@y.com", "Bob")
    with pytest.raises(ValueError):
        service.add_user("x@y.com", "Bob Again")

def test_edit_user(service):
    service.add_user("Test@Email.com", "Alice")
    user = service.edit_user("test@Email.com", "Alice Updated")
    assert user["email"] == "test@email.com"
    assert user["name"] == "Alice Updated"

def test_get_user(service):
    service.add_user("A@B.com", "Charlie")
    user = service.get_user(" a@b.com ")
    assert user["name"] == "Charlie"

def test_delete_user(service):
    service.add_user("z@z.com", "Zelda")
    deleted = service.delete_user("z@z.com")
    assert deleted["name"] == "Zelda"
    assert service.delete_user("z@z.com") is None