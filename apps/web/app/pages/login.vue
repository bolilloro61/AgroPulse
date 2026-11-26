<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-emerald-950 to-slate-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8 px-4">
    <div class="sm:mx-auto sm:w-full sm:max-w-md text-center">
      <NuxtLink to="/" class="inline-flex items-center gap-3 group">
        <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-emerald-500 to-green-400 flex items-center justify-center text-white shadow-lg shadow-emerald-500/30 group-hover:scale-105 transition-transform">
          <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        </div>
        <span class="text-2xl font-black text-white tracking-tight">AgroPulse</span>
      </NuxtLink>
      <h2 class="mt-4 text-2xl sm:text-3xl font-extrabold text-white">
        Iniciar Sesión
      </h2>
      <p class="mt-2 text-sm text-emerald-200/80">
        Accede a tu plataforma de monitoreo y gestión agrícola
      </p>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white/95 backdrop-blur-md py-8 px-6 shadow-2xl rounded-3xl sm:px-10 border border-emerald-100">
        <!-- Error Alert -->
        <div v-if="errorMsg" class="mb-5 p-4 rounded-2xl bg-red-50 border border-red-200 text-red-700 text-xs sm:text-sm flex items-start gap-3">
          <span class="text-lg">⚠️</span>
          <div class="flex-1">{{ errorMsg }}</div>
        </div>

        <form class="space-y-5" @submit.prevent="handleLogin">
          <div>
            <label for="email" class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              Correo Electrónico
            </label>
            <div class="relative">
              <input
                id="email"
                v-model="email"
                name="email"
                type="email"
                autocomplete="email"
                required
                placeholder="productor@agropulse.test"
                class="w-full px-4 py-3 rounded-xl border border-slate-300 bg-slate-50 text-slate-900 placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition-all"
              />
            </div>
          </div>

          <div>
            <label for="password" class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              Contraseña
            </label>
            <div class="relative">
              <input
                id="password"
                v-model="password"
                name="password"
                type="password"
                autocomplete="current-password"
                required
                placeholder="••••••••"
                class="w-full px-4 py-3 rounded-xl border border-slate-300 bg-slate-50 text-slate-900 placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition-all"
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              :disabled="loading"
              class="w-full flex justify-center items-center gap-2 py-3.5 px-4 rounded-xl shadow-lg shadow-emerald-600/30 text-sm font-bold text-white bg-emerald-600 hover:bg-emerald-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 disabled:opacity-60 disabled:cursor-not-allowed transition-all cursor-pointer"
            >
              <svg v-if="loading" class="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>{{ loading ? 'Iniciando sesión...' : 'Iniciar Sesión' }}</span>
            </button>
          </div>
        </form>

        <div class="mt-6 border-t border-slate-200 pt-5 text-center space-y-2">
          <p class="text-xs text-slate-600">
            ¿Aún no tienes una cuenta?
            <NuxtLink to="/register" class="font-bold text-emerald-600 hover:text-emerald-500 transition-colors ml-1">
              Regístrate aquí
            </NuxtLink>
          </p>
          <NuxtLink to="/" class="block text-xs font-medium text-slate-400 hover:text-slate-600 transition-colors">
            ← Volver a la página de inicio
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuth } from '~/composables/useAuth'

const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')

const { login } = useAuth()

const handleLogin = async () => {
  errorMsg.value = ''
  loading.value = true

  try {
    await login(email.value, password.value)
    // Cuando se inicie sesión vuelve a la página de inicio
    await navigateTo('/')
  } catch (err: any) {
    console.error('Error de autenticación:', err)
    if (err.code === 'auth/invalid-credential' || err.code === 'auth/user-not-found' || err.code === 'auth/wrong-password') {
      errorMsg.value = 'Credenciales inválidas. Verifica tu correo y contraseña.'
    } else if (err.code === 'auth/invalid-email') {
      errorMsg.value = 'El formato del correo electrónico no es válido.'
    } else if (err.code === 'auth/too-many-requests') {
      errorMsg.value = 'Demasiados intentos fallidos. Intenta nuevamente en unos minutos.'
    } else {
      errorMsg.value = err.data?.detail || err.message || 'Error al iniciar sesión. Inténtalo nuevamente.'
    }
  } finally {
    loading.value = false
  }
}
</script>
