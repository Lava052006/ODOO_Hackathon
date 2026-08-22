<template>
  <section>
    <header class="page-title-row">
      <div>
        <p class="eyebrow">Time off</p>
        <h1>Give people time, keep work covered.</h1>
        <p>Balances, approvals and team capacity in one decision-ready view.</p>
      </div>
      <button class="primary-button" type="button" @click="$emit('leave')"><Icon name="plus" /> Request time off</button>
    </header>

    <div class="summary-grid four">
      <article class="summary-card"><span class="metric-icon warning"><Icon name="leave" /></span><div><small>Pending requests</small><strong>{{ activeRequests.length }}</strong><em>2 due today</em></div></article>
      <article class="summary-card"><span class="metric-icon"><Icon name="users" /></span><div><small>People away today</small><strong>{{ summary.awayToday || 4 }}</strong><em>Coverage safe</em></div></article>
      <article class="summary-card"><span class="metric-icon"><Icon name="calendar" /></span><div><small>Upcoming this week</small><strong>{{ summary.upcomingThisWeek || 11 }}</strong><em>Across 6 teams</em></div></article>
      <article class="summary-card"><span class="metric-icon"><Icon name="shield" /></span><div><small>Coverage health</small><strong>{{ summary.coverageHealth || '92%' }}</strong><em>No critical gaps</em></div></article>
    </div>

    <div class="content-grid leave-grid">
      <article class="surface">
        <header class="section-heading">
          <div><span class="section-kicker">Decision queue</span><h2>Requests to review ({{ filteredRequests.length }})</h2></div>
          <div class="filter-dropdown-wrap">
            <button class="secondary-button compact" type="button" @click="filterOpen = !filterOpen">
              <Icon name="filter" /> {{ selectedType }}
            </button>
            <div v-if="filterOpen" class="filter-dropdown surface">
              <div class="filter-group">
                <small>Leave type</small>
                <select v-model="selectedType" @change="filterOpen = false">
                  <option>All</option>
                  <option>Paid leave</option>
                  <option>Sick leave</option>
                  <option>Work from home</option>
                  <option>Unpaid leave</option>
                </select>
              </div>
            </div>
          </div>
        </header>
        <button v-for="request in filteredRequests" :key="request.id || request.name" class="leave-review" type="button" @click="$emit('decision', request)">
          <span class="avatar" :class="request.color">{{ initials(request.name) }}</span>
          <span class="leave-main"><strong>{{ request.name }}</strong><small>{{ request.role }}</small></span>
          <span><strong>{{ request.range }}</strong><small>{{ request.leave_type || 'Paid leave' }}</small></span>
          <span class="coverage"><strong>{{ request.team_coverage || '92%' }}</strong><small>Team coverage</small></span>
          <span class="status pending">Review</span>
          <Icon name="chevron" />
        </button>
        <div v-if="!filteredRequests.length" class="empty-state">
          <span><Icon name="check" /></span>
          <h3>All requests reviewed</h3>
          <p>Your approval queue is clear.</p>
        </div>
      </article>

      <article class="surface team-calendar">
        <header class="section-heading">
          <div><span class="section-kicker">August 2026</span><h2>Team away calendar</h2></div>
          <div class="week-control"><button type="button">‹</button><button type="button">›</button></div>
        </header>
        <div class="calendar-week">
          <div v-for="day in calendar" :key="day.date" :class="{ today: day.today }">
            <small>{{ day.name }}</small>
            <strong>{{ day.date }}</strong>
            <span
              v-for="person in day.people"
              :key="person"
              class="calendar-avatar-chip"
              :title="`${person} (On leave)`"
              @click.stop="showPersonInfo(person, day)"
            >
              {{ initials(person) }}
            </span>
          </div>
        </div>
        <div class="coverage-note">
          <Icon name="shield" />
          <span><strong>Coverage protected all week</strong><small>The lowest projected staffing level is 88% on Friday.</small></span>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue"
import Icon from "./Icon.vue"
import { leavesApi } from "../api.js"

const props = defineProps({ requests: { type: Array, default: () => [] } })
const emit = defineEmits(["decision", "leave", "toast"])

const fetchedRequests = ref([])
const summary = ref({})
const filterOpen = ref(false)
const selectedType = ref("All")
const calendar = ref([])

async function loadLeaves() {
  try {
    const data = await leavesApi.getDashboard("pending")
    if (data.requests) fetchedRequests.value = data.requests
    if (data.summary) summary.value = data.summary
    if (data.calendar) calendar.value = data.calendar
  } catch (err) {
    console.error("Failed to load leaves data", err)
  }
}

onMounted(() => {
  loadLeaves()
})

const activeRequests = computed(() => {
  if (props.requests && props.requests.length) return props.requests
  return fetchedRequests.value
})

const filteredRequests = computed(() => {
  if (selectedType.value === "All") return activeRequests.value
  return activeRequests.value.filter((r) => (r.leave_type || "Paid leave") === selectedType.value)
})

function showPersonInfo(person, day) {
  emit("toast", `${person} is scheduled away on ${day.name} ${day.date} Aug`)
}

function initials(name = "") {
  return (name || "").split(" ").filter(Boolean).map((p) => p[0]).join("") || "LV"
}
</script>
