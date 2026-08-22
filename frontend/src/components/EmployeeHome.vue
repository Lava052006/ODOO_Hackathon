<template>
  <section class="employee-dashboard">
    <header class="employee-title">
      <div>
        <p class="eyebrow">My workday</p>
        <h1>Good morning, {{ firstName }}.</h1>
        <p>Everything you need for today, without the HR maze.</p>
      </div>
      <div class="date-callout">
        <Icon name="calendar" />
        <div><strong>Friday, 22 August</strong><span>{{ user.location || 'Connaught Place Office' }}</span></div>
      </div>
    </header>

    <article class="checkin-card">
      <div class="checkmark"><Icon name="check" /></div>
      <div>
        <span class="section-kicker">Today’s attendance</span>
        <h2>{{ checkedIn ? `Checked in at ${checkInTime}` : 'Ready to start your day?' }}</h2>
        <p>{{ checkedIn ? 'You have an active check-in session logged in database.' : 'Your shift runs from 09:00 to 18:00.' }}</p>
      </div>
      <button type="button" :disabled="loading" @click="toggleCheckin">{{ loading ? 'Saving...' : (checkedIn ? 'Check out' : 'Check in') }}</button>
    </article>

    <div class="employee-quick-grid">
      <button type="button" @click="openAttendanceCalendar">
        <span><Icon name="calendar" /></span>
        <strong>Attendance Calendar</strong>
        <small>View interactive schedule</small>
        <Icon name="chevron" />
      </button>
      <button type="button" @click="$emit('leave')">
        <span><Icon name="leave" /></span>
        <strong>Request time off</strong>
        <small>Apply for leave or WFH</small>
        <Icon name="chevron" />
      </button>
      <button type="button" @click="$emit('profile', 'salary')">
        <span><Icon name="rupee" /></span>
        <strong>My salary</strong>
        <small>View payslips and earnings</small>
        <Icon name="chevron" />
      </button>
      <button type="button" @click="$emit('profile', 'personal')">
        <span><Icon name="user" /></span>
        <strong>My profile</strong>
        <small>Update contact information</small>
        <Icon name="chevron" />
      </button>
    </div>

    <div class="employee-grid">
      <article class="surface">
        <header class="section-heading">
          <div><span class="section-kicker">18–24 August</span><h2>My week</h2></div>
          <span class="status protected">On track</span>
        </header>
        <div class="week-table">
          <div v-for="day in week" :key="day.date || day.dayNum" :class="{ today: day.today }">
            <small>{{ day.dayName || day.name }} {{ day.dayNum ? `${day.dayNum} Aug` : '' }}</small>
            <strong>{{ day.status }}</strong>
            <span>{{ day.hours }}</span>
          </div>
        </div>
      </article>

      <article class="surface">
        <header class="section-heading">
          <div><span class="section-kicker">Status & Tracking</span><h2>My requests</h2></div>
          <button class="text-button" type="button" @click="$emit('leave')">New request <Icon name="plus" /></button>
        </header>
        <div v-if="myRequests.length" class="my-requests-list">
          <div v-for="req in myRequests" :key="req.id" class="my-request">
            <span class="metric-icon"><Icon :name="req.leave_type === 'Work from home' ? 'building' : 'leave'" /></span>
            <span><strong>{{ req.leave_type || 'Leave' }}</strong><small>{{ req.range }} · {{ req.reason }}</small></span>
            <span class="status" :class="req.status === 'approved' ? 'protected' : req.status === 'rejected' ? 'risk' : 'pending'">{{ req.status }}</span>
          </div>
        </div>
        <div v-else class="empty-state" style="padding: 1.5rem 0;">
          <span><Icon name="check" /></span>
          <p>No active leave requests.</p>
        </div>
      </article>
    </div>

    <!-- Attendance Interactive Calendar Modal -->
    <Transition name="fade">
      <div v-if="attendanceModalOpen" class="modal-backdrop" @click.self="attendanceModalOpen = false">
        <section class="modal attendance-calendar-modal" role="dialog" aria-modal="true" aria-labelledby="attendance-calendar-title">
          <button class="modal-close" type="button" aria-label="Close" @click="attendanceModalOpen = false"><Icon name="close" /></button>
          
          <header class="calendar-modal-header">
            <div>
              <span class="section-kicker">Attendance Calendar</span>
              <h2 id="attendance-calendar-title">August 2026 Workday Log</h2>
              <p>Review check-in timestamps, working durations and location punches.</p>
            </div>
            
            <div class="calendar-view-toggle">
              <button type="button" :class="{ active: calendarViewMode === 'week' }" @click="calendarViewMode = 'week'">This Week</button>
              <button type="button" :class="{ active: calendarViewMode === 'month' }" @click="calendarViewMode = 'month'">August Month</button>
            </div>
          </header>

          <!-- Metrics summary -->
          <div class="calendar-mini-stats">
            <div><small>Present Days</small><strong>{{ stats.totalPresent || 16 }}</strong></div>
            <div><small>Half-days</small><strong>{{ stats.totalHalfDay || 1 }}</strong></div>
            <div><small>Remote Days</small><strong>{{ stats.totalRemote || 2 }}</strong></div>
            <div><small>Total Logged</small><strong>{{ stats.totalHours || '148h' }}</strong></div>
          </div>

          <!-- Status Filters -->
          <div class="calendar-filters-row">
            <span>Filter by:</span>
            <button
              v-for="flt in ['All', 'Present', 'Remote', 'Half-day', 'Off']"
              :key="flt"
              type="button"
              class="filter-pill"
              :class="{ active: activeStatusFilter === flt }"
              @click="activeStatusFilter = flt"
            >
              {{ flt }}
            </button>
          </div>

          <!-- Calendar Days Grid -->
          <div class="calendar-cards-grid">
            <div
              v-for="item in displayedCalendarDays"
              :key="item.date"
              class="calendar-day-card surface"
              :class="{ 'today-card': item.today, 'future-card': item.isFuture }"
            >
              <div class="card-date-row">
                <strong>{{ item.dayName }} {{ item.dayNum }} Aug</strong>
                <span
                  class="status"
                  :class="item.status === 'Present' ? 'protected' : item.status === 'Half-day' ? 'warn' : item.status === 'Remote' ? 'protected' : 'pending'"
                >
                  {{ item.status }}
                </span>
              </div>
              
              <div class="card-timing-info">
                <div class="punch-times">
                  <span><Icon name="clock" /> In: <b>{{ item.in }}</b></span>
                  <span>Out: <b>{{ item.out }}</b></span>
                </div>
                <div class="duration-row">
                  <small>Duration:</small>
                  <strong>{{ item.hours }}</strong>
                </div>
              </div>

              <div class="card-loc-footer">
                <Icon name="building" />
                <small>{{ item.location || 'New Delhi' }}</small>
              </div>
            </div>
          </div>

          <div class="modal-actions" style="margin-top: 1.5rem;">
            <button class="primary-button" type="button" @click="attendanceModalOpen = false">Done</button>
          </div>
        </section>
      </div>
    </Transition>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue"
import Icon from "./Icon.vue"
import { attendanceApi, leavesApi } from "../api.js"

const props = defineProps({ user: { type: Object, required: true } })
const emit = defineEmits(["leave", "toast", "profile"])
const checkedIn = ref(true)
const checkInTime = ref("09:04")
const loading = ref(false)
const attendanceModalOpen = ref(false)
const calendarViewMode = ref("week") // 'week' or 'month'
const activeStatusFilter = ref("All")

const myRequests = ref([])
const week = ref([])
const fullCalendar = ref([])
const stats = ref({})

const firstName = computed(() => (props.user.name || props.user.first_name || props.user.username || "Employee").split(" ")[0])

async function loadData() {
  try {
    const [attData, leavesData] = await Promise.all([
      attendanceApi.getMyWeek(),
      leavesApi.getDashboard("all")
    ])
    if (attData.week) week.value = attData.week
    if (attData.calendar) fullCalendar.value = attData.calendar
    if (attData.stats) stats.value = attData.stats
    if (leavesData.requests) myRequests.value = leavesData.requests.slice(0, 5)
  } catch (err) {
    console.error("Failed to load employee data", err)
  }
}

onMounted(() => {
  loadData()
})

function openAttendanceCalendar() {
  attendanceModalOpen.value = true
  loadData()
}

const displayedCalendarDays = computed(() => {
  const baseList = calendarViewMode.value === "week" ? week.value : fullCalendar.value
  if (activeStatusFilter.value === "All") return baseList
  return baseList.filter((d) => (d.status || "").toLowerCase() === activeStatusFilter.value.toLowerCase())
})

async function toggleCheckin() {
  loading.value = true
  try {
    const res = await attendanceApi.toggleCheckin()
    checkedIn.value = res.checkedIn
    if (res.checkInTime) checkInTime.value = res.checkInTime
    emit("toast", res.message || (checkedIn.value ? "Checked in successfully" : "Checked out successfully"))
    loadData()
  } catch (err) {
    emit("toast", err.message || "Failed to toggle check-in")
  } finally {
    loading.value = false
  }
}
</script>
