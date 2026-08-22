<template>
  <section>
    <header class="page-title-row">
      <div>
        <p class="eyebrow">Payroll readiness</p>
        <h1>Close payroll without the scramble.</h1>
        <p>Catch attendance, leave and compensation issues before they become payroll errors.</p>
      </div>
      <div class="header-actions">
        <a class="secondary-button" :href="exportReportUrl" download="ARIA-payroll-report.csv"><Icon name="download" /> Report</a>
        <button class="primary-button" type="button" @click="runPayroll"><Icon name="rupee" /> {{ running ? 'Checked' : 'Run payroll check' }}</button>
      </div>
    </header>

    <div class="payroll-hero surface">
      <div class="readiness-ring">
        <span><strong>{{ running ? '100' : '90' }}</strong><small>% ready</small></span>
      </div>
      <div>
        <span class="section-kicker">August 2026 payroll</span>
        <h2>{{ running ? 'Payroll is ready to close' : 'Almost ready. Twelve checks remain.' }}</h2>
        <p>{{ running ? 'All 120 employee records passed validation in PostgreSQL.' : 'Resolve attendance and bank-detail exceptions before 28 August.' }}</p>
        <div class="payroll-tags">
          <span><Icon name="check" /> 108 cleared</span>
          <span class="warn"><Icon name="clock" /> {{ running ? 0 : 12 }} to review</span>
          <span><Icon name="calendar" /> 6 days left</span>
        </div>
      </div>
      <button class="primary-button dark" type="button" @click="runPayroll">{{ running ? 'Close payroll' : 'Review 12 checks' }} <Icon name="arrow" /></button>
    </div>

    <div class="summary-grid four">
      <article class="summary-card"><span class="metric-icon"><Icon name="rupee" /></span><div><small>Gross payroll</small><strong>{{ summary.grossPayroll || '₹84.6L' }}</strong><em>+3.2% MoM</em></div></article>
      <article class="summary-card"><span class="metric-icon"><Icon name="users" /></span><div><small>Employees</small><strong>{{ summary.employeeCount || 120 }}</strong><em>All included</em></div></article>
      <article class="summary-card"><span class="metric-icon"><Icon name="calendar" /></span><div><small>Pay date</small><strong>{{ summary.payDate || '31 Aug' }}</strong><em>On schedule</em></div></article>
      <article class="summary-card"><span class="metric-icon warning"><Icon name="spark" /></span><div><small>Exceptions</small><strong>{{ running ? 0 : (summary.exceptions || 12) }}</strong><em>{{ running ? 'Resolved' : 'Need review' }}</em></div></article>
    </div>

    <div class="content-grid payroll-grid">
      <article class="surface">
        <header class="section-heading">
          <div><span class="section-kicker">Pre-flight checks</span><h2>Payroll checklist</h2></div>
          <span class="status protected">{{ running ? 'Complete' : '90%' }}</span>
        </header>
        <button v-for="check in checks" :key="check.label" type="button" class="payroll-check">
          <span class="metric-icon" :class="check.tone"><Icon :name="check.icon" /></span>
          <span><strong>{{ check.label }}</strong><small>{{ running ? 'No issues found' : check.detail }}</small></span>
          <span class="status" :class="running ? 'protected' : check.statusTone">{{ running ? 'Clear' : check.status }}</span>
          <Icon name="chevron" />
        </button>
      </article>

      <article class="surface cost-card">
        <header class="section-heading">
          <div><span class="section-kicker">Monthly trend</span><h2>Payroll cost</h2></div>
          <span class="status protected">Stable</span>
        </header>
        <div class="cost-chart">
          <div v-for="month in months" :key="month.name">
            <span :style="{ height: month.value + '%' }"></span>
            <strong>₹{{ month.amount }}L</strong>
            <small>{{ month.name }}</small>
          </div>
        </div>
        <div class="forecast">
          <span><small>September forecast</small><strong>₹86.1L</strong></span>
          <span><small>Expected change</small><strong>+1.8%</strong></span>
        </div>
      </article>
    </div>

    <article class="surface table-surface payroll-employee-surface">
      <header class="section-heading table-heading">
        <div><span class="section-kicker">Employee payroll</span><h2>Salary structures and payslips</h2></div>
        <span class="read-note"><Icon name="shield" /> HR admin controls</span>
      </header>
      <div class="payroll-employee-table table-scroll">
        <div class="table-row table-head">
          <span>Employee</span><span>Basic</span><span>Allowances</span><span>Gross salary</span><span>Net pay</span><span>Status</span><span></span>
        </div>
        <button v-for="employee in payrollEmployees" :key="employee.id" class="table-row" type="button" @click="openEmployee(employee)">
          <span class="employee-cell">
            <span class="avatar" :class="employee.color">{{ employee.initials }}</span>
            <span><strong>{{ employee.name }}</strong><small>{{ employee.id }} · {{ employee.role }}</small></span>
          </span>
          <span>{{ currency(employee.basic) }}</span>
          <span>{{ currency(employee.hra + employee.special + employee.other) }}</span>
          <span><strong>{{ currency(gross(employee)) }}</strong></span>
          <span>{{ currency(gross(employee) - employee.deductions) }}</span>
          <span><span class="status protected">Ready</span></span>
          <span><Icon name="chevron" /></span>
        </button>
      </div>
    </article>

    <Transition name="fade">
      <div v-if="selectedPayroll" class="modal-backdrop" @click.self="selectedPayroll = null">
        <section class="modal salary-editor" role="dialog" aria-modal="true" aria-labelledby="salary-editor-title">
          <button class="modal-close" type="button" aria-label="Close" @click="selectedPayroll = null"><Icon name="close" /></button>
          <span class="section-kicker">Admin payroll control</span>
          <h2 id="salary-editor-title">{{ selectedPayroll.name }}</h2>
          <div class="decision-person">
            <span class="avatar" :class="selectedPayroll.color">{{ selectedPayroll.initials }}</span>
            <div><strong>{{ selectedPayroll.role }}</strong><small>{{ selectedPayroll.id }} · August 2026</small></div>
            <span class="status protected">Ready</span>
          </div>
          <div class="salary-editor-grid">
            <label>Basic salary<input v-model.number="selectedPayroll.basic" type="number" /></label>
            <label>House rent allowance<input v-model.number="selectedPayroll.hra" type="number" /></label>
            <label>Special allowance<input v-model.number="selectedPayroll.special" type="number" /></label>
            <label>Other allowance<input v-model.number="selectedPayroll.other" type="number" /></label>
            <label>Deductions<input v-model.number="selectedPayroll.deductions" type="number" /></label>
            <div class="salary-total">
              <small>Estimated net pay</small>
              <strong>{{ currency(gross(selectedPayroll) - selectedPayroll.deductions) }}</strong>
            </div>
          </div>
          <div class="modal-actions">
            <button class="secondary-button" type="button" @click="downloadPayslip(selectedPayroll)"><Icon name="download" /> Payslip</button>
            <button class="primary-button" type="button" @click="saveSalary">Save salary structure <Icon name="check" /></button>
          </div>
        </section>
      </div>
    </Transition>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue"
import Icon from "./Icon.vue"
import { payrollApi } from "../api.js"

const emit = defineEmits(["toast"])
const exportReportUrl = payrollApi.exportReportUrl()
const running = ref(false)
const selectedPayroll = ref(null)
const summary = ref({})
const checks = ref([])
const months = ref([])
const payrollEmployees = ref([])

async function loadPayroll() {
  try {
    const data = await payrollApi.getSummary()
    running.value = Boolean(data.running)
    if (data.summary) summary.value = data.summary
    if (data.checks) checks.value = data.checks
    if (data.months) months.value = data.months
    if (data.payrollEmployees) payrollEmployees.value = data.payrollEmployees
  } catch (err) {
    console.error("Failed to load payroll data", err)
  }
}

onMounted(() => {
  loadPayroll()
})

async function runPayroll() {
  try {
    const res = await payrollApi.runCheck()
    running.value = true
    emit("toast", res.message || "Payroll validation completed — all checks are clear")
    loadPayroll()
  } catch (err) {
    emit("toast", err.message || "Failed to run payroll validation")
  }
}

function gross(employee) {
  return Number(employee.basic || 0) + Number(employee.hra || 0) + Number(employee.special || 0) + Number(employee.other || 0)
}

function currency(value) {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(value || 0)
}

function openEmployee(employee) {
  selectedPayroll.value = { ...employee }
}

async function saveSalary() {
  const emp = selectedPayroll.value
  try {
    const res = await payrollApi.updateSalary(emp.id, emp)
    emit("toast", res.message || `${emp.name}'s salary structure saved to database`)
    selectedPayroll.value = null
    loadPayroll()
  } catch (err) {
    emit("toast", err.message || "Failed to save salary structure")
  }
}

function downloadFile(filename, content, type = "text/plain") {
  const blob = new Blob([content], { type })
  const url = URL.createObjectURL(blob)
  const link = document.createElement("a")
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

function downloadPayslip(employee) {
  downloadFile(
    `ARIA-${employee.id}-August-2026-payslip.txt`,
    `ARIA SALARY SLIP\nEmployee: ${employee.name}\nEmployee ID: ${employee.id}\nPeriod: August 2026\nBasic: ${currency(employee.basic)}\nAllowances: ${currency(employee.hra + employee.special + employee.other)}\nDeductions: ${currency(employee.deductions)}\nNet pay: ${currency(gross(employee) - employee.deductions)}`
  )
  emit("toast", `${employee.name}'s payslip downloaded`)
}
</script>
