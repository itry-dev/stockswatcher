import { createRouter, createWebHistory } from 'vue-router'
import Home from './views/Home.vue'
import StockDetails from './components/StockDetails.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/stock/:ticker',
    name: 'StockDetails',
    component: StockDetails,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
