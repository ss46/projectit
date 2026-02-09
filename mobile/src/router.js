import { createRouter, createWebHistory } from 'vue-router'
import { sessionResource } from './data/session'
import { userResource } from '@/data/user'
import { createResource } from 'frappe-ui'

const routes = [
  {
    path: '/',
    redirect: { name: 'Home' },
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/pages/Home.vue'),
  },
  {
    path : '/workit',
    name : 'WorkIT',
    component : () => import('@/pages/WorkIT.vue'),
  },
  {
    path : '/manageit',
    name : 'ManageIT',
    component : () => import('@/pages/ManageIT.vue'),
  },
  {
    path : '/manageit/edit-instructions/:project_name',
    name : 'EditInstructions',
    component : () => import('@/pages/EditInstructions.vue'),
  },
  {
    path : '/manageit/allocate-employees/:project_name',
    name : 'AllocateEmployees',
    component : () => import('@/pages/AllocateEmployees.vue'),
  },
]

let router = createRouter({
  history: createWebHistory('/projectit'),
  routes,
})

router.beforeEach(async (to, from, next) => {
  sessionResource.fetch()
  if (sessionResource.loading) {
    try {
      await sessionResource.promise
    } catch {
      const redirect = encodeURIComponent(`/projectit${to.fullPath}`)
      window.location.href = `/login?redirect-to=${redirect}`
      return
    }
  }

  if (!sessionResource.data) {
    const redirect = encodeURIComponent(`/projectit${to.fullPath}`)
    window.location.href = `/login?redirect-to=${redirect}`
    return
  }

  if (to.name === 'Home') {
    next()
    return
  }

  const mobileModules = createResource({
    type: 'POST',
    url: 'projectit.api.get_modules_for_router',
  })

  await mobileModules.fetch()

  const routeKey = to.name.toLowerCase()
  const allowed = mobileModules.data?.includes(routeKey)
  
  if (!allowed) {
    next({ name: 'Home' })
    return
  }

  next()
})

export default router