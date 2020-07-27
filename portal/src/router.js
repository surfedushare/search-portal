import Vue from 'vue'
import Router from 'vue-router'
import injector from 'vue-inject'

import Home from '~/pages/index'
import Search from '~/pages/search'
import HowDoesItWork from '~/pages/how-does-it-work'
import Communities from '~/pages/communities'
import MyCollections from '~/pages/my/collections'
import MyCommunity from '~/pages/my/community'
import MyPrivacy from '~/pages/my/privacy'
import Theme from '~/pages/theme'
import Material from '~/pages/material'
import Collection from '~/pages/collection'
import Community from '~/pages/community'
import InfoPage from '~/pages/info'
import { isEqual } from 'lodash'
import axios from '~/axios'
import store from '~/store'
import { localePath } from '~/i18n/plugin.routing'

const $log = injector.get('$log')

Vue.use(Router)

const scrollBehavior = function(to, from, savedPosition) {
  if (savedPosition) {
    return savedPosition
  }

  // Do not scroll to the top when only GET parameters change
  if (from && to.name === from.name && isEqual(to.params, from.params)) {
    return
  }

  return { x: 0, y: 0 }
}

export default new Router({
  mode: 'history',
  base: '/',
  linkActiveClass: 'router-link-active',
  linkExactActiveClass: 'router-link-exact-active',
  scrollBehavior,
  routes: [
    {
      path: '/en/how-does-it-work',
      component: HowDoesItWork,
      name: 'how-does-it-work___en'
    },
    {
      path: '/hoe-werkt-het',
      component: HowDoesItWork,
      name: 'how-does-it-work___nl'
    },
    {
      path: '/en/communities',
      component: Communities,
      name: 'communities___en'
    },
    {
      path: '/communities',
      component: Communities,
      name: 'communities___nl'
    },
    {
      path: '/en/materials/search',
      component: Search,
      name: 'materials-search___en'
    },
    {
      path: '/materialen/zoeken',
      component: Search,
      name: 'materials-search___nl'
    },
    {
      path: '/en/my/collections',
      component: MyCollections,
      name: 'my-collections___en'
    },
    {
      path: '/mijn/collecties',
      component: MyCollections,
      name: 'my-collections___nl'
    },
    {
      path: '/en/my/collection/:id',
      component: Collection,
      name: 'my-collection___en',
      meta: {
        editable: true
      }
    },
    {
      path: '/mijn/collectie/:id',
      component: Collection,
      name: 'my-collection___nl',
      meta: {
        editable: true
      }
    },
    {
      path: '/en/my/communities',
      component: Communities,
      name: 'my-communities___en'
    },
    {
      path: '/mijn/communities',
      component: Communities,
      name: 'my-communities___nl'
    },
    {
      path: '/en/my/community/:community',
      component: MyCommunity,
      name: 'my-community___en'
    },
    {
      path: '/mijn/community/:community',
      component: MyCommunity,
      name: 'my-community___nl'
    },
    {
      path: '/en/my/privacy',
      component: MyPrivacy,
      name: 'my-privacy___en'
    },
    {
      path: '/mijn/privacy',
      component: MyPrivacy,
      name: 'my-privacy___nl'
    },
    {
      path: '/en/themes/:id',
      component: Theme,
      name: 'themes-id___en'
    },
    {
      path: '/themas/:id',
      component: Theme,
      name: 'themes-id___nl'
    },
    {
      path: '/en/materials/:id',
      component: Material,
      name: 'materials-id___en'
    },
    {
      path: '/materialen/:id',
      component: Material,
      name: 'materials-id___nl'
    },
    {
      path: '/en/collections/:id?',
      component: Collection,
      name: 'collections-id___en',
      meta: {
        editable: false
      }
    },
    {
      path: '/collecties/:id?',
      component: Collection,
      name: 'collections-id___nl',
      meta: {
        editable: false
      }
    },
    {
      path: '/en/communities/:community',
      component: Community,
      name: 'communities-community___en'
    },
    {
      path: '/communities/:community',
      component: Community,
      name: 'communities-community___nl'
    },
    {
      path: '/en/privacy',
      component: InfoPage,
      name: 'privacy___en',
      meta: {
        title_translation_key: 'title-privacy-info',
        html_translation_key: 'html-privacy-info'
      }
    },
    {
      path: '/privacy',
      component: InfoPage,
      name: 'privacy___nl',
      meta: {
        title_translation_key: 'title-privacy-info',
        html_translation_key: 'html-privacy-info'
      }
    },
    {
      path: '/en/copyright',
      component: InfoPage,
      name: 'copyright___en',
      meta: {
        title_translation_key: 'title-copyright-info',
        html_translation_key: 'html-copyright-info'
      }
    },
    {
      path: '/copyright',
      component: InfoPage,
      name: 'copyright___nl',
      meta: {
        title_translation_key: 'title-copyright-info',
        html_translation_key: 'html-copyright-info'
      }
    },
    {
      path: '/en/cookies',
      component: InfoPage,
      name: 'cookies___en',
      meta: {
        title_translation_key: 'title-cookies-info',
        html_translation_key: 'html-cookies-info'
      }
    },
    {
      path: '/cookies',
      component: InfoPage,
      name: 'cookies___nl',
      meta: {
        title_translation_key: 'title-cookies-info',
        html_translation_key: 'html-cookies-info'
      }
    },
    {
      path: '/en/disclaimer',
      component: InfoPage,
      name: 'disclaimer___en',
      meta: {
        title_translation_key: 'title-disclaimer-info',
        html_translation_key: 'html-disclaimer-info'
      }
    },
    {
      path: '/disclaimer',
      component: InfoPage,
      name: 'disclaimer___nl',
      meta: {
        title_translation_key: 'title-disclaimer-info',
        html_translation_key: 'html-disclaimer-info'
      }
    },
    {
      path: '/en/',
      component: Home,
      name: 'index___en'
    },
    {
      path: '/',
      component: Home,
      name: 'index___nl'
    },
    {
      path: '/login/permissions',
      beforeEnter(to, from, next) {
        let authFlowToken = to.query.partial_token || null
        store.commit('AUTH_FLOW_TOKEN', authFlowToken)
        next({
          path: localePath('my-privacy'),
          query: { popup: 1 }
        })
      }
    },
    {
      path: '/login/success',
      beforeEnter(to, from, next) {
        axios
          .get('users/obtain-token/')
          .then(response => {
            let token = response.token || response.data.token
            store
              .dispatch('authenticate', { token: token })
              .then(() => {
                next(to.query.continue || '/')
              })
              .catch(error => {
                $log.warn(
                  'Unable to login due to error during store "login" dispatch'
                )
                $log.error(error)
                next('/')
              })
          })
          .catch(error => {
            $log.warn('Unable to login due to error during obtaining a token')
            $log.error(error)
            next('/')
          })
      }
    }
  ],
  fallback: false
})
