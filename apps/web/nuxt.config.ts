// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: ['@nuxtjs/tailwindcss'],
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
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
