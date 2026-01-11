# Medic1 System Fixes - Implementation Plan

## Issues Identified

### 1. ✅ Google Login Redirects to Patient View (FIXED)
**Problem:** Google login hardcoded role as 'patient'
**Solution:** Added role selection modal in Login.vue
**Status:** COMPLETED

### 2. 🔧 Backend API Errors

#### A. Notifications Endpoint Error
**File:** `backend/api_dashboard.py` line 373-393
**Error:** SQL syntax error - two SELECT statements in one query
**Current Code:**
```python
@app.get("/api/notifications/{user_id}")
async def get_notifications(user_id: str):
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT * FROM notifications 
            WHERE user_id = %s 
            SELECT s.*, u.full_name as patient_name   # ERROR: Two SELECTs
            FROM schedules s
            ...
        """, (doctor_id,))  # ERROR: doctor_id not defined
```

**Fix Needed:**
```python
@app.get("/api/notifications/{user_id}")
async def get_notifications(user_id: str):
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT * FROM notifications 
            WHERE user_id = %s 
            ORDER BY created_at DESC
            LIMIT 50
        """, (user_id,))
        return cur.fetchall()

@app.post("/api/notifications/mark-read")
async def mark_notifications_read(data: Dict[str, Any]):
    with get_db_cursor() as cur:
        cur.execute("""
            UPDATE notifications 
            SET is_read = TRUE 
            WHERE user_id = %s
        """, (data['user_id'],))
        return {"message": "Marked as read"}

@app.get("/api/schedules/{doctor_id}")
async def get_schedules(doctor_id: str):
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT s.*, u.full_name as patient_name 
            FROM schedules s
            JOIN users u ON s.patient_id = u.user_id
            WHERE s.doctor_id = %s
        """, (doctor_id,))
        rows = cur.fetchall()
        return [{
            "id": r['schedule_id'],
            "patient_id": r['patient_id'],
            "title": r['patient_name'],
            "start": r['start_time'].isoformat(),
            "end": r['end_time'].isoformat(),
            "notes": r['notes']
        } for r in rows]
```

#### B. Missing Patient Dashboard Endpoints
**Error:** 404 Not Found for:
- `/api/overall-stats?user_id=...`
- `/api/weekly-progress?user_id=...`
- `/api/patient/charts/{patient_id}`

**Add to api_dashboard.py:**
```python
@app.get("/api/overall-stats")
async def get_overall_stats(user_id: Optional[str] = None):
    """Get overall statistics for patient dashboard"""
    with get_db_cursor() as cur:
        if user_id:
            # Total days with activity
            cur.execute("""
                SELECT COUNT(DISTINCT date) as total_days
                FROM exercise_logs_simple
                WHERE user_id = %s
            """, (user_id,))
            total_days = cur.fetchone()['total_days'] or 0
            
            # Total reps
            cur.execute("""
                SELECT COALESCE(SUM(rep_count), 0) as total_reps
                FROM exercise_logs_simple
                WHERE user_id = %s
            """, (user_id,))
            total_reps = cur.fetchone()['total_reps'] or 0
            
            # Total duration
            cur.execute("""
                SELECT COALESCE(SUM(session_duration), 0) as total_duration
                FROM exercise_logs_simple
                WHERE user_id = %s
            """, (user_id,))
            total_duration = cur.fetchone()['total_duration'] or 0
            
            return {
                "total_days": total_days,
                "total_reps": total_reps,
                "total_duration": total_duration
            }
        return {"total_days": 0, "total_reps": 0, "total_duration": 0}

@app.get("/api/weekly-progress")
async def get_weekly_progress(user_id: Optional[str] = None):
    """Get weekly exercise history"""
    with get_db_cursor() as cur:
        if user_id:
            cur.execute("""
                SELECT 
                    date,
                    exercise_type,
                    MAX(rep_count) as max_reps
                FROM exercise_logs_simple
                WHERE user_id = %s
                AND date >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY date, exercise_type
                ORDER BY date DESC
                LIMIT 20
            """, (user_id,))
            return cur.fetchall()
        return []

@app.get("/api/patient/charts/{patient_id}")
async def get_patient_charts(patient_id: str):
    """Get chart data for patient dashboard"""
    with get_db_cursor() as cur:
        # Weekly activity (last 7 days)
        cur.execute("""
            SELECT 
                date::text,
                SUM(rep_count) as reps
            FROM exercise_logs_simple
            WHERE user_id = %s
            AND date >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY date
            ORDER BY date
        """, (patient_id,))
        weekly_activity = cur.fetchall()
        
        # Accuracy trend (mock data for now - would need accuracy tracking)
        accuracy_trend = [
            {"date": "Day 1", "score": 75},
            {"date": "Day 2", "score": 80},
            {"date": "Day 3", "score": 85},
            {"date": "Day 4", "score": 82},
            {"date": "Day 5", "score": 88},
            {"date": "Day 6", "score": 90},
            {"date": "Day 7", "score": 92}
        ]
        
        # Muscle focus (exercise distribution)
        cur.execute("""
            SELECT 
                exercise_type,
                COUNT(*) as count
            FROM exercise_logs_simple
            WHERE user_id = %s
            AND date >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY exercise_type
        """, (patient_id,))
        muscle_focus = cur.fetchall()
        
        return {
            "weekly_activity": weekly_activity,
            "accuracy_trend": accuracy_trend,
            "muscle_focus": muscle_focus
        }
```

#### C. UUID Validation Error
**Error:** `invalid input syntax for type uuid: "null"`
**Location:** `/api/patient/today/{user_id}` endpoint

**Fix:** Add validation before query
```python
@app.get("/api/patient/today/{user_id}")
async def get_today_plan(user_id: str):
    """Get today's exercises for patient"""
    # Validate UUID
    if not user_id or user_id == "null" or user_id == "undefined":
        raise HTTPException(status_code=400, detail="Invalid user_id")
    
    with get_db_cursor() as cur:
        # ... rest of code
```

### 3. 🔧 Patient Tabs Not Clickable

**Issue:** Tabs appear but may not be responding to clicks
**File:** `frontend/src/components02/PatientTabs.vue`

**Check:**
1. Verify `currentTab` ref is properly updating
2. Check if components are properly imported
3. Ensure no z-index issues blocking clicks

**Potential Fix:**
```vue
<!-- Add debugging -->
<button
  v-for="tab in tabs"
  :key="tab.id"
  @click="handleTabClick(tab.id)"  <!-- Use explicit handler -->
  :class="[...]"
>
  ...
</button>

<script setup>
const handleTabClick = (tabId) => {
  console.log('Tab clicked:', tabId)
  currentTab.value = tabId
}
</script>
```

### 4. 🔧 Patient History & Notes Not Updated in Doctor Dashboard

**File:** `frontend/src/components02/Dashboard.vue` or `DoctorDashboard.vue`

**Issue:** History and notes sections show "Đang cập nhật tính năng..."

**Fix Needed:**
1. Implement history tab to call `/api/weekly-progress?user_id={patient_id}`
2. Implement notes tab to call `/api/patient-notes/{patient_id}`
3. Add ability to create new notes via `/api/patient-notes` POST

**Implementation:**
```vue
<!-- In Dashboard.vue detail-content section -->
<div v-if="activeTab === 'history'" class="tab-pane fade-in">
  <div v-if="patientHistory.length === 0" class="empty-state">
    Chưa có lịch sử tập luyện
  </div>
  <div v-else class="history-list">
    <div v-for="item in patientHistory" :key="item.date" class="history-item">
      <span class="date">{{ formatDate(item.date) }}</span>
      <span class="exercise">{{ item.exercise_type }}</span>
      <span class="reps">{{ item.max_reps }} reps</span>
    </div>
  </div>
</div>

<div v-if="activeTab === 'notes'" class="tab-pane fade-in">
  <button @click="showAddNote = true" class="btn-add-note">
    + Thêm ghi chú
  </button>
  <div v-for="note in patientNotes" :key="note.note_id" class="note-card">
    <h4>{{ note.title }}</h4>
    <p>{{ note.content }}</p>
    <span class="note-date">{{ formatDate(note.created_at) }}</span>
  </div>
</div>

<script setup>
const patientHistory = ref([])
const patientNotes = ref([])

const loadPatientData = async (id) => {
  // ... existing code ...
  
  // Load history
  const historyRes = await fetch(`${API_BASE}/weekly-progress?user_id=${id}`)
  if (historyRes.ok) patientHistory.value = await historyRes.json()
  
  // Load notes
  const notesRes = await fetch(`${API_BASE}/patient-notes/${id}`)
  if (notesRes.ok) patientNotes.value = await notesRes.json()
}
</script>
```

### 5. 🔧 Assignment UI Overlap Issues

**File:** `frontend/src/components02/index.vue` (Patient Management Page)

**Issue:** Patient info cards overlap with dropdown search

**Fix:** Adjust z-index and positioning
```css
/* In index.vue styles */
.search-dropdown {
  position: relative;
  z-index: 50; /* Higher than patient cards */
}

.patient-card {
  position: relative;
  z-index: 10; /* Lower than search */
}

/* Ensure dropdown appears above everything */
.dropdown-menu {
  position: absolute;
  z-index: 100;
  background: white;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
}
```

### 6. 🔧 Assignment Feature Improvements

**Needed Enhancements:**
1. Show more patient details in assignment view
2. Allow combo assignment (already supported in backend)
3. Better visual feedback

**Implementation in index.vue:**
```vue
<!-- Add combo selection -->
<div class="assignment-form">
  <div class="form-group">
    <label>Loại phân công</label>
    <select v-model="assignmentType">
      <option value="single">Bài tập đơn lẻ</option>
      <option value="combo">Combo bài tập</option>
    </select>
  </div>
  
  <div v-if="assignmentType === 'combo'" class="form-group">
    <label>Chọn Combo</label>
    <select v-model="selectedCombo">
      <option v-for="combo in combos" :key="combo.combo_id" :value="combo">
        {{ combo.combo_name }}
      </option>
    </select>
    
    <!-- Show combo details -->
    <div v-if="selectedCombo" class="combo-preview">
      <h4>Bài tập trong combo:</h4>
      <ul>
        <li v-for="item in selectedCombo.items" :key="item.item_id">
          {{ item.exercise_type }} - {{ item.target_reps }} reps
        </li>
      </ul>
    </div>
  </div>
</div>
```

## Implementation Order

1. **Priority 1 - Critical Fixes (Do First):**
   - Fix notifications endpoint SQL error
   - Add missing patient dashboard endpoints
   - Fix UUID validation

2. **Priority 2 - Feature Completion:**
   - Implement history and notes tabs
   - Fix assignment UI overlap

3. **Priority 3 - Enhancements:**
   - Improve assignment feature with combo support
   - Add better visual feedback

## Testing Checklist

- [ ] Google login shows role selection
- [ ] Doctor login works correctly
- [ ] Patient login works correctly
- [ ] Notifications load without errors
- [ ] Patient dashboard shows stats
- [ ] Patient dashboard shows charts
- [ ] Patient tabs are all clickable
- [ ] Sports Training tab works
- [ ] Brain Training tab works
- [ ] Messages tab works
- [ ] Doctor can view patient history
- [ ] Doctor can add/view notes
- [ ] Assignment search doesn't overlap
- [ ] Can assign combos to patients
