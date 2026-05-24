import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// Hotlist API
export const getHotlist = (date) =>
  api.get('/hotlist', { params: { date } })

export const getHotItem = (itemId) =>
  api.get(`/hotlist/${itemId}`)

export const getAvailableDates = () =>
  api.get('/hotlist/dates/list')

export const generateDaily = (params = {}) =>
  api.post('/hotlist/generate', params)

// Summary & Script API
export const getSummary = (date) =>
  api.get(`/summary/${date}`)

export const getScript = (date) =>
  api.get(`/script/${date}`)

export const getAudioUrl = (date) =>
  `/api/audio/${date}`

export const getStatus = (date) =>
  api.get(`/status/${date}`)

export default api
