<template>
  <div class="notification-backdrop" @click.self="$emit('close')">
    <aside class="notification-panel" role="dialog" aria-modal="true" aria-labelledby="notification-title">
      <header>
        <div><span class="section-kicker">Live alerts</span><h2 id="notification-title">Notifications</h2></div>
        <button class="modal-close" type="button" aria-label="Close" @click="$emit('close')"><Icon name="close" /></button>
      </header>
      <div class="notification-tabs">
        <button type="button" :class="{ active: tab === 'inbox' }" @click="tab = 'inbox'">Inbox <span>{{ unread }}</span></button>
        <button type="button" :class="{ active: tab === 'preferences' }" @click="tab = 'preferences'">Preferences</button>
      </div>

      <template v-if="tab === 'inbox'">
        <div class="notification-actions">
          <strong>{{ unread }} unread</strong>
          <button class="text-button" type="button" @click="markAllRead">Mark all as read</button>
        </div>
        <button
          v-for="item in notifications"
          :key="item.id"
          class="notification-item"
          :class="{ unread: !item.read }"
          type="button"
          @click="handleNotificationClick(item)"
        >
          <span class="metric-icon" :class="item.tone"><Icon :name="item.icon" /></span>
          <span>
            <strong>{{ item.title }}</strong>
            <small>{{ item.detail }}</small>
            <time>{{ item.time }}</time>
          </span>
          <i v-if="!item.read"></i>
        </button>
        <div v-if="!notifications.length" class="empty-state" style="padding: 2rem 0;">
          <span><Icon name="check" /></span>
          <p>No notifications yet.</p>
        </div>
      </template>

      <template v-else>
        <div class="preference-intro">
          <Icon name="bell" />
          <div><strong>Choose how ARIA reaches you</strong><small>Saved in PostgreSQL database for your user profile.</small></div>
        </div>
        <div v-for="preference in preferences" :key="preference.key" class="preference-row">
          <span><strong>{{ preference.label }}</strong><small>{{ preference.detail }}</small></span>
          <div class="channel-toggles">
            <label><input v-model="preference.email" type="checkbox" /> Email</label>
            <label><input v-model="preference.push" type="checkbox" /> Push</label>
          </div>
        </div>
        <button class="primary-button save-preferences" type="button" @click="savePreferences">Save notification preferences</button>
      </template>
    </aside>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue"
import Icon from "./Icon.vue"
import { coreApi } from "../api.js"

const emit = defineEmits(["close", "toast", "read", "navigate"])
const tab = ref("inbox")
const notifications = ref([])
const preferences = ref([
  { key: "approvals", label: "Approval requests", detail: "Leave and attendance decisions", email: true, push: true },
  { key: "payroll", label: "Payroll alerts", detail: "Readiness checks and pay runs", email: true, push: true },
  { key: "attendance", label: "Attendance exceptions", detail: "Missing or unusual check-ins", email: false, push: true },
  { key: "announcements", label: "Workplace announcements", detail: "HR updates and policy changes", email: true, push: false },
])

async function loadNotifications() {
  try {
    const data = await coreApi.getNotifications()
    if (data.notifications) notifications.value = data.notifications
    if (data.preferences && data.preferences.length) preferences.value = data.preferences
  } catch (err) {
    console.error("Failed to load notifications", err)
  }
}

onMounted(() => {
  loadNotifications()
})

const unread = computed(() => notifications.value.filter((item) => !item.read).length)

function handleNotificationClick(item) {
  item.read = true
  emit("close")
  const title = (item.title || "").toLowerCase()
  if (title.includes("leave") || title.includes("time off")) {
    emit("navigate", "Time off")
  } else if (title.includes("payroll")) {
    emit("navigate", "Payroll")
  } else if (title.includes("roster") || title.includes("shift")) {
    emit("navigate", "Roster")
  } else if (title.includes("attendance") || title.includes("check-in")) {
    emit("navigate", "Attendance")
  } else {
    emit("navigate", "Command centre")
  }
}

async function markAllRead() {
  notifications.value.forEach((item) => { item.read = true })
  try {
    await coreApi.markNotificationsRead()
  } catch (err) {
    console.error("Failed to mark notifications read", err)
  }
  emit("read")
  emit("toast", "All notifications marked as read")
}

async function savePreferences() {
  try {
    await coreApi.savePreferences(preferences.value)
    emit("toast", "Notification preferences saved to database")
  } catch (err) {
    emit("toast", err.message || "Failed to save preferences")
  }
}
</script>
