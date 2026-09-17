<template>
  <div class="data-explorer">
    <div class="toolbar">
      <h2>Data Explorer</h2>
      <div class="filters">
        <select v-model="scope.region" @change="fetchFields">
          <option>USA</option><option>EUR</option><option>ASI</option><option>GLO</option>
        </select>
        <select v-model="scope.universe" @change="fetchFields">
          <option>TOP3000</option><option>TOP2000</option><option>TOP1000</option><option>TOP200</option>
        </select>
        <input type="text" v-model="search" placeholder="Search fields..." @keyup.enter="fetchFields" />
        <button @click="fetchFields">Search</button>
      </div>
    </div>
    
    <div v-if="loading" class="loading">Loading data fields...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="table-container">
      <table>
        <thead>
          <tr>
            <th>Field ID</th>
            <th>Description</th>
            <th>Type</th>
            <th>Category</th>
            <th>Dataset</th>
            <th>Coverage</th>
            <th>Alpha Count</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="field in fields" :key="field.field_id">
            <td class="field-id">{{ field.field_id }}</td>
            <td class="desc" :title="field.description">{{ field.description }}</td>
            <td><span class="badge">{{ field.field_type }}</span></td>
            <td>{{ field.category_name }}</td>
            <td>{{ field.dataset_id }}</td>
            <td>{{ (field.coverage * 100).toFixed(1) }}%</td>
            <td>{{ field.alpha_count }}</td>
          </tr>
        </tbody>
      </table>
      <div class="pagination">
        Showing {{ fields.length }} of {{ total }} fields.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'

const scope = reactive({
  region: 'USA',
  delay: 1,
  universe: 'TOP3000',
  instrumentType: 'EQUITY'
})

const search = ref('')
const fields = ref([])
const total = ref(0)
const loading = ref(true)
const error = ref('')

const fetchFields = async () => {
  loading.value = true
  error.value = ''
  try {
    const qs = `?region=${scope.region}&delay=${scope.delay}&universe=${scope.universe}&instrumentType=${scope.instrumentType}`
    const payload = search.value ? { search: search.value, limit: 100, offset: 0 } : { limit: 100, offset: 0 }
    
    // We hit the Flask proxy route which forwards to alpha-harness
    const res = await axios.post(`http://localhost:5000/api/ah/catalog/fields${qs}`, payload)
    
    fields.value = res.data.results || []
    total.value = res.data.total || 0
  } catch (err) {
    error.value = 'Failed to fetch fields from catalog proxy.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchFields()
})
</script>

<style scoped>
.data-explorer {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.toolbar {
  padding: 20px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar h2 {
  margin: 0;
  font-size: 1.2rem;
  color: var(--accent-color);
}

.filters {
  display: flex;
  gap: 10px;
}

.filters select, .filters input {
  padding: 6px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  border-radius: 4px;
}

.filters button {
  padding: 6px 16px;
  background: var(--accent-color);
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.table-container {
  flex: 1;
  overflow: auto;
  padding: 20px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  text-align: left;
  padding: 10px;
  border-bottom: 2px solid var(--border-color);
  color: var(--text-secondary);
  font-size: 0.85rem;
  text-transform: uppercase;
}

td {
  padding: 12px 10px;
  border-bottom: 1px solid var(--border-color);
  font-size: 0.9rem;
}

.field-id {
  font-family: 'Fira Code', monospace;
  color: var(--accent-color);
}

.desc {
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.badge {
  background: rgba(88, 166, 255, 0.1);
  color: var(--accent-color);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
}

.loading, .error {
  padding: 40px;
  text-align: center;
  color: var(--text-secondary);
}

.pagination {
  margin-top: 20px;
  font-size: 0.85rem;
  color: var(--text-secondary);
}
</style>
