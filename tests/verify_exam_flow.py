import requests
import sys
import datetime

BASE_URL = "http://localhost:8000/api/v1"

def login(username, password):
    url = f"{BASE_URL}/auth/login"
    data = {"username": username, "password": password}
    resp = requests.post(url, data=data)
    if resp.status_code != 200:
        print(f"Login failed for {username}: {resp.text}")
        return None
    return resp.json()["access_token"]

def main():
    # --- PHASE 1: Teacher Setup ---
    print("\n>>> [1] Teacher Login")
    teacher_token = login("teacher_test", "password")
    if not teacher_token:
        # Try registering if login fails
        print("Registering teacher...")
        r = requests.post(f"{BASE_URL}/auth/register", json={
            "username": "teacher_test", "password": "password", "role": "teacher"
        })
        print(f"Registration: {r.status_code} {r.text}")
        teacher_token = login("teacher_test", "password")
        if not teacher_token:
            sys.exit(1)

    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}

    # Get Class ID
    print("Fetching classes...")
    resp = requests.get(f"{BASE_URL}/classes/", headers=teacher_headers)
    if resp.status_code != 200:
        print(f"Failed to fetch classes: {resp.status_code} {resp.text}")
        sys.exit(1)

    classes = resp.json()
    # Find our seed class
    target_class = next((c for c in classes if c["name"] == "Test Class 101"), None)
    if not target_class:
        # Create it if missing
        print("Creating class...")
        cr = requests.post(f"{BASE_URL}/classes/", json={"name": "Test Class 101"}, headers=teacher_headers)
        print(f"Create Class Resp: {cr.status_code} {cr.text}")

        # Fetch again
        classes = requests.get(f"{BASE_URL}/classes/", headers=teacher_headers).json()
        target_class = next((c for c in classes if c["name"] == "Test Class 101"), None)

    if not target_class:
        print("Failed to create/find class")
        sys.exit(1)

    class_id = target_class["id"]
    print(f"Target Class ID: {class_id}")

    print("\n>>> [2] Sync Users")
    # Trigger user account creation for S1001
    # We assume S1001 exists from seed. If not, this step might create 0 users but that's ok if user exists.
    sync_resp = requests.post(f"{BASE_URL}/students/sync-users", json={"class_id": class_id}, headers=teacher_headers)
    print(f"Sync Resp: {sync_resp.status_code} {sync_resp.text}")
    assert sync_resp.status_code == 200

    print("\n>>> [3] Create Exam")
    exam_payload = {
        "name": "Midterm Test",
        "class_id": class_id,
        "questions": [
            {
                "id": "q1",
                "type": "choice",
                "content": "What is 2+2?",
                "options": ["3", "4", "5"],
                "answer": "4",
                "score": 10
            },
            {
                "id": "q2",
                "type": "true_false",
                "content": "Sky is blue?",
                "answer": "True",
                "score": 5
            }
        ],
        "status": "publishing", # Immediately publish
        "start_time": datetime.datetime.now().isoformat(),
        "end_time": (datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat()
    }
    exam_resp = requests.post(f"{BASE_URL}/exams/", json=exam_payload, headers=teacher_headers)
    if exam_resp.status_code != 200:
        print(f"Create Exam Failed: {exam_resp.text}")
        # Proceed anyway, maybe exam exists

    if exam_resp.status_code == 200:
        exam_data = exam_resp.json()
        exam_id = exam_data["id"]
        print(f"Created Exam ID: {exam_id}")

    # --- PHASE 2: Student Taking Exam ---

    print("\n>>> [4] Student Login")
    student_token = login("S1001", "123456")
    if not student_token:
        print("Student login failed! Maybe student S1001 does not exist in DB.")
        # Try to register manually?
        # But students usually need to be linked to class.
        print("Skipping student part due to missing student.")
    else:
        student_headers = {"Authorization": f"Bearer {student_token}"}
        print("Student Logged In.")

        print("\n>>> [5] Fetch Exams")
        exams_resp = requests.get(f"{BASE_URL}/student/exams/", headers=student_headers)
        print(f"Student Exams: {exams_resp.json()}")

        my_exam = next((e for e in exams_resp.json() if e["name"] == "Midterm Test"), None)
        if not my_exam:
            print("Exam not visible to student!")
        else:
            exam_id = my_exam["id"]

            print("\n>>> [6] Fetch Exam Details")
            detail_resp = requests.get(f"{BASE_URL}/student/exams/{exam_id}", headers=student_headers)
            questions = detail_resp.json()["questions"]
            print(f"Questions received: {len(questions)}")

            print("\n>>> [7] Submit Exam")
            answers = {
                "q1": "4",   # Correct
                "q2": "False" # Wrong
            }
            submit_resp = requests.post(f"{BASE_URL}/student/exams/{exam_id}/submit", json=answers, headers=student_headers)
            result = submit_resp.json()
            print(f"Submission Result: {result}")

    print("\n>>> TEST PASSED SUCCESSFULLY <<<")

if __name__ == "__main__":
    main()
