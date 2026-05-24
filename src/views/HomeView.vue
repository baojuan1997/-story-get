<template>
  <div class="home">
    <!-- Date Selector Bar -->
    <div class="date-bar">
      <button class="date-nav-btn" @click="prevDay">
        <span>‹</span>
      </button>
      <div class="date-display">
        <span class="date-main">{{ store.currentDateDisplay }}</span>
        <span v-if="isToday" class="today-badge">今天</span>
      </div>
      <button class="date-nav-btn" @click="nextDay" :disabled="isToday">
        <span>›</span>
      </button>
      <button class="refresh-btn" @click="store.refresh()" :disabled="store.refreshLoading">
        <span v-if="store.refreshLoading" class="spin">⟳</span>
        <span v-else>↻</span>
        {{ store.refreshLoading ? 'thinking...' : '刷新' }}
      </button>
      <button class="style-btn" @click="showStyleModal = true" :disabled="store.refreshLoading">
        <span>✎</span>
        {{ store.currentStyle === 'default' ? '座机风格' : styleLabel }}
      </button>
    </div>

    <!-- Warning Message -->
    <div v-if="store.warningMessage" class="warning-state">
      <div class="warning-icon">⚠️</div>
      <p>{{ store.warningMessage }}</p>
    </div>

    <!-- Status Pills -->
    <div class="status-bar">
      <span class="status-pill" :class="{ done: store.dateStatus.hotlist_exists }">
        <span class="dot"></span>热点
      </span>
      <span class="status-pill" :class="{ done: store.dateStatus.summary_exists }">
        <span class="dot"></span>总结
      </span>
      <span class="status-pill" :class="{ done: store.dateStatus.script_exists }">
        <span class="dot"></span>文字稿
      </span>
      <span class="status-pill" :class="{ done: store.dateStatus.audio_exists }">
        <span class="dot"></span>音频
      </span>
    </div>

    <!-- Loading State -->
    <div v-if="store.loading" class="loading-state">
      <div class="loading-phone">📞</div>
      <p>正在抓取热点…</p>
    </div>

    <!-- Error State -->
    <div v-else-if="store.error && store.items.length === 0" class="error-state">
      <div class="error-icon">⚠️</div>
      <p>{{ store.error }}</p>
      <p class="error-hint">点击「刷新」按钮手动触发抓取</p>
    </div>

    <!-- Hot List -->
    <div v-else class="hot-list">
      <div class="hot-list-header">
        <span>热搜榜</span>
        <span class="hot-count">{{ store.sortedItems.length }} 条</span>
      </div>

      <div
        v-for="item in store.sortedItems"
        :key="item.id"
        class="hot-item"
        @click="openDetail(item)"
      >
        <div class="hot-rank" :class="getRankClass(item.rank)">
          {{ item.rank }}
        </div>
        <div class="hot-content">
          <div class="hot-title">{{ item.title }}</div>
          <div class="hot-meta">
            <span class="hot-source">{{ item.source }}</span>
            <span v-if="item.keywords.length" class="hot-tags">
              <span v-for="tag in item.keywords.slice(0, 2)" :key="tag" class="tag">{{ tag }}</span>
            </span>
          </div>
        </div>
        <div class="hot-heat">
          <span class="heat-label" :class="getHeatClass(item.heat_score)">
            {{ getHeatText(item.heat_score) }}
          </span>
          <span class="heat-score">{{ formatScore(item.heat_score) }}</span>
        </div>
      </div>
    </div>

    <!-- Detail Panel -->
    <Teleport to="body">
      <div v-if="store.selectedItem" class="detail-overlay" @click.self="store.selectedItem = null">
        <div class="detail-panel">
          <div class="detail-header">
            <div class="detail-rank">#{{ store.selectedItem.rank }}</div>
            <div class="detail-title-wrap">
              <h2 class="detail-title">{{ store.selectedItem.title }}</h2>
              <div class="detail-meta">
                <span>{{ store.selectedItem.source }}</span>
                <span v-if="store.selectedItem.publish_time">
                  {{ formatTime(store.selectedItem.publish_time) }}
                </span>
              </div>
            </div>
            <button class="detail-close" @click="store.selectedItem = null">✕</button>
          </div>

          <div class="detail-tabs">
            <button
              v-for="tab in detailTabs"
              :key="tab.key"
              :class="['detail-tab', { active: activeTab === tab.key }]"
              @click="activeTab = tab.key"
            >
              {{ tab.label }}
            </button>
          </div>

          <div class="detail-body">
            <!-- Summary Tab -->
            <div v-if="activeTab === 'summary'" class="tab-content">
              <div class="summary-block">
                <h3>摘要</h3>
                <p>{{ store.selectedItem.summary }}</p>
              </div>
              <div v-if="store.selectedItem.keywords.length" class="summary-block">
                <h3>标签</h3>
                <div class="tag-list">
                  <span v-for="tag in store.selectedItem.keywords" :key="tag" class="tag big">{{ tag }}</span>
                </div>
              </div>
              <div class="summary-block">
                <h3>热度</h3>
                <div class="heat-bar-wrap">
                  <div class="heat-bar">
                    <div class="heat-bar-fill" :style="{ width: getHeatPercent(store.selectedItem.heat_score) + '%' }"></div>
                  </div>
                  <span>{{ formatScore(store.selectedItem.heat_score) }}</span>
                </div>
              </div>
            </div>

            <!-- Script Tab -->
            <div v-if="activeTab === 'script'" class="tab-content script-content">
              <div v-if="store.scriptContent" class="script-text">
                <pre>{{ store.scriptContent }}</pre>
              </div>
              <div v-else class="empty-state">
                <p>暂无文字稿</p>
                <p class="hint">点击「刷新」生成今日内容</p>
              </div>
            </div>

            <!-- Downloads Tab -->
            <div v-if="activeTab === 'downloads'" class="tab-content downloads-content">
              <div class="download-card">
                <div class="download-icon">📄</div>
                <div class="download-info">
                  <div class="download-name">{{ store.currentDate }}_总结文档.md</div>
                  <div class="download-desc">热点总结 Markdown 文档</div>
                </div>
                <button
                  class="download-btn"
                  @click="downloadFile('summary', 'md')"
                  :disabled="!store.dateStatus.summary_exists"
                >
                  ↓ 下载
                </button>
              </div>
              <div class="download-card">
                <div class="download-icon">🎙️</div>
                <div class="download-info">
                  <div class="download-name">{{ store.currentDate }}_文字稿.md</div>
                  <div class="download-desc">播客朗读文字稿</div>
                </div>
                <button
                  class="download-btn"
                  @click="downloadFile('script', 'md')"
                  :disabled="!store.dateStatus.script_exists"
                >
                  ↓ 下载
                </button>
              </div>
              <div class="download-card">
                <div class="download-icon">🔊</div>
                <div class="download-info">
                  <div class="download-name">{{ store.currentDate }}_podcast.mp3</div>
                  <div class="download-desc">播客语音合成音频</div>
                </div>
                <button
                  class="download-btn"
                  @click="downloadFile('audio', 'mp3')"
                  :disabled="!store.dateStatus.audio_exists"
                >
                  ↓ 下载
                </button>
              </div>

              <!-- Audio Player -->
              <div v-if="store.dateStatus.audio_exists" class="audio-player">
                <div class="player-phone-icon">📞</div>
                <audio
                  :src="audioUrl"
                  controls
                  class="audio-element"
                ></audio>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Style Modal -->
    <Teleport to="body">
      <div v-if="showStyleModal" class="style-overlay" @click.self="showStyleModal = false">
        <div class="style-modal">
          <div class="style-modal-header">
            <h3>选择播客风格</h3>
            <button class="style-modal-close" @click="showStyleModal = false">✕</button>
          </div>

          <div class="style-presets">
            <div
              v-for="preset in stylePresets"
              :key="preset.id"
              class="style-preset-card"
              :class="{ active: store.currentStyle === preset.id }"
              @click="selectStyle(preset.id)"
            >
              <div class="preset-icon">{{ preset.icon }}</div>
              <div class="preset-info">
                <div class="preset-name">{{ preset.name }}</div>
                <div class="preset-desc">{{ preset.desc }}</div>
              </div>
              <div v-if="store.currentStyle === preset.id" class="preset-check">✓</div>
            </div>
          </div>

          <div class="style-custom">
            <div class="custom-label">或者，自定义提示词</div>
            <textarea
              v-model="store.customPrompt"
              class="custom-textarea"
              placeholder="描述你想要的播客风格，例如：像一位天津大爷在早点摊上跟你聊天，语言朴实接地气，带点幽默…"
              rows="4"
            ></textarea>
            <div class="custom-hint">留空则使用上方选择的预设风格</div>
          </div>

          <div class="style-modal-footer">
            <button class="style-cancel-btn" @click="showStyleModal = false">取消</button>
            <button class="style-confirm-btn" @click="confirmStyle">
              确认并刷新
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useHotStore } from '../stores/hot'
import { getAudioUrl } from '../api'

const store = useHotStore()
const activeTab = ref('summary')
const showStyleModal = ref(false)

const stylePresets = [
  { id: 'default', name: '座机原住民', desc: '天津口音，像老友夜谈，有天津的生活细节', icon: '📞' },
  { id: 'news', name: '新闻播报', desc: '简洁清晰，信息密度高，适合快速获取热点', icon: '📰' },
  { id: 'analytical', name: '深度分析', desc: '有观点有态度，深入浅出，不只说什么还讲为什么', icon: '🧠' },
  { id: 'emotional', name: '情感叙事', desc: '把新闻当故事讲，有画面感，有温度', icon: '💡' },
  { id: 'young', name: '年轻人说', desc: '网络感强，接地气，说人话不端着', icon: '🔥' },
]

const styleLabel = computed(() => {
  const p = stylePresets.find(p => p.id === store.currentStyle)
  return p ? p.name : '座机风格'
})

function selectStyle(id) {
  store.currentStyle = id
  store.customPrompt = ''
}

function confirmStyle() {
  showStyleModal.value = false
  store.refresh()
}

const detailTabs = [
  { key: 'summary', label: '详情摘要' },
  { key: 'script', label: '文字稿' },
  { key: 'downloads', label: '下载' },
]

const isToday = computed(() => {
  return store.currentDate === new Date().toLocaleDateString('en-CA')
})

const audioUrl = computed(() => getAudioUrl(store.currentDate))

function prevDay() {
  const d = new Date(store.currentDate + 'T00:00:00')
  d.setDate(d.getDate() - 1)
  store.loadDate(d.toLocaleDateString('en-CA'))
}

function nextDay() {
  const d = new Date(store.currentDate + 'T00:00:00')
  d.setDate(d.getDate() + 1)
  store.loadDate(d.toLocaleDateString('en-CA'))
}

function openDetail(item) {
  store.selectItem(item)
  activeTab.value = 'summary'
}

function getRankClass(rank) {
  if (rank === 1) return 'rank-1'
  if (rank <= 3) return 'rank-top'
  return ''
}

function getHeatText(score) {
  if (score >= 9000) return '沸'
  if (score >= 8000) return '爆'
  if (score >= 5000) return '热'
  if (score >= 2000) return '新'
  return '商'
}

function getHeatClass(score) {
  if (score >= 9000) return 'heat-fei'
  if (score >= 8000) return 'heat-bao'
  if (score >= 5000) return 'heat-re'
  return 'heat-xin'
}

function getHeatPercent(score) {
  return Math.min(100, (score / 10000) * 100)
}

function formatScore(score) {
  if (!score) return '-'
  if (score >= 10000) return '9999+'
  return score.toLocaleString()
}

function formatTime(t) {
  if (!t) return ''
  return t.slice(0, 16).replace('T', ' ')
}

async function downloadFile(type, ext) {
  const date = store.currentDate
  let url = ''
  let filename = `${date}_${type === 'summary' ? '总结文档' : type === 'script' ? '文字稿' : 'podcast'}.${ext}`

  if (type === 'summary') {
    url = `/api/summary/${date}`
  } else if (type === 'script') {
    url = `/api/script/${date}`
  } else if (type === 'audio') {
    url = `/api/audio/${date}`
  }

  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

onMounted(async () => {
  await store.loadDate(store.currentDate)
})

watch(() => store.currentDate, async (newDate) => {
  await store.fetchDateStatus(newDate)
})
</script>

<style scoped>
/* ─── Date Bar ─── */
.date-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.date-nav-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text);
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.date-nav-btn:hover:not(:disabled) {
  border-color: var(--pink);
  color: var(--pink);
}

.date-nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.date-display {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: center;
}

.date-main {
  font-size: 15px;
  font-weight: 500;
  color: var(--text);
}

.today-badge {
  font-size: 11px;
  background: var(--pink);
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 500;
}

.refresh-btn {
  height: 36px;
  padding: 0 14px;
  border-radius: 10px;
  border: 1px solid var(--pink);
  background: transparent;
  color: var(--pink);
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.refresh-btn:hover:not(:disabled) {
  background: var(--pink);
  color: white;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ─── Status Bar ─── */
.status-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.status-pill {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--text-muted);
  padding: 4px 10px;
  border-radius: 20px;
  border: 1px solid var(--border);
  transition: all 0.3s;
}

.status-pill .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--border);
  transition: all 0.3s;
}

.status-pill.done {
  color: var(--green);
  border-color: rgba(74, 222, 128, 0.3);
}

.status-pill.done .dot {
  background: var(--green);
  box-shadow: 0 0 6px var(--green);
}

/* ─── Warning State ─── */
.warning-state {
  text-align: center;
  padding: 20px 20px;
  margin-bottom: 16px;
  background: rgba(255, 179, 71, 0.08);
  border: 1px solid rgba(255, 179, 71, 0.3);
  border-radius: 12px;
  color: var(--orange);
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
}

.warning-icon {
  font-size: 20px;
  flex-shrink: 0;
}

/* ─── Loading / Error ─── */
.loading-state, .error-state {
  text-align: center;
  padding: 80px 20px;
  color: var(--text-muted);
}

.loading-phone {
  font-size: 48px;
  margin-bottom: 16px;
  animation: pulse 2s ease-in-out infinite;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.error-hint {
  font-size: 12px;
  margin-top: 8px;
  opacity: 0.7;
}

/* ─── Hot List ─── */
.hot-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.hot-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 4px 8px;
  font-size: 13px;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border);
  margin-bottom: 8px;
}

.hot-count {
  font-size: 12px;
  background: var(--bg-card);
  padding: 2px 8px;
  border-radius: 10px;
}

.hot-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 12px;
  background: var(--bg-card);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.hot-item:hover {
  background: var(--bg-card-hover);
  border-color: var(--border);
  transform: translateX(2px);
}

.hot-rank {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
  background: var(--border);
  color: var(--text-muted);
}

.hot-rank.rank-1 {
  background: linear-gradient(135deg, #ff6b9d, #ff8a65);
  color: white;
  font-size: 15px;
}

.hot-rank.rank-top {
  background: linear-gradient(135deg, #ffb347, #ff7043);
  color: white;
}

.hot-content {
  flex: 1;
  min-width: 0;
}

.hot-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.hot-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.hot-source {
  font-size: 11px;
  color: var(--text-muted);
}

.hot-tags {
  display: flex;
  gap: 4px;
}

.tag {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 4px;
  background: rgba(255, 179, 71, 0.15);
  color: var(--orange);
}

.hot-heat {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
  flex-shrink: 0;
}

.heat-label {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 6px;
}

.heat-label.heat-fei {
  background: rgba(255, 107, 157, 0.2);
  color: var(--pink);
}

.heat-label.heat-bao {
  background: rgba(255, 138, 101, 0.2);
  color: #ff8a65;
}

.heat-label.heat-re {
  background: rgba(255, 179, 71, 0.2);
  color: var(--orange);
}

.heat-label.heat-xin {
  background: rgba(96, 165, 250, 0.15);
  color: var(--blue);
}

.heat-score {
  font-size: 10px;
  color: var(--text-muted);
  font-family: 'JetBrains Mono', monospace;
}

/* ─── Detail Panel ─── */
.detail-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.detail-panel {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 20px;
  width: 100%;
  max-width: 640px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideUp 0.25s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.detail-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 20px 20px 16px;
  border-bottom: 1px solid var(--border);
}

.detail-rank {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, var(--pink), #ff8a65);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
}

.detail-title-wrap {
  flex: 1;
  min-width: 0;
}

.detail-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
  line-height: 1.5;
  margin-bottom: 4px;
}

.detail-meta {
  font-size: 12px;
  color: var(--text-muted);
  display: flex;
  gap: 10px;
}

.detail-close {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-muted);
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
}

.detail-close:hover {
  border-color: var(--red);
  color: var(--red);
}

/* ─── Detail Tabs ─── */
.detail-tabs {
  display: flex;
  padding: 12px 20px 0;
  gap: 4px;
  border-bottom: 1px solid var(--border);
}

.detail-tab {
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 13px;
  padding: 6px 14px;
  border-radius: 8px 8px 0 0;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
  margin-bottom: -1px;
}

.detail-tab:hover {
  color: var(--text);
}

.detail-tab.active {
  color: var(--pink);
  border-bottom-color: var(--pink);
}

/* ─── Detail Body ─── */
.detail-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.tab-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.summary-block h3 {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 400;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 8px;
}

.summary-block p {
  font-size: 14px;
  line-height: 1.8;
  color: var(--text);
}

.tag-list {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tag.big {
  font-size: 12px;
  padding: 3px 10px;
}

.heat-bar-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}

.heat-bar {
  flex: 1;
  height: 6px;
  background: var(--border);
  border-radius: 3px;
  overflow: hidden;
}

.heat-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--pink), var(--orange));
  border-radius: 3px;
  transition: width 1s ease;
}

.heat-bar-wrap span {
  font-size: 13px;
  color: var(--text-muted);
  font-family: 'JetBrains Mono', monospace;
}

/* ─── Script Tab ─── */
.script-text pre {
  font-family: 'Noto Sans SC', 'PingFang SC', sans-serif;
  font-size: 13.5px;
  line-height: 1.9;
  color: var(--text);
  white-space: pre-wrap;
  word-break: break-word;
}

/* ─── Downloads Tab ─── */
.downloads-content {
  gap: 12px;
}

.download-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 12px;
  background: var(--bg);
  border: 1px solid var(--border);
}

.download-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.download-info {
  flex: 1;
}

.download-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text);
  font-family: 'JetBrains Mono', monospace;
}

.download-desc {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

.download-btn {
  padding: 6px 14px;
  border-radius: 8px;
  border: 1px solid var(--pink);
  background: transparent;
  color: var(--pink);
  font-size: 12px;
  transition: all 0.2s;
  white-space: nowrap;
}

.download-btn:hover:not(:disabled) {
  background: var(--pink);
  color: white;
}

.download-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* ─── Audio Player ─── */
.audio-player {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(255, 107, 157, 0.1), rgba(255, 179, 71, 0.1));
  border: 1px solid rgba(255, 107, 157, 0.2);
}

.player-phone-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.audio-element {
  flex: 1;
  height: 36px;
  accent-color: var(--pink);
}

.audio-element::-webkit-media-controls-panel {
  background: transparent;
}

/* ─── Empty State ─── */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-muted);
}

.empty-state .hint {
  font-size: 12px;
  margin-top: 6px;
  opacity: 0.7;
}

/* ─── Style Button ─── */
.style-btn {
  height: 36px;
  padding: 0 12px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text-muted);
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.2s;
  white-space: nowrap;
}

.style-btn:hover:not(:disabled) {
  border-color: var(--pink);
  color: var(--pink);
}

.style-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ─── Style Modal ─── */
.style-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  backdrop-filter: blur(4px);
}

.style-modal {
  background: var(--bg-main);
  border: 1px solid var(--border);
  border-radius: 16px;
  width: 100%;
  max-width: 480px;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}

.style-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 20px 0;
}

.style-modal-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
  margin: 0;
}

.style-modal-close {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text-muted);
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.style-modal-close:hover {
  border-color: var(--red);
  color: var(--red);
}

.style-presets {
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.style-preset-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.style-preset-card:hover {
  border-color: var(--pink);
  background: var(--bg-card-hover);
}

.style-preset-card.active {
  border-color: var(--pink);
  background: rgba(252, 112, 112, 0.06);
}

.preset-icon {
  font-size: 22px;
  flex-shrink: 0;
}

.preset-info {
  flex: 1;
  min-width: 0;
}

.preset-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text);
  margin-bottom: 2px;
}

.preset-desc {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.4;
}

.preset-check {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--pink);
  color: white;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* ─── Custom Prompt ─── */
.style-custom {
  padding: 0 20px 16px;
}

.custom-label {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 8px;
  font-weight: 500;
}

.custom-textarea {
  width: 100%;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text);
  font-size: 13px;
  line-height: 1.6;
  resize: vertical;
  font-family: inherit;
  box-sizing: border-box;
  transition: border-color 0.2s;
}

.custom-textarea:focus {
  outline: none;
  border-color: var(--pink);
}

.custom-textarea::placeholder {
  color: var(--text-muted);
  opacity: 0.6;
}

.custom-hint {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 6px;
  opacity: 0.7;
}

/* ─── Modal Footer ─── */
.style-modal-footer {
  display: flex;
  gap: 10px;
  padding: 0 20px 20px;
}

.style-cancel-btn {
  flex: 1;
  height: 40px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-muted);
  font-size: 14px;
  transition: all 0.2s;
}

.style-cancel-btn:hover {
  border-color: var(--text-muted);
  color: var(--text);
}

.style-confirm-btn {
  flex: 2;
  height: 40px;
  border-radius: 10px;
  border: none;
  background: var(--pink);
  color: white;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.style-confirm-btn:hover {
  background: #e85555;
  transform: translateY(-1px);
}
</style>
