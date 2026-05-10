import { NavLink } from 'react-router-dom'

const links = [
  { to: '/prices', label: 'Price Comparison' },
  { to: '/recipes', label: 'Recipe to Cart' },
  { to: '/meal-planner', label: 'Meal Planner' },
  { to: '/pipeline', label: 'Pipeline Monitor' },
]

export default function Navbar() {
  return (
    <nav className="bg-green-700 text-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center gap-8">
        <span className="font-bold text-xl tracking-tight">GroceryAI</span>
        <div className="flex gap-4">
          {links.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `text-sm font-medium px-3 py-1 rounded transition-colors ${
                  isActive ? 'bg-green-900' : 'hover:bg-green-600'
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </div>
      </div>
    </nav>
  )
}
