<template>
  <section>
    <header class="page-title-row">
      <div>
        <p class="eyebrow">People directory</p>
        <h1>Know the people behind the work.</h1>
        <p>One current record for every teammate, role and reporting line.</p>
      </div>
      <button class="primary-button" type="button" @click="$emit('toast', 'Invite link copied')"><Icon name="user-plus" /> Add employee</button>
    </header>

    <div class="summary-grid four">
      <article class="summary-card">
        <span class="metric-icon"><Icon name="users" /></span>
        <div>
          <small>Active employees</small>
          <strong>{{ summary.activeEmployees || people.length || 120 }}</strong>
          <em>+{{ summary.newJoiners || 5 }} this month</em>
        </div>
      </article>
      <article class="summary-card">
        <span class="metric-icon"><Icon name="building" /></span>
        <div>
          <small>Departments</small>
          <strong>{{ summary.departmentCount || 6 }}</strong>
          <em>All staffed</em>
        </div>
      </article>
      <article class="summary-card">
        <span class="metric-icon"><Icon name="user-plus" /></span>
        <div>
          <small>New joiners</small>
          <strong>{{ summary.newJoiners || 5 }}</strong>
          <em>August cohort</em>
        </div>
      </article>
      <article class="summary-card">
        <span class="metric-icon"><Icon name="clock" /></span>
        <div>
          <small>On probation</small>
          <strong>{{ summary.onProbation || 7 }}</strong>
          <em>Active reviews</em>
        </div>
      </article>
    </div>

    <article class="surface table-surface">
      <header class="section-heading table-heading">
        <div><span class="section-kicker">{{ people.length }} employees</span><h2>Everyone at ARIA</h2></div>
        <div class="table-tools">
          <label class="search-box"><Icon name="search" /><input v-model="query" placeholder="Search people" /></label>
          <button class="secondary-button" type="button"><Icon name="filter" /> Filter</button>
        </div>
      </header>
      <div class="people-table table-scroll">
        <div class="table-row table-head">
          <span>Employee</span>
          <span>Role</span>
          <span>Department</span>
          <span>Status</span>
          <span>Joined</span>
          <span></span>
        </div>
        <button v-for="person in filteredPeople" :key="person.id || person.employeeId" class="table-row" type="button" @click="selected = person">
          <span class="employee-cell">
            <span class="avatar" :class="person.avatarColor || 'teal'">{{ initials(person.name) }}</span>
            <span><strong>{{ person.name }}</strong><small>{{ person.employeeId }} · {{ person.email }}</small></span>
          </span>
          <span><strong>{{ person.jobTitle || person.role }}</strong><small>{{ person.location || 'New Delhi' }}</small></span>
          <span>{{ person.department }}</span>
          <span><i class="presence-dot" :class="(person.status || 'Present').toLowerCase()"></i>{{ person.status || 'Present' }}</span>
          <span>{{ formatDate(person.joiningDate) }}</span>
          <span><Icon name="chevron" /></span>
        </button>
      </div>
    </article>

    <Transition name="slide">
      <aside v-if="selected" class="profile-drawer">
        <button class="modal-close" type="button" aria-label="Close" @click="selected = null"><Icon name="close" /></button>
        <span class="avatar profile-avatar" :class="selected.avatarColor || 'teal'">{{ initials(selected.name) }}</span>
        <h2>{{ selected.name }}</h2>
        <p>{{ selected.jobTitle || selected.role }} · {{ selected.department }}</p>
        <div class="profile-status"><i class="presence-dot present"></i> {{ selected.status || 'Active' }} employee</div>
        <div class="profile-details">
          <div><small>Employee ID</small><strong>{{ selected.employeeId }}</strong></div>
          <div><small>Location</small><strong>{{ selected.location || 'New Delhi' }}</strong></div>
          <div><small>Joined</small><strong>{{ formatDate(selected.joiningDate) }}</strong></div>
          <div><small>Manager</small><strong>{{ selected.manager || 'Arjun Mehta' }}</strong></div>
        </div>
        <button class="primary-button" type="button" @click="$emit('profile', selected)">View full profile <Icon name="arrow" /></button>
        <button class="secondary-button" type="button" @click="$emit('toast', `Email client opened for ${selected.email}`)"><Icon name="mail" /> Send email</button>
      </aside>
    </Transition>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue"
import Icon from "./Icon.vue"
import { employeeApi } from "../api.js"

defineEmits(["toast", "profile"])
const query = ref("")
const selected = ref(null)
const people = ref([])
const summary = ref({})

async function loadPeopleData() {
  try {
    const [peopleData, summaryData] = await Promise.all([
      employeeApi.getAll(),
      employeeApi.getSummary()
    ])
    people.value = Array.isArray(peopleData) ? peopleData : (peopleData.results || [])
    summary.value = summaryData || {}
  } catch (err) {
    console.error("Failed to load employees", err)
  }
}

onMounted(() => {
  loadPeopleData()
})

const filteredPeople = computed(() => {
  return people.value.filter((person) => {
    const text = `${person.name} ${person.jobTitle || ''} ${person.department || ''} ${person.employeeId || ''}`.toLowerCase()
    return text.includes(query.value.toLowerCase())
  })
})

function initials(name = "") {
  return (name || "").split(" ").filter(Boolean).map((part) => part[0]).join("") || "EM"
}

function formatDate(dateStr) {
  if (!dateStr) return "15 Apr 2024"
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" })
  } catch {
    return dateStr
  }
}
</script>
