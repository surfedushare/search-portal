import * as Sentry from '@sentry/browser'
import * as Integrations from '@sentry/integrations'

if (process.env.VUE_APP_USE_SENTRY) {
  Sentry.init({
    dsn: 'https://21fab3e788584cbe999f20ea1bb7e2df@sentry.io/2964956',
    integrations: [new Integrations.CaptureConsole()],
    beforeSend(event) {
      if (event.user) {
        delete event.user
      }
      if (
        event.request &&
        event.request.headers &&
        event.request.headers['User-Agent']
      ) {
        delete event.request.headers['User-Agent']
      }
      return event
    }
  })
}

import Vue from 'vue'
import injector from 'vue-inject'
import i18n, { loadLanguages } from './i18n'
import '@fortawesome/fontawesome-free/css/all.css'
import router from '~/router'
import store from '~/store/index'
import App from './App.vue'
import SocialSharing from 'vue-social-sharing'
import VueClipboard from 'vue-clipboard2'
import VueMasonry from 'vue-masonry-css'
import InfiniteScroll from 'vue-infinite-scroll'
import VueCroppie from 'vue-croppie'
import './i18n/plugin.routing.js'
import 'croppie/croppie.css'

Vue.use(injector)
Vue.use(SocialSharing)
Vue.use(VueClipboard)
Vue.use(VueMasonry)
Vue.use(InfiniteScroll)
Vue.use(VueCroppie)

const $log = injector.get('$log')

async function authenticate() {
  if (store.getters.api_token) {
    return store.dispatch('authenticate', { token: store.getters.api_token })
  }

  return store.dispatch('getUser')
}

async function mountApp() {
  await loadLanguages()

  await authenticate()

  new Vue({
    router,
    store,
    i18n,
    ...App
  }).$mount('#app')
}

mountApp().catch(err => $log.error('Error while initializing app', err))
