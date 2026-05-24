<template>
  <div class="detail-view">
    <div class="detail-nav">
      <button class="back-btn" @click="$router.back()">← 返回</button>
    </div>
    <div v-if="store.selectedItem" class="detail-content">
      <!-- Detail content loaded via store.selectedItem -->
    </div>
    <div v-else class="not-found">
      <p>未找到该条目</p>
      <button @click="$router.push('/')">返回首页</button>
    </div>
  </div>
</template>

<script setup>
import { useHotStore } from '../stores/hot'

const props = defineProps(['id'])
const store = useHotStore()
</script>

<style scoped>
.detail-nav {
  margin-bottom: 20px;
}

.back-btn {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-muted);
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 13px;
  transition: all 0.2s;
}

.back-btn:hover {
  border-color: var(--pink);
  color: var(--pink);
}

.not-found {
  text-align: center;
  padding: 60px;
  color: var(--text-muted);
}
</style>
