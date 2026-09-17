<script setup>
import { ref, onMounted, defineEmits } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const results = ref([])
const loading = ref(true)
const error = ref('')

const emit = defineEmits(['load-alpha'])

const handleRowClick = (res) => {
  emit('load-alpha', res)
}

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
  <div class="results-terminal">
    <div class="results-toolbar">
      <button @click="fetchResults" class="refresh-btn">
        <span class="icon">⟳</span> Refresh Results
      </button>
      <span v-if="loading" class="loading-text">Querying database...</span>
      <span v-if="error" class="error-msg">{{ error }}</span>
    </div>
    
    <div class="table-container" v-if="!loading && !error">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Parent</th>
            <th>Code Logic</th>
            <th>IS Sharpe</th>
            <th>OS Sharpe</th>
            <th>Fitness</th>
            <th>Turnover</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="res in results" :key="res.id" :class="{ 'row-passed': res.passed_threshold, 'clickable-row': true }" @click="handleRowClick(res)">
            <td>#{{ res.id }}</td>
            <td><span v-if="res.parent_id" class="badge">#{{ res.parent_id }}</span><span v-else>---</span></td>
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
.results-terminal {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.results-toolbar {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px 20px;
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 1px solid var(--border-color);
}

.refresh-btn {
  background: rgba(89, 205, 213, 0.1);
  border: 1px solid var(--accent-color);
  color: var(--accent-color);
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.refresh-btn:hover {
  background: rgba(89, 205, 213, 0.2);
}

.table-container {
  flex: 1;
  overflow-y: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

th {
  padding: 10px 20px;
  color: var(--text-secondary);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  background: var(--bg-primary);
  z-index: 10;
}

td {
  padding: 12px 20px;
  border-bottom: 1px solid var(--border-color);
  vertical-align: middle;
}

tr {
  transition: background-color 0.2s;
}

tr.clickable-row {
  cursor: pointer;
}

tr.clickable-row:hover {
  background: var(--bg-secondary);
  box-shadow: inset 2px 0 0 var(--accent-color);
}

.code-cell {
  font-family: 'Fira Code', monospace;
  font-size: 0.8rem;
  color: var(--text-secondary);
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.metric {
  font-family: 'Fira Code', monospace;
  font-size: 0.9rem;
}

.metric.good { color: var(--success-color); }
.metric.bad { color: var(--danger-color); }

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 600;
}

.badge-pass {
  background: rgba(71, 183, 74, 0.1);
  color: var(--success-color);
  border: 1px solid rgba(71, 183, 74, 0.3);
}

.badge-fail {
  background: rgba(224, 81, 83, 0.1);
  color: var(--danger-color);
  border: 1px solid rgba(224, 81, 83, 0.3);
}

.error-msg {
  color: var(--danger-color);
  font-size: 0.85rem;
}

.loading-text {
  color: var(--accent-color);
  font-size: 0.85rem;
  animation: pulse 1.5s infinite;
}
</style>
