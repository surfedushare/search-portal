import '@fortawesome/fontawesome-free/css/all.css'
import 'croppie/croppie.css'
import './i18n/plugin.routing.js'
import './logging.js'

import i18n, { loadLanguages } from './i18n'

import App from './App.vue'
import InfiniteScroll from 'vue-infinite-scroll'
import SocialSharing from 'vue-social-sharing'
import Vue from 'vue'
import VueClipboard from 'vue-clipboard2'
import VueCroppie from 'vue-croppie'
import VueMasonry from 'vue-masonry-css'
import injector from 'vue-inject'
import router from '~/router'
import store from '~/store/index'

Vue.use(injector)
Vue.use(SocialSharing)
Vue.use(VueClipboard)
Vue.use(VueMasonry)
Vue.use(InfiniteScroll)
Vue.use(VueCroppie)

const $log = injector.get('$log')

async function authenticate() {
  if (store.getters.api_token) {
    try {
      return await store.dispatch('authenticate', {
        token: store.getters.api_token,
      })
    } catch {
      return store.dispatch('getUser')
    }
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
    ...App,
  }).$mount('#app')
}

mountApp().catch((err) => $log.error('Error while initializing app', err))
