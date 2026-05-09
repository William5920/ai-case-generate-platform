import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    user: null,
    token: localStorage.getItem('token') || null,
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
    },
    SET_TOKEN(state, token) {
      state.token = token
      localStorage.setItem('token', token)
      state.isLoggedIn = true
    },
    LOGOUT(state) {
      state.user = null
      state.token = null
      state.isLoggedIn = false
      localStorage.removeItem('token')
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
    login({ commit }, { user, token }) {
      commit('SET_USER', user)
      commit('SET_TOKEN', token)
    },
    logout({ commit }) {
      commit('LOGOUT')
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
