import Vue from 'vue'
import i18n from '~/i18n/index'
import router from '~/router'

const routesNameSeparator = '___'

function localePathFactory() {
  const STRATEGIES = {
    PREFIX: 'prefix',
    PREFIX_EXCEPT_DEFAULT: 'prefix_except_default',
    PREFIX_AND_DEFAULT: 'prefix_and_default'
  }
  const STRATEGY = 'prefix_except_default'
  const defaultLocale = 'nl'
  const defaultLocaleRouteNameSuffix = 'default'

  return function localePath(route, locale) {
    // Abort if no route or no locale
    if (!route) return
    locale = locale || i18n.locale
    if (!locale) return

    // If route parameters is a string, use it as the route's name
    if (typeof route === 'string') {
      route = { name: route }
    }

    // Build localized route options
    let name = route.name + routesNameSeparator + locale

    // Match route without prefix for default locale
    if (
      locale === defaultLocale &&
      STRATEGY === STRATEGIES.PREFIX_AND_DEFAULT
    ) {
      name += routesNameSeparator + defaultLocaleRouteNameSuffix
    }

    const localizedRoute = Object.assign({}, route, { name })

    // Resolve localized route
    const resolved = router.resolve(localizedRoute)
    let { href } = resolved

    // Remove baseUrl from href (will be added back by nuxt-link)
    if (router.options.base) {
      const regexp = new RegExp(router.options.base)
      href = href.replace(regexp, '/')
    }

    return href
  }
}

function switchLocalePathFactory() {
  return function switchLocalePath(locale) {
    const name = this.getRouteBaseName()
    if (!name) {
      return ''
    }

    const { params, ...routeCopy } = this.$route
    const baseRoute = Object.assign({}, routeCopy, {
      name,
      params: { ...params, '0': params.pathMatch }
    })
    return this.localePath(baseRoute, locale)
  }
}

function getRouteBaseNameFactory(contextRoute) {
  const routeGetter = contextRoute
    ? route => route || contextRoute
    : function(route) {
        return route || this.$route
      }

  return function getRouteBaseName(route) {
    route = routeGetter.call(this, route)
    if (!route.name) {
      return null
    }
    return route.name.split(routesNameSeparator)[0]
  }
}

function titleTranslation(item) {
  if (item.title_translations) {
    return item.title_translations[i18n.locale]
  }

  return item.name
}

Vue.mixin({
  methods: {
    localePath: localePathFactory(),
    switchLocalePath: switchLocalePathFactory(),
    getRouteBaseName: getRouteBaseNameFactory(),
    titleTranslation: titleTranslation
  }
})

export const localePath = localePathFactory()
