import { createResource } from 'frappe-ui'

export const authResource = createResource({
  url: 'frappe.auth.get_logged_user',
})

export const userProfileResource = createResource({
  url: 'frappe.client.get',
  makeParams() {
    authResource.fetch()
    if (!authResource.data) return null
    return {
      doctype: 'User',
      name: authResource.data,
      fields: ['name', 'full_name', 'image'],
    }
  },
  auto: true,
  transform(user) {
    if (!user?.image) {
      user.image = '/assets/frappe/images/default-avatar.png'
    }
    return user
  },
})
