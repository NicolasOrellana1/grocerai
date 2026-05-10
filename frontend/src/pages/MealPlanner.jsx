import { useState } from 'react'
import axios from 'axios'
import BudgetProgress from '../components/BudgetProgress'
import useStore from '../store/useStore'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
const MEALS = ['breakfast', 'lunch', 'dinner']

export default function MealPlanner() {
  const { budget, mealPlan, setMealPlan } = useStore()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleGenerate = async () => {
    setLoading(true)
    setError(null)
    try {
      const resp = await axios.post(`${API}/optimize/meal-plan`, { budget })
      setMealPlan(resp.data)
    } catch {
      setError('Failed to generate meal plan. Check your Spoonacular API key.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800">7-Day Meal Planner</h1>
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="bg-green-600 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50 transition-colors"
        >
          {loading ? 'Generating...' : 'Generate Plan'}
        </button>
      </div>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      {mealPlan && (
        <>
          <div className="bg-white rounded-xl shadow overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left font-semibold text-gray-600 w-24">Meal</th>
                  {DAYS.map(d => (
                    <th key={d} className="px-4 py-3 text-left font-semibold text-gray-600 capitalize">{d.slice(0, 3)}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {MEALS.map(meal => (
                  <tr key={meal}>
                    <td className="px-4 py-3 font-medium text-gray-700 capitalize">{meal}</td>
                    {DAYS.map(day => (
                      <td key={day} className="px-4 py-3 text-gray-600 text-xs max-w-32">
                        {mealPlan.meals?.[day]?.[meal] || '—'}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="bg-white rounded-xl shadow p-6 space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-semibold text-gray-800">Consolidated Grocery List</h2>
              <span className="text-green-700 font-bold text-lg">${mealPlan.total_cost?.toFixed(2)}</span>
            </div>
            <BudgetProgress spent={mealPlan.total_cost || 0} budget={budget} />
            <div className="divide-y divide-gray-100">
              {(mealPlan.grocery_list || []).map((item, i) => (
                <div key={i} className="flex justify-between py-2 text-sm">
                  <span className="text-gray-700">{item.name}</span>
                  <span className="font-medium">${item.price?.toFixed(2)}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {!mealPlan && !loading && (
        <div className="bg-white rounded-xl shadow p-12 text-center text-gray-400">
          Click "Generate Plan" to create a 7-day meal plan within your ${budget} budget.
        </div>
      )}
    </div>
  )
}
