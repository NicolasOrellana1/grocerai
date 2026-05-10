import { useEffect, useState } from 'react'
import axios from 'axios'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const FLOWER_URL = 'http://localhost:5555'

const SCRAPERS = ['kroger', 'aldi', 'walmart']

export default function PipelineMonitor() {
  const [tasks, setTasks] = useState({})
  const [wsStatus, setWsStatus] = useState('connecting')
  const [lastPriceUpdate, setLastPriceUpdate] = useState(null)
  const [priceCount, setPriceCount] = useState(null)

  useEffect(() => {
    axios.get(`${API}/prices`).then(r => setPriceCount(r.data.length)).catch(() => {})
  }, [])

  useEffect(() => {
    const ws = new WebSocket(`${API.replace('http', 'ws')}/ws/prices`)
    ws.onopen = () => setWsStatus('connected')
    ws.onclose = () => setWsStatus('disconnected')
    ws.onerror = () => setWsStatus('error')
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data)
      setPriceCount(data.length)
      setLastPriceUpdate(new Date().toLocaleTimeString())
    }
    return () => ws.close()
  }, [])

  const wsColor = {
    connected: 'bg-green-400',
    connecting: 'bg-yellow-400',
    disconnected: 'bg-gray-400',
    error: 'bg-red-400',
  }[wsStatus]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Pipeline Monitor</h1>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl shadow p-5">
          <p className="text-xs text-gray-500 uppercase font-semibold">Products tracked</p>
          <p className="text-3xl font-bold text-green-700 mt-1">{priceCount ?? '—'}</p>
        </div>
        <div className="bg-white rounded-xl shadow p-5">
          <p className="text-xs text-gray-500 uppercase font-semibold">WebSocket</p>
          <div className="flex items-center gap-2 mt-1">
            <span className={`inline-block w-3 h-3 rounded-full ${wsColor}`} />
            <p className="text-lg font-semibold capitalize">{wsStatus}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow p-5">
          <p className="text-xs text-gray-500 uppercase font-semibold">Last price push</p>
          <p className="text-lg font-semibold mt-1">{lastPriceUpdate || 'Waiting...'}</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow divide-y divide-gray-100">
        <div className="px-6 py-4">
          <h2 className="font-semibold text-gray-800">Scraper Status</h2>
        </div>
        {SCRAPERS.map(scraper => (
          <div key={scraper} className="flex items-center justify-between px-6 py-4">
            <div>
              <p className="font-medium text-gray-800 capitalize">{scraper}</p>
              <p className="text-xs text-gray-500">
                Celery task: tasks.scrape_{scraper}_task · every 15 min
              </p>
            </div>
            <a
              href={FLOWER_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-green-600 hover:underline"
            >
              View in Flower →
            </a>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl shadow p-6">
        <h2 className="font-semibold text-gray-800 mb-3">Quick Commands</h2>
        <div className="space-y-2 font-mono text-xs text-gray-700 bg-gray-50 rounded-lg p-4">
          <p># Trigger Kroger scraper manually</p>
          <p className="text-green-700">docker exec -it groceryai-scraper-worker-1 celery -A tasks call tasks.scrape_kroger_task</p>
          <p className="mt-2"># View live logs</p>
          <p className="text-green-700">docker compose logs --follow scraper-worker</p>
        </div>
      </div>
    </div>
  )
}
