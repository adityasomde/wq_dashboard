<script setup>
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="app-container">
    <nav v-if="authStore.token" class="navbar glass-panel">
      <div class="brand">WorldQuant BRAIN</div>
      <div class="links">
        <router-link to="/">Dashboard</router-link>
        <router-link to="/results">Results</router-link>
        <a href="#" @click.prevent="logout" class="logout-link">Logout</a>
      </div>
    </nav>
    <main>
      <router-view></router-view>
    </main>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

:root {
  --bg-gradient: radial-gradient(circle at top left, #1a1a2e, #16213e, #0f3460, #1a1a2e);
  --glass-bg: rgba(255, 255, 255, 0.05);
  --glass-border: rgba(255, 255, 255, 0.1);
  --glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  --accent-color: #00f2fe;
  --accent-hover: #4facfe;
  --text-primary: #ffffff;
  --text-secondary: #a0aab2;
}

body {
  margin: 0;
  padding: 0;
  background: var(--bg-gradient);
  background-attachment: fixed;
  color: var(--text-primary);
  font-family: 'Inter', sans-serif;
  min-height: 100vh;
}

.app-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 20px;
}

.glass-panel {
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border);
  box-shadow: var(--glass-shadow);
  border-radius: 16px;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 30px;
  margin-bottom: 40px;
}

.brand {
  font-weight: 700;
  font-size: 1.2rem;
  letter-spacing: 1px;
  color: var(--accent-color);
  text-transform: uppercase;
  text-shadow: 0 0 10px rgba(0, 242, 254, 0.5);
}

.links {
  display: flex;
  gap: 20px;
  align-items: center;
}

.navbar a {
  text-decoration: none;
  color: var(--text-secondary);
  font-weight: 600;
  transition: all 0.3s ease;
}

.navbar a:hover {
  color: var(--text-primary);
  text-shadow: 0 0 8px rgba(255,255,255,0.5);
}

.navbar a.router-link-exact-active {
  color: var(--accent-color);
}

.logout-link {
  padding: 6px 12px;
  border: 1px solid rgba(255, 75, 75, 0.3);
  border-radius: 8px;
  background: rgba(255, 75, 75, 0.1);
  color: #ff4b4b !important;
}

.logout-link:hover {
  background: rgba(255, 75, 75, 0.2);
  box-shadow: 0 0 12px rgba(255, 75, 75, 0.4);
}
</style>
