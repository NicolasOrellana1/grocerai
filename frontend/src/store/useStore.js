import { create } from 'zustand'

const useStore = create((set) => ({
  prices: [],
  cart: [],
  budget: 50.00,
  mealPlan: null,
  pipelineStatus: {},
  setPrices: (prices) => set({ prices }),
  addToCart: (item) => set((s) => ({ cart: [...s.cart, item] })),
  removeFromCart: (id) => set((s) => ({ cart: s.cart.filter(i => i.id !== id) })),
  setBudget: (budget) => set({ budget }),
  setMealPlan: (plan) => set({ mealPlan: plan }),
  setPipelineStatus: (status) => set({ pipelineStatus: status }),
}))

export default useStore
