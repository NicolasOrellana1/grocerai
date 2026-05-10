import { useEffect, useState } from 'react'
import axios from 'axios'
import PriceTable from '../components/PriceTable'
import CartOptimizer from '../components/CartOptimizer'
import useStore from '../store/useStore'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function PriceComparison() {
  const { prices, setPrices, budget } = useStore()
  const [sales, setSales] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      axios.get(`${API}/prices`),
      axios.get(`${API}/prices/sales`),
    ]).then(([pricesRes, salesRes]) => {
      setPrices(pricesRes.data)
      setSales(salesRes.data)
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800">Price Comparison</h1>
        {sales.length > 0 && (
          <span className="bg-red-100 text-red-700 text-xs font-semibold px-3 py-1 rounded-full">
            {sales.length} item{sales.length > 1 ? 's' : ''} on sale
          </span>
        )}
      </div>

      {sales.length > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-4">
          <h2 className="text-sm font-semibold text-green-800 mb-2">Sale Alerts</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
            {sales.map((item, i) => (
              <div key={i} className="bg-white border border-green-100 rounded-lg p-3">
                <p className="font-medium text-gray-800 text-sm">{item.name}</p>
                <p className="text-green-600 font-bold">${item.current_price.toFixed(2)}</p>
                <p className="text-xs text-gray-500">
                  {item.pct_drop}% below 30d avg (${item.avg_30d.toFixed(2)})
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl shadow">
        {loading ? (
          <div className="p-8 text-center text-gray-400">Loading prices...</div>
        ) : (
          <PriceTable prices={prices} />
        )}
      </div>

      <CartOptimizer budget={budget} />
    </div>
  )
}
