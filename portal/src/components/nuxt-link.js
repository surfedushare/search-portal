/**
 * This file is part of the NuxtJS framework. We should replace all uses of nuxt-link with router-link.
 * After that we can remove this file
 */

export default {
  name: 'nuxt-link',
  functional: true,
  render (h, { data, children }) {
    return h('router-link', data, children)
  }
}
