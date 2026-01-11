# Database Architecture Refactoring Plan

## Executive Summary
This plan addresses critical architectural, security, and performance issues identified in the current codebase. The refactoring will consolidate the dual-backend system, implement proper authorization, add database indexes, and establish Pydantic schemas for type safety.

## Critical Issues Identified

### 1. **Architectural Inconsistency (CRITICAL)**
- **Problem**: Dual backend system with `main.py` (psycopg2) and `api_dashboard.py` (SQLAlchemy)
- **Impact**: Code duplication, maintenance nightmare, inconsistent data handling
- **Solution**: Consolidate all APIs into SQLAlchemy-based system

### 2. **Broken Object Level Authorization (CRITICAL SECURITY)**
- **Problem**: No permission checks on resource access (e.g., `/api/medical-records/{patient_id}`)
- **Impact**: Any user can access any patient's data by guessing IDs
- **Solution**: Implement FastAPI dependencies for authorization

### 3. **Redundant Data Storage**
- **Problem**: Both `ExerciseLogSimple` and `WorkoutSession`/`SessionDetail` store workout data
- **Impact**: Data divergence, wasted storage, confusion
- **Solution**: Consolidate into single source of truth

### 4. **Performance Issues**
- **N+1 Query Problem**: Multiple endpoints fetch related data in loops
- **Missing Indexes**: Foreign keys lack indexes
- **No Pagination**: Endpoints return entire tables
- **Solution**: Add eager loading, indexes, and pagination

### 5. **Security Vulnerabilities**
- **Legacy Password Support**: Plain-text password comparison still exists
- **Hardcoded JWT Secret**: Default secret key in production
- **Input Validation**: Using `Dict[str, Any]` instead of Pydantic models
- **Solution**: Remove legacy auth, enforce environment variables, add Pydantic schemas

## Implementation Phases

### Phase 1: Foundation (Security & Infrastructure)
**Priority**: CRITICAL
**Estimated Time**: 2-3 hours

#### 1.1 Create Pydantic Schemas
- [ ] Create `schemas.py` with all request/response models
- [ ] Add validation for all user inputs
- [ ] Define proper response models for API documentation

#### 1.2 Implement Authorization System
- [ ] Create `dependencies.py` with auth dependencies
- [ ] Implement `get_current_user()` dependency
- [ ] Implement `verify_patient_access()` dependency
- [ ] Implement `verify_doctor_access()` dependency
- [ ] Add role-based access control (RBAC)

#### 1.3 Security Hardening
- [ ] Remove legacy password support
- [ ] Enforce environment variable for SECRET_KEY
- [ ] Add startup validation for required env vars
- [ ] Implement rate limiting on auth endpoints

### Phase 2: Database Optimization
**Priority**: HIGH
**Estimated Time**: 2-3 hours

#### 2.1 Add Database Indexes
```sql
-- Add these indexes via Alembic migration
CREATE INDEX idx_assignment_doctor_id ON assignments(doctor_id);
CREATE INDEX idx_schedule_doctor_id ON schedules(doctor_id);
CREATE INDEX idx_schedule_patient_id ON schedules(patient_id);
CREATE INDEX idx_message_sender_id ON messages(sender_id);
CREATE INDEX idx_message_receiver_id ON messages(receiver_id);
CREATE INDEX idx_combo_doctor_id ON combos(doctor_id);
CREATE INDEX idx_workout_session_user_id ON workout_sessions(user_id);
CREATE INDEX idx_brain_exercise_log_user_id ON brain_exercise_logs(user_id);
CREATE INDEX idx_brain_exercise_session_user_id ON brain_exercise_sessions(user_id);
CREATE INDEX idx_patient_note_patient_id ON patient_notes(patient_id);
CREATE INDEX idx_patient_note_doctor_id ON patient_notes(doctor_id);
CREATE INDEX idx_week_plan_patient_id ON week_plans(patient_id);
CREATE INDEX idx_week_plan_doctor_id ON week_plans(doctor_id);
CREATE INDEX idx_notification_user_id ON notifications(user_id);
```

#### 2.2 Consolidate Exercise Logging
- [ ] Create migration to migrate `ExerciseLogSimple` data to `WorkoutSession`/`SessionDetail`
- [ ] Update all endpoints to use unified system
- [ ] Add deprecation warning to old endpoints
- [ ] Remove `ExerciseLogSimple` table after migration

#### 2.3 Fix N+1 Query Problems
- [ ] Update `get_combos` to use `joinedload`
- [ ] Update `get_week_plans` to use `selectinload`
- [ ] Add eager loading to all relationship queries

### Phase 3: API Consolidation
**Priority**: HIGH
**Estimated Time**: 3-4 hours

#### 3.1 Migrate main.py Endpoints to api_dashboard.py
- [ ] Move camera/exercise processing endpoints
- [ ] Migrate authentication endpoints
- [ ] Migrate dashboard endpoints
- [ ] Update all endpoints to use Pydantic schemas
- [ ] Add authorization dependencies to all endpoints

#### 3.2 Implement Pagination
- [ ] Create pagination utility functions
- [ ] Add pagination to `get_patients`
- [ ] Add pagination to `get_recent_activity`
- [ ] Add pagination to `get_messages`
- [ ] Add pagination to all list endpoints

#### 3.3 Restructure API with APIRouter
```python
# Structure:
# api_dashboard.py (main app)
# routers/
#   - auth.py
#   - patients.py
#   - doctors.py
#   - assignments.py
#   - schedules.py
#   - messages.py
#   - exercises.py
#   - medical_records.py
```

### Phase 4: Code Quality & Maintainability
**Priority**: MEDIUM
**Estimated Time**: 2-3 hours

#### 4.1 Create Enums for Constants
```python
# enums.py
class UserRole(str, Enum):
    DOCTOR = "doctor"
    PATIENT = "patient"

class ExerciseType(str, Enum):
    BICEP_CURL = "bicep-curl"
    SHOULDER_FLEXION = "shoulder-flexion"
    SQUAT = "squat"
    KNEE_RAISE = "knee-raise"

class ScheduleStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
```

#### 4.2 Improve Error Handling
- [ ] Create custom exception classes
- [ ] Add proper error messages (no database leaks)
- [ ] Implement global exception handler
- [ ] Add logging for errors

#### 4.3 Add Database Constraints
- [ ] Add CHECK constraints for valid enum values
- [ ] Add NOT NULL constraints where appropriate
- [ ] Add UNIQUE constraints for business rules

### Phase 5: Testing & Migration
**Priority**: HIGH
**Estimated Time**: 2-3 hours

#### 5.1 Create Migration Scripts
- [ ] Alembic migration for indexes
- [ ] Alembic migration for data consolidation
- [ ] Alembic migration for constraints
- [ ] Backup script for production data

#### 5.2 Update Frontend
- [ ] Update API endpoints in frontend
- [ ] Remove calls to deprecated endpoints
- [ ] Test all user flows

#### 5.3 Deprecate main.py
- [ ] Add deprecation warnings to all main.py endpoints
- [ ] Create redirect endpoints to new API
- [ ] Schedule removal date
- [ ] Update documentation

## File Structure After Refactoring

```
backend/
├── alembic/
│   └── versions/
│       ├── 001_add_indexes.py
│       ├── 002_consolidate_exercise_logs.py
│       └── 003_add_constraints.py
├── routers/
│   ├── __init__.py
│   ├── auth.py
│   ├── patients.py
│   ├── doctors.py
│   ├── assignments.py
│   ├── schedules.py
│   ├── messages.py
│   ├── exercises.py
│   └── medical_records.py
├── schemas/
│   ├── __init__.py
│   ├── user.py
│   ├── assignment.py
│   ├── schedule.py
│   ├── exercise.py
│   └── medical_record.py
├── auth.py (enhanced)
├── database.py
├── dependencies.py (NEW)
├── enums.py (NEW)
├── models.py (updated)
├── main.py (NEW - unified app)
├── exercise_logic.py (unchanged)
└── requirements.txt (updated)
```

## Success Metrics

### Security
- [ ] All endpoints have authorization checks
- [ ] No hardcoded secrets in code
- [ ] All passwords hashed with bcrypt
- [ ] Input validation on all endpoints

### Performance
- [ ] All foreign keys indexed
- [ ] No N+1 queries
- [ ] Pagination on all list endpoints
- [ ] Query time < 100ms for 95th percentile

### Code Quality
- [ ] Single source of truth for all data
- [ ] Pydantic schemas for all endpoints
- [ ] No code duplication
- [ ] Comprehensive error handling

### Maintainability
- [ ] Clear API structure with routers
- [ ] Enums for all constants
- [ ] Documentation for all endpoints
- [ ] Migration scripts for all schema changes

## Rollback Plan

1. Keep `main.py` running on port 8000 during transition
2. Run new unified API on port 8001
3. Gradually migrate frontend to new endpoints
4. Monitor error rates and performance
5. If issues arise, revert frontend to old endpoints
6. Database migrations are reversible via Alembic downgrade

## Timeline

- **Week 1**: Phase 1 & 2 (Foundation & Database)
- **Week 2**: Phase 3 (API Consolidation)
- **Week 3**: Phase 4 & 5 (Quality & Testing)
- **Week 4**: Frontend migration & monitoring

## Next Steps

1. Review and approve this plan
2. Create feature branch: `refactor/database-architecture`
3. Begin Phase 1 implementation
4. Create pull request for each phase
5. Test thoroughly before merging
