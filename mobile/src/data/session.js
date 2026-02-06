import { computed, reactive, ref } from 'vue'
import { createResource } from 'frappe-ui'

export const sessionResource = createResource({
  url: 'projectit.api.get_current_projectit_user',
  auto: true,
})

export const session = reactive({
  user: computed(() => sessionResource.data),
  isLoggedIn: computed(() => !!sessionResource.data),

  login: {
    submit() {
      const redirect = encodeURIComponent(
        window.location.pathname + window.location.search
      )
      window.location.href = `/login?redirect-to=${redirect}`
    },
  },

  logout: createResource({
    url: 'logout',
    onSuccess() {
      window.location.href = `/login?redirect-to=/projectit`
    },
  }),

})

export const showAuthenticationError = ref(false)


/*import router from '@/router'
import { computed, reactive, ref } from 'vue'
import { createResource } from 'frappe-ui'

import { userResource } from './user'

export const sessionUserResource = createResource({
  url: 'frappe.auth.get_logged_user',
  auto: true, // вызывается сразу при инициализации
  transform(user) {
    return user === 'Guest' ? null : user
  },
})

export const session = reactive({
  login: createResource({
    url: 'login',
    makeParams({ email, password }) {
      return {
        usr: email,
        pwd: password,
      }
    },
    async onSuccess(data) {
      await sessionUserResource.reload()
      await userResource.reload()

      session.user = sessionUserResource.data

      session.login.reset()
      router.replace(data.default_route || '/home')
    },
    onError(error) {
      if (error.exc_type === 'AuthenticationError') {
        showAuthenticationError.value = true
      }
    },
  }),

  logout: createResource({
    url: 'logout',
    async onSuccess() {
      userResource.reset()
      await sessionUserResource.reload()

      session.user = null
      router.replace({ name: 'Login' })
    },
  }),

  user: null,

  isLoggedIn: computed(() => !!session.user),
})

export async function initSession() {
  await sessionUserResource.reload()
  session.user = sessionUserResource.data
}

export const showAuthenticationError = ref(false)
*/