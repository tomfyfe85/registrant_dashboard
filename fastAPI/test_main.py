from fastapi.testclient import TestClient
from main import app, add_to_buffer, get_db, write_to_postgres
from unittest.mock import patch, MagicMock
client = TestClient(app)

@patch("main.add_to_buffer")        
def test_patch(mock_add_to_buffer):
    id = {'registrant_id': 1}
    response = client.patch(f"/registrant/registrant_id/{id['registrant_id']}", json={"current_status": "CHK"})
    
    assert mock_add_to_buffer.called 
    assert response.status_code == 200
    assert response.json() ==  {"status": "queued", "registrant_id": id['registrant_id']}

@patch("main.get_db")
def test_write_to_postgres(mock_get_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {
        "id": 1, "name": "Tom", "email": "tom@test.com",
        "company_fk_id": 1, "event_id": 1,
        "guest_type": "guest", "current_status": "REG"
    }
    
    write_to_postgres(1, "CHK")
    
    mock_cursor.execute.assert_called_once_with('UPDATE registrants_registrant SET current_status = %s WHERE id = %s RETURNING *', ('CHK', 1))