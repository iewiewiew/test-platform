import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    isDark: false
  }),

  getters: {
    theme: (state) => state.isDark ? 'dark' : 'light'
  },

  actions: {
    // 切换主题
    toggleTheme() {
      this.isDark = !this.isDark
      this.applyTheme()
      this.saveTheme()
    },

    // 设置主题
    setTheme(isDark) {
      this.isDark = isDark
      this.applyTheme()
      this.saveTheme()
    },

    // 应用主题到 DOM
    applyTheme() {
      const html = document.documentElement
      if (this.isDark) {
        html.classList.add('dark')
      } else {
        html.classList.remove('dark')
      }
    },

    // 保存主题到 localStorage
    saveTheme() {
      localStorage.setItem('theme', this.isDark ? 'dark' : 'light')
    },

    // 从 localStorage 加载主题
    loadTheme() {
      const savedTheme = localStorage.getItem('theme')
      if (savedTheme) {
        this.isDark = savedTheme === 'dark'
      } else {
        // 如果没有保存的主题，检查系统偏好
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
        this.isDark = prefersDark
      }
      this.applyTheme()
    },

    // 初始化主题
    initTheme() {
      this.loadTheme()
    }
  }
})

