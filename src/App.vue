<template>
  <div class="app">
    <!-- Header -->
    <header class="app-header">
      <div class="header-left">
        <div class="logo">
          <span class="logo-icon">📞</span>
          <span class="logo-text">"误"联网原住民</span>
        </div>
        <span class="logo-sub">播客助手</span>
      </div>
      <nav class="header-nav">
        <button
          v-for="tab in tabs"
          :key="tab.path"
          :class="['nav-btn', { active: $route.path === tab.path }]"
          @click="$router.push(tab.path)"
        >
          {{ tab.label }}
        </button>
      </nav>
    </header>

    <!-- Main Content -->
    <main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useHotStore } from './stores/hot'

const hotStore = useHotStore()

const tabs = [
  { path: '/', label: '今日热点' },
  { path: '/history', label: '历史记录' },
]

onMounted(async () => {
  await hotStore.fetchAvailableDates()
})
</script>

<style>
/* ─── Global Reset & Variables ─── */
:root {
  --pink: #ff6b9d;
  --pink-glow: rgba(255, 107, 157, 0.3);
  --orange: #ffb347;
  --bg: #0d0d0d;
  --bg-card: #1a1a2e;
  --bg-card-hover: #22223a;
  --border: #2a2a3e;
  --text: #e8e8e8;
  --text-muted: #9999aa;
  --green: #4ade80;
  --blue: #60a5fa;
  --red: #f87171;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background: var(--bg);
  color: var(--text);
  font-family: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
}

button {
  cursor: pointer;
  font-family: inherit;
}

/* ─── App Layout ─── */
.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* ─── Header ─── */
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 60px;
  background: rgba(26, 26, 46, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-icon {
  font-size: 20px;
  animation: pulse 3s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.logo-text {
  font-size: 17px;
  font-weight: 700;
  color: var(--pink);
  letter-spacing: 0.5px;
}

.logo-sub {
  font-size: 12px;
  color: var(--text-muted);
  padding-left: 10px;
  border-left: 1px solid var(--border);
}

.header-nav {
  display: flex;
  gap: 4px;
}

.nav-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 14px;
  padding: 6px 16px;
  border-radius: 8px;
  transition: all 0.2s;
}

.nav-btn:hover {
  color: var(--text);
  background: rgba(255, 255, 255, 0.05);
}

.nav-btn.active {
  color: var(--pink);
  background: var(--pink-glow);
}

/* ─── Main ─── */
.app-main {
  flex: 1;
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
  padding: 24px 16px;
}

/* ─── Page Transitions ─── */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* ─── Scrollbar ─── */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--text-muted);
}
</style>
