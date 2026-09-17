<template>
  <div class="ai-config-view">
    <div class="header">
      <h2>AI Assistant Configuration</h2>
      <p>Configure API keys for Large Language Models to power the Labs.</p>
    </div>

    <div class="content">
      <div class="panel">
        <h3>Add API Key</h3>
        <div class="form-group">
          <label>Provider</label>
          <select v-model="newKey.provider">
            <option value="google">Google (Gemini)</option>
            <option value="openai">OpenAI (ChatGPT)</option>
            <option value="anthropic">Anthropic (Claude)</option>
            <option value="groq">Groq</option>
            <option value="openrouter">OpenRouter</option>
          </select>
        </div>
        <div class="form-group">
          <label>API Key</label>
          <input type="password" v-model="newKey.key" placeholder="Paste your API key here..." />
        </div>
        <div class="form-group">
          <label>Label (Optional)</label>
          <input type="text" v-model="newKey.label" placeholder="e.g. My Personal Key" />
        </div>
        <button class="btn-primary" @click="saveKey">Save Key</button>
        <div v-if="successMsg" class="success">{{ successMsg }}</div>
        <div v-if="errorMsg" class="error">{{ errorMsg }}</div>
      </div>

      <div class="panel mt">
        <h3>Active Keys</h3>
        <table class="keys-table">
          <thead>
            <tr>
              <th>Provider</th>
              <th>Label</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="key in keys" :key="key.id">
              <td>{{ key.provider }}</td>
              <td>{{ key.label || 'Unnamed' }}</td>
              <td>
                <span class="status-indicator" :class="{ active: key.enabled, disabled: !key.enabled }">
                  {{ key.enabled ? 'Active' : 'Disabled' }}
                </span>
              </td>
              <td>
                <button class="btn-small" @click="toggleKey(key)">{{ key.enabled ? 'Disable' : 'Enable' }}</button>
                <button class="btn-small danger" @click="deleteKey(key.id)">Delete</button>
              </td>
            </tr>
            <tr v-if="keys.length === 0">
              <td colspan="4" class="empty-state">No API keys configured.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const keys = ref([])
const newKey = ref({ provider: 'google', key: '', label: '' })
const successMsg = ref('')
const errorMsg = ref('')

const fetchKeys = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/ah/llm/keys')
    keys.value = res.data.keys || []
  } catch (err) {
    console.error("Failed to fetch LLM keys", err)
  }
}

const saveKey = async () => {
  successMsg.value = ''
  errorMsg.value = ''
  if (!newKey.value.key) {
    errorMsg.value = 'API Key is required.'
    return
  }
  
  try {
    await axios.post('http://localhost:5000/api/ah/llm/keys', newKey.value)
    successMsg.value = 'Key saved successfully!'
    newKey.value.key = ''
    newKey.value.label = ''
    fetchKeys()
  } catch (err) {
    errorMsg.value = err.response?.data?.error?.message || 'Failed to save key.'
  }
}

const toggleKey = async (key) => {
  try {
    await axios.put(`http://localhost:5000/api/ah/llm/keys/${key.id}`, { enabled: !key.enabled })
    fetchKeys()
  } catch (err) {
    console.error("Failed to toggle key", err)
  }
}

const deleteKey = async (id) => {
  if (!confirm("Are you sure you want to delete this key?")) return
  try {
    await axios.delete(`http://localhost:5000/api/ah/llm/keys/${id}`)
    fetchKeys()
  } catch (err) {
    console.error("Failed to delete key", err)
  }
}

onMounted(() => {
  fetchKeys()
})
</script>

<style scoped>
.ai-config-view {
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

.panel {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 20px;
  max-width: 600px;
}

.mt {
  margin-top: 20px;
}

h3 {
  margin-top: 0;
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
}

.success { color: var(--success-color); margin-top: 10px; }
.error { color: var(--danger-color); margin-top: 10px; }

.keys-table {
  width: 100%;
  border-collapse: collapse;
}

.keys-table th {
  text-align: left;
  padding: 10px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.keys-table td {
  padding: 12px 10px;
  border-bottom: 1px solid var(--border-color);
  font-size: 0.9rem;
}

.status-indicator {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
}
.status-indicator.active {
  background: rgba(71, 183, 74, 0.1);
  color: var(--success-color);
}
.status-indicator.disabled {
  background: rgba(224, 81, 83, 0.1);
  color: var(--danger-color);
}

.btn-small {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  margin-right: 5px;
}
.btn-small.danger {
  border-color: var(--danger-color);
  color: var(--danger-color);
}
.empty-state {
  text-align: center;
  color: var(--text-secondary);
  font-style: italic;
  padding: 20px !important;
}
</style>
