<template>
  <div class="vault-view">
    <div class="header">
      <h2>Alpha Vault</h2>
      <p>Synchronize and manage all your historical alphas from WorldQuant Brain.</p>
    </div>

    <div class="actions-bar">
      <button class="btn-primary" @click="syncAlphas" :disabled="syncing">
        {{ syncing ? 'Syncing...' : 'Sync from BRAIN' }}
      </button>
      <div v-if="syncTask" class="sync-status">
        Sync Task ID: {{ syncTask }} is running in the background. Check Labs Monitor for progress.
      </div>
    </div>

    <div class="content">
      <div class="filters">
        <input type="text" v-model="filters.search" placeholder="Search expression..." @keyup.enter="loadAlphas" />
        <select v-model="filters.sort_by" @change="loadAlphas">
          <option value="date_created">Date Created</option>
          <option value="sharpe">Out of Sample Sharpe</option>
          <option value="fitness">Fitness</option>
        </select>
        <button class="btn-secondary" @click="loadAlphas">Apply</button>
      </div>

      <div v-if="loading" class="loading">Loading vault...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else class="table-container">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Expression</th>
              <th>Region</th>
              <th>Universe</th>
              <th>IS Sharpe</th>
              <th>OS Sharpe</th>
              <th>Fitness</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="alpha in alphas" :key="alpha.id" class="alpha-row">
              <td class="alpha-id">{{ alpha.id }}</td>
              <td class="expr" :title="alpha.expression">{{ alpha.expression }}</td>
              <td>{{ alpha.region }} (D{{ alpha.delay }})</td>
              <td>{{ alpha.universe }}</td>
              <td :class="getValColor(alpha.is_sharpe)">{{ alpha.is_sharpe?.toFixed(2) || '-' }}</td>
              <td :class="getValColor(alpha.os_sharpe)">{{ alpha.os_sharpe?.toFixed(2) || '-' }}</td>
              <td :class="getValColor(alpha.fitness)">{{ alpha.fitness?.toFixed(2) || '-' }}</td>
              <td>{{ formatDate(alpha.date_created) }}</td>
            </tr>
            <tr v-if="alphas.length === 0">
              <td colspan="8" class="empty-state">No alphas found. Try syncing from BRAIN.</td>
            </tr>
          </tbody>
        </table>
        
        <div class="pagination">
          <button class="btn-small" @click="prevPage" :disabled="filters.offset === 0">Previous</button>
          <span>Showing {{ alphas.length }} alphas (Total matches: {{ total }})</span>
          <button class="btn-small" @click="nextPage" :disabled="alphas.length < filters.limit">Next</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const alphas = ref([])
const total = ref(0)
const loading = ref(false)
const error = ref('')
const syncing = ref(false)
const syncTask = ref(null)

const filters = ref({
  search: '',
  sort_by: 'date_created',
  sort_desc: true,
  limit: 100,
  offset: 0
})

const loadAlphas = async () => {
  loading.value = true
  error.value = ''
  try {
    const payload = { ...filters.value }
    if (!payload.search) delete payload.search
    
    const res = await axios.post('http://localhost:5000/api/ah/vault/alphas/query', payload)
    alphas.value = res.data.results || []
    total.value = res.data.total || 0
  } catch (err) {
    error.value = 'Failed to load alphas from Vault.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const syncAlphas = async () => {
  syncing.value = true
  try {
    const res = await axios.post('http://localhost:5000/api/ah/vault/sync')
    syncTask.value = res.data.taskId
  } catch (err) {
    console.error("Failed to start sync", err)
    alert("Failed to start sync: " + (err.response?.data?.detail?.message || err.message))
  } finally {
    syncing.value = false
  }
}

const nextPage = () => {
  filters.value.offset += filters.value.limit
  loadAlphas()
}

const prevPage = () => {
  filters.value.offset = Math.max(0, filters.value.offset - filters.value.limit)
  loadAlphas()
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
}

const getValColor = (val) => {
  if (!val) return ''
  if (val > 1.5) return 'val-excellent'
  if (val > 1.0) return 'val-good'
  if (val < 0) return 'val-bad'
  return ''
}

onMounted(() => {
  loadAlphas()
})
</script>

<style scoped>
.vault-view {
  padding: 20px;
  background: var(--bg-primary);
  height: 100%;
  overflow: auto;
  display: flex;
  flex-direction: column;
}

.header {
  margin-bottom: 20px;
}

.header h2 {
  color: var(--accent-color);
  margin-bottom: 5px;
}

.actions-bar {
  display: flex;
  gap: 20px;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
}

.sync-status {
  color: var(--success-color);
  font-size: 0.9rem;
}

.content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.filters {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.filters input, .filters select {
  padding: 8px 12px;
  background: var(--bg-secondary);
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
  font-weight: 600;
}
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-secondary {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-small {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
}

.table-container {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  flex: 1;
  overflow: auto;
  display: flex;
  flex-direction: column;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  text-align: left;
  padding: 12px;
  border-bottom: 2px solid var(--border-color);
  color: var(--text-secondary);
  font-size: 0.85rem;
  background: var(--bg-tertiary);
  position: sticky;
  top: 0;
}

td {
  padding: 12px;
  border-bottom: 1px solid var(--border-color);
  font-size: 0.9rem;
}

.alpha-row:hover {
  background: rgba(255, 255, 255, 0.02);
}

.alpha-id {
  font-family: 'Fira Code', monospace;
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.expr {
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-family: 'Fira Code', monospace;
  color: var(--accent-color);
}

.val-excellent { color: #47b74a; font-weight: 600; }
.val-good { color: #8bc34a; }
.val-bad { color: #e05153; }

.pagination {
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--border-color);
  background: var(--bg-tertiary);
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.empty-state {
  text-align: center;
  padding: 40px !important;
  color: var(--text-secondary);
  font-style: italic;
}
</style>
