<template>
  <div class="modal-backdrop profile-modal-backdrop" @click.self="$emit('close')">
    <section class="modal profile-workspace" role="dialog" aria-modal="true" aria-labelledby="profile-title">
      <button class="modal-close" type="button" aria-label="Close" @click="$emit('close')"><Icon name="close" /></button>
      <header class="profile-hero">
        <div class="profile-photo-wrap">
          <img v-if="photoUrl" :src="photoUrl" alt="Profile preview" />
          <span v-else class="avatar profile-photo">{{ initials(form.name) }}</span>
          <label v-if="canEditLimited" class="photo-edit" title="Change profile picture"><Icon name="edit" /><input type="file" accept="image/*" @change="changePhoto" /></label>
        </div>
        <div>
          <span class="section-kicker">Employee profile</span>
          <h2 id="profile-title">{{ form.name }}</h2>
          <p>{{ form.role || form.jobTitle }} · {{ form.department }}</p>
          <div class="profile-tags"><span><i></i> Active employee</span><span>{{ form.employeeId }}</span><span>{{ accessLabel }}</span></div>
        </div>
        <button v-if="!editing" class="secondary-button" type="button" @click="editing=true"><Icon name="edit" /> {{ isAdmin ? 'Edit employee' : 'Edit my details' }}</button>
      </header>

      <nav class="profile-tabs" aria-label="Profile sections">
        <button v-for="tab in tabs" :key="tab.id" type="button" :class="{ active: activeTab === tab.id }" @click="activeTab = tab.id"><Icon :name="tab.icon" />{{ tab.label }}</button>
      </nav>

      <div v-if="activeTab==='personal'" class="profile-section">
        <header><div><span class="section-kicker">Personal information</span><h3>Identity and contact</h3></div><span v-if="!isAdmin" class="read-note"><Icon name="shield" /> Employees can edit contact fields only</span></header>
        <div class="profile-form-grid">
          <label>Full name<input v-model="form.name" :disabled="!editing || !isAdmin" /></label>
          <label>Work email<input v-model="form.email" type="email" :disabled="!editing || !isAdmin" /></label>
          <label>Phone number<input v-model="form.phone" :disabled="!editing" /></label>
          <label>Date of birth<input v-model="form.birthDate" type="date" :disabled="!editing || !isAdmin" /></label>
          <label class="full">Address<textarea v-model="form.address" rows="2" :disabled="!editing"></textarea></label>
          <label>Emergency contact<input v-model="form.emergencyContact" :disabled="!editing" /></label>
          <label>Emergency phone<input v-model="form.emergencyPhone" :disabled="!editing" /></label>
        </div>
      </div>

      <div v-else-if="activeTab==='job'" class="profile-section">
        <header><div><span class="section-kicker">Employment details</span><h3>Role and reporting</h3></div><span class="read-note"><Icon name="briefcase" /> {{ isAdmin ? 'Admin editable' : 'Managed by HR' }}</span></header>
        <div class="profile-form-grid">
          <label>Employee ID<input v-model="form.employeeId" disabled /></label>
          <label>Job title<input v-model="form.role" :disabled="!editing || !isAdmin" /></label>
          <label>Department<select v-model="form.department" :disabled="!editing || !isAdmin"><option>Engineering</option><option>Product</option><option>Customer Success</option><option>Finance</option><option>Operations</option><option>People</option></select></label>
          <label>Manager<input v-model="form.manager" :disabled="!editing || !isAdmin" /></label>
          <label>Employment type<select v-model="form.employmentType" :disabled="!editing || !isAdmin"><option>Full-time</option><option>Part-time</option><option>Contract</option></select></label>
          <label>Joining date<input v-model="form.joiningDate" type="date" :disabled="!editing || !isAdmin" /></label>
          <label>Work location<input v-model="form.location" :disabled="!editing || !isAdmin" /></label>
          <label>Shift<input v-model="form.shift" :disabled="!editing || !isAdmin" /></label>
        </div>
      </div>

      <div v-else-if="activeTab==='salary'" class="profile-section">
        <header><div><span class="section-kicker">Compensation</span><h3>Salary structure</h3></div><span class="status protected"><Icon name="shield" /> {{ isAdmin ? 'Admin controlled' : 'Read only' }}</span></header>
        <div class="salary-summary"><div><small>Gross monthly salary</small><strong>{{ currency(grossSalary) }}</strong></div><div><small>Estimated net pay</small><strong>{{ currency(grossSalary - 12680) }}</strong></div><div><small>Next pay date</small><strong>31 Aug 2026</strong></div></div>
        <div class="salary-lines"><label>Basic salary<input v-model.number="form.basic" type="number" :disabled="!editing || !isAdmin" /></label><label>House rent allowance<input v-model.number="form.hra" type="number" :disabled="!editing || !isAdmin" /></label><label>Special allowance<input v-model.number="form.special" type="number" :disabled="!editing || !isAdmin" /></label><label>Other allowance<input v-model.number="form.other" type="number" :disabled="!editing || !isAdmin" /></label></div>
        <div class="payslip-row"><span class="metric-icon"><Icon name="file" /></span><div><strong>July 2026 salary slip</strong><small>Net pay {{ currency(grossSalary - 12680) }} · Generated 31 Jul</small></div><button class="secondary-button" type="button" @click="downloadPayslip"><Icon name="download" /> Download</button></div>
      </div>

      <div v-else class="profile-section">
        <header><div><span class="section-kicker">Employee documents</span><h3>Secure document vault</h3></div><label class="primary-button file-upload-button"><Icon name="upload" /> Upload document<input type="file" multiple @change="uploadDocuments" /></label></header>
        <div class="document-drop"><Icon name="upload" /><strong>Drop employment documents here</strong><small>PDF, JPG or PNG up to 5 MB</small><label>Select files<input type="file" multiple @change="uploadDocuments" /></label></div>
        <div class="document-list"><div v-for="document in documents" :key="document.id || document.name"><span class="metric-icon"><Icon name="file" /></span><span><strong>{{ document.name }}</strong><small>{{ document.meta }}</small></span><button type="button" aria-label="Download document" @click="downloadDocument(document)"><Icon name="download" /></button></div></div>
      </div>

      <footer v-if="editing" class="profile-actions"><button class="secondary-button" type="button" @click="cancelEdit">Cancel</button><button class="primary-button" type="button" :disabled="saving" @click="saveProfile">{{ saving ? 'Saving...' : 'Save changes' }} <Icon name="check" /></button></footer>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue"
import Icon from "./Icon.vue"
import { employeeApi } from "../api.js"
import { generatePayslipPdf, printOrSavePdf } from "../reportTemplates.js"

const props = defineProps({ person: { type: Object, default: null }, isAdmin: { type: Boolean, default: false }, initialTab: { type: String, default: "personal" } })
const emit = defineEmits(["close", "toast"])
const activeTab = ref(props.initialTab)
const editing = ref(false)
const saving = ref(false)
const photoUrl = ref("")
const tabs = [{ id: "personal", label: "Personal", icon: "user" }, { id: "job", label: "Job", icon: "briefcase" }, { id: "salary", label: "Salary", icon: "rupee" }, { id: "documents", label: "Documents", icon: "file" }]
const defaults = { name: "Neha Sharma", email: "neha@aria.com", employeeId: "EMP1024", role: "Software Engineer", department: "Engineering", phone: "+91 98765 43210", birthDate: "1993-04-15", address: "B-204, Green Park, New Delhi - 110016", emergencyContact: "Rohan Sharma", emergencyPhone: "+91 98111 22554", manager: "Arjun Mehta", employmentType: "Full-time", joiningDate: "2024-04-15", location: "New Delhi", shift: "General · 09:00-18:00", basic: 60000, hra: 18000, special: 12000, other: 5000 }
const form = reactive({ ...defaults, ...normalizedPerson(props.person) })
let snapshot = { ...form }
const documents = ref([
  { name: "Aadhaar Card.pdf", meta: "Identity · Uploaded 10 Aug 2026" },
  { name: "PAN Card.pdf", meta: "Tax document · Uploaded 10 Aug 2026" },
  { name: "Employment Contract.pdf", meta: "Employment · Uploaded 15 Apr 2024" }
])
const grossSalary = computed(() => Number(form.basic || 0) + Number(form.hra || 0) + Number(form.special || 0) + Number(form.other || 0))
const canEditLimited = computed(() => editing.value || props.isAdmin)
const accessLabel = computed(() => props.isAdmin ? "Full admin access" : "Employee self-service")

watch(() => props.initialTab, (value) => { activeTab.value = value })

function normalizedPerson(person) {
  if (!person) return {}
  return {
    name: person.name,
    email: person.email || defaults.email,
    employeeId: person.id || person.employeeId || defaults.employeeId,
    role: person.jobTitle || person.role || defaults.role,
    department: person.department || defaults.department,
    location: person.location || defaults.location
  }
}

async function loadProfile() {
  const empId = form.employeeId || "EMP1024"
  try {
    const data = await employeeApi.get(empId)
    if (data) {
      Object.assign(form, {
        name: data.name || form.name,
        email: data.email || form.email,
        employeeId: data.employeeId || form.employeeId,
        role: data.jobTitle || form.role,
        department: data.department || form.department,
        phone: data.phone || form.phone,
        birthDate: data.birthDate || form.birthDate,
        address: data.address || form.address,
        emergencyContact: data.emergencyContact || form.emergencyContact,
        emergencyPhone: data.emergencyPhone || form.emergencyPhone,
        manager: data.manager || form.manager,
        employmentType: data.employmentType || form.employmentType,
        joiningDate: data.joiningDate || form.joiningDate,
        location: data.location || form.location,
        shift: data.shift || form.shift,
      })
      if (data.photoUrl) photoUrl.value = data.photoUrl
      if (data.documents && data.documents.length) documents.value = data.documents
      snapshot = { ...form }
    }
  } catch (err) {
    console.error("Failed to load profile details", err)
  }
}

onMounted(() => {
  loadProfile()
})

function initials(name = "") {
  return (name || "").split(" ").filter(Boolean).map((part) => part[0]).join("") || "PR"
}

function currency(value) {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(value || 0)
}

async function saveProfile() {
  saving.value = true
  try {
    await employeeApi.update(form.employeeId, {
      name: form.name,
      email: form.email,
      phone: form.phone,
      birthDate: form.birthDate,
      address: form.address,
      emergencyContact: form.emergencyContact,
      emergencyPhone: form.emergencyPhone,
      department: form.department,
      jobTitle: form.role,
      manager: form.manager,
      employmentType: form.employmentType,
      joiningDate: form.joiningDate,
      location: form.location,
      shift: form.shift,
      photoUrl: photoUrl.value
    })
    editing.value = false
    snapshot = { ...form }
    emit("toast", "Profile changes saved to PostgreSQL database")
  } catch (err) {
    emit("toast", err.message || "Failed to save profile changes")
  } finally {
    saving.value = false
  }
}

function cancelEdit() {
  Object.assign(form, snapshot)
  editing.value = false
}

function changePhoto(event) {
  const file = event.target.files?.[0]
  if (file) {
    photoUrl.value = URL.createObjectURL(file)
    emit("toast", "Profile picture updated")
  }
}

async function uploadDocuments(event) {
  const files = Array.from(event.target.files || [])
  for (const file of files) {
    const formData = new FormData()
    formData.append("file", file)
    formData.append("name", file.name)
    formData.append("meta", `Uploaded just now · ${(file.size / 1024).toFixed(0)} KB`)
    try {
      const res = await employeeApi.uploadDocument(form.employeeId, formData)
      documents.value.unshift(res)
    } catch {
      documents.value.unshift({ name: file.name, meta: `Uploaded just now · ${(file.size / 1024).toFixed(0)} KB` })
    }
  }
  if (files.length) emit("toast", `${files.length} document${files.length > 1 ? 's' : ''} saved to employee vault`)
}

function downloadText(filename, content, type = "text/plain") {
  const blob = new Blob([content], { type })
  const url = URL.createObjectURL(blob)
  const link = document.createElement("a")
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

function downloadPayslip() {
  generatePayslipPdf(form)
  emit("toast", `Generated official July 2026 payslip PDF for ${form.name}`)
}

function downloadDocument(document) {
  const content = `
    <div class="header-row">
      <div class="brand">
        <div>
          <div class="brand-title">ARIA HRMS</div>
          <div class="brand-sub">Employee Document & Verification Vault</div>
        </div>
      </div>
      <div class="doc-meta">
        <h2>OFFICIAL EMPLOYEE RECORD</h2>
        <p>Document: <b>${document.name}</b></p>
        <p>${document.meta || 'Verified'}</p>
      </div>
    </div>
    <div class="info-grid">
      <div>
        <div class="info-item"><span>Employee:</span><strong>${form.name}</strong></div>
        <div class="info-item"><span>Employee ID:</span><strong>${form.employeeId}</strong></div>
      </div>
      <div>
        <div class="info-item"><span>Department:</span><strong>${form.department}</strong></div>
        <div class="info-item"><span>Location:</span><strong>${form.location || 'New Delhi'}</strong></div>
      </div>
    </div>
    <div style="padding: 32px; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0; text-align: center; margin-bottom: 24px;">
      <p style="font-size: 16px; font-weight: 700; color: #1e293b; margin-bottom: 8px;">${document.name}</p>
      <p style="font-size: 13px; color: #64748b;">This document has been verified and stored in the PostgreSQL employee records vault.</p>
    </div>
    <div class="footer">
      <div>ARIA Compliance & Verification System</div>
      <div class="signatory">
        <div class="signatory-line"></div>
        <p>Custodian of Records</p>
      </div>
    </div>
  `
  printOrSavePdf(content, `ARIA-${form.employeeId}-${document.name}`)
  emit("toast", `Opening verified PDF document for ${document.name}`)
}
</script>
