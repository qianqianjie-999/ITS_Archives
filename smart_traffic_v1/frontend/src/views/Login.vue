<template>
  <div class="login-container">
    <div class="login-bg">
      <div class="bg-grid"></div>
      <div class="bg-glow bg-glow-1"></div>
      <div class="bg-glow bg-glow-2"></div>
      <div class="bg-particles">
        <div class="particle" v-for="i in 20" :key="i" :style="getParticleStyle(i)"></div>
      </div>
    </div>
    <div class="login-wrapper">
      <div class="login-card">
        <div class="login-header">
          <div class="logo-section">
            <div class="logo-glow"></div>
            <div class="logo-circle">
              <el-icon :size="36" color="#00d4ff"><MapLocation /></el-icon>
            </div>
            <h1 class="system-title">汶上县智能交通档案系统</h1>
            <p class="system-desc">Intelligent Traffic Archive System</p>
          </div>
        </div>

        <el-form ref="formRef" :model="form" :rules="rules" class="login-form">
          <el-form-item prop="username">
            <div class="input-group">
              <el-icon :size="20" class="input-icon"><User /></el-icon>
              <el-input
                v-model="form.username"
                placeholder="请输入用户名"
                :prefix-icon="User"
                size="large"
                class="dark-input"
              />
            </div>
          </el-form-item>

          <el-form-item prop="password">
            <div class="input-group">
              <el-icon :size="20" class="input-icon"><Lock /></el-icon>
              <el-input
                v-model="form.password"
                type="password"
                placeholder="请输入密码"
                :prefix-icon="Lock"
                size="large"
                class="dark-input"
                @keyup.enter="handleLogin"
              />
            </div>
          </el-form-item>

          <el-form-item class="form-options">
            <el-checkbox v-model="rememberMe" class="dark-checkbox">记住我</el-checkbox>
            <a href="#" class="forgot-password">忘记密码？</a>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              :loading="loading"
              style="width: 100%"
              size="large"
              @click="handleLogin"
              class="login-btn"
            >
              <span v-if="!loading">登 录</span>
              <span v-else>登录中...</span>
            </el-button>
          </el-form-item>
        </el-form>

        <div class="login-footer">
          <p>© 2026 汶上县智能交通档案系统. All rights reserved.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { MapLocation, User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const rememberMe = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3-20个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 30, message: '密码长度在6-30个字符之间', trigger: 'blur' }
  ]
}

function getParticleStyle(_index: number) {
  const size = Math.random() * 4 + 2
  const left = Math.random() * 100
  const delay = Math.random() * 5
  const duration = Math.random() * 10 + 10
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${left}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`
  }
}

async function handleLogin() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const success = await userStore.login(form.username, form.password, rememberMe.value)
        if (success) {
          ElMessage.success('登录成功')
          router.push('/')
        } else {
          ElMessage.error('用户名或密码错误')
        }
      } catch (error) {
        ElMessage.error('登录失败，请检查网络连接')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.login-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #141d2d 0%, #1a2335 50%, #1c273d 100%);

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%2300d4ff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  }
}

.bg-grid {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
    linear-gradient(rgba(0, 212, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 212, 255, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
}

.bg-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.5;
}

.bg-glow-1 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(0, 212, 255, 0.15) 0%, transparent 70%);
  top: -200px;
  right: -200px;
  animation: pulse 8s ease-in-out infinite;
}

.bg-glow-2 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(0, 210, 106, 0.1) 0%, transparent 70%);
  bottom: -150px;
  left: -150px;
  animation: pulse 10s ease-in-out infinite reverse;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.1); opacity: 0.7; }
}

.bg-particles {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
}

.particle {
  position: absolute;
  background: $primary-color;
  border-radius: 50%;
  opacity: 0.6;
  animation: float linear infinite;
}

@keyframes float {
  0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
  10% { opacity: 0.6; }
  90% { opacity: 0.6; }
  100% { transform: translateY(-100vh) rotate(720deg); opacity: 0; }
}

.login-wrapper {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 420px;
  padding: $spacing-lg;
}

.login-card {
  background: rgba(17, 24, 39, 0.9);
  backdrop-filter: blur(20px);
  border-radius: $radius-lg;
  padding: $spacing-xl;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(0, 212, 255, 0.1);
  animation: slideUp 0.5s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-header {
  text-align: center;
  margin-bottom: $spacing-xl;
}

.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacing-md;
  position: relative;
}

.logo-glow {
  position: absolute;
  width: 120px;
  height: 120px;
  background: radial-gradient(circle, rgba(0, 212, 255, 0.2) 0%, transparent 70%);
  top: -20px;
  animation: glow-pulse 3s ease-in-out infinite;
}

@keyframes glow-pulse {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.1); }
}

.logo-circle {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #1c273d 0%, #222d42 100%);
  border: 2px solid rgba(0, 212, 255, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 30px rgba(0, 212, 255, 0.3);
  position: relative;
  z-index: 1;

  &::before {
    content: '';
    position: absolute;
    inset: -4px;
    border-radius: 50%;
    background: linear-gradient(135deg, $primary-color, transparent);
    opacity: 0.3;
    z-index: -1;
  }
}

.system-title {
  font-size: 22px;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
  text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
}

.system-desc {
  font-size: 12px;
  color: #64748b;
  margin: 0;
  letter-spacing: 1px;
}

.login-form {
  margin-bottom: $spacing-lg;
}

.input-group {
  position: relative;
}

.input-icon {
  position: absolute;
  left: $spacing-md;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
  z-index: 1;
}

:deep(.dark-input) {
  .el-input__wrapper {
    background-color: #1a2335 !important;
    border: 1px solid #334155 !important;
    padding-left: 40px !important;
    transition: all 0.3s ease;

    &:hover {
      border-color: rgba(0, 212, 255, 0.5) !important;
    }

    &.is-focus {
      border-color: $primary-color !important;
      box-shadow: 0 0 20px rgba(0, 212, 255, 0.2) !important;
    }
  }

  .el-input__inner {
    color: #ffffff !important;

    &::placeholder {
      color: #64748b !important;
    }
  }
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-md;
}

:deep(.dark-checkbox) {
  .el-checkbox__label {
    font-size: $font-size-sm;
    color: #a0aec0;
  }

  .el-checkbox__input.is-checked .el-checkbox__inner {
    background-color: $primary-color;
    border-color: $primary-color;
  }
}

.forgot-password {
  font-size: $font-size-sm;
  color: $primary-color;

  &:hover {
    color: lighten($primary-color, 10%);
    text-decoration: underline;
  }
}

.login-btn {
  height: 48px;
  font-size: $font-size-md;
  font-weight: 600;
  background: linear-gradient(135deg, $primary-color 0%, $primary-dark 100%);
  border: none;
  border-radius: $radius-md;
  letter-spacing: 4px;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 212, 255, 0.4);
  }

  &:active {
    transform: translateY(0);
  }
}

.login-footer {
  text-align: center;
  padding-top: $spacing-lg;
  border-top: 1px solid rgba(255, 255, 255, 0.05);

  p {
    font-size: $font-size-xs;
    color: #475569;
    margin: 0;
  }
}
</style>