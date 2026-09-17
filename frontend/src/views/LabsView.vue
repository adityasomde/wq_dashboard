<template>
  <div class="labs-view">
    <div class="header">
      <h2>Research Labs</h2>
      <p>Automated AI workflows to generate, repair, and optimize alphas.</p>
    </div>

    <div class="content">
      <div class="panel">
        <h3>Search Lab</h3>
        <p class="desc">Automatically searches datasets for alpha combinations using genetic algorithms.</p>
        
        <div class="form-group">
          <label>Region</label>
          <select v-model="searchConfig.region">
            <option>USA</option><option>EUR</option><option>ASI</option>
          </select>
        </div>
        <div class="form-group">
          <label>Delay</label>
          <select v-model="searchConfig.delay">
            <option :value="1">1</option><option :value="0">0</option>
          </select>
        </div>
        <div class="form-group">
          <label>Universe</label>
          <input type="text" v-model="searchConfig.universe" placeholder="e.g. TOP3000" />
        </div>
        <div class="form-group">
          <label>Dataset IDs (Comma separated)</label>
          <input type="text" v-model="searchConfig.dataset_ids" placeholder="e.g. model76" />
        </div>
        <div class="form-group">
          <label>Simulations (Target)</label>
          <input type="number" v-model="searchConfig.simulations" />
        </div>
        <div class="form-group">
          <label>Cores</label>
          <input type="number" v-model="searchConfig.cores" />
        </div>

        <button class="btn-primary" @click="startSearchLab" :disabled="loading">Start Search Task</button>
        <div v-if="successMsg" class="success">{{ successMsg }}</div>
        <div v-if="errorMsg" class="error">{{ errorMsg }}</div>
      </div>

      <div class="panel">
        <h3>Active Tasks</h3>
        <div class="tasks-list" v-if="tasks && tasks.running && tasks.running.length > 0">
          <div v-for="task in tasks.running" :key="task.id" class="task-item">
            <div class="task-title">{{ task.title }}</div>
            <div class="task-status">Status: {{ task.status }} | Progress: {{ Math.round(task.progress * 100) }}%</div>
          </div>
        </div>
        <div v-else class="empty-state">
          No tasks currently running.
        </div>
        <button class="btn-small mt" @click="fetchTasks">Refresh Tasks</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const searchConfig = ref({
  region: 'USA',
  delay: 1,
  universe: 'TOP3000',
  dataset_ids: '',
  simulations: 100,
  cores: 4
})

const loading = ref(false)
const successMsg = ref('')
const errorMsg = ref('')
const tasks = ref(null)

const startSearchLab = async () => {
  loading.value = true
  successMsg.value = ''
  errorMsg.value = ''
  
  try {
    const payload = {
      ...searchConfig.value,
      dataset_ids: searchConfig.value.dataset_ids.split(',').map(s => s.trim()).filter(Boolean)
    }
    const res = await axios.post('http://localhost:5000/api/ah/search-lab/tasks', payload)
    successMsg.value = `Task Started! ID: ${res.data.id}`
    fetchTasks()
  } catch (err) {
    errorMsg.value = err.response?.data?.error?.message || err.response?.data?.detail?.message || 'Failed to start lab.'
  } finally {
    loading.value = false
  }
}

const fetchTasks = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/ah/tasks')
    tasks.value = res.data
  } catch (err) {
    console.error("Failed to fetch tasks", err)
  }
}

let interval = null
onMounted(() => {
  fetchTasks()
  interval = setInterval(fetchTasks, 5000)
})
</script>

<style scoped>
.labs-view {
  padding: 20px;
  background: var(--bg-primary);
  height: 100%;
  overflow: auto;
}

.header {
  margin-bottom: 30px;
}

.header h2 {
  color: var(--accent-color);
  margin-bottom: 5px;
}

.content {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.panel {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 20px;
  flex: 1;
  max-width: 500px;
}

.mt {
  margin-top: 20px;
}

h3 {
  margin-top: 0;
  margin-bottom: 5px;
  color: var(--text-primary);
}

.desc {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 10px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.form-group input, .form-group select {
  width: 100%;
  padding: 8px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  border-radius: 4px;
}

.btn-primary {
  background: var(--accent-color);
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  width: 100%;
}
.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.success { color: var(--success-color); margin-top: 10px; text-align: center;}
.error { color: var(--danger-color); margin-top: 10px; text-align: center;}

.task-item {
  background: rgba(255, 255, 255, 0.05);
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 10px;
}

.task-title {
  font-weight: 600;
  color: var(--accent-color);
  margin-bottom: 4px;
}

.task-status {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.btn-small {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
}
.empty-state {
  text-align: center;
  color: var(--text-secondary);
  font-style: italic;
  padding: 20px !important;
}
</style>
