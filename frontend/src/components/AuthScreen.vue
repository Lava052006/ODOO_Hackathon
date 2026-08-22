<template>
  <main class="auth-shell">
    <section class="auth-story">
      <div class="auth-brand">
        <span class="auth-brand-mark" aria-hidden="true">
          <svg viewBox="0 0 48 48" fill="none"><path d="M10 29c5-6 9-8 14-8s9 2 14 8" stroke="#ffbf39" stroke-width="3.4" stroke-linecap="round"/><path d="M8 34c6-4 11-6 16-6s10 2 16 6" stroke="#51c6b5" stroke-width="3.4" stroke-linecap="round"/><path d="M24 7v7M10 13l5 5M38 13l-5 5M5 24h7M36 24h7" stroke="#ffbf39" stroke-width="3" stroke-linecap="round"/></svg>
        </span>
        <span><strong>ARIA</strong><small>Every workday, perfectly aligned.</small></span>
      </div>
      <div class="auth-story-copy">
        <p class="eyebrow">Human resource management</p>
        <h1>One clear place for every workday.</h1>
        <p>People, attendance, time off and payroll—securely aligned for employees and HR teams.</p>
      </div>
      <div class="auth-proof"><span><Icon name="shield" /></span><div><strong>Frontend security demonstration</strong><small>Validated credentials, role-restricted screens and session controls.</small></div></div>
    </section>

    <section class="auth-form-wrap">
      <div class="auth-form-card">
        <template v-if="screen === 'signin'">
          <span class="section-kicker">Welcome back</span><h2>Sign in to ARIA</h2><p>Use your work account to continue.</p>
          <form @submit.prevent="signIn">
            <label>Email address<input v-model.trim="signin.email" type="email" autocomplete="username" placeholder="name@aria.com" /></label>
            <label>Password<span class="password-input"><input v-model="signin.password" :type="showPassword ? 'text' : 'password'" autocomplete="current-password" placeholder="Enter your password" /><button type="button" @click="showPassword = !showPassword">{{ showPassword ? 'Hide' : 'Show' }}</button></span></label>
            <div class="auth-between"><label class="checkbox-label"><input v-model="signin.remember" type="checkbox" /> Remember me</label><button type="button" class="text-button" @click="screen='forgot'">Forgot password?</button></div>
            <p v-if="error" class="form-error" role="alert"><Icon name="alert" /> {{ error }}</p>
            <button class="primary-button dark auth-submit" type="submit">Sign in <Icon name="arrow" /></button>
          </form>
          <div class="demo-credentials"><strong>Demo accounts</strong><button type="button" @click="useDemo('admin')"><span>HR Admin</span><code>admin@aria.com · Aria@2026</code></button><button type="button" @click="useDemo('employee')"><span>Employee</span><code>employee@aria.com · Aria@2026</code></button></div>
          <p class="auth-switch">New to ARIA? <button type="button" @click="startSignup">Create an account</button></p>
        </template>

        <template v-else-if="screen === 'signup'">
          <button class="auth-back" type="button" @click="screen='signin'">← Back to sign in</button>
          <span class="section-kicker">Create account</span><h2>Join your workspace</h2><p>Use the employee details provided by HR.</p>
          <form @submit.prevent="requestVerification">
            <div class="auth-two"><label>First name<input v-model.trim="signup.firstName" placeholder="Neha" /></label><label>Last name<input v-model.trim="signup.lastName" placeholder="Sharma" /></label></div>
            <label>Employee ID<input v-model.trim="signup.employeeId" placeholder="EMP1024" /></label>
            <label>Work email<input v-model.trim="signup.email" type="email" placeholder="neha@aria.com" /></label>
            <label>Role<select v-model="signup.role"><option value="employee">Employee</option><option value="admin">HR / Admin</option></select></label>
            <label>Password<span class="password-input"><input v-model="signup.password" :type="showPassword ? 'text' : 'password'" placeholder="Create a strong password" /><button type="button" @click="showPassword=!showPassword">{{showPassword?'Hide':'Show'}}</button></span></label>
            <div class="password-rules"><span :class="{met:passwordChecks.length}">8+ characters</span><span :class="{met:passwordChecks.upper}">Uppercase</span><span :class="{met:passwordChecks.number}">Number</span><span :class="{met:passwordChecks.symbol}">Symbol</span></div>
            <label class="checkbox-label terms"><input v-model="signup.terms" type="checkbox" /> I agree to the Terms of Service and Privacy Policy.</label>
            <p v-if="error" class="form-error" role="alert"><Icon name="alert" /> {{error}}</p>
            <button class="primary-button auth-submit" type="submit">Verify email <Icon name="arrow" /></button>
          </form>
        </template>

        <template v-else-if="screen === 'verify'">
          <button class="auth-back" type="button" @click="screen='signup'">← Edit account details</button>
          <div class="verify-icon"><Icon name="mail" /></div><span class="section-kicker">Email verification</span><h2>Check your inbox</h2><p>Enter the 6-digit code sent to <strong>{{signup.email}}</strong>.</p>
          <div class="otp-row"><input v-for="(_,index) in 6" :key="index" :ref="el => otpInputs[index]=el" v-model="otp[index]" inputmode="numeric" maxlength="1" @input="focusNext(index)" @keydown.backspace="focusPrevious(index)" /></div>
          <p class="verification-demo">Demo verification code: <strong>247109</strong></p>
          <p v-if="error" class="form-error" role="alert"><Icon name="alert" /> {{error}}</p>
          <button class="primary-button auth-submit" type="button" @click="verifyEmail">Verify and continue <Icon name="arrow" /></button>
          <button class="secondary-button auth-submit" type="button" @click="resendCode">Resend code</button>
        </template>

        <template v-else>
          <button class="auth-back" type="button" @click="screen='signin'">← Back to sign in</button>
          <div class="verify-icon"><Icon name="shield" /></div><span class="section-kicker">Account recovery</span><h2>Reset your password</h2><p>Enter your work email. We’ll create a secure frontend demo reset link.</p>
          <form @submit.prevent="sendReset"><label>Work email<input v-model.trim="resetEmail" type="email" placeholder="name@aria.com" /></label><p v-if="error" class="form-error" role="alert"><Icon name="alert" /> {{error}}</p><p v-if="resetSent" class="form-success"><Icon name="check" /> Reset instructions are ready for {{resetEmail}}.</p><button class="primary-button auth-submit" type="submit">Send reset instructions</button></form>
        </template>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, reactive, ref } from "vue"
import Icon from "./Icon.vue"

const emit = defineEmits(["authenticated", "toast"])
const screen = ref("signin")
const error = ref("")
const showPassword = ref(false)
const resetEmail = ref("")
const resetSent = ref(false)
const otp = reactive(["", "", "", "", "", ""])
const otpInputs = ref([])
const signin = reactive({ email: "", password: "", remember: true })
const signup = reactive({ firstName: "", lastName: "", employeeId: "", email: "", role: "employee", password: "", terms: false })

const storedAccounts = JSON.parse(localStorage.getItem("aria-demo-accounts") || "{}")
const accounts = {
  "admin@aria.com": { password: "Aria@2026", name: "Arjun Mehta", role: "admin", employeeId: "EMP1001" },
  "employee@aria.com": { password: "Aria@2026", name: "Neha Sharma", role: "employee", employeeId: "EMP1024" },
  ...storedAccounts,
}
const passwordChecks = computed(() => ({ length: signup.password.length >= 8, upper: /[A-Z]/.test(signup.password), number: /\d/.test(signup.password), symbol: /[^A-Za-z0-9]/.test(signup.password) }))
const passwordValid = computed(() => Object.values(passwordChecks.value).every(Boolean))

function useDemo(role) { const email = role === "admin" ? "admin@aria.com" : "employee@aria.com"; signin.email = email; signin.password = accounts[email].password; error.value = "" }
function signIn() { error.value = ""; const account = accounts[signin.email.toLowerCase()]; if (!account || account.password !== signin.password) { error.value = "Incorrect email or password. Try a demo account or create a new one."; return } emit("authenticated", { ...account, email: signin.email.toLowerCase(), remember: signin.remember }) }
function startSignup() { error.value = ""; screen.value = "signup" }
function requestVerification() { error.value = ""; if (!signup.firstName || !signup.lastName || !/^EMP\d{3,}$/i.test(signup.employeeId)) { error.value = "Enter your name and a valid employee ID such as EMP1024."; return } if (!/^\S+@\S+\.\S+$/.test(signup.email)) { error.value = "Enter a valid work email address."; return } if (!passwordValid.value) { error.value = "Your password must meet all four security rules."; return } if (!signup.terms) { error.value = "Accept the Terms of Service and Privacy Policy to continue."; return } screen.value = "verify" }
function focusNext(index) { otp[index] = otp[index].replace(/\D/g, ""); if (otp[index] && index < 5) otpInputs.value[index + 1]?.focus() }
function focusPrevious(index) { if (!otp[index] && index > 0) otpInputs.value[index - 1]?.focus() }
function verifyEmail() { error.value = ""; if (otp.join("") !== "247109") { error.value = "That code is incorrect. Use 247109 for this frontend demo."; return } const account={password:signup.password,name:`${signup.firstName} ${signup.lastName}`,email:signup.email.toLowerCase(),employeeId:signup.employeeId.toUpperCase(),role:signup.role,remember:true,newlyVerified:true};accounts[account.email]=account;localStorage.setItem("aria-demo-accounts",JSON.stringify({...storedAccounts,[account.email]:account}));emit("authenticated",account) }
function resendCode() { otp.splice(0, 6, "", "", "", "", "", ""); emit("toast", "A new verification code was generated: 247109") }
function sendReset() { error.value = ""; resetSent.value = false; if (!/^\S+@\S+\.\S+$/.test(resetEmail.value)) { error.value = "Enter a valid work email address."; return } resetSent.value = true }
</script>
