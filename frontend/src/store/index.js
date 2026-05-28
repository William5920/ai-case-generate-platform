import Vue from 'vue'
import Vuex from 'vuex'
import { authAPI } from '../api'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    token: localStorage.getItem('token') || null,
    refreshToken: localStorage.getItem('refreshToken') || null,
    isLoggedIn: !!localStorage.getItem('token'),
    requirements: [],
    currentRequirement: null,
    mindMapData: null,
    tasks: [],
    knowledgeBase: []
  },
  mutations: {
    SET_USER(state, user) {
      state.user = user
      localStorage.setItem('user', JSON.stringify(user))
    },
    SET_TOKEN(state, token) {
      state.token = token
      localStorage.setItem('token', token)
      state.isLoggedIn = true
    },
    SET_REFRESH_TOKEN(state, refreshToken) {
      state.refreshToken = refreshToken
      if (refreshToken) {
        localStorage.setItem('refreshToken', refreshToken)
      } else {
        localStorage.removeItem('refreshToken')
      }
    },
    LOGOUT(state) {
      state.user = null
      state.token = null
      state.refreshToken = null
      state.isLoggedIn = false
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('user')
    },
    SET_REQUIREMENTS(state, requirements) {
      state.requirements = requirements
    },
    SET_CURRENT_REQUIREMENT(state, requirement) {
      state.currentRequirement = requirement
    },
    SET_MIND_MAP_DATA(state, data) {
      state.mindMapData = data
    },
    SET_TASKS(state, tasks) {
      state.tasks = tasks
    },
    SET_KNOWLEDGE_BASE(state, docs) {
      state.knowledgeBase = docs
    }
  },
  actions: {
    login({ commit }, { user, token, refreshToken }) {
      commit('SET_USER', user)
      commit('SET_TOKEN', token)
      if (refreshToken) {
        commit('SET_REFRESH_TOKEN', refreshToken)
      }
    },
    async logout({ commit, state }) {
      try {
        if (state.refreshToken) {
          await authAPI.logout({ refreshToken: state.refreshToken })
        }
      } catch (e) {
        console.error('Logout API failed:', e)
      } finally {
        commit('LOGOUT')
      }
    },
    setRequirements({ commit }, requirements) {
      commit('SET_REQUIREMENTS', requirements)
    },
    setCurrentRequirement({ commit }, requirement) {
      commit('SET_CURRENT_REQUIREMENT', requirement)
    },
    setMindMapData({ commit }, data) {
      commit('SET_MIND_MAP_DATA', data)
    },
    setTasks({ commit }, tasks) {
      commit('SET_TASKS', tasks)
    },
    setKnowledgeBase({ commit }, docs) {
      commit('SET_KNOWLEDGE_BASE', docs)
    }
  },
  getters: {
    user: state => state.user,
    token: state => state.token,
    isLoggedIn: state => state.isLoggedIn,
    requirements: state => state.requirements,
    currentRequirement: state => state.currentRequirement,
    mindMapData: state => state.mindMapData,
    tasks: state => state.tasks,
    knowledgeBase: state => state.knowledgeBase
  }
})
