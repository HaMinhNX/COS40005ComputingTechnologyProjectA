<template>
  <div class="login-container">
    <!-- Animated Background -->
    <div class="animated-background">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
    </div>

    <!-- Login/Signup Card -->
    <div class="login-card glass-card animate-fade-in">
      <div class="logo-section">
        <div class="logo-icon animate-float">
          <Activity :size="64" color="#667EEA" />
        </div>
        <h1 class="app-name">MEDIC1</h1>
        <p class="app-tagline">Chăm sóc sức khỏe người cao tuổi</p>
      </div>

      <div class="login-form-section">
        <!-- Tab Switcher -->
        <div class="tab-switcher">
          <button @click="isLogin = true" :class="['tab-btn', { active: isLogin }]">
            Đăng nhập
          </button>
          <button @click="isLogin = false" :class="['tab-btn', { active: !isLogin }]">
            Đăng ký
          </button>
        </div>

        <!-- Login Form -->
        <form v-if="isLogin" @submit.prevent="onLogin" class="auth-form">
          <h2 class="form-title">Chào mừng trở lại!</h2>
          <p class="form-subtitle">Đăng nhập để tiếp tục</p>

          <div class="form-group">
            <label class="form-label">Tên đăng nhập</label>
            <div class="input-wrapper">
              <User :size="18" class="input-icon" />
              <input
                v-model="loginForm.username"
                type="text"
                required
                placeholder="Nhập tên đăng nhập"
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
        </form>

        <!-- Signup Form -->
        <form v-else @submit.prevent="onSignup" class="auth-form">
          <h2 class="form-title">Tạo tài khoản mới</h2>
          <p class="form-subtitle">Đăng ký để bắt đầu</p>

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

          <div class="form-group">
            <label class="form-label">Mật khẩu</label>
            <div class="password-input-group">
              <div class="input-wrapper-inner">
                <Lock :size="18" class="input-icon" />
                <input
                  v-model="signupForm.password"
                  :type="showPassword ? 'text' : 'password'"
                  required
                  minlength="6"
                  placeholder="Tối thiểu 6 ký tự"
                  class="form-input with-icon"
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

          <div class="form-group">
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

          <button type="submit" class="btn-submit" :disabled="loading">
            <span v-if="!loading" class="btn-text">Đăng ký</span>
            <span v-else class="btn-text">Đang xử lý...</span>
            <ArrowRight class="btn-icon" :size="20" />
          </button>
        </form>

        <!-- Error/Success Message -->
        <transition name="fade">
          <div v-if="message.text" :class="['message', message.type]">
            <AlertCircle v-if="message.type === 'error'" :size="18" />
            <CheckCircle v-else :size="18" />
            {{ message.text }}
          </div>
        </transition>

        <!-- Demo Accounts (only show in login) -->
        <div v-if="isLogin" class="demo-section">
          <button @click="showDemo = !showDemo" class="demo-toggle-btn">
            <Zap :size="16" />
            {{ showDemo ? 'Ẩn đăng nhập nhanh' : 'Đăng nhập nhanh (Demo)' }}
          </button>

          <transition name="slide-fade">
            <div v-if="showDemo" class="demo-accounts">
              <div class="demo-controls">
                <select v-model="selectedRole" class="demo-select">
                  <option value="doctor">Bác sĩ</option>
                  <option value="patient">Bệnh nhân</option>
                </select>
                <select v-model="selectedDemoUser" @change="fillDemoUser" class="demo-select">
                  <option value="">Chọn tài khoản...</option>
                  <option v-for="user in demoUsers" :key="user.username" :value="user">
                    {{ user.label }}
                  </option>
                </select>
              </div>
            </div>
          </transition>
        </div>
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
  Zap,
} from 'lucide-vue-next'
import { API_BASE_URL } from '../config'

const router = useRouter()
const isLogin = ref(true)
const showDemo = ref(false)
const showPassword = ref(false)
const loading = ref(false)
const message = ref({ text: '', type: '' })

const loginForm = ref({
  username: '',
  password: '',
})

const signupForm = ref({
  username: '',
  password: '',
  full_name: '',
  email: '',
  role: '',
})

const selectedRole = ref('doctor')
const selectedDemoUser = ref('')

const demoUsers = computed(() => {
  if (selectedRole.value === 'doctor') {
    return Array.from({ length: 5 }, (_, i) => ({
      username: `doctor_dummy_${i + 1}`,
      password: '123',
      label: `Bác sĩ Demo ${i + 1}`,
    }))
  } else {
    return Array.from({ length: 10 }, (_, i) => ({
      username: `patient_dummy_${i + 1}`,
      password: '123',
      label: `Bệnh nhân Demo ${i + 1}`,
    }))
  }
})

const fillDemoUser = () => {
  if (selectedDemoUser.value) {
    loginForm.value.username = selectedDemoUser.value.username
    loginForm.value.password = selectedDemoUser.value.password
    // Auto login
    onLogin()
  }
}

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
        // 1. Get raw field name and translate
        let rawField = err.loc ? err.loc[err.loc.length - 1] : 'Lỗi'
        const fieldName = fieldMap[rawField] || rawField

        // 2. Clean up message
        let msg = err.msg

        // Remove "Value error, " prefix from custom validators
        msg = msg.replace(/^Value error,\s*/i, '')

        // 3. Translate specific messages
        // Translate dynamic length errors
        msg = msg.replace(
          /String should have at least (\d+) characters/i,
          'Phải có ít nhất $1 ký tự',
        )
        msg = msg.replace(/String should have at most (\d+) characters/i, 'Không được quá $1 ký tự')

        const lowerMsg = msg.toLowerCase()

        // Standard Pydantic errors
        if (lowerMsg === 'field required') msg = 'Bắt buộc nhập'
        if (lowerMsg.includes('not a valid email')) msg = 'Email không hợp lệ'
        if (lowerMsg.includes('input should be a valid string')) msg = 'Giá trị phải là chuỗi ký tự'

        // Custom password validators
        if (lowerMsg.includes('at least 8 characters')) msg = 'Phải có ít nhất 8 ký tự'
        if (lowerMsg.includes('must contain at least one uppercase letter'))
          msg = 'Phải có ít nhất 1 chữ in hoa'
        if (lowerMsg.includes('must contain at least one lowercase letter'))
          msg = 'Phải có ít nhất 1 chữ thường'
        if (lowerMsg.includes('must contain at least one digit')) msg = 'Phải có ít nhất 1 số'

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

const onSignup = async () => {
  loading.value = true
  message.value = { text: '', type: '' }

  try {
    const res = await fetch(`${API_BASE_URL}/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(signupForm.value),
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

.animated-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  z-index: 0;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.6;
  animation: float 6s ease-in-out infinite;
}

.orb-1 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, #ff6b6b 0%, transparent 70%);
  top: -100px;
  left: -100px;
}
.orb-2 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, #4ecdc4 0%, transparent 70%);
  bottom: -150px;
  right: -150px;
  animation-delay: 2s;
}
.orb-3 {
  width: 350px;
  height: 350px;
  background: radial-gradient(circle, #ffe66d 0%, transparent 70%);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: 4s;
}

@keyframes float {
  0%,
  100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(20px, 20px);
  }
}

.login-card {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 500px;
  padding: 3rem;
  border-radius: 2rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
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

.btn-submit {
  margin-top: 1rem;
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
  box-shadow: 0 10px 15px -3px rgba(102, 126, 234, 0.4);
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 20px 25px -5px rgba(102, 126, 234, 0.4);
}

.btn-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
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

.demo-section {
  margin-top: 2rem;
  text-align: center;
}

.demo-toggle-btn {
  background: none;
  border: none;
  color: #667eea;
  font-weight: 700;
  font-size: 0.875rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  transition: background 0.2s;
}

.demo-toggle-btn:hover {
  background: rgba(102, 126, 234, 0.1);
}

.demo-accounts {
  margin-top: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 1rem;
  border: 1px dashed #cbd5e1;
}

.demo-controls {
  display: flex;
  gap: 0.5rem;
}

.demo-select {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  font-size: 0.875rem;
}

.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease-out;
}
.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
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
