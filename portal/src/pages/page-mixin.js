import injector from 'vue-inject'

function pageReadyCallback(pageComponent, route) {
  return () => {
    pageComponent.$meta().refresh()
    pageComponent.isReady = true
    const $log = injector.get('$log')
    $log.pageView(route.fullPath)
  }
}

export default {
  data() {
    return {
      pageLoad: Promise.resolve(),
      isReady: false
    }
  },

  beforeRouteEnter(to, from, next) {
    // this method hooks into vue-router

    // Upon route enter we send a signal to analytics to keep track of (anonymous) app usage
    next(page => {
      // The analytics pageView signal will be send when two conditions are met:
      //    1)   Auto track has not been disabled
      //    2)   The page has loaded the data it needs or failed to do so
      // These conditions make sure that updates from XHR have propagated to the page.
      // In order to fulfill these conditions a property named pageLoad is exposed.
      // A page can set its property to a promise and this method acts when that resolves/rejects.
      if (!to.meta.noAutoTrack) {
        page.pageLoad.finally(pageReadyCallback(page, to))
      } else {
        page.isReady = true
      }
    })
  },

  beforeRouteUpdate(to, from, next) {
    if (!to.meta.noAutoTrack) {
      this.pageLoad.finally(pageReadyCallback(this, to))
    } else {
      this.isReady = true
    }
    next()
  }
}
