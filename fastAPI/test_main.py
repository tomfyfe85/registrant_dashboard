from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch
import main
import json

client = TestClient(app)

# @patch("cache.add_to_buffer")
# def test_patch(cache):
#     data = {"current_status": "CHK"}
#     response = client.patch(f"/registrant/registrant_id/{1}")
#     print("hello", response)
#     assert response == 200

@patch("main.add_to_buffer")        
def test_patch(mock_add_to_buffer):
    id = {'registrant_id': 1}
    response = client.patch(f"/registrant/registrant_id/{id['registrant_id']}", json={"current_status": "CHK"})
    
    assert mock_add_to_buffer.called 
    assert response.status_code == 200
    assert response.json() ==  {"status": "queued", "registrant_id": id['registrant_id']}

    