import { useState } from 'react'
import axios from 'axios'
import BudgetProgress from './BudgetProgress'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function CartOptimizer({ budget }) {
  const [items, setItems] = useState('')
  const [store, setStore] = useState('kroger')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleOptimize = async () => {
    setLoading(true)
    setError(null)
    try {
      const itemList = items.split('\n').map(s => s.trim()).filter(Boolean)
      const resp = await axios.post(`${API}/optimize/cart`, {
        items: itemList,
        budget,
        store,
      })
      setResult(resp.data)
    } catch (e) {
      setError('Failed to optimize cart. Make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-xl shadow p-6 space-y-4">
      <h2 className="text-lg font-semibold text-gray-800">Cart Optimizer</h2>
      <textarea
        className="w-full border border-gray-300 rounded-lg p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-green-500"
        rows={5}
        placeholder={"chicken breast\neggs\nmilk\nbread\nrice"}
        value={items}
        onChange={e => setItems(e.target.value)}
      />
      <div className="flex gap-3 items-center">
        <select
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none"
          value={store}
          onChange={e => setStore(e.target.value)}
        >
          <option value="kroger">Kroger</option>
          <option value="aldi">Aldi</option>
          <option value="walmart">Walmart</option>
        </select>
        <button
          onClick={handleOptimize}
          disabled={loading || !items.trim()}
          className="bg-green-600 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50 transition-colors"
        >
          {loading ? 'Optimizing...' : 'Optimize'}
        </button>
      </div>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      {result && (
        <div className="space-y-3">
          <BudgetProgress spent={result.total_cost} budget={budget} />
          <div className="divide-y divide-gray-100">
            {result.items.map((item, i) => (
              <div key={i} className="flex justify-between py-2 text-sm">
                <span className="text-gray-700">{item.name} × {item.quantity}</span>
                <span className="font-medium">${(item.price * item.quantity).toFixed(2)}</span>
              </div>
            ))}
          </div>
          {result.substitutions?.length > 0 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
              <p className="text-xs font-semibold text-yellow-800 mb-1">Substitution suggestions</p>
              {result.substitutions.map((s, i) => (
                <p key={i} className="text-xs text-yellow-700">
                  Swap <b>{s.original}</b> → <b>{s.substitute}</b> and save ${s.savings.toFixed(2)}
                </p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
