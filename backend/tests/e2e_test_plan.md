# End-to-End Test Plan

This document outlines the end-to-end test scenarios for the Product Evaluation Management System. These tests should be performed manually to verify that all components work together correctly and that the system meets the requirements specified in the requirements document.

## Prerequisites

- The application is running with both frontend and backend components
- The database is initialized with the required tables
- Test users with different roles are available:
  - Admin user: username `admin`, password `Password123`
  - Regular user: username `user`, password `Password123`

## Test Scenarios

### 1. User Authentication

#### 1.1 Login

1. Navigate to the login page
2. Enter valid credentials for the admin user
3. Click the login button
4. Verify that the user is redirected to the dashboard
5. Verify that the user's name is displayed in the header

#### 1.2 Logout

1. Click the logout button in the header
2. Verify that the user is redirected to the login page
3. Verify that the user cannot access protected routes without logging in again

### 2. User Profile Management

#### 2.1 View Profile

1. Log in as a regular user
2. Navigate to the profile page
3. Verify that the user's information is displayed correctly:
   - Full name
   - Email
   - Department
   - Position
   - Role

#### 2.2 Update Profile

1. Click the edit button on the personal information card
2. Update the following fields:
   - Full name: "Updated User"
   - Email: "updated.user@example.com"
   - Department: "Engineering"
   - Position: "Senior Developer"
3. Click the update profile button
4. Verify that a success message is displayed
5. Verify that the updated information is displayed in the profile

#### 2.3 Change Password

1. Enter the current password: "Password123"
2. Enter a new password: "NewPassword123"
3. Confirm the new password: "NewPassword123"
4. Click the change password button
5. Verify that a success message is displayed
6. Log out and log back in with the new password
7. Verify that the login is successful

### 3. Evaluation Management

#### 3.1 Create Evaluation

1. Log in as a regular user
2. Navigate to the evaluations page
3. Click the "New Evaluation" button
4. Fill in the evaluation form:
   - Evaluation number: "EV-20250101-TEST"
   - Evaluation type: "New Product"
   - Product name: "Test Product"
   - Part number: "TP-001"
   - Evaluation reason: "Testing"
   - Description: "Test evaluation description"
   - Start date: Current date
   - Expected end date: 30 days from now
   - Process step: "M001"
5. Click the submit button
6. Verify that a success message is displayed
7. Verify that the new evaluation appears in the evaluation list

#### 3.2 View Evaluation Details

1. Click on the evaluation created in the previous step
2. Verify that the evaluation details are displayed correctly:
   - Evaluation number
   - Evaluation type
   - Product name
   - Part number
   - Evaluation reason
   - Description
   - Start date
   - Expected end date
   - Process step
   - Status

#### 3.3 Update Evaluation

1. Click the edit button on the evaluation details page
2. Update the following fields:
   - Product name: "Updated Test Product"
   - Description: "Updated test evaluation description"
   - Process step: "M002"
3. Click the save button
4. Verify that a success message is displayed
5. Verify that the updated information is displayed in the evaluation details

#### 3.4 Evaluation Lifecycle Management

1. Start the evaluation by changing its status to "In Progress"
2. Verify that the status is updated in the evaluation details
3. Pause the evaluation by clicking the pause button
4. Verify that the status is changed to "Paused"
5. Resume the evaluation by clicking the resume button
6. Verify that the status is changed back to "In Progress"
7. Complete the evaluation by clicking the complete button
8. Verify that the status is changed to "Completed"
9. Verify that the actual end date is set to the current date

### 4. Admin User Management

#### 4.1 View User List

1. Log in as an admin user
2. Navigate to the users page
3. Verify that a list of users is displayed
4. Verify that the list includes the following information for each user:
   - Username
   - Full name
   - Email
   - Department
   - Position
   - Role
   - Status

#### 4.2 Create User

1. Click the "Add User" button
2. Fill in the user form:
   - Username: "testuser"
   - Full name: "Test User"
   - Email: "testuser@example.com"
   - Department: "Testing"
   - Position: "Tester"
   - Role: "User"
   - Password: "Password123"
   - Confirm password: "Password123"
3. Click the save button
4. Verify that a success message is displayed
5. Verify that the new user appears in the user list

#### 4.3 Edit User

1. Click the edit button for the user created in the previous step
2. Update the following fields:
   - Full name: "Updated Test User"
   - Email: "updated.testuser@example.com"
   - Department: "Quality Assurance"
   - Position: "Senior Tester"
   - Role: "Part Leader"
3. Click the save button
4. Verify that a success message is displayed
5. Verify that the updated information is displayed in the user list

#### 4.4 Deactivate and Activate User

1. Click the deactivate button for the user created in the previous step
2. Confirm the deactivation
3. Verify that a success message is displayed
4. Verify that the user's status is changed to "Inactive"
5. Click the activate button for the same user
6. Confirm the activation
7. Verify that a success message is displayed
8. Verify that the user's status is changed to "Active"

#### 4.5 Delete User

1. Click the delete button for the user created in the previous step
2. Confirm the deletion
3. Verify that a success message is displayed
4. Verify that the user is removed from the user list

### 5. Operation Logging

#### 5.1 View Operation Logs

1. Log in as an admin user
2. Create a new evaluation
3. Update the evaluation
4. Change the evaluation status
5. Navigate to the evaluation details page
6. Verify that operation logs are displayed for each action:
   - Creation
   - Update
   - Status change
7. Verify that each log includes:
   - User name
   - Operation type
   - Timestamp
   - Description

## Test Reporting

For each test scenario, record the following information:

- Test ID
- Test description
- Steps performed
- Expected result
- Actual result
- Pass/Fail status
- Comments or issues encountered

## Defect Reporting

If any defects are found during testing, report them with the following information:

- Defect ID
- Defect description
- Steps to reproduce
- Expected behavior
- Actual behavior
- Severity (Critical, Major, Minor, Cosmetic)
- Priority (High, Medium, Low)
- Screenshots or videos (if applicable)

## Test Environment

Document the test environment details:

- Frontend version
- Backend version
- Database version
- Browser and version
- Operating system
- Screen resolution
- Device type (desktop, tablet, mobile)