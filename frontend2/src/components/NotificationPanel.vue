<template>
  <div class="notification-backdrop" @click.self="$emit('close')">
    <aside class="notification-panel" role="dialog" aria-modal="true" aria-labelledby="notification-title">
      <header><div><span class="section-kicker">Live alerts</span><h2 id="notification-title">Notifications</h2></div><button class="modal-close" type="button" aria-label="Close" @click="$emit('close')"><Icon name="close" /></button></header>
      <div class="notification-tabs"><button type="button" :class="{active:tab==='inbox'}" @click="tab='inbox'">Inbox <span>{{unread}}</span></button><button type="button" :class="{active:tab==='preferences'}" @click="tab='preferences'">Preferences</button></div>
      <template v-if="tab==='inbox'">
        <div class="notification-actions"><strong>{{unread}} unread</strong><button class="text-button" type="button" @click="markAllRead">Mark all as read</button></div>
        <button v-for="item in notifications" :key="item.id" class="notification-item" :class="{unread:!item.read}" type="button" @click="item.read=true">
          <span class="metric-icon" :class="item.tone"><Icon :name="item.icon" /></span><span><strong>{{item.title}}</strong><small>{{item.detail}}</small><time>{{item.time}}</time></span><i v-if="!item.read"></i>
        </button>
      </template>
      <template v-else>
        <div class="preference-intro"><Icon name="bell" /><div><strong>Choose how ARIA reaches you</strong><small>These controls are stored locally for the frontend demonstration.</small></div></div>
        <div v-for="preference in preferences" :key="preference.key" class="preference-row"><span><strong>{{preference.label}}</strong><small>{{preference.detail}}</small></span><div class="channel-toggles"><label><input v-model="preference.email" type="checkbox" /> Email</label><label><input v-model="preference.push" type="checkbox" /> Push</label></div></div>
        <button class="primary-button save-preferences" type="button" @click="savePreferences">Save notification preferences</button>
      </template>
    </aside>
  </div>
</template>
<script setup>
import { computed, reactive, ref } from "vue"
import Icon from "./Icon.vue"
const emit=defineEmits(["close","toast","read"])
const tab=ref("inbox")
const notifications=reactive([{id:1,title:"Leave request needs review",detail:"Aisha Khan · 24–25 Aug",time:"2 minutes ago",icon:"leave",tone:"warning",read:false},{id:2,title:"Payroll check completed",detail:"12 employee records need attention",time:"18 minutes ago",icon:"rupee",tone:"",read:false},{id:3,title:"Roster published",detail:"Support team · 18–24 August",time:"1 hour ago",icon:"calendar",tone:"",read:false},{id:4,title:"Profile updated",detail:"Neha Sharma changed her phone number",time:"Yesterday",icon:"user",tone:"",read:true}])
const preferences=reactive([{key:"approvals",label:"Approval requests",detail:"Leave and attendance decisions",email:true,push:true},{key:"payroll",label:"Payroll alerts",detail:"Readiness checks and pay runs",email:true,push:true},{key:"attendance",label:"Attendance exceptions",detail:"Missing or unusual check-ins",email:false,push:true},{key:"announcements",label:"Workplace announcements",detail:"HR updates and policy changes",email:true,push:false}])
const unread=computed(()=>notifications.filter(item=>!item.read).length)
function markAllRead(){notifications.forEach(item=>item.read=true);emit("read");emit("toast","All notifications marked as read")}
function savePreferences(){localStorage.setItem("aria-notification-preferences",JSON.stringify(preferences));emit("toast","Notification preferences saved locally")}
</script>
