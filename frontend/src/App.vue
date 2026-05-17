<template>
  <div class="min-h-screen bg-gray-50">
    <TopNav v-if="$route.meta.requiresAuth" />
    <main :class="$route.meta.requiresAuth ? 'h-[calc(100vh-64px)]' : 'h-screen'">
      <router-view />
    </main>
  </div>
</template>

<script>
import TopNav from './components/TopNav.vue'

export default {
  name: 'App',
  components: {
    TopNav
  }
}
</script>
