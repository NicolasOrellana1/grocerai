export default function BudgetProgress({ spent, budget }) {
  const pct = Math.min((spent / budget) * 100, 100)
  const color = pct > 90 ? 'bg-red-500' : pct > 70 ? 'bg-yellow-500' : 'bg-green-500'

  return (
    <div className="w-full">
      <div className="flex justify-between text-sm mb-1">
        <span className="font-medium">${spent.toFixed(2)} spent</span>
        <span className="text-gray-500">${budget.toFixed(2)} budget</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-3">
        <div
          className={`${color} h-3 rounded-full transition-all duration-300`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <p className="text-xs text-gray-500 mt-1">${(budget - spent).toFixed(2)} remaining</p>
    </div>
  )
}
