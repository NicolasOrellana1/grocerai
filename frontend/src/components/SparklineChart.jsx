import { LineChart, Line, Tooltip, ResponsiveContainer } from 'recharts'
import { useEffect, useState } from 'react'
import axios from 'axios'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function SparklineChart({ productId }) {
  const [data, setData] = useState([])

  useEffect(() => {
    axios.get(`${API}/prices/${productId}/history`).then(r => {
      setData(r.data.map(p => ({ price: p.price })))
    }).catch(() => {})
  }, [productId])

  if (!data.length) return <span className="text-gray-400 text-xs">No history</span>

  return (
    <ResponsiveContainer width={100} height={32}>
      <LineChart data={data}>
        <Line type="monotone" dataKey="price" stroke="#16a34a" dot={false} strokeWidth={1.5} />
        <Tooltip
          formatter={(v) => [`$${v.toFixed(2)}`, 'Price']}
          contentStyle={{ fontSize: 11 }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
