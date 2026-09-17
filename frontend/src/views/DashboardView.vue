<template>
  <div class="dashboard-ide">
    <!-- Top Action Bar -->
    <div class="ide-topbar">
      <div class="selector-group">
        <label>Type</label>
        <select v-model="settings.type">
          <option>REGULAR</option>
          <option>SUPER</option>
        </select>
      </div>
      <div class="selector-group">
        <label>Region</label>
        <select v-model="settings.region" v-if="schema.region?.choices" :disabled="schema.region.blocked">
          <option v-for="c in schema.region.choices" :key="c.value" :value="c.value">{{ c.label || c.value }}</option>
        </select>
        <select v-else v-model="settings.region"><option>USA</option></select>
      </div>
      <div class="selector-group">
        <label>Universe</label>
        <select v-model="settings.universe" v-if="schema.universe?.choices" :disabled="schema.universe.blocked">
          <option v-for="c in schema.universe.choices" :key="c.value" :value="c.value">{{ c.label || c.value }}</option>
        </select>
        <select v-else v-model="settings.universe"><option>TOP3000</option></select>
      </div>
      <div class="selector-group">
        <label>Dataset</label>
        <select>
          <option>Fundamental</option>
        </select>
      </div>
      <div class="topbar-spacer"></div>
      <button @click="triggerSimulation" class="simulate-btn" :disabled="currentTaskState === 'PENDING' || currentTaskState === 'STARTED'">
        <span class="btn-icon">▶</span> Simulate
      </button>
    </div>

    <!-- Code Editor Area -->
    <div class="ide-editor">
      <div class="editor-tabs">
        <div class="tab active">alpha.py <span v-if="parentId" class="parent-badge">(Forked from #{{ parentId }})</span></div>
      </div>
      <div class="code-area-wrapper">
        <codemirror
          v-model="alphaCode"
          placeholder="# Type your Python Alpha here...
def generate_alpha():
    pass"
          :style="{ height: '100%', width: '100%' }"
          :autofocus="true"
          :indent-with-tab="true"
          :tab-size="4"
          :extensions="extensions"
          class="cm-custom-theme"
        />
      </div>
    </div>

    <!-- Right Settings Panel -->
    <div class="ide-settings">
      <h3>Simulation Settings</h3>
      
      <div v-if="schema && Object.keys(schema).length > 0">
        <template v-for="(field, key) in schema" :key="key">
          <!-- Only show fields not already in the topbar -->
          <div class="setting-item" v-if="!['region', 'universe', 'instrumentType'].includes(key)">
            <label>{{ field.label || key }}</label>
            
            <select v-if="field.choices" v-model="settings[key]" :disabled="field.blocked">
              <option v-for="c in field.choices" :key="c.value" :value="c.value">{{ c.label || c.value }}</option>
            </select>
            
            <input v-else-if="field.type === 'integer' || field.type === 'float'" 
                   type="number" 
                   :step="field.type === 'integer' ? '1' : '0.01'" 
                   :min="field.min" :max="field.max"
                   v-model="settings[key]" 
                   :disabled="field.blocked"/>
                   
            <input v-else type="text" v-model="settings[key]" :disabled="field.blocked" />
          </div>
        </template>
      </div>
      <div v-else class="setting-item">
        <p style="color: var(--text-secondary); font-size: 0.8rem;">Loading dynamic schema from WQ API...</p>
      </div>

      <div class="telemetry-box" v-if="currentTaskState">
        <h4>Task Telemetry <span class="pulse-dot" v-if="currentTaskState !== 'SUCCESS' && currentTaskState !== 'FAILURE'"></span></h4>
        <div class="t-row">
          <span>State:</span> <strong :class="currentTaskState.toLowerCase()">{{ currentTaskState }}</strong>
        </div>
        <div class="t-row detail">
          {{ currentTaskStatus }}
        </div>
      </div>
    </div>

    <!-- Bottom Terminal / Results -->
    <div class="ide-terminal">
      <div class="terminal-tabs">
        <div class="tab active">Results</div>
        <div class="tab">Logs</div>
      </div>
      <div class="terminal-content">
        <ResultsView @load-alpha="handleLoadAlpha" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onUnmounted, watch, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import ResultsView from './ResultsView.vue'
import { Codemirror } from 'vue-codemirror'
import { python } from '@codemirror/lang-python'
import { oneDark } from '@codemirror/theme-one-dark'

const extensions = [python(), oneDark]

const authStore = useAuthStore()
const message = ref('')
const currentTaskState = ref('')
const currentTaskStatus = ref('')
const alphaCode = ref('')
const parentId = ref(null)

const handleLoadAlpha = (alpha) => {
  alphaCode.value = alpha.expression_string
  parentId.value = alpha.id
}

const settings = reactive({
  type: 'REGULAR',
  region: 'USA',
  universe: 'TOP3000',
  delay: 1,
  decay: 0,
  truncation: 0.08,
  pasteurization: 'ON',
  nanHandling: 'OFF'
})

let pollInterval = null

const schema = ref({})

const fetchSchema = async () => {
  try {
    const res = await axios.post('http://localhost:5000/api/schema', settings, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    schema.value = res.data
  } catch (err) {
    console.error("Failed to load schema", err)
  }
}

watch(settings, (newVal, oldVal) => {
  // Avoid infinite loops if possible, but fetch schema when settings change
  // to update interdependent dropdowns (like region -> universe)
  fetchSchema()
}, { deep: true })

onMounted(() => {
  fetchSchema()
})

const triggerSimulation = async () => {
  try {
    const payload = {
      settings: settings,
      alphaCode: alphaCode.value,
      parentId: parentId.value
    }
    const res = await axios.post('http://localhost:5000/api/simulate', payload, {
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

<style scoped>
.dashboard-ide {
  display: grid;
  grid-template-columns: 1fr 300px;
  grid-template-rows: 50px 1fr 300px;
  height: 100%;
  width: 100%;
}

.ide-topbar {
  grid-column: 1 / 3;
  grid-row: 1 / 2;
  display: flex;
  align-items: center;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  padding: 0 20px;
  gap: 20px;
}

.selector-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.selector-group label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  text-transform: uppercase;
}

.selector-group select {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 4px 8px;
  border-radius: 4px;
  outline: none;
}

.topbar-spacer {
  flex: 1;
}

.simulate-btn {
  background: var(--success-color);
  color: #fff;
  border: none;
  padding: 6px 16px;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: opacity 0.2s;
}

.simulate-btn:hover:not(:disabled) {
  opacity: 0.8;
}

.simulate-btn:disabled {
  background: var(--border-color);
  cursor: not-allowed;
}

.ide-editor {
  grid-column: 1 / 2;
  grid-row: 2 / 3;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border-color);
}

.editor-tabs, .terminal-tabs {
  display: flex;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.tab {
  padding: 8px 16px;
  font-size: 0.85rem;
  color: var(--text-secondary);
  cursor: pointer;
  border-right: 1px solid var(--border-color);
}

.tab.active {
  background: var(--bg-primary);
  color: var(--accent-color);
  border-top: 2px solid var(--accent-color);
}

.code-area-wrapper {
  flex: 1;
  background: #282c34;
  overflow: auto;
}

.cm-custom-theme {
  height: 100%;
  font-family: 'Fira Code', monospace;
  font-size: 14px;
}
.cm-custom-theme .cm-scroller {
  padding: 10px;
}
.parent-badge {
  background: var(--accent-color);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.7rem;
  margin-left: 10px;
}

.ide-settings {
  grid-column: 2 / 3;
  grid-row: 2 / 4;
  background: var(--bg-secondary);
  padding: 20px;
  overflow-y: auto;
}

.ide-settings h3 {
  margin-top: 0;
  font-size: 0.9rem;
  text-transform: uppercase;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 10px;
  margin-bottom: 20px;
}

.setting-item {
  margin-bottom: 15px;
}

.setting-item label {
  display: block;
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-bottom: 5px;
}

.setting-item input, .setting-item select {
  width: 100%;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 6px;
  border-radius: 4px;
  box-sizing: border-box;
}

.telemetry-box {
  margin-top: 30px;
  padding: 15px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
}

.telemetry-box h4 {
  margin-top: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 0.85rem;
  text-transform: uppercase;
}

.t-row {
  font-size: 0.85rem;
  margin-bottom: 8px;
}

.t-row.detail {
  font-family: monospace;
  color: var(--accent-color);
  word-break: break-all;
}

.success { color: var(--success-color); }
.failure { color: var(--danger-color); }
.pending, .started { color: var(--accent-color); }

.pulse-dot {
  width: 8px;
  height: 8px;
  background-color: var(--accent-color);
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(88, 166, 255, 0.7); }
  70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(88, 166, 255, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(88, 166, 255, 0); }
}

.ide-terminal {
  grid-column: 1 / 2;
  grid-row: 3 / 4;
  display: flex;
  flex-direction: column;
  border-top: 1px solid var(--border-color);
  background: var(--bg-primary);
}

.terminal-content {
  flex: 1;
  overflow-y: auto;
  position: relative;
}
</style>
