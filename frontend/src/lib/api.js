import axios from 'axios'
const API = import.meta.env.VITE_API_URL

export async function analyzeImage(file) {
  const form = new FormData()
  form.append('file', file)
  const res = await axios.post(`${API}/analyze`, form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return res.data
}