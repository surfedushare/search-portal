import Vue from 'vue'
import injector from 'vue-inject'

import router from './router.js'
import App from './App.vue'
import { setContext, getLocation } from './utils'
import { createStore } from './store.js'
import i18n, { loadLanguages } from './i18n'
import pluginRouting from './i18n/plugin.routing.js'

import SocialSharing from 'vue-social-sharing'
import VueClipboard from 'vue-clipboard2'
import VueMasonry from 'vue-masonry-css'
import InfiniteScroll from 'vue-infinite-scroll'

Vue.use(injector)
Vue.use(SocialSharing)
Vue.use(VueClipboard)
Vue.use(VueMasonry)
Vue.use(InfiniteScroll)

async function createApp(ssrContext) {
  const store = createStore()

  await loadLanguages()

  // Create Root instance
  // here we inject the store to all child components,
  // making it available everywhere as `this.$store`.
  const app = {
    store,
    i18n,
    ...App
  }

  store.app = app
  // Make app available from anywhere through injector
  injector.constant('App', app)

  const next = location => router.push(location)

  // Resolve route
  const path = getLocation(router.options.base)
  const route = router.resolve(path).route

  // Set context to app.context
  await setContext(app, {
    route,
    next,
    error: null,
    store,
    payload: ssrContext ? ssrContext.payload : undefined,
    req: ssrContext ? ssrContext.req : undefined,
    res: ssrContext ? ssrContext.res : undefined,
    beforeRenderFns: ssrContext ? ssrContext.beforeRenderFns : undefined
  })

  pluginRouting(app.context)

  if (store.getters.api_token) {
    store.dispatch('authenticate', { token: store.getters.api_token })
  } else {
    store.dispatch('getUser')
  }

  return {
    app,
    store
  }
}

export { createApp }
