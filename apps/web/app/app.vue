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
            <button
              v-if="user"
              @click="abrirModalParcelas"
              class="px-3.5 py-1.5 rounded-lg text-sm font-bold text-emerald-800 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 transition-all flex items-center gap-1.5 cursor-pointer"
            >
              <span>🌱</span>
              <span>Parcelas</span>
            </button>
          </nav>

          <div class="flex items-center space-x-2 sm:space-x-3">
            <template v-if="!user">
              <button
                @click="abrirAuthModal('login')"
                class="px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-semibold text-slate-700 hover:text-emerald-700 hover:bg-slate-100 border border-slate-200 transition-all cursor-pointer"
              >
                Iniciar Sesión
              </button>

              <button
                @click="abrirAuthModal('registro')"
                class="px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-bold bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm shadow-emerald-600/30 transition-all cursor-pointer"
              >
                Registrarse
              </button>
            </template>

            <template v-else>
              <div class="hidden sm:flex items-center gap-2 px-3 py-1 bg-emerald-50 border border-emerald-200 rounded-xl">
                <span class="text-xs text-emerald-800 font-bold uppercase tracking-wider">{{ role || 'Usuario' }}</span>
                <span class="text-xs text-slate-500">({{ user.email?.split('@')[0] }})</span>
              </div>

              <button
                @click="abrirModalParcelas"
                class="px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-bold bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm shadow-emerald-600/30 transition-all flex items-center gap-1 cursor-pointer"
              >
                <span>🌱</span>
                <span>Mis Parcelas</span>
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
          class="px-2.5 py-1 text-xs whitespace-nowrap rounded-md font-medium bg-white text-slate-600 border border-slate-200 hover:bg-emerald-50 hover:text-emerald-700 transition-colors cursor-pointer"
        >
          {{ nav.icon }} {{ nav.label }}
        </button>
        <button
          v-if="user"
          @click="abrirModalParcelas"
          class="px-2.5 py-1 text-xs whitespace-nowrap rounded-md font-bold bg-emerald-100 text-emerald-800 border border-emerald-200 cursor-pointer"
        >
          🌱 Parcelas
        </button>
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
              <button
                v-if="!user"
                @click="abrirAuthModal('registro')"
                class="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm transition-all shadow-lg shadow-emerald-500/30 hover:scale-[1.02] cursor-pointer"
              >
                <span>Crear Cuenta Gratis</span>
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </button>

              <button
                v-else
                @click="abrirModalParcelas"
                class="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm transition-all shadow-lg shadow-emerald-500/30 hover:scale-[1.02] cursor-pointer"
              >
                <span>🌱 Ir al Panel de Parcelas</span>
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </button>

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
                <span>Inspeccion totalmente transparente</span>
              </div>
              <div class="flex items-center gap-2">
                <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <span>Roles para cada nivel de tu organización</span>
              </div>
              <div class="flex items-center gap-2">
               <svg
    class="w-4 h-4 text-emerald-400 shrink-0"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      stroke-width="2"
      d="M5 13l4 4L19 7"
    />
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
            Nuestro Proposito
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
                v-model="simulacion.cultivo"
                class="w-full bg-white border border-slate-300 rounded-xl px-3 py-2 text-xs sm:text-sm text-slate-800 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
              >
                <option value="Tomate Saladette">Tomate Saladette (Óptimo: 60-80% hum, 18-27°C | Letal ≤ 2°C)</option>
                <option value="Maíz Grano">Maíz Grano (Óptimo: 50-70% hum, 20-30°C | Letal ≤ 0°C)</option>
                <option value="Aguacate Hass">Aguacate Hass (Óptimo: 55-75% hum, 15-26°C | Letal ≤ 0°C)</option>
                <option value="Vid / Uva">Vid / Uva (Óptimo: 40-65% hum, 16-28°C | Letal ≤ -1°C)</option>
              </select>
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
                <span class="font-medium text-white">{{ simulacion.cultivo }}</span>
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
          <template v-if="!user">
            <button
              @click="abrirAuthModal('registro')"
              class="px-6 py-3 rounded-xl bg-white text-emerald-900 font-bold text-sm hover:bg-emerald-50 transition-all shadow-lg shadow-black/10 hover:scale-105 cursor-pointer"
            >
              Registrarse en la Plataforma
            </button>
            <button
              @click="abrirAuthModal('login')"
              class="px-6 py-3 rounded-xl bg-emerald-900/40 hover:bg-emerald-900/60 border border-white/20 text-white font-semibold text-sm transition-all cursor-pointer"
            >
              Iniciar Sesión
            </button>
          </template>
          <template v-else>
            <button
              @click="abrirModalParcelas"
              class="px-6 py-3 rounded-xl bg-white text-emerald-900 font-bold text-sm hover:bg-emerald-50 transition-all shadow-lg shadow-black/10 hover:scale-105 cursor-pointer"
            >
              Gestionar mis Parcelas ({{ role || 'Usuario' }})
            </button>
          </template>
        </div>
      </section>

    </main>

    <footer class="bg-white border-t border-slate-200 mt-16 py-8">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
        <div class="flex items-center gap-2">
          <span class="font-bold text-slate-800">AgroPulse (AgroPulse)</span>
          <span>•</span>
          <span>Plataforma de Agricultura de Precisión</span>
        </div>
        <div>
          <span>Monitoreo & Recomendaciones Agronómicas Explicables</span>
        </div>
      </div>
    </footer>

    <!-- MODAL DE AUTENTICACIÓN (LOGIN Y REGISTRO) -->
    <div v-if="modalAuth" class="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-white rounded-3xl max-w-md w-full p-6 sm:p-8 space-y-5 shadow-2xl border border-emerald-100 relative">
        <button
          @click="cerrarAuthModal"
          class="absolute top-5 right-5 text-slate-400 hover:text-slate-600 text-xl font-bold p-1 cursor-pointer"
        >
          ✕
        </button>

        <div class="text-center space-y-1">
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold uppercase tracking-wider mb-1">
            {{ modalAuthTipo === 'login' ? 'Acceso al Sistema' : 'Registro de Usuario' }}
          </div>
          <h3 class="text-2xl font-black text-slate-900">
            {{ modalAuthTipo === 'login' ? 'Iniciar Sesión' : 'Crear Cuenta' }}
          </h3>
          <p class="text-xs text-slate-500">
            {{ modalAuthTipo === 'login' ? 'Ingresa tus credenciales o selecciona un usuario de prueba' : 'Regístrate en la plataforma AgroPulse con perfil de Gerente' }}
          </p>
        </div>

        <!-- Usuarios de Prueba del README (Acceso Rápido para Login) -->
        <div v-if="modalAuthTipo === 'login'" class="p-3 bg-slate-50 border border-slate-200 rounded-2xl space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-extrabold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
              <span>🔑</span> Usuarios de prueba (README)
            </span>
            <span class="text-[10px] text-emerald-700 font-bold bg-emerald-100 px-2 py-0.5 rounded-full">Clic para autocompletar</span>
          </div>
          <div class="grid grid-cols-2 gap-1.5">
            <button
              v-for="u in usuariosPrueba"
              :key="u.email"
              type="button"
              @click="seleccionarUsuarioPrueba(u.email, u.pass)"
              class="text-left p-2 rounded-xl border border-slate-200 bg-white hover:border-emerald-500 hover:bg-emerald-50/60 transition-all cursor-pointer group"
            >
              <div class="flex items-center justify-between">
                <span class="font-extrabold text-slate-800 group-hover:text-emerald-700 block text-[11px]">{{ u.nombre }}</span>
                <span class="text-[9px] px-1.5 py-0.2 rounded bg-slate-100 text-slate-600 font-semibold">{{ u.rol }}</span>
              </div>
              <span class="text-[10px] text-slate-500 block truncate">{{ u.email }}</span>
            </button>
          </div>
        </div>

        <!-- Alerta de Error -->
        <div v-if="authError" class="p-3.5 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-start gap-2.5">
          <span class="text-base">⚠️</span>
          <span class="flex-1">{{ authError }}</span>
        </div>

        <form class="space-y-4" @submit.prevent="handleAuthSubmit">
          <div>
            <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Correo Electrónico</label>
            <input
              v-model="authEmail"
              type="email"
              required
              placeholder="tu-correo@agropulse.com"
              class="w-full px-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            />
          </div>

          <!-- Rol Asignado Automáticamente: Gerente (Sin selector, todos con acceso total) -->
          <div v-if="modalAuthTipo === 'registro'" class="p-3.5 rounded-2xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-900 flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center text-xl shrink-0 shadow-sm">
              🛡️
            </div>
            <div>
              <span class="font-extrabold block text-emerald-950 text-sm">Rol Asignado: Gerente</span>
              <span class="text-[11px] text-emerald-700 leading-tight block">Todos los usuarios registrados obtienen acceso total y todos los permisos del sistema.</span>
            </div>
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Contraseña</label>
            <input
              v-model="authPassword"
              type="password"
              required
              minlength="6"
              placeholder="••••••••"
              class="w-full px-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            />
          </div>

          <div v-if="modalAuthTipo === 'registro'">
            <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Confirmar Contraseña</label>
            <input
              v-model="authConfirmPassword"
              type="password"
              required
              minlength="6"
              placeholder="••••••••"
              class="w-full px-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            />
          </div>

          <button
            type="submit"
            :disabled="authLoading"
            class="w-full py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm transition-all shadow-lg shadow-emerald-600/30 flex items-center justify-center gap-2 disabled:opacity-60 cursor-pointer"
          >
            <svg v-if="authLoading" class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>{{ authLoading ? 'Procesando...' : (modalAuthTipo === 'login' ? 'Iniciar Sesión' : 'Crear Cuenta (Gerente)') }}</span>
          </button>
        </form>

        <div class="border-t border-slate-100 pt-3 text-center">
          <button
            v-if="modalAuthTipo === 'login'"
            @click="modalAuthTipo = 'registro'; authError = ''"
            class="text-xs text-slate-600 hover:text-emerald-700 cursor-pointer"
          >
            ¿No tienes cuenta? <span class="font-bold text-emerald-600">Regístrate aquí</span>
          </button>
          <button
            v-else
            @click="modalAuthTipo = 'login'; authError = ''"
            class="text-xs text-slate-600 hover:text-emerald-700 cursor-pointer"
          >
            ¿Ya tienes cuenta? <span class="font-bold text-emerald-600">Inicia sesión</span>
          </button>
        </div>
      </div>
    </div>

    <!-- MODAL DE PARCELAS Y FINCAS -->
    <div v-if="modalParcelas" class="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-white rounded-3xl max-w-4xl w-full max-h-[90vh] overflow-y-auto p-6 sm:p-8 space-y-6 shadow-2xl border border-slate-200 relative">
        <button
          @click="cerrarModalParcelas"
          class="absolute top-5 right-5 text-slate-400 hover:text-slate-600 text-xl font-bold p-1 cursor-pointer"
        >
          ✕
        </button>

        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-4 border-b border-slate-200">
          <div>
            <div class="inline-flex items-center gap-2 px-3 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold uppercase tracking-wider mb-1">
              🌱 Panel de Fincas y Parcelas
            </div>
            <h3 class="text-2xl font-black text-slate-900">
              Catálogo de Fincas & Umbrales Biológicos
            </h3>
            <p class="text-xs text-slate-500">
              Sesión activa como: <strong class="text-emerald-800 font-bold uppercase">{{ role || 'Usuario' }}</strong> ({{ user?.email }})
            </p>
          </div>

          <button
            @click="mostrarFormFinca = !mostrarFormFinca"
            class="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md shadow-emerald-600/30 flex items-center gap-1.5 cursor-pointer shrink-0"
          >
            <span>➕</span>
            <span>Nueva Finca</span>
          </button>
        </div>

        <!-- Formulario Crear Finca -->
        <div v-if="mostrarFormFinca" class="bg-emerald-50/60 p-4 rounded-2xl border border-emerald-200 space-y-3">
          <h4 class="text-xs font-bold text-emerald-900 uppercase">Dar de alta nueva Finca</h4>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <input
              v-model="nuevaFinca.name"
              placeholder="Nombre de la finca (ej. Finca Santa Lucía)"
              class="px-3 py-2 rounded-xl border border-slate-300 text-xs bg-white focus:outline-none"
            />
            <input
              v-model="nuevaFinca.location"
              placeholder="Ubicación / Sector"
              class="px-3 py-2 rounded-xl border border-slate-300 text-xs bg-white focus:outline-none"
            />
          </div>
          <div class="flex justify-end gap-2">
            <button @click="mostrarFormFinca = false" class="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-200 cursor-pointer">
              Cancelar
            </button>
            <button @click="guardarFinca" class="px-4 py-1.5 rounded-lg bg-emerald-600 text-white text-xs font-bold hover:bg-emerald-500 cursor-pointer">
              Guardar Finca
            </button>
          </div>
        </div>

        <!-- Lista de Fincas -->
        <div class="space-y-6">
          <div
            v-for="farm in farms"
            :key="farm.id"
            class="bg-slate-50 rounded-2xl p-5 border border-slate-200 space-y-4"
          >
            <div class="flex justify-between items-center pb-3 border-b border-slate-200">
              <div>
                <h4 class="text-lg font-black text-slate-900 flex items-center gap-2">
                  <span>🏡</span> {{ farm.name }}
                </h4>
                <p class="text-xs text-slate-500">📍 {{ farm.location }}</p>
              </div>
              <button
                @click="abrirFormParcela(farm.id)"
                class="px-3 py-1.5 rounded-lg bg-white border border-emerald-300 text-emerald-800 text-xs font-bold hover:bg-emerald-50 flex items-center gap-1 cursor-pointer"
              >
                <span>➕</span> Parcela
              </button>
            </div>

            <!-- Formulario Parcela para esta finca -->
            <div v-if="fincaActivaParcelaId === farm.id" class="bg-white p-4 rounded-xl border border-emerald-300 space-y-3">
              <h5 class="text-xs font-bold text-slate-800 uppercase">Nueva Parcela en {{ farm.name }}</h5>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <input
                  v-model="nuevaParcela.name"
                  placeholder="Nombre de la parcela (ej. Lote 4 Maíz)"
                  class="px-3 py-2 rounded-lg border border-slate-300 text-xs"
                />
                <select v-model="nuevaParcela.cropType" class="px-3 py-2 rounded-lg border border-slate-300 text-xs bg-white">
                  <option value="Tomate Saladette">Tomate Saladette</option>
                  <option value="Maíz Grano">Maíz Grano</option>
                  <option value="Aguacate Hass">Aguacate Hass</option>
                  <option value="Vid / Uva">Vid / Uva</option>
                </select>
              </div>
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                <div>
                  <label class="block text-[10px] text-slate-500 font-bold">Hum Mín (%)</label>
                  <input v-model.number="nuevaParcela.thresholds.humidity.min" type="number" class="w-full px-2 py-1.5 border rounded-lg" />
                </div>
                <div>
                  <label class="block text-[10px] text-slate-500 font-bold">Hum Máx (%)</label>
                  <input v-model.number="nuevaParcela.thresholds.humidity.max" type="number" class="w-full px-2 py-1.5 border rounded-lg" />
                </div>
                <div>
                  <label class="block text-[10px] text-slate-500 font-bold">Temp Mín (°C)</label>
                  <input v-model.number="nuevaParcela.thresholds.temperature.min" type="number" class="w-full px-2 py-1.5 border rounded-lg" />
                </div>
                <div>
                  <label class="block text-[10px] text-slate-500 font-bold">Temp Máx (°C)</label>
                  <input v-model.number="nuevaParcela.thresholds.temperature.max" type="number" class="w-full px-2 py-1.5 border rounded-lg" />
                </div>
              </div>
              <div class="flex justify-end gap-2 pt-1">
                <button @click="fincaActivaParcelaId = null" class="px-3 py-1 rounded-lg text-xs font-semibold text-slate-500 hover:bg-slate-100 cursor-pointer">
                  Cancelar
                </button>
                <button @click="guardarParcela" class="px-3 py-1 rounded-lg bg-emerald-600 text-white text-xs font-bold hover:bg-emerald-500 cursor-pointer">
                  Guardar
                </button>
              </div>
            </div>

            <!-- Parcelas -->
            <div v-if="farm.plots && farm.plots.length > 0" class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div
                v-for="plot in farm.plots"
                :key="plot.id"
                class="bg-white p-3.5 rounded-xl border border-slate-200 space-y-2"
              >
                <div class="flex justify-between items-start">
                  <h5 class="text-sm font-bold text-slate-900">{{ plot.name }}</h5>
                  <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                    {{ plot.cropType }}
                  </span>
                </div>
                <div class="text-[11px] text-slate-600 bg-slate-50 p-2 rounded-lg space-y-1 font-mono">
                  <div class="flex justify-between">
                    <span>💧 Humedad:</span>
                    <span class="font-bold text-emerald-700">{{ plot.thresholds.humidity.min }}% - {{ plot.thresholds.humidity.max }}%</span>
                  </div>
                  <div class="flex justify-between">
                    <span>🌡️ Temp:</span>
                    <span class="font-bold text-amber-700">{{ plot.thresholds.temperature.min }}°C - {{ plot.thresholds.temperature.max }}°C</span>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-xs text-slate-400 italic py-2 text-center bg-white rounded-xl border border-dashed border-slate-200">
              Sin parcelas registradas aún.
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuth } from '~/composables/useAuth'

const { user, role, login, register, logout } = useAuth()

const modalAuth = ref(false)
const modalAuthTipo = ref<'login' | 'registro'>('login')
const authEmail = ref('')
const authPassword = ref('')
const authConfirmPassword = ref('')
const authLoading = ref(false)
const authError = ref('')

// Usuarios de prueba del README para acceso rápido
const usuariosPrueba = [
  { nombre: 'Gerente', rol: 'Gerente', email: 'gerente@agropulse.com', pass: 'password123' },
  { nombre: 'Admin', rol: 'Gerente', email: 'admin@agropulse.com', pass: 'password123' },
  { nombre: 'Productor', rol: 'Gerente', email: 'productor@agropulse.com', pass: 'password123' },
  { nombre: 'Técnico', rol: 'Gerente', email: 'tecnico@agropulse.com', pass: 'password123' }
]

const seleccionarUsuarioPrueba = (email: string, pass: string) => {
  authEmail.value = email
  authPassword.value = pass
  authError.value = ''
}

const abrirAuthModal = (tipo: 'login' | 'registro') => {
  modalAuthTipo.value = tipo
  authError.value = ''
  authEmail.value = ''
  authPassword.value = ''
  authConfirmPassword.value = ''
  modalAuth.value = true
}

const cerrarAuthModal = () => {
  modalAuth.value = false
  authError.value = ''
}

const handleAuthSubmit = async () => {
  authError.value = ''

  if (modalAuthTipo.value === 'registro') {
    if (authPassword.value !== authConfirmPassword.value) {
      authError.value = 'Las contraseñas no coinciden.'
      return
    }
    if (authPassword.value.length < 6) {
      authError.value = 'La contraseña debe tener al menos 6 caracteres.'
      return
    }
  }

  authLoading.value = true

  try {
    if (modalAuthTipo.value === 'login') {
      await login(authEmail.value, authPassword.value)
    } else {
      // Registro automático como Gerente con todos los permisos
      await register(authEmail.value, authPassword.value, 'Gerente')
    }
    cerrarAuthModal()
  } catch (err: any) {
    console.error('Error de autenticación:', err)
    if (err.code === 'auth/invalid-credential' || err.code === 'auth/wrong-password' || err.code === 'auth/user-not-found') {
      authError.value = 'Credenciales inválidas. Verifica tu correo y contraseña.'
    } else if (err.code === 'auth/email-already-in-use') {
      authError.value = 'Este correo electrónico ya está registrado.'
    } else if (err.code === 'auth/weak-password') {
      authError.value = 'La contraseña debe tener al menos 6 caracteres.'
    } else if (err.code === 'auth/invalid-email') {
      authError.value = 'El formato del correo es inválido.'
    } else {
      authError.value = err.message || 'Ocurrió un error. Intenta nuevamente.'
    }
  } finally {
    authLoading.value = false
  }
}

// Modal y Gestión de Parcelas y Fincas
const modalParcelas = ref(false)
const mostrarFormFinca = ref(false)
const fincaActivaParcelaId = ref<string | null>(null)

const nuevaFinca = ref({ name: '', location: '' })
const nuevaParcela = ref({
  name: '',
  cropType: 'Tomate Saladette',
  thresholds: {
    humidity: { min: 60, max: 80 },
    temperature: { min: 18, max: 27 }
  }
})

const farms = ref([
  {
    id: 'f1',
    name: 'Finca Los Olivos',
    location: 'Valle Central, Sector A',
    plots: [
      {
        id: 'p1',
        name: 'Lote Tomates Norte',
        cropType: 'Tomate Saladette',
        thresholds: {
          humidity: { min: 60, max: 80 },
          temperature: { min: 18, max: 27 }
        }
      },
      {
        id: 'p2',
        name: 'Lote Maíz Sur',
        cropType: 'Maíz Grano',
        thresholds: {
          humidity: { min: 50, max: 70 },
          temperature: { min: 20, max: 30 }
        }
      }
    ]
  },
  {
    id: 'f2',
    name: 'Finca El Nogal',
    location: 'Sierra Norte, Km 45',
    plots: [
      {
        id: 'p3',
        name: 'Parcela Aguacates',
        cropType: 'Aguacate Hass',
        thresholds: {
          humidity: { min: 55, max: 75 },
          temperature: { min: 15, max: 26 }
        }
      }
    ]
  }
])

const abrirModalParcelas = () => {
  modalParcelas.value = true
}

const cerrarModalParcelas = () => {
  modalParcelas.value = false
}

const guardarFinca = () => {
  if (!nuevaFinca.value.name || !nuevaFinca.value.location) return
  farms.value.push({
    id: 'f_' + Date.now(),
    name: nuevaFinca.value.name,
    location: nuevaFinca.value.location,
    plots: []
  })
  nuevaFinca.value = { name: '', location: '' }
  mostrarFormFinca.value = false
}

const abrirFormParcela = (farmId: string) => {
  fincaActivaParcelaId.value = farmId
}

const guardarParcela = () => {
  const farm = farms.value.find(f => f.id === fincaActivaParcelaId.value)
  if (!farm || !nuevaParcela.value.name) return
  farm.plots.push({
    id: 'p_' + Date.now(),
    name: nuevaParcela.value.name,
    cropType: nuevaParcela.value.cropType,
    thresholds: {
      humidity: { ...nuevaParcela.value.thresholds.humidity },
      temperature: { ...nuevaParcela.value.thresholds.temperature }
    }
  })
  nuevaParcela.value = {
    name: '',
    cropType: 'Tomate Saladette',
    thresholds: {
      humidity: { min: 60, max: 80 },
      temperature: { min: 18, max: 27 }
    }
  }
  fincaActivaParcelaId.value = null
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

const rangosCultivo: Record<string, { tempLetal: number; tempMinOpt: number; tempMaxOpt: number; tempMaxCrit: number; humMinOpt: number; humMaxOpt: number }> = {
  'Tomate Saladette': { tempLetal: 2, tempMinOpt: 18, tempMaxOpt: 27, tempMaxCrit: 32, humMinOpt: 60, humMaxOpt: 80 },
  'Maíz Grano': { tempLetal: 0, tempMinOpt: 20, tempMaxOpt: 30, tempMaxCrit: 35, humMinOpt: 50, humMaxOpt: 70 },
  'Aguacate Hass': { tempLetal: 0, tempMinOpt: 15, tempMaxOpt: 26, tempMaxCrit: 32, humMinOpt: 55, humMaxOpt: 75 },
  'Vid / Uva': { tempLetal: -1, tempMinOpt: 16, tempMaxOpt: 28, tempMaxCrit: 35, humMinOpt: 40, humMaxOpt: 65 }
}

const simulacion = ref({
  cultivo: 'Tomate Saladette',
  humedad: 32,
  temperatura: 31,
  tendencia: 'caida_brusca'
})

const simulacionResultado = computed(() => {
  const h = simulacion.value.humedad
  const t = simulacion.value.temperatura
  const c = simulacion.value.cultivo
  const tend = simulacion.value.tendencia
  const cfg = rangosCultivo[c] || rangosCultivo['Tomate Saladette']

  if (t <= cfg.tempLetal) {
    return {
      nivel: 'Emergencia por Helada',
      badgeColor: 'bg-indigo-600/30 text-indigo-200 border border-indigo-400/50',
      accion: 'Activar de urgencia sistemas antiheladas (aspersión térmica, cubiertas o calefactores) e inspeccionar tejidos.',
      explicacion: `DISPARADOR: Temperatura registrada (${t}°C) está en o por debajo del umbral letal (${cfg.tempLetal}°C) para ${c}. El cultivo no sobrevive a 0°C; sufre congelamiento celular y colapso irreversible de tejidos sin mitigación activa.`
    }
  }

  if (t < cfg.tempMinOpt) {
    return {
      nivel: 'Alerta por Estrés de Frío',
      badgeColor: 'bg-sky-500/20 text-sky-300 border border-sky-500/30',
      accion: 'Monitorear descenso térmico nocturno y evitar riegos fríos que reduzcan la temperatura de la raíz.',
      explicacion: `DISPARADOR: Temperatura registrada (${t}°C) por debajo del mínimo vegetativo (${cfg.tempMinOpt}°C) para ${c}. Provoca parálisis fotosintética y detención del cuajado.`
    }
  }

  if (t >= cfg.tempMaxCrit || tend === 'alza_temperatura') {
    return {
      nivel: 'Alerta por Golpe de Calor',
      badgeColor: 'bg-amber-500/20 text-amber-300 border border-amber-500/30',
      accion: 'Programar micropulverización o riego de mitigación térmica en horario vespertino para disipar calor.',
      explicacion: `DISPARADOR: Temperatura registrada (${t}°C) supera el umbral crítico (${cfg.tempMaxCrit}°C) para ${c}. Riesgo de quemaduras foliares y esterilidad de floración.`
    }
  }

  if (h < cfg.humMinOpt - 15 || tend === 'caida_brusca') {
    return {
      nivel: 'Crítico por Estrés Hídrico',
      badgeColor: 'bg-red-500/20 text-red-300 border border-red-500/30',
      accion: 'Activar ciclo de riego por goteo inmediato (45 min) e inspeccionar sensor de humedad en parcela.',
      explicacion: `DISPARADOR: Humedad registrada (${h}%) se encuentra severamente por debajo del rango óptimo (${cfg.humMinOpt}% - ${cfg.humMaxOpt}%) para ${c}, con rápida desecación en el bulbo radicular.`
    }
  }

  if (h < cfg.humMinOpt) {
    return {
      nivel: 'Precaución de Riego',
      badgeColor: 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30',
      accion: 'Programar próximo turno de riego para reponer humedad en el bulbo radicular antes de entrar en déficit.',
      explicacion: `DISPARADOR: Humedad del suelo (${h}%) está por debajo del rango óptimo recomendado (${cfg.humMinOpt}% - ${cfg.humMaxOpt}%) para ${c}.`
    }
  }

  if (h > cfg.humMaxOpt) {
    return {
      nivel: 'Precaución por Sobresaturación',
      badgeColor: 'bg-blue-500/20 text-blue-300 border border-blue-500/30',
      accion: 'Suspender ciclos de riego programados y verificar drenaje para prevenir asfixia radicular y hongos.',
      explicacion: `DISPARADOR: Humedad del suelo (${h}%) supera el límite superior óptimo (${cfg.humMaxOpt}%) para ${c}. Riesgo de asfixia radicular y patógenos fúngicos.`
    }
  }

  return {
    nivel: 'Condición Óptima',
    badgeColor: 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30',
    accion: 'Mantener esquema de monitoreo estándar. Parcela en condiciones biológicas ideales.',
    explicacion: `DISPARADOR: Tanto la humedad (${h}%) como la temperatura (${t}°C) se mantienen dentro de la banda agronómica óptima (${cfg.humMinOpt}% - ${cfg.humMaxOpt}% hum, ${cfg.tempMinOpt}°C - ${cfg.tempMaxOpt}°C) para ${c}.`
  }
})
</script>
