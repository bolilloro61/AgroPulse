// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  ssr: false,
  modules: ['@nuxtjs/tailwindcss'],
  compatibilityDate: '2025-07-15',
  devtools: { enabled: false },
  vite: {
    optimizeDeps: {
      include: [
        'firebase/app',
        'firebase/auth',
        'firebase/firestore'
      ]
    }
  },
  runtimeConfig: {
    public: {
      firebaseApiKey: process.env.NUXT_PUBLIC_FIREBASE_API_KEY || 'AIzaSyCW7OMGhKSL5JRXpso0p8rfxdPfXrlX8kw',
      firebaseAuthDomain: process.env.NUXT_PUBLIC_FIREBASE_AUTH_DOMAIN || 'agropulse-da94e.firebaseapp.com',
      firebaseProjectId: process.env.NUXT_PUBLIC_FIREBASE_PROJECT_ID || 'agropulse-da94e',
      firebaseStorageBucket: process.env.NUXT_PUBLIC_FIREBASE_STORAGE_BUCKET || 'agropulse-da94e.firebasestorage.app',
      firebaseMessagingSenderId: process.env.NUXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || '204509694716',
      firebaseAppId: process.env.NUXT_PUBLIC_FIREBASE_APP_ID || '1:204509694716:web:f68ffb0ecef8545c43a579',
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
    }
  },
  app: {
    head: {
      title: 'AgroPulse / AgroScan - Monitoreo y Recomendaciones Agronómicas',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        {
          name: 'description',
          content: 'Plataforma web para el monitoreo de parcelas agrícolas, análisis de parámetros ambientales y recomendaciones agronómicas transparentes.'
        }
      ]
    }
  }
})
