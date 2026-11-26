<template>
  <div class="min-h-screen bg-slate-50 text-slate-800 antialiased font-sans scroll-smooth">
    <header class="sticky top-0 z-40 bg-white/95 backdrop-blur border-b border-emerald-100 shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center space-x-3 cursor-pointer" @click="scrollToSection('hero')">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-green-500 flex items-center justify-center text-white shadow-md shadow-emerald-500/20">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
            <div>
              <div class="flex items-center gap-2">
                <span class="text-xl font-extrabold tracking-tight text-slate-900">AgroPulse</span>
              </div>
              <p class="text-xs text-slate-500 hidden sm:block">Monitoreo & Recomendaciones Agronómicas</p>
            </div>
          </div>

          <nav class="hidden md:flex items-center space-x-1 lg:space-x-2">
            <button
              v-for="nav in navItems"
              :key="nav.id"
              @click="scrollToSection(nav.id)"
              class="px-3.5 py-1.5 rounded-lg text-sm font-medium text-slate-600 hover:text-emerald-700 hover:bg-emerald-50 transition-all flex items-center gap-1.5 cursor-pointer"
            >
              <span>{{ nav.icon }}</span>
              <span>{{ nav.label }}</span>
            </button>

            <!-- Sección de parcelas en el header para usuarios autenticados -->
            <NuxtLink
              v-if="user"
              to="/parcelas"
              class="px-3.5 py-1.5 rounded-lg text-sm font-bold text-emerald-800 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 transition-all flex items-center gap-1.5 cursor-pointer"
            >
              <span>🌱</span>
              <span>Parcelas</span>
            </NuxtLink>
          </nav>

          <div class="flex items-center space-x-2 sm:space-x-3">
            <template v-if="!user">
              <NuxtLink
                to="/login"
                class="px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-semibold text-slate-700 hover:text-emerald-700 hover:bg-slate-100 border border-slate-200 transition-all"
              >
                Iniciar Sesión
              </NuxtLink>

              <NuxtLink
                to="/register"
                class="px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-bold bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm shadow-emerald-600/30 transition-all"
              >
                Registrarse
              </NuxtLink>
            </template>

            <template v-else>
              <div class="hidden sm:flex items-center gap-2 px-3 py-1 bg-emerald-50 border border-emerald-200 rounded-xl">
                <span class="text-xs text-emerald-800 font-bold uppercase tracking-wider">{{ role || 'Usuario' }}</span>
                <span class="text-xs text-slate-500">({{ user.email?.split('@')[0] }})</span>
              </div>

              <button
                @click="showAlertsModal = true"
                class="px-3 py-1.5 rounded-xl text-xs sm:text-sm font-semibold text-slate-700 hover:text-emerald-700 hover:bg-emerald-50 border border-slate-200 transition-all flex items-center gap-1.5 cursor-pointer"
                v-if="hasActiveAlerts"
              >
                <span class="relative">
                  <span class="text-lg">🔔</span>
                  <span class="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
                    {{ alerts.length }}
                  </span>
                </span>
              </button>

              <button
                @click="logout"
                class="px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-semibold text-slate-700 hover:text-red-600 hover:bg-red-50 border border-slate-200 transition-all cursor-pointer"
              >
                Cerrar Sesión
              </button>
            </template>
          </div>
        </div>
      </div>

      <div class="flex md:hidden border-t border-slate-100 overflow-x-auto py-2 px-4 gap-2 bg-slate-50">
        <button
          v-for="nav in navItems"
          :key="nav.id"
          @click="scrollToSection(nav.id)"
          class="px-2.5 py-1 text-xs whitespace-nowrap rounded-md font-medium bg-white text-slate-600 border border-slate-200 hover:bg-emerald-50 hover:text-emerald-700 transition-colors"
        >
          {{ nav.icon }} {{ nav.label }}
        </button>
        <NuxtLink
          v-if="user"
          to="/parcelas"
          class="px-2.5 py-1 text-xs whitespace-nowrap rounded-md font-bold bg-emerald-100 text-emerald-800 border border-emerald-200"
        >
          🌱 Parcelas
        </NuxtLink>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 space-y-16 sm:space-y-24">
      <section id="hero" class="relative overflow-hidden rounded-3xl bg-gradient-to-br from-emerald-950 via-emerald-900 to-teal-950 text-white p-6 sm:p-10 lg:p-12 shadow-2xl">
        <div class="absolute -right-20 -top-20 w-96 h-96 rounded-full bg-emerald-500/20 blur-3xl pointer-events-none"></div>
        <div class="absolute right-1/4 -bottom-20 w-80 h-80 rounded-full bg-teal-400/15 blur-2xl pointer-events-none"></div>

        <div class="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center">
          <div class="lg:col-span-7 space-y-5">
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-400/30 text-emerald-200 text-xs font-semibold">
              <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              Plataforma de Agricultura de Precisión AgroPulse
            </div>

            <h1 class="text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight leading-tight">
              Monitoreo Inteligente & <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-300 via-teal-200 to-green-300">Recomendaciones Agronómicas</span>
            </h1>

            <p class="text-emerald-100/90 text-sm sm:text-base lg:text-lg max-w-2xl leading-relaxed">
              Plataforma web full-stack para el monitoreo de parcelas agrícolas y el análisis continuo de parámetros ambientales (humedad del suelo, temperatura y microclima), orientada a la detección oportuna de anomalías y la generación de recomendaciones transparentes de riego e inspección.
            </p>

            <div class="pt-2 flex flex-wrap items-center gap-3">
              <NuxtLink
                v-if="!user"
                to="/register"
                class="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm transition-all shadow-lg shadow-emerald-500/30 hover:scale-[1.02]"
              >
                <span>Crear Cuenta Gratis</span>
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </NuxtLink>

              <NuxtLink
                v-else
                to="/parcelas"
                class="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm transition-all shadow-lg shadow-emerald-500/30 hover:scale-[1.02]"
              >
                <span>🌱 Ir al Panel de Parcelas</span>
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </NuxtLink>

              <button
                @click="scrollToSection('proposito')"
                class="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-white font-semibold text-sm transition-all backdrop-blur"
              >
                <span>Conocer el Propósito</span>
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              <button
                @click="scrollToSection('recomendaciones')"
                class="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 border border-amber-400/40 text-amber-200 font-semibold text-sm transition-all"
              >
                <span>⚡ Probar Motor Explicable</span>
              </button>
            </div>

            <div class="pt-4 flex flex-wrap items-center gap-6 text-xs text-emerald-200/80 border-t border-white/10">
              <div class="flex items-center gap-2">
                <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <span>Inspección totalmente transparente</span>
              </div>
              <div class="flex items-center gap-2">
                <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <span>Roles para cada nivel de tu organización</span>
              </div>
              <div class="flex items-center gap-2">
                <svg class="w-4 h-4 text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <span class="inline-flex items-center gap-1.5">
                  Persistencia en la nube con
                  <img
                    src="https://upload.wikimedia.org/wikipedia/commons/0/0b/New_Firebase_logo.svg"
                    alt="Firebase"
                    class="h-5 w-auto object-contain inline-block"
                  />
                </span>
              </div>
            </div>
          </div>

          <div class="lg:col-span-5 flex items-center justify-center">
            <img
              src="/images/logo.png"
              alt="AgroPulse"
              class="w-full h-full object-contain rounded-2xl"
            />
          </div>
        </div>
      </section>

      <section id="proposito" class="scroll-mt-24 space-y-8">
        <div class="max-w-3xl">
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold uppercase tracking-wider mb-2">
            Nuestro Propósito
          </div>
          <h2 class="text-2xl sm:text-3xl font-black text-slate-900">
            ¿Por qué existe AgroPulse y qué problemática resuelve?
          </h2>
          <p class="text-sm sm:text-base text-slate-600 mt-2">
            Un análisis directo de los desafíos en campo y la respuesta tecnológica planteada en AgroPulse.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="bg-white rounded-3xl p-6 sm:p-8 border border-red-100 shadow-sm hover:shadow-md transition-all flex flex-col justify-between space-y-4">
            <div class="space-y-4">
              <div class="w-12 h-12 rounded-2xl bg-red-50 text-red-600 flex items-center justify-center text-2xl">
                ⚠️
              </div>
              <h3 class="text-lg font-bold text-slate-900">1. La Problemática Agrícola</h3>
              <p class="text-xs sm:text-sm text-slate-600 leading-relaxed">
                En la gestión agrícola moderna, la falta de monitoreo continuo y sistematizado sobre las condiciones ambientales suele derivar en estrés hídrico, pérdidas por variaciones bruscas de temperatura y uso ineficiente del agua.
              </p>
              <ul class="text-xs text-slate-600 space-y-2 list-disc list-inside bg-red-50/50 p-3 rounded-xl border border-red-100">
                <li>Uso ineficiente o sobre-irrigación de parcelas.</li>
                <li>Pérdidas de cosechas por estrés térmico no advertido.</li>
                <li>Ausencia de una herramienta centralizada e intuitiva.</li>
                <li>Dependencia de automatizaciones o cajas negras a ciegas.</li>
              </ul>
            </div>
            <div class="pt-2 text-[11px] font-semibold text-red-700 uppercase tracking-wider">
              Diagnóstico en campo
            </div>
          </div>

          <div class="bg-white rounded-3xl p-6 sm:p-8 border border-emerald-100 shadow-sm hover:shadow-md transition-all flex flex-col justify-between space-y-4">
            <div class="space-y-4">
              <div class="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center text-2xl">
                🎯
              </div>
              <h3 class="text-lg font-bold text-slate-900">2. El Objetivo General</h3>
              <p class="text-xs sm:text-sm text-slate-600 leading-relaxed">
                Desarrollar una aplicación web full-stack con persistencia en la nube para registrar, consultar y analizar parámetros ambientales por finca y parcela.
              </p>
              <ul class="text-xs text-slate-600 space-y-2 list-disc list-inside bg-emerald-50/50 p-3 rounded-xl border border-emerald-100">
                <li>Gestión integral de fincas, parcelas y cultivos.</li>
                <li>Captura manual en campo e importación masiva de mediciones.</li>
                <li>Monitoreo de series históricas y detección de anomalías.</li>
                <li>Soporte técnico fundamentado para la toma de decisiones.</li>
              </ul>
            </div>
            <div class="pt-2 text-[11px] font-semibold text-emerald-700 uppercase tracking-wider">
              Solución Full-Stack
            </div>
          </div>

          <div class="bg-white rounded-3xl p-6 sm:p-8 border border-blue-100 shadow-sm hover:shadow-md transition-all flex flex-col justify-between space-y-4">
            <div class="space-y-4">
              <div class="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center text-2xl">
                💡
              </div>
              <h3 class="text-lg font-bold text-slate-900">3. El Valor y Transparencia</h3>
              <p class="text-xs sm:text-sm text-slate-600 leading-relaxed">
                A diferencia de sistemas cerrados que entregan predicciones opacas, AgroPulse se enfoca en la explicabilidad: el productor y el técnico siempre conocen el fundamento exacto de cada sugerencia.
              </p>
              <ul class="text-xs text-slate-600 space-y-2 list-disc list-inside bg-blue-50/50 p-3 rounded-xl border border-blue-100">
                <li>Justificación explícita de mediciones y tendencias.</li>
                <li>Bitácora de atención técnica con observaciones.</li>
                <li>Roles diferenciados: Productor y Técnico Supervisor.</li>
                <li>Control total sobre umbrales y reglas agronómicas.</li>
              </ul>
            </div>
            <div class="pt-2 text-[11px] font-semibold text-blue-700 uppercase tracking-wider">
              Explicabilidad Agronómica
            </div>
          </div>
        </div>
      </section>

      <section id="enfoque" class="scroll-mt-24 space-y-8">
        <div class="max-w-3xl">
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-100 text-blue-800 text-xs font-bold uppercase tracking-wider mb-2">
            Enfoque del Proyecto
          </div>
          <h2 class="text-2xl sm:text-3xl font-black text-slate-900">
            Pilares Técnicos y Alcance del Producto
          </h2>
          <p class="text-sm sm:text-base text-slate-600 mt-2">
            Estructuración de capacidades clave acordadas para la plataforma AgroPulse.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="pilar in pilaresEnfoque"
            :key="pilar.titulo"
            class="bg-white rounded-3xl p-6 border border-slate-200/90 shadow-sm hover:border-emerald-300 hover:shadow-md transition-all space-y-3"
          >
            <div class="flex items-center justify-between">
              <span class="text-3xl">{{ pilar.icono }}</span>
              <span class="px-2.5 py-0.5 text-xs font-bold rounded-full" :class="pilar.badgeClass">
                {{ pilar.tag }}
              </span>
            </div>
            <h3 class="text-base font-bold text-slate-900">{{ pilar.titulo }}</h3>
            <p class="text-xs sm:text-sm text-slate-600 leading-relaxed">{{ pilar.descripcion }}</p>
            <div class="pt-2 border-t border-slate-100">
              <span class="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Capacidad Clave:</span>
              <p class="text-xs font-medium text-emerald-800 mt-0.5">{{ pilar.mecanismo }}</p>
            </div>
          </div>
        </div>
      </section>

      <section id="recomendaciones" class="scroll-mt-24 bg-white rounded-3xl p-6 sm:p-10 border border-emerald-200 shadow-sm space-y-8">
        <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-200 pb-6">
          <div class="max-w-2xl">
            <div class="inline-flex items-center gap-2 px-3 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-200 mb-2">
              Componente Innovador
            </div>
            <h2 class="text-2xl sm:text-3xl font-black text-slate-900">
              Calculadora de Recomendaciones Agronómicas
            </h2>
            <p class="text-xs sm:text-sm text-slate-600 mt-1 leading-relaxed">
              Módulo algorítmico que evalúa las condiciones climáticas y la dinámica del suelo para emitir recomendaciones transparentes, indicando exactamente qué regla disparó la sugerencia.
            </p>
          </div>
          <div class="bg-emerald-50 px-4 py-2 rounded-2xl border border-emerald-200 text-xs font-semibold text-emerald-800">
            Transparencia y Criterio Agronómico
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          <div class="lg:col-span-5 bg-slate-50 rounded-2xl p-6 border border-slate-200 space-y-5">
            <div class="flex items-center justify-between">
              <h3 class="text-xs font-bold text-slate-800 uppercase tracking-wider">Probar Lectura Agronómica</h3>
              <span class="text-[11px] font-semibold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded">Interactivo</span>
            </div>

            <div>
              <label class="block text-xs font-bold text-slate-700 mb-1.5">Cultivo Objetivo:</label>
              <select
                v-model="simulacion.cropId"
                :disabled="cultivos.length === 0"
                class="w-full bg-white border border-slate-300 rounded-xl px-3 py-2 text-xs sm:text-sm text-slate-800 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
              >
                <option v-for="crop in cultivos" :key="crop.id" :value="crop.id">
                  {{ crop.name }} (Óptimo: {{ crop.thresholds.humidity.min }}-{{ crop.thresholds.humidity.max }}% hum,
                  {{ crop.thresholds.temperature.min }}-{{ crop.thresholds.temperature.max }}°C)
                </option>
              </select>
              <p v-if="errorCalculadora" role="alert" class="mt-2 text-xs text-red-700">
                {{ errorCalculadora }}
              </p>
            </div>

            <div>
              <div class="flex justify-between items-center text-xs font-semibold text-slate-700 mb-1.5">
                <span>Humedad del Suelo:</span>
                <span class="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold font-mono">{{ simulacion.humedad }}%</span>
              </div>
              <input
                v-model.number="simulacion.humedad"
                type="range"
                min="10"
                max="95"
                class="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-emerald-600"
              />
              <div class="flex justify-between text-[11px] text-slate-400 mt-1">
                <span>10% (Estrés seco)</span>
                <span>50%</span>
                <span>95% (Saturado)</span>
              </div>
            </div>

            <div>
              <div class="flex justify-between items-center text-xs font-semibold text-slate-700 mb-1.5">
                <span>Temperatura Ambiental:</span>
                <span class="px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-bold font-mono">{{ simulacion.temperatura }}°C</span>
              </div>
              <input
                v-model.number="simulacion.temperatura"
                type="range"
                min="0"
                max="45"
                class="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-amber-600"
              />
              <div class="flex justify-between text-[11px] text-slate-400 mt-1">
                <span>0°C (Helada)</span>
                <span>25°C</span>
                <span>45°C (Ola de calor)</span>
              </div>
            </div>

            <div>
              <label class="block text-xs font-bold text-slate-700 mb-1.5">Tendencia de las últimas 6 horas:</label>
              <select
                v-model="simulacion.tendencia"
                class="w-full bg-white border border-slate-300 rounded-xl px-3 py-2 text-xs sm:text-sm text-slate-800 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
              >
                <option value="caida_brusca">Caída brusca de humedad (-15% en 6h)</option>
                <option value="estable">Condiciones estables</option>
                <option value="alza_temperatura">Alza térmica pronunciada (+8°C)</option>
              </select>
            </div>
          </div>

          <div class="lg:col-span-7 bg-emerald-950 text-white rounded-2xl p-6 sm:p-8 border border-emerald-800/80 shadow-inner space-y-5">
            <div class="flex items-center justify-between border-b border-emerald-800/80 pb-3">
              <span class="text-xs text-emerald-400 font-mono uppercase tracking-wider flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                Resultado Generado por el Motor Explicable
              </span>
              <span class="px-2.5 py-1 text-xs font-bold rounded-lg" :class="simulacionResultado.badgeColor">
                {{ simulacionResultado.nivel }}
              </span>
            </div>

            <div class="space-y-1.5">
              <span class="text-xs text-emerald-300 font-bold uppercase tracking-wider">Acción Agronómica Sugerida:</span>
              <p class="text-lg sm:text-xl font-extrabold text-white leading-snug">{{ simulacionResultado.accion }}</p>
            </div>

            <div class="bg-emerald-900/60 rounded-xl p-4 border border-emerald-700/60 space-y-2">
              <div class="flex items-center gap-1.5 text-xs text-emerald-200 font-bold uppercase">
                <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>Justificación Transparente (Regla Disparadora):</span>
              </div>
              <p class="text-xs sm:text-sm text-emerald-100 font-mono leading-relaxed">
                {{ simulacionResultado.explicacion }}
              </p>
            </div>

            <div class="grid grid-cols-3 gap-2 pt-3 text-[11px] text-emerald-300/80 border-t border-emerald-800/80">
              <div>
                <span class="text-slate-400 block">Cultivo:</span>
                <span class="font-medium text-white">{{ cultivoSeleccionado?.name || 'Cargando catálogo...' }}</span>
              </div>
              <div>
                <span class="text-slate-400 block">Humedad / Temp:</span>
                <span class="font-medium text-white">{{ simulacion.humedad }}% | {{ simulacion.temperatura }}°C</span>
              </div>
              <div>
                <span class="text-slate-400 block">Lógica:</span>
                <span class="font-medium text-emerald-300">Reglas + Tendencia</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="rounded-3xl bg-gradient-to-r from-emerald-800 via-emerald-700 to-teal-800 text-white p-8 sm:p-12 text-center space-y-5 shadow-xl">
        <h2 class="text-2xl sm:text-4xl font-black">
          ¿Listo para optimizar la gestión de tus cultivos?
        </h2>
        <p class="text-emerald-100 text-sm sm:text-base max-w-2xl mx-auto leading-relaxed">
          AgroPulse está diseñado para empoderar a productores y técnicos supervisores con datos claros, alertas oportunas y soporte transparente en cada ciclo de riego.
        </p>
        <div class="pt-2 flex flex-wrap justify-center gap-3">
          <NuxtLink
            v-if="!user"
            to="/register"
            class="px-6 py-3 rounded-xl bg-white text-emerald-900 font-bold text-sm hover:bg-emerald-50 transition-all shadow-lg shadow-black/10 hover:scale-105"
          >
            Registrarse en la Plataforma
          </NuxtLink>
          <NuxtLink
            v-if="!user"
            to="/login"
            class="px-6 py-3 rounded-xl bg-emerald-900/40 hover:bg-emerald-900/60 border border-white/20 text-white font-semibold text-sm transition-all"
          >
            Iniciar Sesión
          </NuxtLink>
          <NuxtLink
            v-else
            to="/parcelas"
            class="px-6 py-3 rounded-xl bg-white text-emerald-900 font-bold text-sm hover:bg-emerald-50 transition-all shadow-lg shadow-black/10 hover:scale-105"
          >
            Ver mis Parcelas ({{ role }})
          </NuxtLink>
        </div>
      </section>
    </main>

    <footer class="bg-white border-t border-slate-200 mt-16 py-8">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
        <div class="flex items-center gap-2">
          <span class="font-bold text-slate-800">AgroPulse</span>
          <span>•</span>
          <span>Plataforma de Agricultura de Precisión</span>
        </div>
        <div>
          <span>Monitoreo & Recomendaciones Agronómicas Explicables</span>
        </div>
      </div>
    </footer>

    <div v-if="showAlertsModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:p-4 sm:p-left">
        <div class="fixed inset-0 bg-black/50 transition-opacity" @click="showAlertsModal = false"></div>
        <div class="inline-block w-full max-w-2xl transform overflow-hidden rounded-2xl bg-white text-left shadow-xl transition-all">
          <div class="bg-emerald-50 px-6 py-4 border-b border-emerald-200">
            <h3 class="text-lg font-bold text-slate-900 flex items-center gap-2">
              <span class="text-2xl">🔔</span>
              Alertas Activas
            </h3>
          </div>
          <div class="px-6 py-4 max-h-96 overflow-y-auto">
            <div v-if="alertsLoading" class="text-center py-8">
              <span class="text-slate-500">Cargando alertas...</span>
            </div>
            <div v-else-if="alerts.length === 0" class="text-center py-8">
              <p class="text-slate-500">No hay alertas activas en tus parcelas.</p>
            </div>
            <div v-else class="space-y-4">
              <div
                v-for="alert in alerts"
                :key="alert.farmId + alert.plot.id"
                class="border rounded-xl p-4 hover:shadow-sm transition-all"
                :class="alert.averageStatus.status === 'risk' ? 'border-red-300 bg-red-50/50' : 'border-slate-200'"
              >
                <div class="flex items-start gap-3">
                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-1">
                      <span class="font-bold text-slate-900">{{ alert.farmName }}</span>
                      <span class="text-xs text-slate-500">•</span>
                      <span class="text-xs font-medium text-slate-600">{{ alert.plot.name }}</span>
                    </div>
                    <div class="text-xs text-slate-500 mb-2">
                      Cultivo: {{ alert.plot.cropId }}
                    </div>
                    <div class="flex items-center gap-2 mb-2">
                      <span
                        class="px-2 py-0.5 text-xs font-semibold rounded"
                        :class="alertBadgeClass(alert.recommendation.tipo)"
                      >
                        {{ alert.recommendation.nivel }}
                      </span>
                      <span
                        class="px-2 py-0.5 text-xs font-semibold rounded"
                        :class="[alert.averageStatus.claseEstado, alert.averageStatus.claseTexto]"
                      >
                        {{ alert.averageStatus.icono }} Promedio: {{ alert.averageStatus.estado }}
                      </span>
                    </div>
                    <p class="text-xs text-slate-600 mb-2">
                      {{ alert.averageStatus.tendencia }}. {{ alert.averageStatus.consejo }}
                    </p>
                    <p class="text-sm text-slate-700 mb-1 font-medium">{{ alert.recommendation.accion }}</p>
                    <p class="text-xs text-slate-600">{{ alert.recommendation.explicacion }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-6 py-4 border-t border-gray-200 rounded-b-2xl flex justify-end gap-3">
            <button
              @click="showAlertsModal = false"
              class="px-4 py-2 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-100 transition-colors"
            >
              Cerrar
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useAuth } from '~/composables/useAuth'
import { useRecommendation, type CropOption, type RecommendationResult } from '~/composables/useRecommendation'
import { useAlerts } from '~/composables/useAlerts'

const { user, role, logout } = useAuth()
const { getCrops, evaluateMeasurement } = useRecommendation()
const { alerts, hasActiveAlerts, fetchFarmsAndCheckAlerts, loading: alertsLoading } = useAlerts()

const showAlertsModal = ref(false)

const alertBadgeClass = (tipo: string) => {
  const classes: Record<string, string> = {
    helada: 'bg-indigo-100 text-indigo-800 border border-indigo-200',
    advertencia: 'bg-amber-100 text-amber-800 border border-amber-200',
    critico: 'bg-red-100 text-red-800 border border-red-200',
    precaucion: 'bg-yellow-100 text-yellow-800 border border-yellow-200'
  }
  return classes[tipo] || 'bg-gray-100 text-gray-800 border border-gray-200'
}

const navItems = [
  { id: 'proposito', label: 'Propósito', icon: '🎯' },
  { id: 'enfoque', label: 'Enfoque', icon: '🔬' },
  { id: 'recomendaciones', label: 'Innovación', icon: '⚡' },
]

const scrollToSection = (id: string) => {
  const element = document.getElementById(id)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

const pilaresEnfoque = [
  {
    titulo: 'Motor de Recomendaciones Explicables',
    icono: '🧠',
    tag: 'Innovación Core',
    badgeClass: 'bg-amber-100 text-amber-800 border border-amber-200',
    descripcion: 'Algoritmo agronómico que evalúa reglas por cultivo y tendencias recientes para sugerir riego e inspección.',
    mecanismo: 'Regla + Tendencia + Justificación explícita'
  },
  {
    titulo: 'Monitoreo y Ciclo de Alertas',
    icono: '📈',
    tag: 'Operativo',
    badgeClass: 'bg-emerald-100 text-emerald-800 border border-emerald-200',
    descripcion: 'Detección oportuna de lecturas fuera de rango o caídas bruscas, con flujo de atención y bitácora técnica de resolución.',
    mecanismo: 'Umbrales dinámicos por parcela'
  },
  {
    titulo: 'Ingesta Dual de Datos (Manual + CSV)',
    icono: '📥',
    tag: 'Flexibilidad',
    badgeClass: 'bg-blue-100 text-blue-800 border border-blue-200',
    descripcion: 'Captura manual rápida para operadores en campo e importación masiva por archivo CSV con validación estricta de datos.',
    mecanismo: 'Procesamiento y validación estricta'
  },
  {
    titulo: 'Control de Acceso Basado en Roles',
    icono: '🛡️',
    tag: 'Seguridad',
    badgeClass: 'bg-purple-100 text-purple-800 border border-purple-200',
    descripcion: 'Dos perfiles especializados: Productor (lectura/registro operativo) y Técnico Supervisor (parametrización y motor de sugerencias).',
    mecanismo: 'Permisos diferenciados por rol'
  },
  {
    titulo: 'Gestión Jerárquica de Entidades',
    icono: '🗺️',
    tag: 'Catálogo',
    badgeClass: 'bg-teal-100 text-teal-800 border border-teal-200',
    descripcion: 'Estructuración clara de Fincas -> Parcelas -> Cultivos -> Sensores, permitiendo parametrizar rangos ideales por especie.',
    mecanismo: 'Parámetros y umbrales por cultivo'
  },
  {
    titulo: 'Transparencia y Explicabilidad Agronómica',
    icono: '⚡',
    tag: 'Diferenciador',
    badgeClass: 'bg-rose-100 text-rose-800 border border-rose-200',
    descripcion: 'Generación de sugerencias fundamentadas donde cada acción técnica explica con exactitud la causa que la disparó.',
    mecanismo: 'Trazabilidad completa de sugerencias'
  }
]

const simulacion = ref({
  cropId: 'tomate-saladette',
  humedad: 32,
  temperatura: 31,
  tendencia: 'caida_brusca'
})

const cultivos = ref<CropOption[]>([])
const errorCalculadora = ref('')
const recomendacion = ref<RecommendationResult | null>(null)
const catalogoListo = ref(false)

const simulacionSituaciones: Record<string, string> = {
  caida_brusca: 'Caída brusca de humedad (-15%)',
  alza_temperatura: 'Alza térmica pronunciada (+8°C)',
  estable: 'Condición estable'
}

const simulacionBadgeColors: Record<RecommendationResult['tipo'], string> = {
  helada: 'bg-indigo-600/30 text-indigo-200 border border-indigo-400/50',
  advertencia: 'bg-amber-500/20 text-amber-300 border border-amber-500/30',
  critico: 'bg-red-500/20 text-red-300 border border-red-500/30',
  precaucion: 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30',
  optimo: 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
}

const cultivoSeleccionado = computed(() =>
  cultivos.value.find(crop => crop.id === simulacion.value.cropId)
)

const simulacionResultado = computed(() => {
  if (!recomendacion.value) {
    return {
      nivel: catalogoListo.value ? 'Consultando el motor...' : 'Cargando catálogo...',
      tipo: 'optimo' as const,
      badgeColor: simulacionBadgeColors.optimo,
      accion: 'La recomendación se calculará en el backend.',
      explicacion: 'La API de AgroPulse evalúa el cultivo y los parámetros seleccionados.'
    }
  }

  return {
    ...recomendacion.value,
    badgeColor: simulacionBadgeColors[recomendacion.value.tipo]
  }
})

let latestRequest = 0
let recommendationTimer: ReturnType<typeof setTimeout> | undefined

const solicitarRecomendacion = async () => {
  if (!simulacion.value.cropId) return
  const requestId = ++latestRequest
  try {
    const result = await evaluateMeasurement(
      simulacion.value.cropId,
      Number(simulacion.value.humedad),
      Number(simulacion.value.temperatura),
      simulacionSituaciones[simulacion.value.tendencia] || simulacionSituaciones.estable
    )
    if (requestId === latestRequest) {
      recomendacion.value = result
      errorCalculadora.value = ''
    }
  } catch (error) {
    console.error('Error al solicitar recomendación al backend:', error)
    if (requestId === latestRequest) {
      recomendacion.value = null
      errorCalculadora.value = 'No se pudo consultar la API. Comprueba que el backend esté encendido.'
    }
  }
}

watch(simulacion, () => {
  if (!catalogoListo.value) return
  if (recommendationTimer) clearTimeout(recommendationTimer)
  recommendationTimer = setTimeout(() => {
    void solicitarRecomendacion()
  }, 250)
}, { deep: true })

onMounted(async () => {
  try {
    cultivos.value = await getCrops()
    if (!cultivos.value.some(crop => crop.id === simulacion.value.cropId)) {
      simulacion.value.cropId = cultivos.value[0]?.id || ''
    }
    catalogoListo.value = true
    if (simulacion.value.cropId) await solicitarRecomendacion()
    if (cultivos.value.length === 0) {
      errorCalculadora.value = 'El catálogo de cultivos está vacío en Firebase.'
    }
  } catch (error) {
    console.error('Error al cargar cultivos desde el backend:', error)
    errorCalculadora.value = 'No se pudo cargar el catálogo. Comprueba que el backend y Firebase estén configurados.'
  }

  if (user.value) {
    await fetchFarmsAndCheckAlerts()
  }
})

watch(user, async (newUser) => {
  if (newUser) {
    await fetchFarmsAndCheckAlerts()
  } else {
    alerts.value = []
  }
})

onUnmounted(() => {
  if (recommendationTimer) clearTimeout(recommendationTimer)
})
</script>
