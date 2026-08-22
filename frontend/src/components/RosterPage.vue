<template>
  <section>
    <header class="page-title-row">
      <div>
        <p class="eyebrow">Roster planning</p>
        <h1>Coverage you can see and trust.</h1>
        <p>Build the week around skills, workload and the people who make it work.</p>
      </div>
      <div class="header-actions">
        <div class="filter-dropdown-wrap">
          <button class="secondary-button" type="button" @click="exportDropdownOpen = !exportDropdownOpen">
            <Icon name="download" /> Export <Icon name="chevron" />
          </button>
          <div v-if="exportDropdownOpen" class="filter-dropdown surface" style="min-width: 180px;">
            <button class="text-button" type="button" @click="exportRosterCsv">Download CSV</button>
            <button class="text-button" type="button" @click="exportRosterPdf">Weekly Schedule PDF</button>
          </div>
        </div>
        <button class="primary-button" type="button" @click="publish"><Icon name="check" /> {{ published ? 'Published' : 'Publish roster' }}</button>
      </div>
    </header>

    <div class="roster-banner surface">
      <div>
        <span class="section-kicker">18–24 August 2026</span>
        <h2>{{ published ? 'Roster published to the team' : 'Next week is 98% covered' }}</h2>
        <p>{{ published ? 'Everyone has been notified of their assigned shifts.' : 'One evening shift needs a support specialist before publishing.' }}</p>
      </div>
      <div class="coverage-meter"><span :style="{ width: published ? '100%' : `${coveragePercent}%` }"></span></div>
      <strong>{{ published ? '100%' : `${coveragePercent}%` }}</strong>
    </div>

    <article id="roster-table-section" class="surface roster-surface">
      <header class="section-heading table-heading">
        <div>
          <span class="section-kicker">Weekly schedule</span>
          <h2>Team roster <small v-if="highlightSupport" style="color: var(--teal); font-size: 0.9rem;">(Highlighted: Cover Candidates)</small></h2>
        </div>
        <div class="shift-legend">
          <span><i class="morning"></i> Morning</span>
          <span><i class="evening"></i> Evening</span>
          <span><i class="night"></i> Night</span>
          <span><i class="leave"></i> Leave</span>
          <span><i class="off"></i> Off</span>
        </div>
      </header>
      <div class="roster-table table-scroll">
        <div class="roster-row roster-head">
          <span>Employee</span>
          <span v-for="day in days" :key="day.name"><b>{{ day.name }}</b><small>{{ day.date }} Aug</small></span>
        </div>
        <div
          v-for="person in people"
          :key="person.employeeId || person.name"
          class="roster-row"
          :class="{ 'highlighted-row': highlightSupport && (person.role === 'Customer Success' || person.role === 'Support') }"
        >
          <span class="employee-cell">
            <span class="avatar" :class="person.color">{{ person.initials }}</span>
            <span><strong>{{ person.name }}</strong><small>{{ person.role }}</small></span>
          </span>
          <button v-for="(shift, index) in person.shifts" :key="index" type="button" class="shift-cell" :class="shift.type" @click="cycleShift(person, index)">
            <b>{{ shift.code }}</b>
            <small>{{ shift.label }}</small>
          </button>
        </div>
      </div>
    </article>

    <div class="content-grid roster-bottom">
      <article class="surface">
        <header class="section-heading">
          <div><span class="section-kicker">Skill coverage</span><h2>Coverage by team</h2></div>
        </header>
        <div v-for="team in teams" :key="team.name" class="team-coverage">
          <span><strong>{{ team.name }}</strong><small>{{ team.detail }}</small></span>
          <div class="progress"><span :style="{ width: team.value + '%' }" :class="team.value < 90 ? 'warn' : 'good'"></span></div>
          <b>{{ team.value }}%</b>
        </div>
      </article>

      <article class="surface">
        <header class="section-heading">
          <div><span class="section-kicker">Watch list</span><h2>Potential gaps</h2></div>
        </header>
        <div class="gap-item">
          <span class="metric-icon warning"><Icon name="spark" /></span>
          <span><strong>Saturday evening · Support</strong><small>1 experienced specialist still needed</small></span>
          <button class="text-button" type="button" @click="findCover">Find cover</button>
        </div>
        <div class="gap-item safe">
          <span class="metric-icon"><Icon name="shield" /></span>
          <span><strong>All critical skills protected</strong><small>No single-point-of-failure shifts</small></span>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue"
import Icon from "./Icon.vue"
import { rosterApi } from "../api.js"
import { downloadCsv, printOrSavePdf } from "../reportTemplates.js"

const emit = defineEmits(["toast"])
const exportDropdownOpen = ref(false)
const published = ref(false)
const coveragePercent = ref(98)
const days = ref([])
const people = ref([])
const teams = ref([])
const highlightSupport = ref(false)

const base = {
  M: { code: "M", label: "Morning", type: "morning" },
  E: { code: "E", label: "Evening", type: "evening" },
  N: { code: "N", label: "Night", type: "night" },
  L: { code: "L", label: "Leave", type: "leave" },
  W: { code: "W", label: "Weekly off", type: "off" },
}
const cycle = [base.M, base.E, base.N, base.L, base.W]

async function loadRoster() {
  try {
    const data = await rosterApi.getDashboard()
    published.value = Boolean(data.published)
    coveragePercent.value = data.coveragePercent || 98
    if (data.days) days.value = data.days
    if (data.people) people.value = data.people
    if (data.teams) teams.value = data.teams
  } catch (err) {
    console.error("Failed to load roster data", err)
  }
}

onMounted(() => {
  loadRoster()
})

async function cycleShift(person, index) {
  const current = cycle.findIndex((item) => item.code === person.shifts[index].code)
  const next = cycle[(current + 1) % cycle.length]
  person.shifts[index] = { ...next }
  const dayDate = days.value[index]?.date || (18 + index)

  try {
    await rosterApi.updateShift(person.employeeId, dayDate, next.code)
    emit("toast", `${person.name}'s shift updated to ${next.label}`)
  } catch (err) {
    emit("toast", err.message || "Failed to persist shift in database")
  }
}

async function publish() {
  try {
    const res = await rosterApi.publish()
    published.value = true
    coveragePercent.value = 100
    emit("toast", res.message || "Roster published and team notified")
  } catch (err) {
    emit("toast", err.message || "Failed to publish roster")
  }
}

function findCover() {
  highlightSupport.value = true
  const el = document.getElementById("roster-table-section")
  if (el) {
    el.scrollIntoView({ behavior: "smooth" })
    emit("toast", "Highlighted Support Specialists eligible for Saturday shift")
  }
}

function exportRosterCsv() {
  exportDropdownOpen.value = false
  const header = "Employee ID,Name,Department," + days.value.map((d) => `${d.name} ${d.date} Aug`).join(",") + "\n"
  const rows = people.value.map((p) => {
    const shiftCodes = p.shifts.map((s) => s.code || "M").join(",")
    return `"${p.employeeId}","${p.name}","${p.role}",${shiftCodes}`
  })
  downloadCsv("ARIA-Roster-18-24-Aug-2026.csv", header + rows.join("\n"))
  emit("toast", "Roster schedule exported to CSV")
}

function exportRosterPdf() {
  exportDropdownOpen.value = false
  const dayHeaders = days.value.map((d) => `<th class="text-center">${d.name}<br><small>${d.date} Aug</small></th>`).join('')
  const rosterRows = people.value.map((p) => {
    const shiftCells = p.shifts.map((s) => `
      <td class="text-center">
        <span style="display: inline-block; padding: 2px 6px; border-radius: 4px; font-weight: 700; font-size: 11px; ${
          s.code === 'M' ? 'background: #ccfbf1; color: #0f766e;' :
          s.code === 'E' ? 'background: #e0e7ff; color: #4338ca;' :
          s.code === 'N' ? 'background: #f1f5f9; color: #334155;' :
          s.code === 'L' ? 'background: #fee2e2; color: #b91c1c;' : 'background: #fef3c7; color: #b45309;'
        }">
          ${s.code}
        </span>
      </td>
    `).join('')

    return `
      <tr>
        <td><strong>${p.name}</strong><br><small style="color: #64748b;">${p.role}</small></td>
        <td>${p.employeeId}</td>
        ${shiftCells}
      </tr>
    `
  }).join('')

  const content = `
    <div class="header-row">
      <div class="brand">
        <div>
          <div class="brand-title">ARIA HRMS</div>
          <div class="brand-sub">Workforce Roster & Shift Planning</div>
        </div>
      </div>
      <div class="doc-meta">
        <h2>TEAM ROSTER SCHEDULE</h2>
        <p>Period: <b>18–24 August 2026</b></p>
        <p>Coverage: <b>${coveragePercent.value}% Capacity</b></p>
      </div>
    </div>

    <div class="info-grid">
      <div>
        <div class="info-item"><span>Roster Status:</span><strong style="color: #15803d;">${published.value ? 'Published & Confirmed' : 'Pre-Lock Draft'}</strong></div>
        <div class="info-item"><span>Total Planned Shifts:</span><strong>840 Assignments</strong></div>
      </div>
      <div>
        <div class="info-item"><span>Core Shift Types:</span><strong>M (Morning), E (Evening), N (Night)</strong></div>
        <div class="info-item"><span>Standby Cover:</span><strong>Support Team Verified</strong></div>
      </div>
    </div>

    <table class="report-table">
      <thead>
        <tr>
          <th>Employee</th>
          <th>ID</th>
          ${dayHeaders}
        </tr>
      </thead>
      <tbody>
        ${rosterRows}
      </tbody>
    </table>

    <div class="footer">
      <div>ARIA Schedule Master · Official Workforce Distribution</div>
      <div class="signatory">
        <div class="signatory-line"></div>
        <p>Staffing Coordinator</p>
      </div>
    </div>
  `

  printOrSavePdf(content, `ARIA-Roster-Schedule-18-24-Aug-2026`)
  emit("toast", "Opening Weekly Roster Schedule PDF for print/save")
}
</script>
