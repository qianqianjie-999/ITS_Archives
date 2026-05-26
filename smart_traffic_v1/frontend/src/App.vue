<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

onMounted(async () => {
  userStore.initFromStorage()
  if (localStorage.getItem('token')) {
    await userStore.fetchCurrentUser()
  }
})
</script>

<style lang="scss">
@import './styles/global.scss';
</style>