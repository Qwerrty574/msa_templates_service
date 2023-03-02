import requests

BASE_URL = "http://localhost:8080"


def test_create_template():
    payload = {"title": "Test template", "content": "This is a test template."}
    response = requests.post(f"{BASE_URL}/templates/", json=payload)
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "Test template", "content": "This is a test template."}


def test_get_template():
    response = requests.get(f"{BASE_URL}/templates/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "Test template", "content": "This is a test template."}


def test_list_templates():
    response = requests.get(f"{BASE_URL}/templates/")
    assert response.status_code == 200
    assert response.json() == [{"id": 1, "title": "Test template", "content": "This is a test template."}]


def test_healthcheck():
    response = requests.get(f"{BASE_URL}/__health")
    assert response.status_code == 200
