<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'
import axios from 'axios'

const authStore = useAuthStore()
const router = useRouter()
const userStats = ref(null)

const fetchUserStats = async () => {
  if (!authStore.token) return
  try {
    const res = await axios.get('http://localhost:5000/api/me', {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    userStats.value = res.data
  } catch (err) {
    console.error("Failed to load user stats", err)
  }
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}

onMounted(() => {
  fetchUserStats()
})
</script>

<template>
  <div class="ide-container" v-if="authStore.token">
    <aside class="sidebar">
      <div class="sidebar-logo">WQ BRAIN</div>
      <nav class="sidebar-nav">
        <router-link to="/" active-class="active" exact><span class="icon">⛭</span> Simulate</router-link>
        <router-link to="/results" active-class="active"><span class="icon">Σ</span> Old Results</router-link>
        <router-link to="/vault" active-class="active"><span class="icon">🏛️</span> Vault</router-link>
        <router-link to="/data-explorer" active-class="active"><span class="icon">📊</span> Data</router-link>
        <router-link to="/labs" active-class="active"><span class="icon">🔬</span> Labs</router-link>
        <router-link to="/ai-settings" active-class="active"><span class="icon">💡</span> AI Settings</router-link>
        <a href="#"><span class="icon">🏆</span> Competitions (6)</a>
        <a href="#"><span class="icon">👥</span> Community</a>
      </nav>
      <div class="sidebar-bottom">
        <a href="#"><span class="icon">🎁</span> Refer a friend</a>
      </div>
    </aside>
    <div class="main-column">
      <header class="topnav">
        <div class="nav-links">
          <router-link to="/">Dashboard</router-link>
          <router-link to="/data-explorer">Data Explorer</router-link>
          <a href="#">Courses</a>
          <a href="#">Documentation</a>
          <a href="#">Operators</a>
          <a href="#">FAQ</a>
          <a href="#">Events</a>
          <a href="#">Glossary</a>
        </div>
        <div class="user-menu">
          <div v-if="userStats" class="user-stats">
            <span class="score-badge">Points: {{ userStats.points }}</span>
            <span class="rank-badge">Rank: {{ userStats.rank }}</span>
          </div>
          <a href="#">🔔 Notifications</a>
          <a href="#">👤 {{ userStats ? userStats.username : 'User menu' }}</a>
          <a href="#" @click.prevent="logout" class="logout-link">Logout</a>
        </div>
      </header>
      <main class="ide-workspace">
        <router-view></router-view>
      </main>
    </div>
  </div>
  <div class="login-layout" v-else>
    <router-view></router-view>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Fira+Code:wght@400;600&display=swap');

:root {
  --bg-primary: #0a0e17; /* Exact WQ Brain base background */
  --bg-secondary: #121826; /* Panel background */
  --bg-tertiary: #1c2333;
  --border-color: #2a3441;
  --accent-color: #59cdd5; /* WQ Brain primary cyan */
  --accent-hover: #4fb6f5;
  --text-primary: #eaecf0;
  --text-secondary: #8b96a5;
  --success-color: #47b74a;
  --danger-color: #e05153;
}

body {
  margin: 0;
  padding: 0;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: 'Plus Jakarta Sans', sans-serif;
  height: 100vh;
  overflow: hidden;
}

.login-layout {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at top left, #121826, #0a0e17, #0a0e17);
}

.ide-container {
  display: flex;
  height: 100vh;
  width: 100vw;
}

.sidebar {
  width: 240px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
}

.sidebar-logo {
  height: 60px;
  display: flex;
  align-items: center;
  padding-left: 20px;
  font-weight: 700;
  font-size: 1.2rem;
  color: var(--accent-color);
  border-bottom: 1px solid var(--border-color);
  letter-spacing: 1px;
}

.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 15px 0;
}

.sidebar-nav a, .sidebar-bottom a {
  padding: 12px 20px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.2s;
  font-weight: 500;
}

.sidebar-nav a .icon, .sidebar-bottom a .icon {
  font-size: 1.1rem;
  width: 20px;
  text-align: center;
}

.sidebar-nav a:hover, .sidebar-bottom a:hover {
  background: rgba(89, 205, 213, 0.05);
  color: var(--text-primary);
}

.sidebar-nav a.active {
  background: rgba(89, 205, 213, 0.1);
  color: var(--accent-color);
  border-left: 3px solid var(--accent-color);
}

.sidebar-bottom {
  padding-bottom: 15px;
  border-top: 1px solid var(--border-color);
}

.main-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.topnav {
  height: 60px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.nav-links, .user-menu {
  display: flex;
  gap: 20px;
  align-items: center;
}


.topnav a {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  transition: color 0.2s;
}

.topnav a:hover {
  color: var(--text-primary);
}

.topnav a.router-link-exact-active {
  color: var(--accent-color);
}

.user-stats {
  display: flex;
  gap: 10px;
  align-items: center;
}

.score-badge, .rank-badge {
  background: rgba(89, 205, 213, 0.1);
  border: 1px solid var(--accent-color);
  color: var(--accent-color);
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
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
