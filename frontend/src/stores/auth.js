import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
  }),
  actions: {
    async checkSavedCredentials() {
      try {
        const response = await axios.get('http://localhost:5000/api/credentials/check')
        return response.data
      } catch (error) {
        return { exists: false }
      }
    },
    async loginSaved() {
      try {
        const response = await axios.post('http://localhost:5000/api/login/saved')
        this.token = response.data.token
        localStorage.setItem('token', this.token)
        return { success: true }
      } catch (error) {
        console.error('Saved login failed:', error)
        if (error.response?.data?.error === 'biometrics') {
          return { success: false, isBiometrics: true, url: error.response.data.url, email: error.response.data.email }
        }
        return { success: false, error: error.response?.data?.error || 'Server error' }
      }
    },
    async login(email, password) {
      try {
        const response = await axios.post('http://localhost:5000/api/login', {
          email,
          password
        })
        this.token = response.data.token
        localStorage.setItem('token', this.token)
        return { success: true }
      } catch (error) {
        console.error('Login failed:', error)
        if (error.response?.data?.error === 'biometrics') {
          return { success: false, isBiometrics: true, url: error.response.data.url, email: error.response.data.email }
        }
        return { success: false, error: error.response?.data?.error || 'Server error' }
      }
    },
    logout() {
      this.token = null
      localStorage.removeItem('token')
    }
  }
})
