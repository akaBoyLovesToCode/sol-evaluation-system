"""Integration tests for the EvaluationProcess API endpoints.

This test script requires the Flask server to be running on localhost:5000.
Run it separately from the unit tests to test the actual API endpoints.
"""

import json
import sys
from datetime import datetime

import requests

# Test configuration
BASE_URL = "http://localhost:5000/api"
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"


def get_auth_token():
    """Get authentication token"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": TEST_USERNAME, "password": TEST_PASSWORD},
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None


def test_evaluation_processes_api():
    """Test evaluation processes API functionality"""
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token")
        return False

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Create a test evaluation first
    evaluation_data = {
        "evaluation_type": "new_product",
        "product_name": "Test Product for Processes",
        "part_number": "TEST-PROC-001",
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "process_step": "M031",
        "evaluation_reason": "new_product_development",
        "description": "Test evaluation for processes functionality",
    }

    try:
        # Create evaluation
        response = requests.post(
            f"{BASE_URL}/evaluations", headers=headers, json=evaluation_data
        )

        if response.status_code != 201:
            print(
                f"Failed to create evaluation: {response.status_code} - {response.text}"
            )
            return False

        evaluation = response.json()["data"]["evaluation"]
        evaluation_id = evaluation["id"]
        print(
            f"Created evaluation: {evaluation['evaluation_number']} (ID: {evaluation_id})"
        )

        # Test 1: Create evaluation process
        process_data = {
            "title": "PRQ Evaluation Process",
            "eval_code": "PRQ-001",
            "lot_number": "LOT202401001",
            "quantity": 1000,
            "process_description": "M031 -> RDT+TC600 -> LI",
            "manufacturing_test_results": "All tests passed, yield 98.5%",
            "defect_analysis_results": "Minor cosmetic defects, within acceptable limits",
            "aql_result": "AQL 1.0 Pass",
        }

        response = requests.post(
            f"{BASE_URL}/evaluations/{evaluation_id}/processes",
            headers=headers,
            json=process_data,
        )

        if response.status_code != 201:
            print(f"Failed to create process: {response.status_code} - {response.text}")
            return False

        process = response.json()["data"]["process"]
        process_id = process["id"]
        print(f"Created process: {process['eval_code']} (ID: {process_id})")

        # Test 2: Get all processes for evaluation
        response = requests.get(
            f"{BASE_URL}/evaluations/{evaluation_id}/processes", headers=headers
        )

        if response.status_code != 200:
            print(f"Failed to get processes: {response.status_code} - {response.text}")
            return False

        processes = response.json()["data"]["processes"]
        print(f"Found {len(processes)} processes for evaluation")

        # Test 3: Get specific process
        response = requests.get(
            f"{BASE_URL}/evaluations/{evaluation_id}/processes/{process_id}",
            headers=headers,
        )

        if response.status_code != 200:
            print(f"Failed to get process: {response.status_code} - {response.text}")
            return False

        process_details = response.json()["data"]["process"]
        print(
            f"Process details: {json.dumps(process_details, indent=2, ensure_ascii=False)}"
        )

        # Test 4: Update process
        update_data = {
            "quantity": 1500,
            "aql_result": "AQL 0.65 Pass",
            "status": "completed",
        }

        response = requests.put(
            f"{BASE_URL}/evaluations/{evaluation_id}/processes/{process_id}",
            headers=headers,
            json=update_data,
        )

        if response.status_code != 200:
            print(f"Failed to update process: {response.status_code} - {response.text}")
            return False

        updated_process = response.json()["data"]["process"]
        print(f"Updated process quantity: {updated_process['quantity']}")
        print(f"Updated process status: {updated_process['status']}")

        # Test 5: Create another process (for multiple processes test)
        process_data2 = {
            "title": "PPQ Evaluation Process",
            "eval_code": "PPQ-001",
            "lot_number": "LOT202401002",
            "quantity": 500,
            "process_description": "M031 -> TC600 -> Final Test",
            "manufacturing_test_results": "Process capability study completed",
            "defect_analysis_results": "No critical defects found",
            "aql_result": "AQL 2.5 Pass",
        }

        response = requests.post(
            f"{BASE_URL}/evaluations/{evaluation_id}/processes",
            headers=headers,
            json=process_data2,
        )

        if response.status_code != 201:
            print(
                f"Failed to create second process: {response.status_code} - {response.text}"
            )
            return False

        process2 = response.json()["data"]["process"]
        print(f"Created second process: {process2['eval_code']}")

        # Test 6: Verify multiple processes exist
        response = requests.get(
            f"{BASE_URL}/evaluations/{evaluation_id}/processes", headers=headers
        )

        if response.status_code != 200:
            print(
                f"Failed to get processes after second creation: {response.status_code} - {response.text}"
            )
            return False

        processes = response.json()["data"]["processes"]
        print(f"Total processes after second creation: {len(processes)}")

        # Test 7: Delete a process
        response = requests.delete(
            f"{BASE_URL}/evaluations/{evaluation_id}/processes/{process_id}",
            headers=headers,
        )

        if response.status_code != 200:
            print(f"Failed to delete process: {response.status_code} - {response.text}")
            return False

        print("Process deleted successfully")

        # Final verification
        response = requests.get(
            f"{BASE_URL}/evaluations/{evaluation_id}/processes", headers=headers
        )

        if response.status_code != 200:
            print(
                f"Failed to get processes after deletion: {response.status_code} - {response.text}"
            )
            return False

        processes = response.json()["data"]["processes"]
        print(f"Final process count: {len(processes)}")

        print("\n✅ All evaluation process API tests passed!")
        return True

    except Exception as e:
        print(f"Test error: {e}")
        return False


if __name__ == "__main__":
    print("Testing Evaluation Processes API...")
    success = test_evaluation_processes_api()
    sys.exit(0 if success else 1)
