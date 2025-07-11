**Error Report: Mission Module Integration Tests**

**Date:** Thursday, July 10, 2025
**Test File:** `tests/integration/test_mission_flow.py`

**Summary of Results:**
*   `test_list_missions`: PASSED
*   `test_accept_mission`: PASSED
*   `test_complete_mission`: PASSED
*   `test_duplicate_accept`: FAILED
*   `test_progress_persistence`: FAILED

**Detailed Analysis of Failures:**

---

**1. `test_duplicate_accept` Failure**

*   **Error Type:** `ValueError`
*   **Location:** `src/services/mission_service.py:76`
*   **Description:** This test aims to verify that a user cannot accept the same mission twice if it's already in progress. The `MissionService.start_mission` method, when called a second time for an already in-progress mission, explicitly raises a `ValueError` with the message "Mission m002 is already in progress for user 42."
*   **Expected Behavior (from test case):** The test expects `start_mission` to return the existing `UserMissionProgress` object for the in-progress mission, indicating that it doesn't create a new one or prevent the operation if it's merely a re-attempt to "accept" an already accepted mission.
*   **Actual Behavior:** The `MissionService` prevents re-acceptance of an in-progress mission by raising a `ValueError`.
*   **Recommendation:**
    *   **Option A (Modify Test):** If the intended behavior is indeed to prevent re-acceptance and raise an error, the test should be updated to assert that a `ValueError` is raised on the second call to `start_mission`.
    *   **Option B (Modify `MissionService`):** If the `MissionService` should allow re-calling `start_mission` for an already in-progress mission (e.g., to simply return the existing progress without error), then the logic in `src/services/mission_service.py` needs to be adjusted to handle this case gracefully instead of raising a `ValueError`. Given the test's description ("The user cannot accept a mission twice"), Option A seems more aligned with the current implementation's intent.

---

**2. `test_progress_persistence` Failure**

*   **Error Type:** `AssertionError`
*   **Location:** `tests/integration/test_mission_flow.py:114`
*   **Description:** This test simulates updating mission progress in steps (50%, then 75%) and then completing the mission. The failure occurs at the assertion `assert updated_mission_75.progress == 75.0`.
*   **Expected Value:** `75.0`
*   **Actual Value:** `100.0`
*   **Reason:** The log output shows:
    ```
    INFO     root:mission_service.py:100 Updating progress for user 42, mission m004 by 50.0
    INFO     root:mission_service.py:115 Mission m004 for user 42 automatically completed.
    INFO     root:mission_service.py:116 Progress for user 42, mission m004 updated to 100.0.
    ```
    This indicates that when `update_mission_progress` is called with `progress_delta=75.0` (which, when added to the previous 50.0, results in 125.0), the `MissionService` automatically completes the mission and sets its progress to 100.0 because `new_progress` (125.0) is greater than or equal to 100.0. The test then asserts that the progress is 75.0, which is incorrect given the service's auto-completion logic.
*   **Recommendation:**
    *   **Option A (Adjust Test Values):** Modify the `progress_delta` values in the test to ensure that intermediate updates do not trigger auto-completion if that's not the desired test scenario. For example, if the mission starts at 0, update to 50, then update by 25 (total 75), then update by 25 (total 100).
    *   **Option B (Adjust Assertion):** If the auto-completion is the desired behavior, then the assertion should be changed to `assert updated_mission_75.progress == 100.0` and potentially also assert that the status is "completed".

---

**Affected Files (Copies saved in `test misiones/`):**

*   `tests/integration/test_mission_flow.py`
*   `tests/conftest.py`
*   `src/services/mission_service.py`
