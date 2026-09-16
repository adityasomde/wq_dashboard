<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const errorMsg = ref('')
const biometricsUrl = ref('')
const savedEmail = ref('')
import axios from 'axios'

onMounted(async () => {
  const res = await authStore.checkSavedCredentials()
  if (res.exists) {
    savedEmail.value = res.email
  }
})

const handleLoginSaved = async () => {
  errorMsg.value = ''
  biometricsUrl.value = ''
  const result = await authStore.loginSaved()
  if (result.success) {
    router.push('/')
  } else {
    if (result.isBiometrics) {
      biometricsUrl.value = result.url
    } else {
      errorMsg.value = result.error
    }
  }
}

const handleLogin = async () => {
  errorMsg.value = ''
  biometricsUrl.value = ''
  const result = await authStore.login(email.value, password.value)
  if (result.success) {
    router.push('/')
  } else {
    if (result.isBiometrics) {
      biometricsUrl.value = result.url
    } else {
      errorMsg.value = result.error
    }
  }
}

const completeBiometrics = async () => {
  try {
    const res = await axios.post('http://localhost:5000/api/login/biometrics', { email: email.value })
    authStore.token = res.data.token
    localStorage.setItem('token', authStore.token)
    router.push('/')
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Biometrics completion failed'
  }
}
</script>

<template>
  <div class="login-container glass-panel">
    <h2>Platform Access</h2>
    <form v-if="!biometricsUrl" @submit.prevent="handleLogin">
      <div class="form-group">
        <label>Email</label>
        <input type="email" v-model="email" class="glass-input" required />
      </div>
      <div class="form-group">
        <label>Password</label>
        <input type="password" v-model="password" class="glass-input" required />
      </div>
      <button type="submit" class="action-btn">Login</button>
      
      <div v-if="savedEmail" class="saved-creds">
        <div class="divider"><span>OR</span></div>
        <p class="saved-text">Saved credentials found for <span class="highlight">{{ savedEmail }}</span></p>
        <button type="button" @click="handleLoginSaved" class="action-btn saved-btn">Secure Auto-Login</button>
      </div>
      
      <p v-if="errorMsg" class="error-msg" v-html="errorMsg"></p>
    </form>
    
    <div v-else class="biometrics-panel">
      <h3><span class="pulse-dot"></span> Biometrics Required</h3>
      <p>Please click the link below, complete the facial scan in the new tab, and then click "I have completed the scan".</p>
      <a :href="biometricsUrl" target="_blank" class="bio-link">Open Biometrics Scanner</a>
      <button @click="completeBiometrics" class="action-btn success-btn">I have completed the scan</button>
      <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
      <button @click="biometricsUrl = ''" class="action-btn cancel-btn">Back to Login</button>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  max-width: 420px;
  margin: 80px auto;
  padding: 40px;
  text-align: center;
}

h2 {
  margin-bottom: 30px;
  color: #fff;
  font-weight: 300;
  letter-spacing: 2px;
}

h3 {
  color: var(--accent-color);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.form-group {
  margin-bottom: 25px;
  text-align: left;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: var(--text-secondary);
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.glass-input {
  width: 100%;
  padding: 12px 15px;
  box-sizing: border-box;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: #fff;
  font-size: 1rem;
  transition: all 0.3s;
  outline: none;
}

.glass-input:focus {
  border-color: var(--accent-color);
  box-shadow: 0 0 10px rgba(0, 242, 254, 0.2);
}

.action-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(45deg, var(--accent-color), var(--accent-hover));
  color: #000;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  margin-top: 10px;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 242, 254, 0.4);
}

.divider {
  display: flex;
  align-items: center;
  text-align: center;
  margin: 30px 0;
}
.divider::before, .divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid var(--glass-border);
}
.divider span {
  padding: 0 10px;
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.saved-text {
  margin-bottom: 15px;
  color: var(--text-secondary);
}

.highlight {
  color: var(--accent-color);
  font-weight: 600;
}

.saved-btn {
  background: linear-gradient(45deg, #11998e, #38ef7d);
  color: #fff;
}

.saved-btn:hover {
  box-shadow: 0 5px 15px rgba(56, 239, 125, 0.4);
}

.error-msg {
  color: #ff4b4b;
  margin-top: 20px;
  padding: 10px;
  background: rgba(255, 75, 75, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(255, 75, 75, 0.3);
}

.bio-link {
  display: inline-block;
  margin: 20px 0;
  color: var(--accent-color);
  font-weight: 600;
  text-decoration: none;
  padding: 10px 20px;
  border: 1px dashed var(--accent-color);
  border-radius: 8px;
}

.bio-link:hover {
  background: rgba(0, 242, 254, 0.1);
}

.cancel-btn {
  background: transparent;
  border: 1px solid var(--glass-border);
  color: var(--text-secondary);
  margin-top: 15px;
}

.cancel-btn:hover {
  background: rgba(255,255,255,0.05);
  color: #fff;
  box-shadow: none;
}

.pulse-dot {
  width: 10px;
  height: 10px;
  background-color: var(--accent-color);
  border-radius: 50%;
  box-shadow: 0 0 0 0 rgba(0, 242, 254, 0.7);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 242, 254, 0.7); }
  70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(0, 242, 254, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 242, 254, 0); }
}
</style>
