---
description: Sports Training Tab Improvements Plan
---

# Sports Training Tab - Comprehensive Improvement Plan

## Problem Analysis

### 1. **422 Unprocessable Content Error**
**Root Cause**: The backend expects `current_exercise` to match specific values:
- `squat`
- `bicep-curl`
- `shoulder-flexion`
- `knee-raise`

But the frontend is sending exercise names from the database like:
- "Squat" or "Đứng lên ngồi xuống"
- "Bicep Curl" or "Gập bắp tay"
- "Shoulder Flexion" or "Nâng 2 tay lên cao liên tục để tập vai"
- "Knee Raise" or "Nâng 2 tay lên cao liên tục để tập tay cùng nâng đầu gối so le chân và tay"

**Solution**: Create an exercise name mapping function to convert Vietnamese/display names to backend API keys.

### 2. **Exercise Display Issues**
**Problem**: The tab doesn't show the correct 4 exercises you've implemented.

**Solution**: 
- Ensure the database has the correct exercise names
- Map display names properly
- Show all 4 exercises in the UI

### 3. **UI/UX Issues**
**Problems**:
- Video feed is too small
- Rep counter is not prominent enough
- Feedback text is too small and hard to read

**Solution**: Redesign the layout with:
- Larger horizontal video feed (80% of screen width)
- Massive rep counter (120px font size)
- Large, clear feedback display (24px font size)

### 4. **Feedback System Issues**
**Problems**:
- Continuous feedback changes are confusing
- Feedback appears and disappears too quickly
- No clear indication of what the user should do

**Solution**: Implement a **3-Tier Feedback System**:

#### **Tier 1: Current State Guidance (Always Visible)**
- Shows what the user should do RIGHT NOW
- Examples: "Đứng thẳng", "Hạ thấp người xuống", "Gập tay lên"
- Color: Blue background
- Updates smoothly based on exercise state

#### **Tier 2: Real-time Corrections (Sticky for 3 seconds)**
- Shows form errors detected during the movement
- Examples: "Khép khuỷu tay lại!", "Thẳng lưng lên"
- Color: Orange/Yellow background
- Stays visible for 3 seconds minimum
- Priority: Overrides Tier 1

#### **Tier 3: Rep Completion Feedback (Sticky for 2 seconds)**
- Shows summary after completing a rep
- Examples: "TỐT LẮM! ✅", "Cần cải thiện: Khép khuỷu tay"
- Color: Green (good) or Red (needs improvement)
- Stays visible for 2 seconds
- Priority: Highest, overrides all

### 5. **Rep Counting Accuracy**
**Problems**:
- System doesn't automatically detect exercise completion
- Counting logic is not accurate enough for elderly users

**Solution**:
- Implement stricter validation for each exercise
- Add confidence thresholds
- Only count reps when form is correct
- Add visual confirmation when rep is counted

## Implementation Steps

### Step 1: Fix the 422 Error (CRITICAL - DO FIRST)
1. Create exercise name mapping in frontend
2. Map Vietnamese names to backend API keys
3. Test with all 4 exercises

### Step 2: Redesign UI Layout
1. Make video feed horizontal and larger (80% width)
2. Enlarge rep counter (120px font)
3. Enlarge feedback display (24px font)
4. Add clear visual hierarchy

### Step 3: Implement 3-Tier Feedback System
1. Create feedback state management
2. Implement priority queue
3. Add sticky timers
4. Add smooth transitions

### Step 4: Improve Rep Counting Logic
1. Add stricter validation
2. Implement confidence scoring
3. Add visual/audio confirmation
4. Test with all exercises

### Step 5: Test with All 4 Exercises
1. Test Squat (Đứng lên ngồi xuống)
2. Test Bicep Curl (Gập bắp tay)
3. Test Shoulder Flexion (Nâng 2 tay lên cao - vai)
4. Test Knee Raise (Nâng đầu gối + tay đối diện)

## Exercise Name Mapping

```javascript
const EXERCISE_MAPPING = {
  // Vietnamese to API key
  'Đứng lên ngồi xuống': 'squat',
  'Squat': 'squat',
  'Gập bắp tay': 'bicep-curl',
  'Bicep Curl': 'bicep-curl',
  'Nâng 2 tay lên cao liên tục để tập vai': 'shoulder-flexion',
  'Shoulder Flexion': 'shoulder-flexion',
  'Nâng 2 tay lên cao liên tục để tập tay cùng nâng đầu gối so le chân và tay': 'knee-raise',
  'Knee Raise': 'knee-raise',
  
  // Fallback: Try to match keywords
  default: (name) => {
    if (name.includes('Squat') || name.includes('ngồi xuống')) return 'squat';
    if (name.includes('Curl') || name.includes('bắp tay')) return 'bicep-curl';
    if (name.includes('Shoulder') || name.includes('vai')) return 'shoulder-flexion';
    if (name.includes('Knee') || name.includes('đầu gối')) return 'knee-raise';
    return null;
  }
};
```

## New Feedback Display Design

```
┌─────────────────────────────────────────────────────────┐
│                    VIDEO FEED (LARGE)                    │
│                                                          │
│                    [Skeleton overlay]                    │
│                                                          │
└─────────────────────────────────────────────────────────┘

┌──────────────────┐  ┌─────────────────────────────────┐
│   REP COUNTER    │  │      FEEDBACK DISPLAY           │
│                  │  │                                 │
│      15          │  │  🎯 Tier 1: "Hạ thấp xuống"    │
│     ────         │  │  ⚠️  Tier 2: "Khép khuỷu tay!"  │
│      20          │  │  ✅ Tier 3: "TỐT LẮM!"         │
│                  │  │                                 │
│  (120px font)    │  │  (24px font, color-coded)       │
└──────────────────┘  └─────────────────────────────────┘
```

## Success Criteria

✅ All 4 exercises work without 422 errors
✅ Video feed is large and clear
✅ Rep counter is easily visible from 2 meters away
✅ Feedback is clear, stable, and not confusing
✅ Rep counting is accurate (95%+ accuracy)
✅ System only counts reps with correct form
✅ Elderly users can understand the feedback immediately
✅ No false positives in rep counting
✅ Smooth, professional user experience
