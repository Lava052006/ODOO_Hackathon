<template>
  <AuthScreen v-if="!currentUser" @authenticated="handleAuthenticated" @toast="showToast" />
  <div v-else class="app-shell" :class="{ 'employee-mode': mode === 'employee' }">
    <aside class="sidebar" :class="{ open: mobileMenu }">
      <button class="brand" type="button" @click="handleBrandClick" aria-label="ARIA home">
        <span class="brand-mark" aria-hidden="true">
          <svg viewBox="0 0 48 48" fill="none">
            <path d="M10 29c5-6 9-8 14-8s9 2 14 8" stroke="#ffbf39" stroke-width="3.4" stroke-linecap="round"/>
            <path d="M8 34c6-4 11-6 16-6s10 2 16 6" stroke="#51c6b5" stroke-width="3.4" stroke-linecap="round"/>
            <path d="M24 7v7M10 13l5 5M38 13l-5 5M5 24h7M36 24h7" stroke="#ffbf39" stroke-width="3" stroke-linecap="round"/>
          </svg>
        </span>
        <span><strong>ARIA</strong><small>Every workday, perfectly aligned.</small></span>
      </button>

      <nav class="main-nav" aria-label="Workspace navigation">
        <button v-for="item in availableNavItems" :key="item.label" type="button" :class="{ active: page === item.label && mode === 'admin' }" @click="selectPage(item.label)">
          <Icon :name="item.icon" />
          <span>{{ item.label }}</span>
          <span v-if="item.count" class="nav-count">{{ item.count }}</span>
        </button>
      </nav>

      <div class="workspace-health">
        <span class="health-dot"></span>
        <div><strong>PostgreSQL Connected</strong><small>Live HR workspace active</small></div>
      </div>

      <button class="admin-card" type="button" @click="openProfile(null, 'personal')">
        <span class="avatar amber">{{ initials(currentUser.name || currentUser.username) }}</span>
        <span><strong>{{ currentUser.name || currentUser.username }}</strong><small>{{ currentUser.role === 'admin' ? 'HR Administrator' : 'Employee self-service' }}</small></span>
        <Icon name="chevron" />
      </button>
      <button class="logout-button" type="button" @click="logout"><Icon name="logout" /> Sign out</button>
    </aside>
    <button v-if="mobileMenu" class="scrim" type="button" aria-label="Close menu" @click="mobileMenu = false"></button>

    <main class="workspace">
      <header class="topbar">
        <button class="menu-button" type="button" aria-label="Open menu" @click="mobileMenu = true"><Icon name="menu" /></button>
        <div class="breadcrumb"><span>Workspace</span><b>/</b><strong>{{ mode === 'employee' ? 'My workday' : page }}</strong></div>
        <div class="top-actions">
          <button v-if="isAdmin" class="mode-switch" type="button" @click="toggleMode">
            <Icon :name="mode === 'admin' ? 'building' : 'user'" />
            {{ mode === 'admin' ? 'Admin view' : 'Employee view' }}
          </button>
          <button class="live-chip" type="button"><span></span> Live HR workspace</button>
          <button class="icon-button" type="button" aria-label="Notifications" @click="notificationsOpen = true"><Icon name="bell" /><i v-if="notificationsUnread"></i></button>
          <button class="avatar navy avatar-button" type="button" aria-label="Open profile" @click="openProfile(null, 'personal')">{{ initials(currentUser.name || currentUser.username) }}</button>
        </div>
      </header>

      <div class="page-body">
        <template v-if="mode === 'employee'">
          <EmployeeHome :user="currentUser" @leave="leaveDialog = true" @toast="showToast" @profile="openProfile(null, $event)" />
        </template>

        <template v-else-if="page === 'Command centre'">
          <section class="hero">
            <div>
              <p class="eyebrow">Workday command centre</p>
              <h1>See the whole workday<br />before it drifts.</h1>
              <p class="hero-copy">People, attendance, leave and payroll — aligned in one clear operating view.</p>
            </div>
            <div class="date-callout"><Icon name="calendar" /><div><strong>22 Aug 2026</strong><span>Monthly payroll closes in <b>6 days</b></span></div></div>
          </section>

          <section class="journey-strip" aria-label="Workday status">
            <div v-for="(step, index) in journey" :key="step.label" class="journey-step" @click="selectPage(step.label)" style="cursor: pointer;">
              <span>{{ index + 1 }}</span>
              <div><strong>{{ step.label }}</strong><small>{{ step.note }}</small></div>
            </div>
          </section>

          <section class="command-grid">
            <article class="surface attention-card">
              <header class="section-heading"><div><span class="section-kicker">Decision queue</span><h2>Needs attention</h2></div><button type="button" class="text-button" @click="selectPage('Time off')">View all <Icon name="arrow" /></button></header>
              <button v-for="request in pendingRequests" :key="request.id || request.name" class="person-request" type="button" @click="openDecision(request)">
                <span class="avatar" :class="request.color">{{ initials(request.name) }}</span>
                <span class="person-copy"><strong>{{ request.name }}</strong><small>{{ request.reason }}</small><em>Applied {{ request.applied }}</em></span>
                <span class="status pending">Pending</span>
                <Icon name="chevron" />
              </button>
              <div v-if="!pendingRequests.length" class="empty-state" style="padding: 1rem 0;"><span><Icon name="check" /></span><p>All pending requests are reviewed.</p></div>
              <div class="queue-insight"><Icon name="spark" /><span><strong>{{ pendingRequests.length }} decisions waiting</strong><small>Resolve before today’s 4 PM roster lock.</small></span></div>
            </article>

            <article class="surface alignment-card">
              <header class="section-heading"><div><span class="section-kicker">Live operating view</span><h2>Today is aligned</h2></div><span class="status protected"><Icon name="shield" /> Protected</span></header>
              <div v-for="row in alignment" :key="row.label" class="alignment-row">
                <span class="metric-icon"><Icon :name="row.icon" /></span>
                <div class="alignment-copy"><strong>{{ row.label }}</strong><small>{{ row.detail }}</small></div>
                <b>{{ row.value }}</b>
                <div class="progress"><span :style="{ width: row.progress + '%' }" :class="row.tone"></span></div>
                <button type="button" aria-label="Review" @click="selectPage(row.page)"><Icon name="chevron" /></button>
              </div>
              <div class="mini-metrics">
                <div><Icon name="users" /><span><small>Active employees</small><strong>{{ miniMetrics.activeEmployees || 120 }}</strong></span></div>
                <div><Icon name="leave" /><span><small>On leave today</small><strong>{{ miniMetrics.onLeaveToday || 4 }}</strong></span></div>
                <div><Icon name="clock" /><span><small>Weekly off today</small><strong>{{ miniMetrics.weeklyOffToday || 8 }}</strong></span></div>
                <div><Icon name="user-plus" /><span><small>New hires · Aug</small><strong>{{ miniMetrics.newHires || 5 }}</strong></span></div>
              </div>
              <button class="primary-button dark" type="button" @click="reviewPanel = !reviewPanel">Review today’s actions <Icon name="arrow" /></button>
            </article>
          </section>

          <section v-if="reviewPanel" class="surface review-panel">
            <div><span class="section-kicker">Recommended sequence</span><h2>Close the day in three moves</h2></div>
            <div class="review-steps">
              <button type="button" @click="selectPage('Time off')"><span>01</span><strong>Review {{ pendingRequests.length }} leave requests</strong><small>Prevents a roster gap</small></button>
              <button type="button" @click="selectPage('Attendance')"><span>02</span><strong>Resolve check-in exceptions</strong><small>Keeps payroll clean</small></button>
              <button type="button" @click="selectPage('Roster')"><span>03</span><strong>Publish next week’s roster</strong><small>98% coverage ready</small></button>
            </div>
          </section>

          <section class="lower-grid">
            <article class="surface pulse-card">
              <header class="section-heading"><div><span class="section-kicker">7-day signal</span><h2>Attendance pulse</h2></div><button class="text-button" type="button" @click="selectPage('Attendance')">Open attendance <Icon name="arrow" /></button></header>
              <div class="bars" aria-label="Weekly attendance bar chart">
                <div v-for="bar in attendanceBars" :key="bar.day"><span :style="{ height: bar.value + '%' }"></span><b>{{ bar.value }}%</b><small>{{ bar.day }}</small></div>
              </div>
            </article>
            <article class="surface activity-card">
              <header class="section-heading"><div><span class="section-kicker">Live feed</span><h2>What changed</h2></div><span class="live-label"><i></i> Live</span></header>
              <div v-for="event in activity" :key="event.id || event.title" class="activity-item"><span :class="event.tone"><Icon :name="event.icon" /></span><div><strong>{{ event.title }}</strong><small>{{ event.detail }}</small></div><time>{{ event.time }}</time></div>
            </article>
          </section>
        </template>

        <PeoplePage v-else-if="page === 'People'" @toast="showToast" @profile="openProfile($event, 'personal')" />
        <AttendancePage v-else-if="page === 'Attendance'" @toast="showToast" />
        <TimeOffPage v-else-if="page === 'Time off'" :requests="pendingRequests" @decision="openDecision" @leave="leaveDialog = true" @toast="showToast" />
        <PayrollPage v-else-if="page === 'Payroll'" @toast="showToast" @navigate="handleNavigate" />
        <RosterPage v-else-if="page === 'Roster'" @toast="showToast" />
      </div>
    </main>

    <Transition name="fade">
      <div v-if="decisionDialog" class="modal-backdrop" @click.self="decisionDialog = null">
        <section class="modal decision-modal" role="dialog" aria-modal="true" aria-labelledby="decision-title">
          <button class="modal-close" type="button" aria-label="Close" @click="decisionDialog = null"><Icon name="close" /></button>
          <span class="section-kicker">Leave request review</span>
          <h2 id="decision-title">Make the decision with context</h2>
          <div class="decision-person"><span class="avatar teal">{{ initials(decisionDialog.name) }}</span><div><strong>{{ decisionDialog.name }}</strong><small>{{ decisionDialog.role }}</small></div><span class="status pending">Pending</span></div>
          <div class="decision-facts"><div><small>Date range</small><strong>{{ decisionDialog.range }}</strong></div><div><small>Leave type</small><strong>{{ decisionDialog.leave_type || 'Paid leave' }}</strong></div><div><small>Team coverage</small><strong class="safe">Safe · {{ decisionDialog.team_coverage || '92%' }}</strong></div><div><small>Payroll impact</small><strong>₹0</strong></div></div>
          <div class="impact-note"><Icon name="spark" /><span><strong>Coverage remains protected.</strong><small>No critical skill or deadline conflict detected.</small></span></div>
          <label>Admin comment<textarea v-model="decisionComment" rows="3" placeholder="Add a clear note for the employee"></textarea></label>
          <div class="modal-actions"><button class="secondary-button danger" type="button" @click="resolveDecision('rejected')">Reject</button><button class="primary-button" type="button" @click="resolveDecision('approved')">Approve request <Icon name="arrow" /></button></div>
        </section>
      </div>
    </Transition>

    <Transition name="fade">
      <div v-if="leaveDialog" class="modal-backdrop" @click.self="leaveDialog = false">
        <section class="modal" role="dialog" aria-modal="true" aria-labelledby="leave-title">
          <button class="modal-close" type="button" aria-label="Close" @click="leaveDialog = false"><Icon name="close" /></button>
          <span class="section-kicker">Time off</span><h2 id="leave-title">Request leave</h2>
          <div class="form-grid"><label>Leave type<select v-model="leaveForm.type"><option>Paid leave</option><option>Sick leave</option><option>Unpaid leave</option><option>Work from home</option></select></label><label>From<input v-model="leaveForm.from" type="date" /></label><label>To<input v-model="leaveForm.to" type="date" /></label><label class="full">Reason<textarea v-model="leaveForm.reason" rows="3" placeholder="A short reason helps your manager decide"></textarea></label></div>
          <div class="impact-note"><Icon name="shield" /><span><strong>Your team remains covered.</strong><small>Estimated balance after request: 7 paid days.</small></span></div>
          <div class="modal-actions"><button class="secondary-button" type="button" @click="leaveDialog = false">Cancel</button><button class="primary-button" type="button" @click="submitLeave">Submit request <Icon name="arrow" /></button></div>
        </section>
      </div>
    </Transition>

    <Transition name="fade"><ProfilePanel v-if="profileOpen" :person="profilePerson" :is-admin="isAdmin" :initial-tab="profileTab" @close="profileOpen=false" @toast="showToast" /></Transition>
    <Transition name="fade"><NotificationPanel v-if="notificationsOpen" @close="notificationsOpen=false" @toast="showToast" @read="notificationsUnread=false" @navigate="handleNavigate" /></Transition>

    <Transition name="toast"><div v-if="toast" class="toast" role="status"><span><Icon name="check" /></span>{{ toast }}</div></Transition>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue"
import Icon from "./components/Icon.vue"
import AuthScreen from "./components/AuthScreen.vue"
import ProfilePanel from "./components/ProfilePanel.vue"
import NotificationPanel from "./components/NotificationPanel.vue"
import PeoplePage from "./components/PeoplePage.vue"
import AttendancePage from "./components/AttendancePage.vue"
import TimeOffPage from "./components/TimeOffPage.vue"
import PayrollPage from "./components/PayrollPage.vue"
import RosterPage from "./components/RosterPage.vue"
import EmployeeHome from "./components/EmployeeHome.vue"
import { authApi, coreApi, leavesApi } from "./api.js"

const savedSession = sessionStorage.getItem("aria-session")
const currentUser = ref(savedSession ? JSON.parse(savedSession) : null)
const page = ref("Command centre")
const mode = ref(currentUser.value?.role === "employee" ? "employee" : "admin")
const mobileMenu = ref(false)
const reviewPanel = ref(false)
const decisionDialog = ref(null)
const decisionComment = ref("")
const leaveDialog = ref(false)
const toast = ref("")
const profileOpen = ref(false)
const profilePerson = ref(null)
const profileTab = ref("personal")
const notificationsOpen = ref(false)
const notificationsUnread = ref(false)
const leaveForm = ref({ type: "Paid leave", from: "2026-08-25", to: "2026-08-27", reason: "Family event" })
const isAdmin = computed(() => currentUser.value?.role === "admin")

const navItems = [
  { label: "Command centre", icon: "command" },
  { label: "People", icon: "users" },
  { label: "Attendance", icon: "clock", count: 2 },
  { label: "Time off", icon: "leave", count: 3 },
  { label: "Payroll", icon: "rupee", count: 12 },
  { label: "Roster", icon: "calendar" },
]
const availableNavItems = computed(() => isAdmin.value ? navItems : [])

const journey = ref([
  { label: "People", note: "Team ready" },
  { label: "Attendance", note: "98 present" },
  { label: "Time off", note: "7 to review" },
  { label: "Payroll", note: "12 checks" },
  { label: "Roster", note: "Coverage ready" },
])

const pendingRequests = ref([])
const alignment = ref([])
const attendanceBars = ref([])
const activity = ref([])
const miniMetrics = ref({})

async function loadCommandCentre() {
  try {
    const data = await coreApi.getCommandCentre()
    if (data.journey) journey.value = data.journey
    if (data.alignment) alignment.value = data.alignment
    if (data.attendanceBars) attendanceBars.value = data.attendanceBars
    if (data.pendingRequests) pendingRequests.value = data.pendingRequests
    if (data.activity) activity.value = data.activity
    if (data.miniMetrics) miniMetrics.value = data.miniMetrics
  } catch (err) {
    console.error("Failed to load command centre data", err)
  }
}

async function checkNotifications() {
  try {
    const data = await coreApi.getNotifications()
    if (data.notifications && data.notifications.some((n) => !n.read)) {
      notificationsUnread.value = true
    }
  } catch {
    // Ignore notification check error
  }
}

onMounted(() => {
  if (currentUser.value) {
    loadCommandCentre()
    checkNotifications()
  }
})

function initials(name = "") {
  return (name || "").split(" ").filter(Boolean).map((part) => part[0]).join("") || "AR"
}

function handleBrandClick() {
  if (currentUser.value?.role === "employee") {
    mode.value = "employee"
  } else {
    selectPage("Command centre")
  }
  mobileMenu.value = false
  window.scrollTo({ top: 0, behavior: "smooth" })
}

function selectPage(value) {
  page.value = value
  mode.value = "admin"
  mobileMenu.value = false
  window.scrollTo({ top: 0, behavior: "smooth" })
  if (value === "Command centre") {
    loadCommandCentre()
  }
}

function handleNavigate(target) {
  selectPage(target)
}

function toggleMode() {
  mode.value = mode.value === "admin" ? "employee" : "admin"
}

function handleAuthenticated(user) {
  currentUser.value = user
  mode.value = user.role === "admin" ? "admin" : "employee"
  sessionStorage.setItem("aria-session", JSON.stringify(user))
  if (user.newlyVerified) showToast("Email verified — your ARIA account is ready")
  loadCommandCentre()
  checkNotifications()
}

async function logout() {
  try {
    await authApi.logout()
  } catch (err) {
    // Ignore logout network errors
  }
  sessionStorage.removeItem("aria-session")
  currentUser.value = null
  mode.value = "admin"
  page.value = "Command centre"
  mobileMenu.value = false
  showToast("Signed out securely")
}

function openProfile(person = null, tab = "personal") {
  profilePerson.value = person || {
    name: currentUser.value.name,
    email: currentUser.value.email,
    employeeId: currentUser.value.employeeId,
    role: currentUser.value.jobTitle || (currentUser.value.role === "admin" ? "HR Administrator" : "Software Engineer"),
    department: currentUser.value.department || (currentUser.value.role === "admin" ? "People" : "Engineering"),
    location: currentUser.value.location || "New Delhi"
  }
  profileTab.value = tab
  profileOpen.value = true
}

function openDecision(request) {
  decisionDialog.value = request
  decisionComment.value = ""
}

async function resolveDecision(state) {
  const req = decisionDialog.value
  const name = req.name
  try {
    await leavesApi.resolve(req.id, state, decisionComment.value)
    pendingRequests.value = pendingRequests.value.filter((r) => r.id !== req.id && r !== req)
    decisionDialog.value = null
    showToast(`${name}'s request was ${state}`)
    loadCommandCentre()
  } catch (err) {
    showToast(err.message || "Failed to update decision")
  }
}

async function submitLeave() {
  try {
    await leavesApi.submit(leaveForm.value)
    leaveDialog.value = false
    showToast("Leave request submitted for approval")
    loadCommandCentre()
  } catch (err) {
    showToast(err.message || "Failed to submit leave request")
  }
}

let toastTimer
function showToast(message) {
  toast.value = message
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    toast.value = ""
  }, 2800)
}
</script>
