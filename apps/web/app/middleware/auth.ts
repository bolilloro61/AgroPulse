export default defineNuxtRouteMiddleware(async (to) => {
  const { user, isAuthReady } = useAuth()
  
  if (import.meta.client) {
    if (!isAuthReady.value) {
      await new Promise<void>((resolve) => {
        const stop = watch(isAuthReady, (ready) => {
          if (ready) {
            stop()
            resolve()
          }
        }, { immediate: true })
      })
    }
  }

  if (!user.value) {
    return navigateTo({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  }
})

