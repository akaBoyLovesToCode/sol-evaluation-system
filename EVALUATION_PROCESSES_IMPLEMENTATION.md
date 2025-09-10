# Evaluation Processes Implementation Summary

## Overview
This document summarizes the changes made to support multiple evaluation processes per evaluation, addressing the requirements for:
1. New product development needing multiple evaluation types (PRQ, PPQ, etc.)
2. Support for re-evaluation when the first attempt fails

## Database Changes

### New Table: `evaluation_processes`
```sql
CREATE TABLE evaluation_processes (
    id INTEGER PRIMARY KEY,
    evaluation_id INTEGER NOT NULL REFERENCES evaluations(id),
    eval_code VARCHAR(50) NOT NULL,
    lot_number VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    process_description TEXT NOT NULL,
    manufacturing_test_results TEXT,
    defect_analysis_results TEXT,
    aql_result VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Added Relationship
- `Evaluation.processes`: One-to-many relationship from Evaluation to EvaluationProcess

## API Endpoints Added

### 1. Create Evaluation Process
- **POST** `/api/evaluations/{evaluation_id}/processes`
- Creates a new evaluation process for the specified evaluation
- Required fields: `eval_code`, `lot_number`, `quantity`, `process_description`
- Optional fields: `manufacturing_test_results`, `defect_analysis_results`, `aql_result`

### 2. Get All Evaluation Processes
- **GET** `/api/evaluations/{evaluation_id}/processes`
- Returns all processes for the specified evaluation

### 3. Get Specific Evaluation Process
- **GET** `/api/evaluations/{evaluation_id}/processes/{process_id}`
- Returns details of a specific evaluation process

### 4. Update Evaluation Process
- **PUT** `/api/evaluations/{evaluation_id}/processes/{process_id}`
- Updates an existing evaluation process
- Supports partial updates of all process fields

### 5. Delete Evaluation Process
- **DELETE** `/api/evaluations/{evaluation_id}/processes/{process_id}`
- Deletes an evaluation process

## Frontend Changes

### EvaluationDetail.vue
- Added new section to display evaluation processes
- Each process shows:
  - Evaluation code and lot number
  - Quantity and process flow description
  - Manufacturing test results
  - Defect analysis results
  - AQL result (optional)
  - Process status with color-coded tags
  - Creation timestamp

### NewEvaluation.vue
- Replaced old process selection with dynamic process forms
- Users can add multiple evaluation processes
- Each process includes:
  - Evaluation code input (required)
  - Lot number input (required)
  - Quantity input (required, numeric)
  - Process flow description textarea (required)
  - Manufacturing test results textarea (optional)
  - Defect analysis results textarea (optional)
  - AQL result input (optional)
- Processes can be added/removed dynamically
- Form validation for required fields

## Data Model

### EvaluationProcess Fields
- `eval_code`: Unique identifier for the evaluation process (e.g., "PRQ-001")
- `lot_number`: Manufacturing lot number
- `quantity`: Number of units evaluated
- `process_description`: Detailed process flow (e.g., "M031 -> RDT+TC600 -> LI")
- `manufacturing_test_results`: Results from manufacturing tests
- `defect_analysis_results`: Analysis of defects found
- `aql_result`: AQL test results (optional)
- `status`: Process status (pending, in_progress, completed, failed)

## Translation Updates

Added new translation keys for all languages (English, Chinese, Korean):

### Evaluation Terms
- `evaluationProcesses`: "Evaluation Processes"
- `evalCode`: "Eval Code"
- `lotNumber`: "Lot Number"
- `quantity`: "Quantity"
- `processFlow`: "Process Flow"
- `manufacturingTestResults`: "Manufacturing Test Results"
- `defectAnalysisResults`: "Defect Analysis Results"
- `aqlResult`: "AQL Result"
- `addProcess`: "Add Process"
- `remove`: "Remove"

### Process Status
- `processStatus.pending`: "Pending"
- `processStatus.in_progress`: "In Progress"
- `processStatus.completed`: "Completed"
- `processStatus.failed`: "Failed"

### Validation Messages
- Required field validation for all process fields

## Usage Examples

### 1. New Product Development
- Create evaluation with multiple processes: PRQ, PPQ, DOE
- Each process can have different lot numbers and quantities
- Track results and defects separately for each evaluation type

### 2. Re-evaluation Scenario
- First process fails: status marked as "failed"
- Add new process with corrected parameters
- Track both attempts with full history

### 3. Multiple Lot Evaluation
- Evaluate different manufacturing lots in separate processes
- Compare results across different lots
- Track AQL results for each lot separately

## Benefits

1. **Flexibility**: Support for any number of evaluation processes
2. **Traceability**: Complete history of all evaluation attempts
3. **Detailed Reporting**: Separate tracking of manufacturing tests, defect analysis, and AQL results
4. **Status Tracking**: Individual status for each evaluation process
5. **Re-evaluation Support**: Easy to add new processes when previous attempts fail

## Testing

A comprehensive test script (`test_evaluation_processes.py`) has been provided to verify:
- Process creation with all field types
- Multiple processes per evaluation
- Process updates and status changes
- Process deletion
- Error handling and validation

## Migration

The changes require database migration to add the `evaluation_processes` table and update the `evaluations` table with the new relationship.

## Backward Compatibility

Existing evaluations will continue to work without any processes. The system gracefully handles both old single-process and new multi-process evaluations.