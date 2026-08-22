<template>
  <section>
    <header class="page-title-row">
      <div><p class="eyebrow">People directory</p><h1>Know the people behind the work.</h1><p>One current record for every teammate, role and reporting line.</p></div>
      <button class="primary-button" type="button" @click="$emit('toast', 'Invite link copied')"><Icon name="user-plus" /> Add employee</button>
    </header>
    <div class="summary-grid four">
      <article class="summary-card"><span class="metric-icon"><Icon name="users" /></span><div><small>Active employees</small><strong>120</strong><em>+5 this month</em></div></article>
      <article class="summary-card"><span class="metric-icon"><Icon name="building" /></span><div><small>Departments</small><strong>8</strong><em>All staffed</em></div></article>
      <article class="summary-card"><span class="metric-icon"><Icon name="user-plus" /></span><div><small>New joiners</small><strong>5</strong><em>August cohort</em></div></article>
      <article class="summary-card"><span class="metric-icon"><Icon name="clock" /></span><div><small>On probation</small><strong>7</strong><em>2 reviews due</em></div></article>
    </div>
    <article class="surface table-surface">
      <header class="section-heading table-heading"><div><span class="section-kicker">120 employees</span><h2>Everyone at ARIA</h2></div><div class="table-tools"><label class="search-box"><Icon name="search" /><input v-model="query" placeholder="Search people" /></label><button class="secondary-button" type="button"><Icon name="filter" /> Filter</button></div></header>
      <div class="people-table table-scroll">
        <div class="table-row table-head"><span>Employee</span><span>Role</span><span>Department</span><span>Status</span><span>Joined</span><span></span></div>
        <button v-for="person in filteredPeople" :key="person.id" class="table-row" type="button" @click="selected = person">
          <span class="employee-cell"><span class="avatar" :class="person.color">{{ initials(person.name) }}</span><span><strong>{{ person.name }}</strong><small>{{ person.id }} · {{ person.email }}</small></span></span>
          <span><strong>{{ person.role }}</strong><small>{{ person.location }}</small></span>
          <span>{{ person.department }}</span>
          <span><i class="presence-dot" :class="person.status.toLowerCase()"></i>{{ person.status }}</span>
          <span>{{ person.joined }}</span><span><Icon name="chevron" /></span>
        </button>
      </div>
    </article>

    <Transition name="slide"><aside v-if="selected" class="profile-drawer">
      <button class="modal-close" type="button" aria-label="Close" @click="selected = null"><Icon name="close" /></button>
      <span class="avatar profile-avatar" :class="selected.color">{{ initials(selected.name) }}</span><h2>{{ selected.name }}</h2><p>{{ selected.role }} · {{ selected.department }}</p>
      <div class="profile-status"><i class="presence-dot present"></i> Active employee</div>
      <div class="profile-details"><div><small>Employee ID</small><strong>{{ selected.id }}</strong></div><div><small>Location</small><strong>{{ selected.location }}</strong></div><div><small>Joined</small><strong>{{ selected.joined }}</strong></div><div><small>Manager</small><strong>Arjun Mehta</strong></div></div>
      <button class="primary-button" type="button" @click="$emit('profile', selected)">View full profile <Icon name="arrow" /></button>
      <button class="secondary-button" type="button"><Icon name="mail" /> Send email</button>
    </aside></Transition>
  </section>
</template>

<script setup>
import { computed, ref } from "vue"
import Icon from "./Icon.vue"
defineEmits(["toast", "profile"])
const query = ref("")
const selected = ref(null)
const people = [
  { name: "Neha Sharma", id: "EMP1024", email: "neha@aria.com", role: "Software Engineer", department: "Engineering", location: "New Delhi", status: "Present", joined: "15 Apr 2024", color: "teal" },
  { name: "Aisha Khan", id: "EMP1038", email: "aisha@aria.com", role: "UX Designer", department: "Product", location: "Mumbai", status: "On leave", joined: "02 Jun 2024", color: "blue" },
  { name: "Rohit Sharma", id: "EMP0991", email: "rohit@aria.com", role: "Support Specialist", department: "Customer Success", location: "Pune", status: "Present", joined: "18 Nov 2023", color: "coral" },
  { name: "Priya Desai", id: "EMP1018", email: "priya@aria.com", role: "Finance Analyst", department: "Finance", location: "Bengaluru", status: "Present", joined: "09 Feb 2024", color: "violet" },
  { name: "Vikram Singh", id: "EMP1042", email: "vikram@aria.com", role: "Operations Lead", department: "Operations", location: "New Delhi", status: "Remote", joined: "12 Jul 2024", color: "amber" },
  { name: "Meera Iyer", id: "EMP0974", email: "meera@aria.com", role: "People Partner", department: "People", location: "Chennai", status: "Present", joined: "01 Aug 2023", color: "teal" },
]
const filteredPeople = computed(() => people.filter((person) => `${person.name} ${person.role} ${person.department}`.toLowerCase().includes(query.value.toLowerCase())))
function initials(name) { return name.split(" ").map((part) => part[0]).join("") }
</script>
