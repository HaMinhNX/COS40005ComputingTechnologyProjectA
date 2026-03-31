# Medic1 Rehabilitation Platform — Metrics & Visualizations Summary

> **For your Data Analyst resume** — This is a healthcare rehabilitation web application that tracks patients' physical and cognitive recovery using AI-powered pose estimation and data analytics.

---

## 1. Doctor Dashboard — Aggregate KPIs

| Metric | Description | Visualization |
|---|---|---|
| **Total Patients** | Count of all patients in the system | KPI card with monthly growth trend (%) |
| **Active Patients** | Patients with workout activity in the last 7 days | KPI card with daily trend (%) |
| **Needs Attention** | Patients inactive for 3–7 days (flagged as at-risk) | Alert KPI card with new alert count |
| **Average Form Score** | Mean accuracy score across all exercise sessions | KPI card with progress bar |
| **Patient Trend** | Month-over-month patient growth rate | Percentage trend indicator |
| **Activity Trend** | Day-over-day session count comparison | Percentage trend indicator |

### Per-Patient Detail Panel
| Metric | Visualization |
|---|---|
| **Accuracy Score over time** | D3.js **line chart** (Catmull-Rom curve) of last 10 exercise logs |
| **Reps completed per session** | Recent activity list |
| **Exercise history** | Tabular log with exercise type, rep count, accuracy %, timestamps |
| **Session quality** | Color-coded indicator (error count threshold) |
| **Patient progress** | Progress bar derived from average accuracy or session count |
| **Patient status** | Derived classification: Active / Needs Attention / Inactive |

---

## 2. Patient Health Dashboard — Smartwatch Metrics

| Metric | Unit | Visualization |
|---|---|---|
| **Heart Rate** | BPM | Large KPI card + D3.js **bar chart** (7-day trend) |
| **Blood Oxygen (SpO2)** | % | KPI card with status badge |
| **Sleep Quality** | Score /100 | KPI card |
| **Calories Burned** | KCAL | KPI card |
| **Resting Heart Rate** | BPM | KPI card |
| **Total Days Exercised** | Count | KPI card |
| **Total Reps** | Count | KPI card |
| **Weekly Reps Progress** | Reps/day | D3.js **line chart** (7-day trend) |

---

## 3. Physical Rehabilitation — AI Pose Estimation Metrics

Uses **MediaPipe Pose Landmarker** for real-time body tracking and exercise form analysis.

| Metric | Description |
|---|---|
| **Rep Count** | Per-exercise repetition counter (Squat, Bicep Curl, Shoulder Flexion, Knee Raise) |
| **Accuracy Score** | Form quality percentage per session detail |
| **Mistakes Count** | Number of form errors detected per exercise |
| **Session Duration** | Time spent per exercise (seconds) |
| **Reps Completed** | Actual reps vs target reps |
| **Joint Angles** | Real-time calculated angles (knee, bicep, shoulder flexion, elbow, hip-shoulder, back) |
| **Exercise State** | State machine tracking (e.g., SquatState, BicepCurlState transitions) |
| **Real-time Feedback** | Form correction messages (posture, range of motion) |

### Chart Endpoints (Backend API)
| Chart | Data |
|---|---|
| **Weekly Activity** | Reps per day for last 7 days (bar/line chart data) |
| **Accuracy Trend** | Average accuracy score per day over 10 data points |
| **Muscle Focus Distribution** | Exercise type frequency (pie/donut chart data) |

---

## 4. Brain Exercise — Cognitive Rehabilitation Metrics

| Metric | Description |
|---|---|
| **Score** | Correct answers per session |
| **Total Questions** | Questions attempted per session |
| **Percentage** | Score as percentage (score/total × 100) |
| **Is Correct** | Per-question correctness (boolean) |
| **Today's Score** | Cumulative score for the current day |
| **Streak** | Consecutive days of brain exercise activity |

**Game Types Tracked:** Math, Memory (sequence recall), Pattern Recognition, Word Games

---

## 5. Patient Management & Compliance Metrics

| Metric | Description |
|---|---|
| **Compliance Rate** | Completed assignments / Total assignments × 100 |
| **Total Workout Sessions** | Lifetime session count |
| **Total Exercise Time** | Cumulative duration in hours |
| **Average Accuracy** | Lifetime mean accuracy score |
| **Last Active Timestamp** | Most recent workout session time |
| **Assignment Completion** | Boolean tracking per exercise assignment |

---

## 6. Automated Reporting

- **Email Reports**: Automated rehabilitation progress reports sent via SMTP to patients/caregivers

---

## Resume Bullet Point Suggestions

> **Data Analyst | Medic1 Rehabilitation Platform**
>
> - Designed and implemented **20+ KPIs and metrics** across physical rehabilitation, cognitive training, and patient health domains, tracked via a PostgreSQL database and visualized with **D3.js interactive charts**
> - Built **real-time analytics dashboards** for doctors monitoring patient compliance rates, exercise accuracy trends, and activity patterns (active/at-risk/inactive classification)
> - Developed **trend analysis** features including month-over-month patient growth, day-over-day activity trends, weekly rep progression, and accuracy score trendlines
> - Tracked **AI-powered pose estimation metrics** (joint angles, form accuracy, error detection) from MediaPipe to quantify patient rehabilitation progress
> - Created **patient health metric cards** integrating smartwatch data (heart rate, SpO2, sleep quality, calories) with exercise performance data
> - Implemented **automated email reporting** for rehabilitation progress summaries
