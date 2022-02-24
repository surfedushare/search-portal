import './logging.js'
import Vue from 'vue'
import injector from 'vue-inject'
import i18n, { loadLanguages } from './i18n'
import Vuetify from 'vuetify'
import 'vuetify/dist/vuetify.min.css'
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
Vue.use(Vuetify)

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
    vuetify: new Vuetify({
      theme: {
        themes: {
          light: {
            anchor: '#2CA055',
          },
        },
      }
    }),
    ...App,
  }).$mount('#app')
}

mountApp().catch((err) => $log.error('Error while initializing app', err))
