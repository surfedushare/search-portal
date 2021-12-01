import Vue from 'vue'
import injector from 'vue-inject'

const $window = injector.get('$window')

export default {

  data() {
    return {
      pageLoad: Promise.resolve(),
      isReady: false
    }
  },

  beforeRouteEnter(to, from, next) {  // this method hooks into vue-router

    // Upon route enter we send a signal to analytics to keep track of (anonymous) app usage
    next((page) => {

      // The analytics pageView signal will be send when two conditions are met:
      //    1)   Auto track has not been disabled
      //    2)   The page has loaded the data it needs or failed to do so
      // These conditions make sure that updates from XHR have propagated to the page.
      // In order to fulfill these conditions a property named pageLoad is exposed.
      // A page can set its property to a promise and this method acts when that resolves/rejects.
      if(!to.meta.noAutoTrack) {
        console.log(page)
        page.pageLoad.finally(() => {
          page.$meta().refresh()
          page.isReady = true
          const $log = injector.get('$log')
          $log.pageView(to.path)
        })
      } else {
        page.isReady = true
      }
    })
  }
}
