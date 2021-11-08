import * as Sentry from '@sentry/browser'
import injector from 'vue-inject'

if (process.env.VUE_APP_USE_SENTRY) {
  Sentry.init({
    dsn: `${window.location.protocol}//21fab3e788584cbe999f20ea1bb7e2df@${window.location.host}/sentry/2964956`,
    beforeSend(event) {
      if (window.location.host !== 'edusources.nl') {
        return event
      }
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

injector.decorator('$log', function($log) {
  /***************************
   * CUSTOM METHODS
   ***************************/

  $log.pageView = function(page) {
    $log.info('Visiting: ' + page)
  }

  $log.customEvent = function(category, action, label, value, dimensions) {
    if (!label && !value) {
      $log.info('Trigger: ' + category + ' => ' + action)
    } else if (label) {
      $log.info('Trigger: ' + category + ' (' + label + ') => ' + action)
    } else if (value) {
      $log.info('Trigger: ' + category + ' (' + value + ') => ' + action)
    }
    if (dimensions) {
      $log.info('Custom dimensions:', dimensions)
    }
  }
  $log.setIsStaff = function(value) {
    $log.info('Set is_staff: ', value)
  }

  /***************************
   * PRODUCTION
   ***************************/

  // In non-production we do nothing special after adding custom methods
  if (!window.MATOMO_ID) {
    return $log
  }

  /***************************
   * MATOMO
   ***************************/

  $log._pageView = $log.pageView
  $log._customEvent = $log.customEvent
  $log._setIsStaff = $log.setIsStaff

  $log.pageView = function(page) {
    window._paq.push(['trackPageView'])
    $log._pageView(page)
  }

  $log.customEvent = function(category, action, label, value, dimensions) {
    $log._customEvent(category, action, label, value, dimensions)
    window._paq.push(['trackEvent', category, action, label, value, dimensions]) // NB: this modifies dimensions!
  }

  $log.setIsStaff = function(value) {
    if (value) {
      window._paq.push(['setCustomDimension', 1, value])
    } else {
      window._paq.push(['deleteCustomDimension', 1])
    }
    $log._setIsStaff(value)
  }

  /***************************
   * SENTRY
   ***************************/

  $log._warn = $log.warn
  $log._error = $log.error

  $log.warn = function(message, context) {
    if (context) {
      $log._warn(message, context)
      Sentry.captureEvent({
        message: message,
        level: 'warning',
        extra: context
      })
    } else {
      $log._warn(message)
      Sentry.captureEvent({
        message: message,
        level: 'warning'
      })
    }
  }

  $log.error = function(message, context) {
    if (context) {
      $log._error(message, context)
      Sentry.captureEvent({
        message: message,
        level: 'error',
        extra: context
      })
    } else {
      $log._error(message)
      Sentry.captureEvent({
        message: message,
        level: 'error'
      })
    }
  }

  return $log
})
