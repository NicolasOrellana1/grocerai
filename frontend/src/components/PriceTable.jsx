import SparklineChart from './SparklineChart'

export default function PriceTable({ prices }) {
  const stores = [...new Set(prices.map(p => p.store))]

  const byProduct = {}
  for (const p of prices) {
    if (!byProduct[p.name]) byProduct[p.name] = { product_id: p.product_id, name: p.name, stores: {} }
    byProduct[p.name].stores[p.store] = p.current_price
  }

  const rows = Object.values(byProduct)

  if (!rows.length) {
    return <p className="text-gray-500 text-sm">No price data available yet. Run the scraper first.</p>
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-left font-semibold text-gray-600">Product</th>
            {stores.map(s => (
              <th key={s} className="px-4 py-3 text-left font-semibold text-gray-600 capitalize">{s}</th>
            ))}
            <th className="px-4 py-3 text-left font-semibold text-gray-600">Lowest</th>
            <th className="px-4 py-3 text-left font-semibold text-gray-600">30d Trend</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100 bg-white">
          {rows.map((row) => {
            const storeValues = Object.values(row.stores).filter(Boolean)
            const lowest = storeValues.length ? Math.min(...storeValues) : null
            return (
              <tr key={row.name} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-gray-800">{row.name}</td>
                {stores.map(s => (
                  <td key={s} className="px-4 py-3 text-gray-700">
                    {row.stores[s] != null ? (
                      <span className={row.stores[s] === lowest ? 'text-green-600 font-semibold' : ''}>
                        ${row.stores[s].toFixed(2)}
                      </span>
                    ) : '—'}
                  </td>
                ))}
                <td className="px-4 py-3 text-green-600 font-semibold">
                  {lowest != null ? `$${lowest.toFixed(2)}` : '—'}
                </td>
                <td className="px-4 py-3">
                  <SparklineChart productId={row.product_id} />
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
