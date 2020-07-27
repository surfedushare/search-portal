import Vue from 'vue'
import i18n from '~/i18n/index'

const routesNameSeparator = '___'

export function localePath(route, overridenLocale) {
  if (!route) return
  const locale = overridenLocale || i18n.locale
  if (!locale) return

  // If route parameters is a string, use it as the route's name
  if (typeof route === 'string') {
    route = { name: route }
  }

  const localizedName = route.name + routesNameSeparator + locale

  return { ...route, name: localizedName }
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
    localePath: localePath,
    switchLocalePath: switchLocalePathFactory(),
    getRouteBaseName: getRouteBaseNameFactory(),
    titleTranslation: titleTranslation
  }
})
