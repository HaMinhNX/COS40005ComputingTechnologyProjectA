<template>
  <div class="login-container">
    <!-- Clean Background -->
    <div class="clean-background"></div>

    <!-- Login/Signup Card -->
    <div class="login-card glass-card animate-fade-in">
      <div class="logo-section">
        <div class="logo-icon animate-float">
          <Activity :size="64" color="#667EEA" />
        </div>
        <h1 class="app-name">HaminG</h1>
        <p class="app-tagline">Chăm sóc sức khỏe người cao tuổi</p>
      </div>

      <div class="login-form-section">
        <!-- Tab Switcher -->
        <div class="tab-switcher" v-if="!isForgotPassword">
          <button
            @click="
              isLogin = true;
              isForgotPassword = false;
            "
            :class="['tab-btn', { active: isLogin }]"
          >
            Đăng nhập
          </button>
          <button
            @click="
              isLogin = false;
              isForgotPassword = false;
            "
            :class="['tab-btn', { active: !isLogin }]"
          >
            Đăng ký
          </button>
        </div>

        <!-- Login Form -->
        <form v-if="isLogin" @submit.prevent="onLogin" class="auth-form">
          <h2 class="form-title">Chào mừng trở lại!</h2>
          <p class="form-subtitle">Đăng nhập để tiếp tục</p>

          <div class="form-group">
            <label class="form-label">Email</label>
            <div class="input-wrapper">
              <Mail :size="18" class="input-icon" />
              <input
                v-model="loginForm.username"
                type="email"
                required
                placeholder="Nhập email"
                class="form-input with-icon"
              />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Mật khẩu</label>
            <div class="password-input-group">
              <div class="input-wrapper-inner">
                <Lock :size="18" class="input-icon" />
                <input
                  v-model="loginForm.password"
                  :type="showPassword ? 'text' : 'password'"
                  required
                  placeholder="Nhập mật khẩu"
                  class="form-input with-icon"
                />
              </div>
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="password-toggle-external"
                tabindex="-1"
              >
                <Eye v-if="!showPassword" :size="20" />
                <EyeOff v-else :size="20" />
              </button>
            </div>
          </div>

          <button type="submit" class="btn-submit" :disabled="loading">
            <span v-if="!loading" class="btn-text">Đăng nhập</span>
            <span v-else class="btn-text">Đang xử lý...</span>
            <ArrowRight class="btn-icon" :size="20" />
          </button>

          <div style="text-align: right; margin-top: 5px">
            <a
              href="#"
              @click.prevent="
                isForgotPassword = true;
                isLogin = false;
                forgotPasswordStep = 1;
              "
              style="color: #667eea; text-decoration: none; font-size: 14px"
              >Quên mật khẩu?</a
            >
          </div>
        </form>

        <!-- Signup Form -->
        <form
          v-else-if="!isLogin && !isForgotPassword"
          @submit.prevent="onSignup"
          class="auth-form"
        >
          <h2 class="form-title">Tạo tài khoản mới</h2>
          <p class="form-subtitle">Đăng ký để bắt đầu</p>

          <div v-if="!isOTPStep">
            <div class="form-group">
              <label class="form-label">Họ và tên</label>
              <div class="input-wrapper">
                <User :size="18" class="input-icon" />
                <input
                  v-model="signupForm.full_name"
                  type="text"
                  required
                  placeholder="Nguyễn Văn A"
                  class="form-input with-icon"
                />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Email</label>
              <div class="input-wrapper">
                <Mail :size="18" class="input-icon" />
                <input
                  v-model="signupForm.email"
                  type="email"
                  required
                  placeholder="example@email.com"
                  class="form-input with-icon"
                />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Tên đăng nhập</label>
              <div class="input-wrapper">
                <UserCircle :size="18" class="input-icon" />
                <input
                  v-model="signupForm.username"
                  type="text"
                  required
                  placeholder="Chọn tên đăng nhập"
                  class="form-input with-icon"
                />
              </div>
            </div>

            <!-- Password Field -->
            <div class="form-group">
              <label class="form-label">Mật khẩu</label>
              <div class="password-input-group">
                <div class="input-wrapper-inner">
                  <Lock :size="18" class="input-icon" />
                  <input
                    v-model="signupForm.password"
                    :type="showPassword ? 'text' : 'password'"
                    required
                    placeholder="Nhập mật khẩu"
                    class="form-input with-icon"
                    @input="checkPasswordStrength(signupForm.password, 'signup')"
                  />
                </div>
                <button
                  type="button"
                  @click="showPassword = !showPassword"
                  class="password-toggle-external"
                >
                  <Eye v-if="!showPassword" :size="20" />
                  <EyeOff v-else :size="20" />
                </button>
              </div>
            </div>

            <!-- Confirm Password Field -->
            <div class="form-group">
              <label class="form-label">Xác nhận mật khẩu</label>
              <div class="password-input-group">
                <div class="input-wrapper-inner">
                  <Lock :size="18" class="input-icon" />
                  <input
                    v-model="signupForm.confirmPassword"
                    :type="showConfirmPassword ? 'text' : 'password'"
                    required
                    placeholder="Nhập lại mật khẩu"
                    class="form-input with-icon"
                  />
                </div>
                <button
                  type="button"
                  @click="showConfirmPassword = !showConfirmPassword"
                  class="password-toggle-external"
                >
                  <Eye v-if="!showConfirmPassword" :size="20" />
                  <EyeOff v-else :size="20" />
                </button>
              </div>
              <!-- Match indicator -->
              <div v-if="signupForm.confirmPassword" class="password-match-indicator">
                <span v-if="signupForm.password === signupForm.confirmPassword" class="match-ok">
                  <CheckCircle :size="14" /> Mật khẩu khớp
                </span>
                <span v-else class="match-fail">
                  <AlertCircle :size="14" /> Mật khẩu không khớp
                </span>
              </div>
            </div>

            <!-- Password Requirements -->
            <div class="password-requirements" v-if="signupForm.password">
              <p class="req-title">Yêu cầu mật khẩu:</p>
              <div class="req-list">
                <div :class="['req-item', signupPasswordRules.minLength ? 'req-met' : 'req-unmet']">
                  <CheckCircle v-if="signupPasswordRules.minLength" :size="13" />
                  <AlertCircle v-else :size="13" />
                  Ít nhất 8 ký tự
                </div>
                <div :class="['req-item', signupPasswordRules.maxLength ? 'req-met' : 'req-unmet']">
                  <CheckCircle v-if="signupPasswordRules.maxLength" :size="13" />
                  <AlertCircle v-else :size="13" />
                  Không quá 40 ký tự
                </div>
                <div :class="['req-item', signupPasswordRules.hasUpper ? 'req-met' : 'req-unmet']">
                  <CheckCircle v-if="signupPasswordRules.hasUpper" :size="13" />
                  <AlertCircle v-else :size="13" />
                  Có chữ hoa (A-Z)
                </div>
                <div :class="['req-item', signupPasswordRules.hasLower ? 'req-met' : 'req-unmet']">
                  <CheckCircle v-if="signupPasswordRules.hasLower" :size="13" />
                  <AlertCircle v-else :size="13" />
                  Có chữ thường (a-z)
                </div>
                <div :class="['req-item', signupPasswordRules.hasDigit ? 'req-met' : 'req-unmet']">
                  <CheckCircle v-if="signupPasswordRules.hasDigit" :size="13" />
                  <AlertCircle v-else :size="13" />
                  Có chữ số (0-9)
                </div>
                <div
                  :class="['req-item', signupPasswordRules.hasSpecial ? 'req-met' : 'req-unmet']"
                >
                  <CheckCircle v-if="signupPasswordRules.hasSpecial" :size="13" />
                  <AlertCircle v-else :size="13" />
                  Có ký tự đặc biệt (!@#$%...)
                </div>
              </div>
            </div>

            <div class="form-group" style="margin-top: 1rem">
              <label class="form-label">Vai trò</label>
              <div class="input-wrapper">
                <ShieldCheck :size="18" class="input-icon" />
                <select v-model="signupForm.role" required class="form-select with-icon">
                  <option value="">Chọn vai trò</option>
                  <option value="patient">Bệnh nhân</option>
                  <option value="doctor">Bác sĩ</option>
                </select>
              </div>
            </div>

            <div v-if="signupForm.role === 'doctor'" class="form-group doctor-certificate-group">
              <label class="form-label">Chứng chỉ bác sĩ (JPG/PNG/PDF)</label>
              <div class="certificate-upload">
                <label class="certificate-upload-btn" for="doctor-certificate-input">
                  Chọn tệp
                </label>
                <input
                  id="doctor-certificate-input"
                  type="file"
                  accept=".jpg,.jpeg,.png,.pdf"
                  class="certificate-hidden-input"
                  @change="onCertificateChange"
                />
                <span class="certificate-file-name">
                  {{ selectedCertificate ? selectedCertificate.name : 'Chưa chọn tệp nào' }}
                </span>
              </div>
              <p class="certificate-hint">Dung lượng khuyến nghị dưới 5MB.</p>
            </div>

            <button type="button" @click="onRequestOTP" class="btn-submit" :disabled="loading || !isSignupPasswordValid || signupForm.password !== signupForm.confirmPassword">
              <span v-if="!loading" class="btn-text">{{ signupForm.role === 'doctor' ? 'Đăng ký bác sĩ' : 'Đăng ký &amp; Nhận mã OTP' }}</span>
              <span v-else class="btn-text">Đang xử lý...</span>
              <ArrowRight class="btn-icon" :size="20" />
            </button>
          </div>

          <div v-else>
            <div class="form-group">
              <label class="form-label">Mã xác nhận (OTP)</label>
              <div class="input-wrapper">
                <Lock :size="18" class="input-icon" />
                <input
                  v-model="otpCode"
                  type="text"
                  required
                  maxlength="6"
                  placeholder="Nhập mã 6 số từ email"
                  class="form-input with-icon"
                />
              </div>
            </div>

            <button type="submit" class="btn-submit" :disabled="loading">
              <span v-if="!loading" class="btn-text">Xác nhận OTP &amp; Đăng ký</span>
              <span v-else class="btn-text">Đang xử lý...</span>
              <CheckCircle class="btn-icon" :size="20" />
            </button>
            <div style="text-align: center; margin-top: 15px">
              <a
                href="#"
                @click.prevent="isOTPStep = false"
                style="color: #667eea; text-decoration: none; font-size: 14px"
                >Quay lại chỉnh sửa thông tin</a
              >
            </div>
          </div>
        </form>

        <!-- Forgot Password Form -->
        <form
          v-else-if="isForgotPassword"
          @submit.prevent="onForgotPasswordSubmit"
          class="auth-form"
        >
          <h2 class="form-title">Quên mật khẩu</h2>
          <p class="form-subtitle">
            <span v-if="forgotPasswordStep === 1">Nhập email để nhận mã xác nhận</span>
            <span v-else-if="forgotPasswordStep === 2">Nhập mã OTP được gửi đến email</span>
            <span v-else>Tạo mật khẩu mới</span>
          </p>

          <div v-if="forgotPasswordStep === 1">
            <div class="form-group">
              <label class="form-label">Email</label>
              <div class="input-wrapper">
                <Mail :size="18" class="input-icon" />
                <input
                  v-model="forgotPasswordForm.email"
                  type="email"
                  required
                  placeholder="Nhập email của bạn"
                  class="form-input with-icon"
                />
              </div>
            </div>
          </div>

          <div v-else-if="forgotPasswordStep === 2">
            <div class="form-group">
              <label class="form-label">Mã xác nhận (OTP)</label>
              <div class="input-wrapper">
                <Lock :size="18" class="input-icon" />
                <input
                  v-model="forgotPasswordForm.otpCode"
                  type="text"
                  required
                  maxlength="6"
                  placeholder="Nhập mã 6 số từ email"
                  class="form-input with-icon"
                />
              </div>
            </div>
          </div>

          <div v-else-if="forgotPasswordStep === 3">
            <!-- New Password -->
            <div class="form-group">
              <label class="form-label">Mật khẩu mới</label>
              <div class="password-input-group">
                <div class="input-wrapper-inner">
                  <Lock :size="18" class="input-icon" />
                  <input
                    v-model="forgotPasswordForm.newPassword"
                    :type="showPassword ? 'text' : 'password'"
                    required
                    placeholder="Nhập mật khẩu mới"
                    class="form-input with-icon"
                    @input="checkPasswordStrength(forgotPasswordForm.newPassword, 'forgot')"
                  />
                </div>
                <button
                  type="button"
                  @click="showPassword = !showPassword"
                  class="password-toggle-external"
                >
                  <Eye v-if="!showPassword" :size="20" />
                  <EyeOff v-else :size="20" />
                </button>
              </div>
            </div>

            <!-- Confirm New Password -->
            <div class="form-group">
              <label class="form-label">Xác nhận mật khẩu mới</label>
              <div class="password-input-group">
                <div class="input-wrapper-inner">
                  <Lock :size="18" class="input-icon" />
                  <input
                    v-model="forgotPasswordForm.confirmNewPassword"
                    :type="showConfirmPassword ? 'text' : 'password'"
                    required
                    placeholder="Nhập lại mật khẩu mới"
                    class="form-input with-icon"
                  />
                </div>
                <button
                  type="button"
                  @click="showConfirmPassword = !showConfirmPassword"
                  class="password-toggle-external"
                >
                  <Eye v-if="!showConfirmPassword" :size="20" />
                  <EyeOff v-else :size="20" />
                </button>
              </div>
              <!-- Match indicator -->
              <div v-if="forgotPasswordForm.confirmNewPassword" class="password-match-indicator">
                <span
                  v-if="forgotPasswordForm.newPassword === forgotPasswordForm.confirmNewPassword"
                  class="match-ok"
                >
                  <CheckCircle :size="14" /> Mật khẩu khớp
                </span>
                <span v-else class="match-fail">
                  <AlertCircle :size="14" /> Mật khẩu không khớp
                </span>
              </div>
            </div>

            <!-- Password Requirements -->
            <div class="password-requirements" v-if="forgotPasswordForm.newPassword">
              <p class="req-title">Yêu cầu mật khẩu:</p>
              <div class="req-list">
                <div :class="['req-item', forgotPasswordRules.minLength ? 'req-met' : 'req-unmet']">
                  <CheckCircle v-if="forgotPasswordRules.minLength" :size="13" />
                  <AlertCircle v-else :size="13" />
                  Ít nhất 8 ký tự
                </div>
                <div :class="['req-item', forgotPasswordRules.maxLength ? 'req-met' : 'req-unmet']">
                  <CheckCircle v-if="forgotPasswordRules.maxLength" :size="13" />
                  <AlertCircle v-else :size="13" />
                  Không quá 40 ký tự
                </div>
                <div :class="['req-item', forgotPasswordRules.hasUpper ? 'req-met' : 'req-unmet']">
                  <CheckCircle v-if="forgotPasswordRules.hasUpper" :size="13" />
                  <AlertCircle v-else :size="13" />
                  Có chữ hoa (A-Z)
                </div>
                <div :class="['req-item', forgotPasswordRules.hasLower ? 'req-met' : 'req-unmet']">
                  <CheckCircle v-if="forgotPasswordRules.hasLower" :size="13" />
                  <AlertCircle v-else :size="13" />
                  Có chữ thường (a-z)
                </div>
                <div :class="['req-item', forgotPasswordRules.hasDigit ? 'req-met' : 'req-unmet']">
                  <CheckCircle v-if="forgotPasswordRules.hasDigit" :size="13" />
                  <AlertCircle v-else :size="13" />
                  Có chữ số (0-9)
                </div>
                <div
                  :class="['req-item', forgotPasswordRules.hasSpecial ? 'req-met' : 'req-unmet']"
                >
                  <CheckCircle v-if="forgotPasswordRules.hasSpecial" :size="13" />
                  <AlertCircle v-else :size="13" />
                  Có ký tự đặc biệt (!@#$%...)
                </div>
              </div>
            </div>
          </div>

          <button
            type="submit"
            class="btn-submit"
            :disabled="
              loading ||
              (forgotPasswordStep === 3 &&
                (!isForgotPasswordValid ||
                  forgotPasswordForm.newPassword !== forgotPasswordForm.confirmNewPassword))
            "
          >
            <span v-if="!loading" class="btn-text">
              <span v-if="forgotPasswordStep === 1">Gửi mã OTP</span>
              <span v-else-if="forgotPasswordStep === 2">Xác nhận OTP</span>
              <span v-else>Đặt lại mật khẩu</span>
            </span>
            <span v-else class="btn-text">Đang xử lý...</span>
            <ArrowRight class="btn-icon" :size="20" v-if="forgotPasswordStep !== 3" />
            <CheckCircle class="btn-icon" :size="20" v-else />
          </button>

          <div style="text-align: center; margin-top: 15px">
            <a
              href="#"
              @click.prevent="
                isForgotPassword = false;
                isLogin = true;
              "
              style="color: #667eea; text-decoration: none; font-size: 14px"
              >Quay lại đăng nhập</a
            >
          </div>
        </form>

        <!-- Error/Success Message -->
        <transition name="fade">
          <div v-if="message.text" :class="['message', message.type]">
            <AlertCircle v-if="message.type === 'error'" :size="18" />
            <CheckCircle v-else :size="18" />
            {{ message.text }}
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  Activity,
  User,
  Lock,
  Eye,
  EyeOff,
  ArrowRight,
  Mail,
  UserCircle,
  ShieldCheck,
  AlertCircle,
  CheckCircle,
} from 'lucide-vue-next'
import { API_BASE_URL } from '../config'

const router = useRouter()
const isLogin = ref(true)
const isForgotPassword = ref(false)
const isOTPStep = ref(false)
const forgotPasswordStep = ref(1)
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const loading = ref(false)
const message = ref({ text: '', type: '' })
const otpCode = ref('')
const selectedCertificate = ref(null)

const loginForm = ref({
  username: '',
  password: '',
})

const forgotPasswordForm = ref({
  email: '',
  otpCode: '',
  newPassword: '',
  confirmNewPassword: '',
})

const signupForm = ref({
  username: '',
  password: '',
  confirmPassword: '',
  full_name: '',
  email: '',
  role: '',
})

// --- Password Rules State ---
const defaultRules = () => ({
  minLength: false,
  maxLength: true,
  hasUpper: false,
  hasLower: false,
  hasDigit: false,
  hasSpecial: false,
})

const signupPasswordRules = ref(defaultRules())
const forgotPasswordRules = ref(defaultRules())

const SPECIAL_CHAR_REGEX = /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?`~]/

const checkPasswordStrength = (password, form) => {
  const rules = {
    minLength: password.length >= 8,
    maxLength: password.length <= 40,
    hasUpper: /[A-Z]/.test(password),
    hasLower: /[a-z]/.test(password),
    hasDigit: /[0-9]/.test(password),
    hasSpecial: SPECIAL_CHAR_REGEX.test(password),
  }
  if (form === 'signup') {
    signupPasswordRules.value = rules
  } else {
    forgotPasswordRules.value = rules
  }
}

const isSignupPasswordValid = computed(() => {
  const r = signupPasswordRules.value
  return r.minLength && r.maxLength && r.hasUpper && r.hasLower && r.hasDigit && r.hasSpecial
})

const isForgotPasswordValid = computed(() => {
  const r = forgotPasswordRules.value
  return r.minLength && r.maxLength && r.hasUpper && r.hasLower && r.hasDigit && r.hasSpecial
})

const showMessage = (text, type = 'error') => {
  message.value = { text, type }
  setTimeout(() => {
    message.value = { text: '', type: '' }
  }, 5000)
}

const getErrorMessage = (data) => {
  if (!data.detail) return 'Có lỗi xảy ra'

  if (typeof data.detail === 'string') {
    return data.detail
  }

  if (Array.isArray(data.detail)) {
    const fieldMap = {
      username: 'Tên đăng nhập',
      password: 'Mật khẩu',
      email: 'Email',
      full_name: 'Họ và tên',
      role: 'Vai trò',
    }

    return data.detail
      .map((err) => {
        let rawField = err.loc ? err.loc[err.loc.length - 1] : 'Lỗi'
        const fieldName = fieldMap[rawField] || rawField

        let msg = err.msg
        msg = msg.replace(/^Value error,\s*/i, '')
        msg = msg.replace(
          /String should have at least (\d+) characters/i,
          'Phải có ít nhất $1 ký tự',
        )
        msg = msg.replace(/String should have at most (\d+) characters/i, 'Không được quá $1 ký tự')

        const lowerMsg = msg.toLowerCase()

        if (lowerMsg === 'field required') msg = 'Bắt buộc nhập'
        if (lowerMsg.includes('not a valid email')) msg = 'Email không hợp lệ'
        if (lowerMsg.includes('input should be a valid string')) msg = 'Giá trị phải là chuỗi ký tự'
        if (lowerMsg.includes('at least 8 characters')) msg = 'Phải có ít nhất 8 ký tự'
        if (lowerMsg.includes('must contain at least one uppercase letter'))
          msg = 'Phải có ít nhất 1 chữ in hoa'
        if (lowerMsg.includes('must contain at least one lowercase letter'))
          msg = 'Phải có ít nhất 1 chữ thường'
        if (lowerMsg.includes('must contain at least one digit')) msg = 'Phải có ít nhất 1 số'
        if (lowerMsg.includes('must contain at least one special character'))
          msg = 'Phải có ít nhất 1 ký tự đặc biệt'

        return `${fieldName}: ${msg}`
      })
      .join('\n')
  }

  return JSON.stringify(data.detail)
}

const onLogin = async () => {
  loading.value = true
  message.value = { text: '', type: '' }

  try {
    const res = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(loginForm.value),
    })

    const data = await res.json()

    if (!res.ok) {
      throw new Error(getErrorMessage(data))
    }

    // Save user data and token
    localStorage.setItem('token', data.access_token)
    localStorage.setItem(
      'user',
      JSON.stringify({
        user_id: data.user_id,
        role: data.role,
        full_name: data.full_name,
      }),
    )

    showMessage('Đăng nhập thành công!', 'success')

    // Redirect based on role
    setTimeout(() => {
      if (data.role === 'doctor') {
        router.push('/doctor')
      } else if (data.role === 'admin') {
        router.push('/admin')
      } else {
        router.push('/patient')
      }
    }, 500)
  } catch (e) {
    showMessage(e.message, 'error')
  } finally {
    loading.value = false
  }
}

const onRequestOTP = async () => {
  if (
    !signupForm.value.full_name ||
    !signupForm.value.email ||
    !signupForm.value.username ||
    !signupForm.value.password ||
    !signupForm.value.role
  ) {
    showMessage('Vui lòng điền đủ thông tin', 'error')
    return
  }

  if (!isSignupPasswordValid.value) {
    showMessage('Mật khẩu chưa đáp ứng yêu cầu bảo mật', 'error')
    return
  }

  if (signupForm.value.password !== signupForm.value.confirmPassword) {
    showMessage('Mật khẩu xác nhận không khớp', 'error')
    return
  }

  loading.value = true
  message.value = { text: '', type: '' }

  try {
    if (signupForm.value.role === 'doctor') {
      if (!selectedCertificate.value) {
        throw new Error('Vui lòng tải lên chứng chỉ bác sĩ')
      }

      const formData = new FormData()
      formData.append('username', signupForm.value.username)
      formData.append('password', signupForm.value.password)
      formData.append('email', signupForm.value.email)
      formData.append('full_name', signupForm.value.full_name)
      formData.append('certificate', selectedCertificate.value)

      const res = await fetch(`${API_BASE_URL}/signup/doctor-with-certificate`, {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()
      if (!res.ok) {
        throw new Error(getErrorMessage(data))
      }
      showMessage(
        data.message || 'Đăng ký bác sĩ thành công. Vui lòng chờ admin phê duyệt tài khoản.',
        'success',
      )
      return
    }

    const payload = { ...signupForm.value }
    delete payload.confirmPassword
    const res = await fetch(`${API_BASE_URL}/signup/request-otp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    const data = await res.json()

    if (!res.ok) {
      throw new Error(getErrorMessage(data))
    }

    showMessage(data.message || 'Mã OTP đã được gửi!', 'success')
    isOTPStep.value = true
  } catch (e) {
    showMessage(e.message, 'error')
  } finally {
    loading.value = false
  }
}

const onCertificateChange = (event) => {
  const file = event.target.files?.[0] || null
  selectedCertificate.value = file
}

const onForgotPasswordSubmit = async () => {
  if (forgotPasswordStep.value === 1) {
    if (!forgotPasswordForm.value.email) {
      showMessage('Vui lòng nhập email', 'error')
      return
    }

    loading.value = true
    message.value = { text: '', type: '' }

    try {
      const res = await fetch(`${API_BASE_URL}/forgot-password/request-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: forgotPasswordForm.value.email }),
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(getErrorMessage(data))
      }

      showMessage(data.message || 'Mã OTP đã được gửi!', 'success')
      forgotPasswordStep.value = 2
    } catch (e) {
      showMessage(e.message, 'error')
    } finally {
      loading.value = false
    }
  } else if (forgotPasswordStep.value === 2) {
    if (!forgotPasswordForm.value.otpCode) {
      showMessage('Vui lòng nhập mã OTP', 'error')
      return
    }

    loading.value = true
    message.value = { text: '', type: '' }

    try {
      const res = await fetch(`${API_BASE_URL}/forgot-password/verify-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: forgotPasswordForm.value.email,
          otp_code: forgotPasswordForm.value.otpCode,
        }),
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(getErrorMessage(data))
      }

      showMessage('Mã OTP hợp lệ, vui lòng tạo mật khẩu mới.', 'success')
      forgotPasswordStep.value = 3
    } catch (e) {
      showMessage(e.message, 'error')
    } finally {
      loading.value = false
    }
  } else if (forgotPasswordStep.value === 3) {
    if (!forgotPasswordForm.value.newPassword) {
      showMessage('Vui lòng nhập mật khẩu mới', 'error')
      return
    }

    if (!isForgotPasswordValid.value) {
      showMessage('Mật khẩu mới chưa đáp ứng yêu cầu bảo mật', 'error')
      return
    }

    if (forgotPasswordForm.value.newPassword !== forgotPasswordForm.value.confirmNewPassword) {
      showMessage('Mật khẩu xác nhận không khớp', 'error')
      return
    }

    loading.value = true
    message.value = { text: '', type: '' }

    try {
      const res = await fetch(`${API_BASE_URL}/forgot-password/reset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: forgotPasswordForm.value.email,
          otp_code: forgotPasswordForm.value.otpCode,
          new_password: forgotPasswordForm.value.newPassword,
        }),
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(getErrorMessage(data))
      }

      showMessage('Đặt lại mật khẩu thành công! Bạn có thể đăng nhập.', 'success')
      isForgotPassword.value = false
      isLogin.value = true
      forgotPasswordStep.value = 1
      forgotPasswordForm.value = { email: '', otpCode: '', newPassword: '', confirmNewPassword: '' }
    } catch (e) {
      showMessage(e.message, 'error')
    } finally {
      loading.value = false
    }
  }
}

const onSignup = async () => {
  if (!otpCode.value) {
    showMessage('Vui lòng nhập mã OTP', 'error')
    return
  }

  loading.value = true
  message.value = { text: '', type: '' }

  try {
    const res = await fetch(`${API_BASE_URL}/signup/verify-otp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: signupForm.value.email, otp_code: otpCode.value }),
    })

    const data = await res.json()

    if (!res.ok) {
      throw new Error(getErrorMessage(data))
    }

    // Save user data and token
    localStorage.setItem('token', data.access_token)
    localStorage.setItem(
      'user',
      JSON.stringify({
        user_id: data.user_id,
        role: data.role,
        full_name: data.full_name,
      }),
    )

    showMessage('Đăng ký thành công!', 'success')

    // Redirect based on role
    setTimeout(() => {
      if (data.role === 'doctor') {
        router.push('/doctor')
      } else if (data.role === 'admin') {
        router.push('/admin')
      } else {
        router.push('/patient')
      }
    }, 500)
  } catch (e) {
    showMessage(e.message, 'error')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  position: relative;
  overflow: hidden;
  background: #f8fafc;
}

.clean-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #f8fafc;
  background-image:
    radial-gradient(#e2e8f0 1px, transparent 1px), radial-gradient(#e2e8f0 1px, transparent 1px);
  background-size: 40px 40px;
  background-position:
    0 0,
    20px 20px;
  opacity: 0.5;
  z-index: 1;
}

.login-card {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 520px;
  padding: 3rem;
  border-radius: 2rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  max-height: 92vh;
  overflow-y: auto;
  scrollbar-width: thin;
}

.logo-section {
  text-align: center;
  margin-bottom: 2rem;
}

.logo-icon {
  margin-bottom: 1rem;
  display: inline-block;
}

.app-name {
  font-size: 2.5rem;
  font-weight: 900;
  margin: 0;
  color: #6366f1;
  letter-spacing: -1px;
}

.app-tagline {
  font-size: 1rem;
  color: #64748b;
  font-weight: 500;
}

.tab-switcher {
  display: flex;
  background: #f1f5f9;
  padding: 0.25rem;
  border-radius: 1rem;
  margin-bottom: 2rem;
  gap: 0.5rem;
}

.tab-btn {
  flex: 1;
  padding: 0.75rem;
  border: none;
  background: transparent;
  font-weight: 700;
  color: #64748b;
  cursor: pointer;
  border-radius: 0.75rem;
  transition: all 0.2s;
}

.tab-btn.active {
  background: white;
  color: #667eea;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.form-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.form-subtitle {
  color: #64748b;
  margin-bottom: 1.5rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.doctor-certificate-group {
  margin-top: 0.4rem;
  margin-bottom: 0.9rem;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 700;
  color: #475569;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input-group {
  display: flex;
  gap: 0.5rem;
  align-items: stretch;
}

.input-wrapper-inner {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 1rem;
  color: #94a3b8;
}

.form-input,
.form-select {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 0.75rem;
  font-size: 1rem;
  transition: all 0.2s;
  background: white;
}

.form-input.with-icon,
.form-select.with-icon {
  padding-left: 3rem;
}

.certificate-upload {
  width: 100%;
  min-height: 56px;
  border: 2px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 0.6rem 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #fff;
  transition: all 0.2s ease;
}

.certificate-upload:focus-within {
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.certificate-hidden-input {
  display: none;
}

.certificate-upload-btn {
  background: #eef2ff;
  color: #4338ca;
  border: 1px solid #c7d2fe;
  border-radius: 0.65rem;
  padding: 0.5rem 0.85rem;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.certificate-upload-btn:hover {
  background: #e0e7ff;
}

.certificate-file-name {
  color: #475569;
  font-size: 0.9rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.certificate-hint {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 0.25rem;
  margin-bottom: 0;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.password-toggle-external {
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 0 1rem;
  cursor: pointer;
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.password-toggle-external:hover {
  border-color: #667eea;
  color: #667eea;
  background: #f8fafc;
}

.password-toggle-external:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

/* Password Match Indicator */
.password-match-indicator {
  display: flex;
  align-items: center;
  font-size: 0.78rem;
  font-weight: 600;
  margin-top: 4px;
}

.match-ok {
  color: #16a34a;
  display: flex;
  align-items: center;
  gap: 4px;
}

.match-fail {
  color: #dc2626;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* Password Requirements */
.password-requirements {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 0.75rem 1rem;
  margin-top: -0.5rem;
}

.req-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: #64748b;
  margin: 0 0 0.5rem 0;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.req-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.35rem 0.75rem;
}

.req-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.78rem;
  font-weight: 600;
  transition: all 0.25s;
}

.req-met {
  color: #16a34a;
}

.req-unmet {
  color: #94a3b8;
  opacity: 0.6;
}

.btn-submit {
  margin-top: 1.25rem;
  padding: 1rem;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 1rem;
  font-weight: 800;
  font-size: 1.125rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  transition: all 0.2s;
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 20px 25px -5px rgba(102, 126, 234, 0.4);
}

.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.message {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 600;
  white-space: pre-line;
}

.message.error {
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fee2e2;
}
.message.success {
  background: #f0fdf4;
  color: #166534;
  border: 1px solid #dcfce7;
}

.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-float {
  animation: floatIcon 3s ease-in-out infinite;
}
@keyframes floatIcon {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}
</style>
