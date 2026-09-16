<script setup>
import { ref, onUnmounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const message = ref('')
const currentTaskState = ref('')
const currentTaskStatus = ref('')

let pollInterval = null

const triggerSimulation = async () => {
  try {
    const res = await axios.post('http://localhost:5000/api/simulate', {}, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    message.value = res.data.message
    const taskId = res.data.task_id
    startPolling(taskId)
  } catch (error) {
    message.value = 'Failed to trigger simulation'
  }
}

const startPolling = (taskId) => {
  if (pollInterval) clearInterval(pollInterval)
  
  pollInterval = setInterval(async () => {
    try {
      const res = await axios.get(`http://localhost:5000/api/task/${taskId}`, {
        headers: { Authorization: `Bearer ${authStore.token}` }
      })
      currentTaskState.value = res.data.state
      currentTaskStatus.value = res.data.status
      
      if (res.data.state === 'SUCCESS' || res.data.state === 'FAILURE') {
        clearInterval(pollInterval)
      }
    } catch (err) {
      console.error(err)
      clearInterval(pollInterval)
    }
  }, 2000)
}

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})
</script>

<template>
  <div class="dashboard">
    <div class="control-panel glass-panel">
      <div class="panel-header">
        <h2>Simulation Engine</h2>
        <span class="badge ready">Ready</span>
      </div>
      <p class="panel-desc">Deploy your generated Python Alpha into the WorldQuant BRAIN pipeline. This will run Celery asynchronously.</p>
      <button @click="triggerSimulation" class="action-btn">
        <span class="btn-icon">🚀</span> Launch Simulation
      </button>
      <p v-if="message" class="system-msg">{{ message }}</p>
    </div>
    
    <div v-if="currentTaskState" class="status-panel glass-panel" :class="{'is-running': currentTaskState === 'PENDING' || currentTaskState === 'STARTED'}">
      <h3>
        <span class="pulse-dot" v-if="currentTaskState !== 'SUCCESS' && currentTaskState !== 'FAILURE'"></span> 
        Live Telemetry
      </h3>
      <div class="telemetry-grid">
        <div class="t-card">
          <span class="t-label">Task State</span>
          <span class="t-value" :class="currentTaskState.toLowerCase()">{{ currentTaskState }}</span>
        </div>
        <div class="t-card">
          <span class="t-label">Detailed Status</span>
          <span class="t-value detail">{{ currentTaskStatus }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.control-panel, .status-panel {
  padding: 30px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.panel-header h2 {
  margin: 0;
  color: #fff;
  font-weight: 300;
  letter-spacing: 1px;
}

.badge {
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}
.badge.ready {
  background: rgba(56, 239, 125, 0.2);
  color: #38ef7d;
  border: 1px solid rgba(56, 239, 125, 0.4);
}

.panel-desc {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 25px;
}

.action-btn {
  background: linear-gradient(45deg, #11998e, #38ef7d);
  color: #000;
  border: none;
  border-radius: 8px;
  padding: 15px 30px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 10px;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(56, 239, 125, 0.3);
}

.system-msg {
  margin-top: 15px;
  color: var(--accent-color);
}

/* Status Panel */
.status-panel {
  transition: box-shadow 0.5s ease;
}
.status-panel.is-running {
  box-shadow: 0 0 20px rgba(0, 242, 254, 0.2), inset 0 0 10px rgba(0, 242, 254, 0.1);
  border-color: rgba(0, 242, 254, 0.3);
}

.status-panel h3 {
  color: #fff;
  font-weight: 300;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 0;
  margin-bottom: 25px;
}

.telemetry-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.t-card {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.t-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.t-value {
  font-size: 1.2rem;
  font-weight: 600;
}
.t-value.detail {
  font-family: monospace;
  color: #a0aab2;
  word-break: break-all;
}

.success { color: #38ef7d; }
.failure { color: #ff4b4b; }
.pending, .started { color: var(--accent-color); }

.pulse-dot {
  width: 12px;
  height: 12px;
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
