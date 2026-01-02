import io
from backend.services.storage import get_storage_service, LocalStorage

def test_local_storage():
    service = get_storage_service()
    assert isinstance(service, LocalStorage)

    filename = "test_file.txt"
    content = b"Hello World"
    file_obj = io.BytesIO(content)

    saved_name = service.save_file(file_obj, filename)
    assert saved_name == filename

    url = service.get_url(filename)
    assert url == f"/uploads/{filename}"

    print("Storage Test Passed")

if __name__ == "__main__":
    test_local_storage()
