<template>
  <section>
    <header class="page-title-row">
      <div>
        <p class="eyebrow">Attendance intelligence</p>
        <h1>Every hour, accounted for.</h1>
        <p>Spot exceptions early without turning presence into surveillance.</p>
      </div>
      <div class="header-actions">
        <a class="secondary-button" :href="exportUrl" download="ARIA-attendance.csv"><Icon name="download" /> Export</a>
        <button class="primary-button" type="button" @click="openQuickMark"><Icon name="check" /> Mark attendance</button>
      </div>
    </header>

    <div class="summary-grid four">
      <article class="summary-card"><span class="metric-icon"><Icon name="check" /></span><div><small>Present today</small><strong>{{ stats.presentToday || 98 }}</strong><em>{{ stats.presentPercentage || 81.7 }}% of team</em></div></article>
      <article class="summary-card"><span class="metric-icon"><Icon name="clock" /></span><div><small>Average check-in</small><strong>{{ stats.avgCheckIn || '09:06' }}</strong><em>4 min earlier</em></div></article>
      <article class="summary-card"><span class="metric-icon warning"><Icon name="spark" /></span><div><small>Exceptions</small><strong>{{ stats.exceptionsCount || 0 }}</strong><em>{{ exceptions.length }} in queue</em></div></article>
      <article class="summary-card"><span class="metric-icon"><Icon name="user" /></span><div><small>Remote today</small><strong>{{ stats.remoteToday || 10 }}</strong><em>{{ stats.remotePercentage || 8.3 }}% of team</em></div></article>
    </div>

    <div class="content-grid attendance-content">
      <article class="surface weekly-panel">
        <header class="section-heading">
          <div><span class="section-kicker">{{ weekLabel }}</span><h2>Weekly attendance</h2></div>
          <div class="week-control">
            <button type="button" aria-label="Previous week" @click="changeWeek(-1)">‹</button>
            <strong>{{ weekOffset === 0 ? 'This week (18–24 Aug)' : 'Last week (11–17 Aug)' }}</strong>
            <button type="button" aria-label="Next week" :disabled="!canGoForward" :style="{ opacity: canGoForward ? 1 : 0.35, cursor: canGoForward ? 'pointer' : 'not-allowed' }" @click="changeWeek(1)">›</button>
          </div>
        </header>
        <div class="attendance-chart">
          <div v-for="bar in days" :key="bar.day" class="attendance-day">
            <div class="chart-track">
              <span v-if="!bar.isFuture" :style="{ height: bar.value + '%' }" :class="bar.tone"></span>
              <span v-else class="future-bar" style="height: 10%; background: rgba(255,255,255,0.08); border-style: dashed;"></span>
            </div>
            <strong>{{ bar.isFuture ? '—' : `${bar.value}%` }}</strong>
            <small>{{ bar.day }} {{ bar.date }}</small>
          </div>
        </div>
        <div class="chart-legend">
          <span><i class="teal"></i> Present</span>
          <span><i class="amber"></i> Half day</span>
          <span><i class="coral"></i> Exception</span>
          <span><i class="dashed-legend"></i> Upcoming</span>
        </div>
      </article>

      <article class="surface exceptions-panel">
        <header class="section-heading">
          <div><span class="section-kicker">Requires review</span><h2>Attendance exceptions</h2></div>
          <span class="status pending">{{ exceptions.length }} issues</span>
        </header>
        <button v-for="item in exceptions" :key="item.id || item.name" class="exception-item" type="button" @click="selectedException = item">
          <span class="avatar" :class="item.color">{{ item.initials }}</span>
          <span><strong>{{ item.name }}</strong><small>{{ item.issue }}</small></span>
          <time>{{ item.time }}</time>
          <Icon name="chevron" />
        </button>
        <div v-if="!exceptions.length" class="empty-state" style="padding: 1.5rem 0;">
          <span><Icon name="check" /></span>
          <p>All attendance exceptions resolved.</p>
        </div>
        <button class="text-button wide" type="button" @click="toggleExceptionsFilter">
          {{ exceptionsOnly ? 'Show all employees' : 'Filter table to exceptions' }} <Icon name="arrow" />
        </button>
      </article>
    </div>

    <article class="surface table-surface">
      <header class="section-heading table-heading">
        <div>
          <span class="section-kicker">Live today</span>
          <h2>Team attendance <small v-if="exceptionsOnly" style="color: var(--amber); font-size: 0.9rem;">(Filtered: Exceptions Only)</small></h2>
        </div>
        <div class="table-tools">
          <label class="search-box"><Icon name="search" /><input v-model="search" placeholder="Search employee" /></label>
          <button v-if="exceptionsOnly" class="secondary-button compact" type="button" @click="exceptionsOnly = false">Clear filter</button>
        </div>
      </header>
      <div class="attendance-table table-scroll">
        <div class="table-row table-head">
          <span>Employee</span><span>Status</span><span>Check-in</span><span>Check-out</span><span>Work hours</span><span>Location</span><span>Action</span>
        </div>
        <div v-for="item in filteredRows" :key="item.id || item.name" class="table-row">
          <span class="employee-cell">
            <span class="avatar" :class="item.color">{{ item.initials }}</span>
            <strong>{{ item.name }}</strong>
          </span>
          <span><span class="status" :class="item.tone">{{ item.status }}</span></span>
          <span>{{ item.in }}</span>
          <span>{{ item.out }}</span>
          <span>{{ item.hours }}</span>
          <span>{{ item.location }}</span>
          <span>
            <button v-if="item.isException" class="text-button" type="button" @click="selectedException = item">Resolve</button>
            <span v-else class="status protected" style="font-size: 0.8rem;">Clear</span>
          </span>
        </div>
      </div>
    </article>

    <!-- Exception Resolution Modal -->
    <Transition name="fade">
      <div v-if="selectedException" class="modal-backdrop" @click.self="selectedException = null">
        <section class="modal" role="dialog" aria-modal="true" aria-labelledby="exception-modal-title">
          <button class="modal-close" type="button" aria-label="Close" @click="selectedException = null"><Icon name="close" /></button>
          <span class="section-kicker">Attendance Resolution</span>
          <h2 id="exception-modal-title">Regularize Attendance</h2>
          <div class="decision-person">
            <span class="avatar teal">{{ selectedException.initials }}</span>
            <div><strong>{{ selectedException.name }}</strong><small>{{ selectedException.issue }}</small></div>
            <span class="status pending">Exception</span>
          </div>
          <div class="decision-facts">
            <div><small>Employee</small><strong>{{ selectedException.name }}</strong></div>
            <div><small>Current Status</small><strong>{{ selectedException.status || 'Missing punch' }}</strong></div>
            <div><small>Date</small><strong>22 Aug 2026</strong></div>
          </div>
          <div class="modal-actions" style="margin-top: 1.5rem; display: flex; gap: 0.75rem; flex-wrap: wrap;">
            <button class="secondary-button" type="button" @click="resolveCurrentException('dismiss')">Dismiss</button>
            <button class="secondary-button" type="button" @click="resolveCurrentException('half_day')">Mark Half-Day</button>
            <button class="primary-button" type="button" @click="resolveCurrentException('regularize')">Regularize (09:00 - 18:00) <Icon name="check" /></button>
          </div>
        </section>
      </div>
    </Transition>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue"
import Icon from "./Icon.vue"
import { attendanceApi } from "../api.js"

const emit = defineEmits(["toast"])
const search = ref("")
const exportUrl = attendanceApi.exportCsvUrl()
const weekOffset = ref(0)
const canGoForward = ref(false)
const exceptionsOnly = ref(false)
const selectedException = ref(null)

const stats = ref({})
const days = ref([])
const exceptions = ref([])
const rows = ref([])

const weekLabel = computed(() => {
  if (weekOffset.value === 0) return "18–24 August 2026"
  if (weekOffset.value === -1) return "11–17 August 2026"
  return "Current August Cycle"
})

async function loadAttendance() {
  try {
    const data = await attendanceApi.getSummary(weekOffset.value)
    if (data.stats) stats.value = data.stats
    if (data.days) days.value = data.days
    if (data.exceptions) exceptions.value = data.exceptions
    if (data.rows) rows.value = data.rows
    canGoForward.value = Boolean(data.canGoForward)
  } catch (err) {
    console.error("Failed to load attendance data", err)
  }
}

onMounted(() => {
  loadAttendance()
})

function changeWeek(delta) {
  if (delta > 0 && !canGoForward.value) return
  weekOffset.value += delta
  loadAttendance()
}

function toggleExceptionsFilter() {
  exceptionsOnly.value = !exceptionsOnly.value
}

const filteredRows = computed(() => {
  return rows.value.filter((item) => {
    const matchesSearch = item.name.toLowerCase().includes(search.value.toLowerCase())
    const matchesException = !exceptionsOnly.value || item.isException
    return matchesSearch && matchesException
  })
})

function openQuickMark() {
  emit("toast", "Synchronized team attendance records from biometric gateway")
  loadAttendance()
}

async function resolveCurrentException(action) {
  if (!selectedException.value) return
  const id = selectedException.value.id
  try {
    const res = await attendanceApi.resolveException(id, action)
    emit("toast", res.message || "Exception updated in database")
    selectedException.value = null
    loadAttendance()
  } catch (err) {
    emit("toast", err.message || "Failed to resolve exception")
  }
}
</script>
