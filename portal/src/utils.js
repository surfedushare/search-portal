import Vue from 'vue'

export const PublishStatus = {
  // NB: this enum has a hard copy in the API
  DRAFT: 0,
  REVIEW: 1,
  PUBLISHED: 2
}

export function sanitizeComponent(Component) {
  // If Component already sanitized
  if (Component.options && Component._Ctor === Component) {
    return Component
  }
  if (!Component.options) {
    Component = Vue.extend(Component) // fix issue #6
    Component._Ctor = Component
  } else {
    Component._Ctor = Component
    Component.extendOptions = Component.options
  }
  // For debugging purpose
  if (!Component.options.name && Component.options.__file) {
    Component.options.name = Component.options.__file
  }
  return Component
}

export function getMatchedComponents(route, matches = false) {
  return Array.prototype.concat.apply(
    [],
    route.matched.map((m, index) => {
      return Object.keys(m.components).map(key => {
        matches && matches.push(index)
        return m.components[key]
      })
    })
  )
}

export function flatMapComponents(route, fn) {
  return Array.prototype.concat.apply(
    [],
    route.matched.map((m, index) => {
      return Object.keys(m.components).reduce((promises, key) => {
        if (m.components[key]) {
          promises.push(fn(m.components[key], m.instances[key], m, key, index))
        } else {
          delete m.components[key]
        }
        return promises
      }, [])
    })
  )
}

export function resolveRouteComponents(route) {
  return Promise.all(
    flatMapComponents(route, async (Component, _, match, key) => {
      // If component is a function, resolve it
      if (typeof Component === 'function' && !Component.options) {
        Component = await Component()
      }
      return (match.components[key] = sanitizeComponent(Component))
    })
  )
}

export async function getRouteData(route) {
  // Make sure the components are resolved (code-splitting)
  await resolveRouteComponents(route)
  // Send back a copy of route with meta based on Component definition
  return {
    ...route,
    meta: getMatchedComponents(route).map(Component => {
      return Component.options.meta || {}
    })
  }
}

export async function setContext(app, context) {
  // If context not defined, create it
  if (!app.context) {
    app.context = {
      isStatic: process.static,
      isDev: false,
      isHMR: false,
      app,
      store: app.store,
      payload: context.payload,
      error: context.error,
      base: '/',
      env: {
        frontendUrl: process.env.VUE_APP_FRONTEND_URL
      }
    }
    // Only set once
    if (context.req) app.context.req = context.req
    if (context.res) app.context.res = context.res
    app.context.redirect = (status, path, query) => {
      if (!status) {
        return
      }
      // Used in middleware
      app.context._redirected = true
      // if only 1 or 2 arguments: redirect('/') or redirect('/', { foo: 'bar' })
      let pathType = typeof path
      if (
        typeof status !== 'number' &&
        (pathType === 'undefined' || pathType === 'object')
      ) {
        query = path || {}
        path = status
        pathType = typeof path
        status = 302
      }
      if (pathType === 'object') {
        path = app.router.resolve(path).href
      }
      // "/absolute/route", "./relative/route" or "../relative/route"
      if (/(^[.]{1,2}\/)|(^\/(?!\/))/.test(path)) {
        app.context.next({
          path: path,
          query: query,
          status: status
        })
      } else {
        path = formatUrl(path, query)
        if (process.server) {
          app.context.next({
            path: path,
            status: status
          })
        }
        if (process.client) {
          // https://developer.mozilla.org/en-US/docs/Web/API/Location/replace
          window.location.replace(path)

          // Throw a redirect error
          throw new Error('ERR_REDIRECT')
        }
      }
    }
    // if (process.server) app.context.beforeNuxtRender = fn => context.beforeRenderFns.push(fn)
    // if (process.client) app.context.nuxtState = window.__NUXT__
  }
  // Dynamic keys
  app.context.next = context.next
  app.context._redirected = false
  app.context._errored = false
  app.context.isHMR = !!context.isHMR
  if (context.route) {
    app.context.route = await getRouteData(context.route)
  }
  app.context.params = app.context.route.params || {}
  app.context.query = app.context.route.query || {}
  if (context.from) {
    app.context.from = await getRouteData(context.from)
  }
}

// Imported from vue-router
export function getLocation(base, mode) {
  var path = window.location.pathname
  if (mode === 'hash') {
    return window.location.hash.replace(/^#\//, '')
  }
  if (base && path.indexOf(base) === 0) {
    path = path.slice(base.length)
  }
  return (path || '/') + window.location.search + window.location.hash
}

/**
 * Format given url, append query to url query string
 *
 * @param  {string} url
 * @param  {string} query
 * @return {string}
 */
function formatUrl(url, query) {
  let protocol
  let index = url.indexOf('://')
  if (index !== -1) {
    protocol = url.substring(0, index)
    url = url.substring(index + 3)
  } else if (url.indexOf('//') === 0) {
    url = url.substring(2)
  }

  let parts = url.split('/')
  let result = (protocol ? protocol + '://' : '//') + parts.shift()

  let path = parts.filter(Boolean).join('/')
  let hash
  parts = path.split('#')
  if (parts.length === 2) {
    path = parts[0]
    hash = parts[1]
  }

  result += path ? '/' + path : ''

  if (query && JSON.stringify(query) !== '{}') {
    result += (url.split('?').length === 2 ? '&' : '?') + formatQuery(query)
  }
  result += hash ? '#' + hash : ''

  return result
}

/**
 * Transform data object to query string
 *
 * @param  {object} query
 * @return {string}
 */
function formatQuery(query) {
  return Object.keys(query)
    .sort()
    .map(key => {
      var val = query[key]
      if (val == null) {
        return ''
      }
      if (Array.isArray(val)) {
        return val
          .slice()
          .map(val2 => [key, '=', val2].join(''))
          .join('&')
      }
      return key + '=' + val
    })
    .filter(Boolean)
    .join('&')
}
