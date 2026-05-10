import { useState } from 'react'
import axios from 'axios'
import useStore from '../store/useStore'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function RecipeToCart() {
  const { addToCart } = useStore()
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSearch = async () => {
    if (!query.trim()) return
    setLoading(true)
    setError(null)
    try {
      const resp = await axios.post(`${API}/recipes/to-cart`, { recipe_name: query })
      setResults(resp.data)
    } catch {
      setError('Failed to fetch recipe. Make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const total = results.reduce((sum, r) => sum + (r.price || 0), 0)

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Recipe to Cart</h1>

      <div className="bg-white rounded-xl shadow p-6 space-y-4">
        <div className="flex gap-3">
          <input
            type="text"
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="e.g. spaghetti bolognese, chicken stir fry..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
          />
          <button
            onClick={handleSearch}
            disabled={loading || !query.trim()}
            className="bg-green-600 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50 transition-colors"
          >
            {loading ? 'Searching...' : 'Find Ingredients'}
          </button>
        </div>

        {error && <p className="text-red-500 text-sm">{error}</p>}

        {results.length > 0 && (
          <div>
            <div className="flex justify-between items-center mb-3">
              <p className="text-sm text-gray-500">{results.length} ingredients found</p>
              <p className="font-semibold text-green-700">Est. total: ${total.toFixed(2)}</p>
            </div>
            <div className="divide-y divide-gray-100">
              {results.map((item, i) => (
                <div key={i} className="flex items-center justify-between py-3">
                  <div>
                    <p className="text-sm font-medium text-gray-800">{item.ingredient}</p>
                    {item.matched_product && (
                      <p className="text-xs text-gray-500">
                        Matched: {item.matched_product}
                        {item.match_score && ` (${item.match_score}% match)`}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-3">
                    {item.price != null ? (
                      <span className="font-semibold text-green-600">${item.price.toFixed(2)}</span>
                    ) : (
                      <span className="text-gray-400 text-xs">No match</span>
                    )}
                    {item.matched_product && (
                      <button
                        onClick={() => addToCart({ id: i, name: item.matched_product, price: item.price })}
                        className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded hover:bg-green-200 transition-colors"
                      >
                        Add
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
