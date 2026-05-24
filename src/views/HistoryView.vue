<template>
  <div class="history">
    <div class="history-header">
      <h2>历史记录</h2>
      <p>查看往日热点、总结和音频</p>
    </div>

    <div v-if="store.availableDates.length === 0" class="empty-history">
      <div class="empty-icon">📅</div>
      <p>暂无历史数据</p>
      <p class="hint">每日 8:00 自动生成，或点击「今日热点」页面的刷新按钮</p>
    </div>

    <div v-else class="date-grid">
      <div
        v-for="date in store.availableDates"
        :key="date"
        class="date-card"
        @click="selectDate(date)"
      >
        <div class="date-card-inner">
          <div class="date-weekday">{{ formatWeekday(date) }}</div>
          <div class="date-str">{{ date }}</div>
          <div class="date-status-dots">
            <span
              v-for="(label, idx) in ['H', 'S', 'Sc', 'A']"
              :key="idx"
              class="dot-sm"
              :title="['热点', '总结', '文字稿', '音频'][idx]"
            >{{ label }}</span>
          </div>
          <button
            class="view-btn"
            @click.stop="goToDate(date)"
          >查看</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useHotStore } from '../stores/hot'

const router = useRouter()
const store = useHotStore()

function formatWeekday(dateStr) {
  const d = new Date(dateStr + 'T00:00:00')
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  if (d.getTime() === today.getTime()) return '今天'
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return weekdays[d.getDay()]
}

function goToDate(date) {
  store.loadDate(date)
  router.push('/')
}

async function selectDate(date) {
  await store.fetchDateStatus(date)
}
</script>

<style scoped>
.history-header {
  margin-bottom: 24px;
}

.history-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 4px;
}

.history-header p {
  font-size: 13px;
  color: var(--text-muted);
}

.empty-history {
  text-align: center;
  padding: 80px 20px;
  color: var(--text-muted);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-history .hint {
  font-size: 12px;
  margin-top: 8px;
  opacity: 0.7;
}

.date-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 12px;
}

.date-card {
  cursor: pointer;
}

.date-card-inner {
  padding: 16px;
  border-radius: 14px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.date-card-inner:hover {
  border-color: var(--pink);
  background: var(--bg-card-hover);
  transform: translateY(-2px);
}

.date-weekday {
  font-size: 12px;
  color: var(--pink);
  font-weight: 500;
}

.date-str {
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
  font-family: 'JetBrains Mono', monospace;
}

.date-status-dots {
  display: flex;
  gap: 4px;
  margin: 2px 0;
}

.dot-sm {
  font-size: 9px;
  width: 16px;
  height: 16px;
  border-radius: 4px;
  background: var(--border);
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
}

.view-btn {
  margin-top: 4px;
  padding: 5px 0;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-muted);
  font-size: 12px;
  transition: all 0.2s;
}

.view-btn:hover {
  border-color: var(--pink);
  color: var(--pink);
}
</style>
