<template>
  <section class="employee-dashboard">
    <header class="employee-title"><div><p class="eyebrow">My workday</p><h1>Good morning, {{firstName}}.</h1><p>Everything you need for today, without the HR maze.</p></div><div class="date-callout"><Icon name="calendar" /><div><strong>Friday, 22 August</strong><span>Connaught Place Office</span></div></div></header>
    <article class="checkin-card"><div class="checkmark"><Icon name="check" /></div><div><span class="section-kicker">Today’s attendance</span><h2>{{checkedIn ? 'Checked in at 09:04' : 'Ready to start your day?'}}</h2><p>{{checkedIn ? 'You have worked 6h 42m so far.' : 'Your shift runs from 09:00 to 18:00.'}}</p></div><button type="button" @click="toggleCheckin">{{checkedIn?'Check out':'Check in'}}</button></article>
    <div class="employee-quick-grid"><button type="button" @click="activePanel='attendance'"><span><Icon name="calendar" /></span><strong>My attendance</strong><small>View weekly attendance</small><Icon name="chevron" /></button><button type="button" @click="$emit('leave')"><span><Icon name="leave" /></span><strong>Request time off</strong><small>Apply for leave or WFH</small><Icon name="chevron" /></button><button type="button" @click="$emit('profile','salary')"><span><Icon name="rupee" /></span><strong>My salary</strong><small>View payslips and earnings</small><Icon name="chevron" /></button><button type="button" @click="$emit('profile','personal')"><span><Icon name="user" /></span><strong>My profile</strong><small>Update your information</small><Icon name="chevron" /></button></div>
    <div class="employee-grid">
      <article class="surface"><header class="section-heading"><div><span class="section-kicker">18–24 August</span><h2>My week</h2></div><span class="status protected">On track</span></header><div class="week-table"><div v-for="day in week" :key="day.name" :class="{today:day.today}"><small>{{day.name}}</small><strong>{{day.status}}</strong><span>{{day.hours}}</span></div></div></article>
      <article class="surface"><header class="section-heading"><div><span class="section-kicker">Next up</span><h2>My requests</h2></div><button class="text-button" type="button" @click="$emit('leave')">New request <Icon name="plus" /></button></header><div class="my-request"><span class="metric-icon"><Icon name="leave" /></span><span><strong>Paid leave</strong><small>25–27 Aug · 3 days</small></span><span class="status pending">Pending</span></div><div class="my-request"><span class="metric-icon"><Icon name="rupee" /></span><span><strong>Travel expense</strong><small>₹2,800 · Submitted 19 Aug</small></span><span class="status protected">Approved</span></div></article>
    </div>
    <article v-if="activePanel" class="surface employee-detail"><button class="modal-close" type="button" @click="activePanel=''" aria-label="Close"><Icon name="close" /></button><span class="section-kicker">{{activePanel}}</span><h2>{{panelTitle}}</h2><p>{{panelCopy}}</p><button class="primary-button" type="button" @click="$emit('toast',`${panelTitle} opened`)" >Continue <Icon name="arrow" /></button></article>
  </section>
</template>
<script setup>
import { computed, ref } from "vue"
import Icon from "./Icon.vue"
const props=defineProps({user:{type:Object,required:true}})
const emit=defineEmits(["leave","toast","profile"])
const checkedIn=ref(true)
const activePanel=ref("")
const firstName=computed(()=>props.user.name.split(" ")[0])
const week=[{name:"Mon",status:"Present",hours:"9h 01m"},{name:"Tue",status:"Present",hours:"9h 08m"},{name:"Wed",status:"Half-day",hours:"4h 05m"},{name:"Thu",status:"Present",hours:"8h 58m"},{name:"Fri",status:"Present",hours:"6h 42m",today:true},{name:"Sat",status:"Off",hours:"—"},{name:"Sun",status:"Off",hours:"—"}]
const panelTitle=computed(()=>({attendance:"Weekly attendance",salary:"Salary and payslips",profile:"Personal profile"}[activePanel.value]||""))
const panelCopy=computed(()=>({attendance:"You have completed 37h 54m this week with no unresolved exceptions.",salary:"Your July payslip is ready. Net pay: ₹74,320.",profile:"Your contact and employment information is complete."}[activePanel.value]||""))
function toggleCheckin(){checkedIn.value=!checkedIn.value;emit("toast",checkedIn.value?"Checked in successfully":"Checked out successfully")}
</script>
