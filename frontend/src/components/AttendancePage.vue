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
        <button class="primary-button" type="button" @click="markAttendance"><Icon name="check" /> Mark attendance</button>
      </div>
    </header>

    <div class="summary-grid four">
      <article class="summary-card"><span class="metric-icon"><Icon name="check" /></span><div><small>Present today</small><strong>{{ stats.presentToday || 98 }}</strong><em>{{ stats.presentPercentage || 81.7 }}% of team</em></div></article>
      <article class="summary-card"><span class="metric-icon"><Icon name="clock" /></span><div><small>Average check-in</small><strong>{{ stats.avgCheckIn || '09:06' }}</strong><em>4 min earlier</em></div></article>
      <article class="summary-card"><span class="metric-icon warning"><Icon name="spark" /></span><div><small>Exceptions</small><strong>{{ stats.exceptionsCount || 6 }}</strong><em>2 need action</em></div></article>
      <article class="summary-card"><span class="metric-icon"><Icon name="user" /></span><div><small>Remote today</small><strong>{{ stats.remoteToday || 10 }}</strong><em>{{ stats.remotePercentage || 8.3 }}% of team</em></div></article>
    </div>

    <div class="content-grid attendance-content">
      <article class="surface weekly-panel">
        <header class="section-heading">
          <div><span class="section-kicker">18–24 August 2026</span><h2>Weekly attendance</h2></div>
          <div class="week-control"><button type="button">‹</button><strong>This week</strong><button type="button">›</button></div>
        </header>
        <div class="attendance-chart">
          <div v-for="bar in days" :key="bar.day" class="attendance-day">
            <div class="chart-track"><span :style="{ height: bar.value + '%' }" :class="bar.tone"></span></div>
            <strong>{{ bar.value }}%</strong><small>{{ bar.day }}</small>
          </div>
        </div>
        <div class="chart-legend">
          <span><i class="teal"></i> Present</span><span><i class="amber"></i> Half day</span><span><i class="coral"></i> Exception</span>
        </div>
      </article>

      <article class="surface exceptions-panel">
        <header class="section-heading">
          <div><span class="section-kicker">Requires review</span><h2>Attendance exceptions</h2></div>
          <span class="status pending">{{ exceptions.length }} issues</span>
        </header>
        <button v-for="item in exceptions" :key="item.name" class="exception-item" type="button" @click="$emit('toast', `${item.name}'s attendance record opened`)">
          <span class="avatar" :class="item.color">{{ item.initials }}</span>
          <span><strong>{{ item.name }}</strong><small>{{ item.issue }}</small></span>
          <time>{{ item.time }}</time>
          <Icon name="chevron" />
        </button>
        <button class="text-button wide" type="button" @click="$emit('toast', 'Viewing all exceptions')">View all exceptions <Icon name="arrow" /></button>
      </article>
    </div>

    <article class="surface table-surface">
      <header class="section-heading table-heading">
        <div><span class="section-kicker">Live today</span><h2>Team attendance</h2></div>
        <label class="search-box"><Icon name="search" /><input v-model="search" placeholder="Search employee" /></label>
      </header>
      <div class="attendance-table table-scroll">
        <div class="table-row table-head">
          <span>Employee</span><span>Status</span><span>Check-in</span><span>Check-out</span><span>Work hours</span><span>Location</span>
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
        </div>
      </div>
    </article>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue"
import Icon from "./Icon.vue"
import { attendanceApi } from "../api.js"

const emit = defineEmits(["toast"])
const search = ref("")
const exportUrl = attendanceApi.exportCsvUrl()

const stats = ref({})
const days = ref([
  { day: "Mon", value: 94, tone: "good" },
  { day: "Tue", value: 97, tone: "good" },
  { day: "Wed", value: 88, tone: "warn" },
  { day: "Thu", value: 96, tone: "good" },
  { day: "Fri", value: 98, tone: "good" },
  { day: "Sat", value: 72, tone: "low" },
  { day: "Sun", value: 40, tone: "low" }
])
const exceptions = ref([])
const rows = ref([])

async function loadAttendance() {
  try {
    const data = await attendanceApi.getSummary()
    if (data.stats) stats.value = data.stats
    if (data.days) days.value = data.days
    if (data.exceptions) exceptions.value = data.exceptions
    if (data.rows) rows.value = data.rows
  } catch (err) {
    console.error("Failed to load attendance data", err)
  }
}

onMounted(() => {
  loadAttendance()
})

const filteredRows = computed(() =>
  rows.value.filter((item) => item.name.toLowerCase().includes(search.value.toLowerCase()))
)

function markAttendance() {
  emit("toast", "Attendance marked for today in PostgreSQL")
  loadAttendance()
}
</script>
