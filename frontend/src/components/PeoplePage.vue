<template>
  <section>
    <header class="page-title-row">
      <div>
        <p class="eyebrow">People directory</p>
        <h1>Know the people behind the work.</h1>
        <p>One current record for every teammate, role and reporting line.</p>
      </div>
      <button class="primary-button" type="button" @click="addModalOpen = true"><Icon name="user-plus" /> Add employee</button>
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
        <div><span class="section-kicker">{{ filteredPeople.length }} employees</span><h2>Everyone at ARIA</h2></div>
        <div class="table-tools">
          <label class="search-box"><Icon name="search" /><input v-model="query" placeholder="Search people" /></label>
          <div class="filter-dropdown-wrap">
            <button class="secondary-button" type="button" @click="filterOpen = !filterOpen">
              <Icon name="filter" /> Filter
              <span v-if="selectedDept !== 'All' || selectedStatus !== 'All'" class="filter-badge">●</span>
            </button>
            <div v-if="filterOpen" class="filter-dropdown surface">
              <div class="filter-group">
                <small>Department</small>
                <select v-model="selectedDept">
                  <option>All</option>
                  <option>Engineering</option>
                  <option>Product</option>
                  <option>Customer Success</option>
                  <option>Finance</option>
                  <option>Operations</option>
                  <option>People</option>
                </select>
              </div>
              <div class="filter-group">
                <small>Status</small>
                <select v-model="selectedStatus">
                  <option>All</option>
                  <option>Present</option>
                  <option>On leave</option>
                  <option>Remote</option>
                  <option>Late</option>
                  <option>Off</option>
                </select>
              </div>
              <button class="text-button" type="button" @click="resetFilters">Reset filters</button>
            </div>
          </div>
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

    <!-- Profile Drawer -->
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
        <button class="secondary-button" type="button" @click="sendEmail(selected.email)"><Icon name="mail" /> Send email</button>
      </aside>
    </Transition>

    <!-- Add Employee Modal -->
    <Transition name="fade">
      <div v-if="addModalOpen" class="modal-backdrop" @click.self="addModalOpen = false">
        <section class="modal" role="dialog" aria-modal="true" aria-labelledby="add-employee-title">
          <button class="modal-close" type="button" aria-label="Close" @click="addModalOpen = false"><Icon name="close" /></button>
          <span class="section-kicker">New onboarding</span>
          <h2 id="add-employee-title">Add Employee</h2>
          <form @submit.prevent="createEmployee">
            <div class="form-grid">
              <label>First name<input v-model="newForm.firstName" required placeholder="e.g. Arjun" /></label>
              <label>Last name<input v-model="newForm.lastName" required placeholder="e.g. Kapoor" /></label>
              <label>Employee ID<input v-model="newForm.employeeId" placeholder="EMP1121 (auto if blank)" /></label>
              <label>Work email<input v-model="newForm.email" type="email" placeholder="arjun.kapoor@aria.com" /></label>
              <label>Department
                <select v-model="newForm.department">
                  <option>Engineering</option>
                  <option>Product</option>
                  <option>Customer Success</option>
                  <option>Finance</option>
                  <option>Operations</option>
                  <option>People</option>
                </select>
              </label>
              <label>Role / Job title<input v-model="newForm.role" required placeholder="e.g. QA Engineer" /></label>
              <label>Location<input v-model="newForm.location" placeholder="New Delhi" /></label>
            </div>
            <div class="modal-actions" style="margin-top: 1.5rem;">
              <button class="secondary-button" type="button" @click="addModalOpen = false">Cancel</button>
              <button class="primary-button" type="submit" :disabled="creating">{{ creating ? 'Creating...' : 'Create Employee' }} <Icon name="check" /></button>
            </div>
          </form>
        </section>
      </div>
    </Transition>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue"
import Icon from "./Icon.vue"
import { employeeApi } from "../api.js"

const emit = defineEmits(["toast", "profile"])
const query = ref("")
const selected = ref(null)
const people = ref([])
const summary = ref({})
const filterOpen = ref(false)
const selectedDept = ref("All")
const selectedStatus = ref("All")
const addModalOpen = ref(false)
const creating = ref(false)

const newForm = reactive({
  firstName: "",
  lastName: "",
  employeeId: "",
  email: "",
  department: "Engineering",
  role: "Software Engineer",
  location: "New Delhi"
})

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
    const matchesQuery = text.includes(query.value.toLowerCase())
    const matchesDept = selectedDept.value === "All" || person.department === selectedDept.value
    const matchesStatus = selectedStatus.value === "All" || (person.status || "Present") === selectedStatus.value
    return matchesQuery && matchesDept && matchesStatus
  })
})

function resetFilters() {
  selectedDept.value = "All"
  selectedStatus.value = "All"
  filterOpen.value = false
}

function sendEmail(email) {
  if (email) {
    window.location.href = `mailto:${email}`
    emit("toast", `Opening email client for ${email}`)
  }
}

async function createEmployee() {
  creating.value = true
  try {
    const created = await employeeApi.create(newForm)
    addModalOpen.value = false
    emit("toast", `${created.name || 'New employee'} added to database`)
    // Reset form
    Object.assign(newForm, {
      firstName: "",
      lastName: "",
      employeeId: "",
      email: "",
      department: "Engineering",
      role: "Software Engineer",
      location: "New Delhi"
    })
    loadPeopleData()
  } catch (err) {
    emit("toast", err.message || "Failed to create employee")
  } finally {
    creating.value = false
  }
}

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
