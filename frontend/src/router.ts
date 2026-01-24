import { createRouter, createWebHistory } from 'vue-router'
import HostListView from './views/HostListView.vue'
import TaskBroadcastView from './views/TaskBroadcastView.vue'
import TaskDetailView from './views/TaskDetailView.vue'
import TaskListView from './views/TaskListView.vue'
import EnvConfigView from './views/EnvConfigView.vue'
import LoginView from './views/LoginView.vue'
import UserListView from './views/UserListView.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { public: true }
  },
  {
    path: '/',
    name: 'Home',
    component: HostListView
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: TaskListView
  },
  {
    path: '/tasks/new',
    name: 'TaskCreate',
    component: TaskBroadcastView
  },
  {
    path: '/tasks/:id',
    name: 'TaskDetail',
    component: TaskDetailView,
    props: true
  },
  {
    path: '/env-configs',
    name: 'EnvConfigs',
    component: EnvConfigView
  },
  {
      path: '/users',
      name: 'Users',
      component: UserListView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

/*
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token')
    if (!to.meta.public && !token) {
        next('/login')
    } else {
        next()
    }
})
*/

export default router
