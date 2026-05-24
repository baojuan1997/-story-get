import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as api from '../api'

export const useHotStore = defineStore('hot', () => {
  const currentDate = ref(new Date().toLocaleDateString('en-CA'))
  const warningMessage = ref('')
  const items = ref([])
  const selectedItem = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const availableDates = ref([])
  const dateStatus = ref({
    hotlist_exists: false,
    summary_exists: false,
    script_exists: false,
    audio_exists: false,
  })
  const summaryContent = ref('')
  const scriptContent = ref('')
  const refreshLoading = ref(false)
  const currentStyle = ref('default')
  const customPrompt = ref('')

  const currentDateDisplay = computed(() => {
    const d = new Date(currentDate.value + 'T00:00:00')
    return d.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      weekday: 'long',
    })
  })

  const sortedItems = computed(() =>
    [...items.value].sort((a, b) => a.rank - b.rank)
  )

  async function fetchHotlist(date) {
    loading.value = true
    error.value = null
    try {
      const resp = await api.getHotlist(date)
      items.value = resp.data.items || []
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      items.value = []
    } finally {
      loading.value = false
    }
  }

  async function fetchAvailableDates() {
    try {
      const resp = await api.getAvailableDates()
      availableDates.value = resp.data.dates || []
    } catch (e) {
      console.error('Failed to fetch dates', e)
    }
  }

  async function fetchDateStatus(date) {
    try {
      const resp = await api.getStatus(date)
      dateStatus.value = resp.data
    } catch (e) {
      console.error('Failed to fetch status', e)
    }
  }

  async function fetchSummary(date) {
    try {
      const resp = await api.getSummary(date)
      summaryContent.value = resp.data.content || ''
    } catch (e) {
      summaryContent.value = ''
    }
  }

  async function fetchScript(date) {
    try {
      const resp = await api.getScript(date)
      scriptContent.value = resp.data.content || ''
    } catch (e) {
      scriptContent.value = ''
    }
  }

  async function selectItem(item) {
    selectedItem.value = item
    await fetchSummary(currentDate.value)
    await fetchScript(currentDate.value)
  }

  async function refresh() {
    const today = new Date().toLocaleDateString('en-CA')
    if (currentDate.value !== today) {
      warningMessage.value = '当前查看的是历史日期，无法重新生成内容。请切换到「今天」后再刷新。'
      return
    }
    warningMessage.value = ''
    refreshLoading.value = true
    try {
      await api.generateDaily({ date: currentDate.value, style: currentStyle.value, custom_prompt: customPrompt.value })
      await fetchHotlist(currentDate.value)
      await fetchDateStatus(currentDate.value)
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
    } finally {
      refreshLoading.value = false
    }
  }

  async function loadDate(date) {
    warningMessage.value = ''
    currentDate.value = date
    await fetchHotlist(date)
    await fetchDateStatus(date)
    selectedItem.value = null
    summaryContent.value = ''
    scriptContent.value = ''
  }

  return {
    currentDate,
    items,
    selectedItem,
    loading,
    error,
    availableDates,
    dateStatus,
    summaryContent,
    scriptContent,
    refreshLoading,
    currentStyle,
    customPrompt,
    currentDateDisplay,
    warningMessage,
    sortedItems,
    fetchHotlist,
    fetchAvailableDates,
    fetchDateStatus,
    fetchSummary,
    fetchScript,
    selectItem,
    refresh,
    loadDate,
  }
})
