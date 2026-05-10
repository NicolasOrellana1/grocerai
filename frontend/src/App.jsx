import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar'
import PriceComparison from './pages/PriceComparison'
import RecipeToCart from './pages/RecipeToCart'
import MealPlanner from './pages/MealPlanner'
import PipelineMonitor from './pages/PipelineMonitor'

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="max-w-7xl mx-auto px-4 py-6">
          <Routes>
            <Route path="/" element={<Navigate to="/prices" replace />} />
            <Route path="/prices" element={<PriceComparison />} />
            <Route path="/recipes" element={<RecipeToCart />} />
            <Route path="/meal-planner" element={<MealPlanner />} />
            <Route path="/pipeline" element={<PipelineMonitor />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
