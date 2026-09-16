<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const results = ref([])
const loading = ref(true)
const error = ref('')

const fetchResults = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/results', {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    results.value = res.data
  } catch (err) {
    error.value = 'Failed to load results.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchResults()
})
</script>

<template>
  <div class="results glass-panel">
    <div class="results-header">
      <h2>Simulation Results Engine</h2>
      <button @click="fetchResults" class="refresh-btn">⟳ Refresh</button>
    </div>
    <p v-if="loading" class="loading-text">Querying database...</p>
    <p v-if="error" class="error-msg">{{ error }}</p>
    
    <div class="table-container" v-if="!loading && !error">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Code Logic</th>
            <th>IS Sharpe</th>
            <th>OS Sharpe</th>
            <th>Fitness</th>
            <th>Turnover</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="res in results" :key="res.id" :class="{ 'row-passed': res.passed_threshold }">
            <td>#{{ res.id }}</td>
            <td class="code-cell">{{ res.expression_string }}</td>
            <td class="metric">{{ res.is_sharpe?.toFixed(2) ?? '---' }}</td>
            <td class="metric" :class="{'good': res.os_sharpe > 1, 'bad': res.os_sharpe < 0}">{{ res.os_sharpe?.toFixed(2) ?? '---' }}</td>
            <td class="metric">{{ res.fitness?.toFixed(2) ?? '---' }}</td>
            <td class="metric">{{ res.turnover?.toFixed(4) ?? '---' }}</td>
            <td>
              <span class="badge" :class="res.passed_threshold ? 'badge-pass' : 'badge-fail'">
                {{ res.passed_threshold ? 'PASSED' : 'REJECTED' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.results {
  padding: 30px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

h2 {
  margin: 0;
  color: #fff;
  font-weight: 300;
  letter-spacing: 1px;
}

.refresh-btn {
  background: rgba(0, 242, 254, 0.1);
  border: 1px solid var(--accent-color);
  color: var(--accent-color);
  padding: 8px 15px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn:hover {
  background: rgba(0, 242, 254, 0.2);
  box-shadow: 0 0 10px rgba(0, 242, 254, 0.3);
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

th {
  padding: 15px;
  color: var(--text-secondary);
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  border-bottom: 1px solid var(--glass-border);
  white-space: nowrap;
}

td {
  padding: 15px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  vertical-align: middle;
}

tr {
  transition: background-color 0.2s;
}

tr:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.code-cell {
  font-family: monospace;
  font-size: 0.85rem;
  color: #a0aab2;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.metric {
  font-family: monospace;
  font-size: 1rem;
}

.metric.good { color: #38ef7d; }
.metric.bad { color: #ff4b4b; }

.badge {
  padding: 5px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-pass {
  background: rgba(56, 239, 125, 0.1);
  color: #38ef7d;
  border: 1px solid rgba(56, 239, 125, 0.3);
}

.badge-fail {
  background: rgba(255, 75, 75, 0.1);
  color: #ff4b4b;
  border: 1px solid rgba(255, 75, 75, 0.3);
}

.error-msg {
  color: #ff4b4b;
}
.loading-text {
  color: var(--accent-color);
  animation: pulse 1.5s infinite;
}
</style>
