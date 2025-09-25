// src/lib/exercise-logic.js

// Enums as objects
export const SquatState = { IDLE: 0, SQUAT_START: 1, SQUAT_DOWN: 2, SQUAT_HOLD: 3, SQUAT_UP: 4 };
export const BicepCurlState = { IDLE: 0, CURL_START: 1, CURL_UP: 2, CURL_HOLD: 3, CURL_DOWN: 4 };
const FeedbackPriority = { LOW: 1, MEDIUM: 2, HIGH: 3 };

// FeedbackManager class
class FeedbackManager {
    constructor(window_size = 5) {
        this.feedback_window = [];
        this.window_size = window_size;
        this.current_feedback = [];
        this.priority_queue = [];
    }

    add_feedback(feedback, priority) {
        this.priority_queue.push({ priority: -priority, feedback });
        this.priority_queue.sort((a, b) => a.priority - b.priority);
        this.feedback_window.push({ feedback, priority });
        if (this.feedback_window.length > this.window_size) {
            this.feedback_window.shift();
        }
        this._process_feedback();
    }

    _process_feedback() {
        const feedback_count = {};
        this.feedback_window.forEach(({ feedback }) => {
            feedback_count[feedback] = (feedback_count[feedback] || 0) + 1;
        });
        const threshold = Math.floor(this.feedback_window.length / 2);
        this.current_feedback = Object.keys(feedback_count).filter(key => feedback_count[key] > threshold);
    }

    get_feedback() {
        if (this.priority_queue.length > 0) {
            return [this.priority_queue[0].feedback];
        }
        return [];
    }

    clear_feedback() {
        this.feedback_window = [];
        this.current_feedback = [];
        this.priority_queue = [];
    }
}

// AngleCalculator class
export class AngleCalculator {
    static calculate_angle(a, b, c) {
        a = [a.x, a.y];
        b = [b.x, b.y];
        c = [c.x, c.y];
        const radians = Math.atan2(c[1] - b[1], c[0] - b[0]) - Math.atan2(a[1] - b[1], a[0] - b[0]);
        let angle = Math.abs(radians * 180.0 / Math.PI);
        return angle <= 180 ? angle : 360 - angle;
    }

    static calculate_vertical_angle(point1, point2) {
        const [x1, y1] = point1;
        const [x2, y2] = point2;
        const dx = x2 - x1;
        const dy = y2 - y1;
        return Math.abs(Math.atan2(dx, -dy) * 180.0 / Math.PI);
    }

    static findDistance(x1, y1, x2, y2) {
        return Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
    }

    static findAngle(x1, y1, x2, y2) {
        const theta = Math.acos((y2 - y1) * (-y1) / (Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) * y1));
        return Math.floor(180 / Math.PI * theta);
    }

    static angle_deg(p1, pref, p2) {
        p1 = Array.isArray(p1) ? p1.slice(0, 2) : [p1.x, p1.y];
        pref = Array.isArray(pref) ? pref.slice(0, 2) : [pref.x, pref.y];
        p2 = Array.isArray(p2) ? p2.slice(0, 2) : [p2.x, p2.y];
        
        const p1ref = [p1[0] - pref[0], p1[1] - pref[1]];
        const p2ref = [p2[0] - pref[0], p2[1] - pref[1]];
        const dot_product = p1ref[0] * p2ref[0] + p1ref[1] * p2ref[1];
        const magnitude_p1ref = Math.sqrt(p1ref[0]**2 + p1ref[1]**2);
        const magnitude_p2ref = Math.sqrt(p2ref[0]**2 + p2ref[1]**2);
        const cos_theta = dot_product / (magnitude_p1ref * magnitude_p2ref);
        const angle_rad = Math.acos(Math.max(-1, Math.min(1, cos_theta)));
        return angle_rad * 180 / Math.PI;
    }

    static calculate_elbow_torso_angle(left_hip, left_shoulder, left_elbow, right_hip, right_shoulder, right_elbow, visibility_threshold = 0.6) {
        const is_visible = points => points.every(p => p.visibility > visibility_threshold);
        const left_points = [left_hip, left_shoulder, left_elbow];
        const right_points = [right_hip, right_shoulder, right_elbow];
        const left_visible = is_visible(left_points);
        const right_visible = is_visible(right_points);

        if (left_visible && right_visible) {
            const left_angle = this.angle_deg(left_hip, left_shoulder, left_elbow);
            const right_angle = this.angle_deg(right_hip, right_shoulder, right_elbow);
            return [left_angle, right_angle, (left_angle + right_angle) / 2, "front"];
        } else if (left_visible) {
            const left_angle = this.angle_deg(left_hip, left_shoulder, left_elbow);
            return [left_angle, null, left_angle, "left_side"];
        } else if (right_visible) {
            const right_angle = this.angle_deg(right_hip, right_shoulder, right_elbow);
            return [null, right_angle, right_angle, "right_side"];
        } else {
            return [null, null, null, "unclear"];
        }
    }

    static calculate_hip_shoulder_angle(hip, shoulder, visibility_threshold = 0.6) {
        if (hip.visibility > visibility_threshold && shoulder.visibility > visibility_threshold) {
            return this.findAngle(hip.x, hip.y, shoulder.x, shoulder.y);
        }
        return null;
    }
}

// ExerciseCounter class
export class ExerciseCounter {
     constructor(thresholds = {}) {
        this.curl_counter = 0;
        this.bicep_curl_state = BicepCurlState.IDLE;
        this.curl_start_threshold = 160;
        this.curl_up_threshold = 90;
        this.curl_down_threshold = 150;

        this.squat_counter = 0;
        this.squat_state = SquatState.IDLE;
        this.squat_threshold = 80;
        this.start_threshold = 160;

        this.thresholds = thresholds || {
            squat_too_deep: 60,
            squat_not_deep_enough: 90,
            squat_forward_bend_too_little: 10,
            squat_forward_bend_too_much: 30,
            bicep_curl_not_low_enough: 160,
            bicep_curl_not_high_enough: 60,
            bicep_curl_elbow_movement: 20,
            bicep_curl_body_swing: 10
        };

        this.total_reps = 0;
        this.bicep_curl_feedback_manager = new FeedbackManager();
        this.squat_feedback_manager = new FeedbackManager();
    }

    process_bicep_curl(shoulder, elbow, wrist, hip, bicep_angle, elbow_torso_angle, hip_shoulder_angle) {
        if (this.bicep_curl_state === BicepCurlState.CURL_DOWN && bicep_angle < this.thresholds.bicep_curl_not_low_enough) {
            this.bicep_curl_feedback_manager.add_feedback("Arm not fully extended at bottom", FeedbackPriority.HIGH);
        }
        if (this.bicep_curl_state === BicepCurlState.CURL_UP && bicep_angle > this.thresholds.bicep_curl_not_high_enough) {
            this.bicep_curl_feedback_manager.add_feedback("Curl higher", FeedbackPriority.HIGH);
        }
        if (elbow_torso_angle && Math.abs(elbow_torso_angle - 90) > this.thresholds.bicep_curl_elbow_movement) {
            this.bicep_curl_feedback_manager.add_feedback("Keep elbow stationary", FeedbackPriority.MEDIUM);
        }
        if (hip_shoulder_angle && Math.abs(hip_shoulder_angle - 90) > this.thresholds.bicep_curl_body_swing) {
            this.bicep_curl_feedback_manager.add_feedback("Avoid swinging body", FeedbackPriority.MEDIUM);
        }

        if (this.bicep_curl_state === BicepCurlState.IDLE && bicep_angle < this.curl_start_threshold) {
            this.bicep_curl_state = BicepCurlState.CURL_START;
        } else if (this.bicep_curl_state === BicepCurlState.CURL_START && bicep_angle < this.curl_up_threshold) {
            this.bicep_curl_state = BicepCurlState.CURL_UP;
        } else if (this.bicep_curl_state === BicepCurlState.CURL_UP && bicep_angle > this.curl_down_threshold) {
            this.bicep_curl_state = BicepCurlState.CURL_DOWN;
            this.curl_counter++;
            this.total_reps++;
        } else if (this.bicep_curl_state === BicepCurlState.CURL_DOWN && bicep_angle > this.curl_start_threshold) {
            this.bicep_curl_state = BicepCurlState.IDLE;
        }
        return [this.bicep_curl_state, this.bicep_curl_feedback_manager.get_feedback()];
    }

    process_squat(knee_angle, back_angle) {
        if (knee_angle < this.thresholds.squat_too_deep) {
            this.squat_feedback_manager.add_feedback("Squat too deep", FeedbackPriority.HIGH);
        } else if (knee_angle > this.thresholds.squat_not_deep_enough) {
            this.squat_feedback_manager.add_feedback("Squat not deep enough", FeedbackPriority.HIGH);
        }
        if (back_angle < this.thresholds.squat_forward_bend_too_little) {
            this.squat_feedback_manager.add_feedback("Lean forward more", FeedbackPriority.MEDIUM);
        } else if (back_angle > this.thresholds.squat_forward_bend_too_much) {
            this.squat_feedback_manager.add_feedback("Don't lean too far forward", FeedbackPriority.MEDIUM);
        }
        
        if (this.squat_state === SquatState.IDLE && knee_angle < this.start_threshold) {
            this.squat_state = SquatState.SQUAT_START;
        } else if (this.squat_state === SquatState.SQUAT_START && knee_angle < this.squat_threshold) {
            this.squat_state = SquatState.SQUAT_DOWN;
        } else if (this.squat_state === SquatState.SQUAT_DOWN && knee_angle > this.start_threshold) {
            this.squat_state = SquatState.SQUAT_UP;
            this.squat_counter++;
            this.total_reps++;
        } else if (this.squat_state === SquatState.SQUAT_UP && knee_angle > this.start_threshold) {
            this.squat_state = SquatState.IDLE;
        }
        return [this.squat_state, this.squat_feedback_manager.get_feedback()];
    }
}