import Vue from 'vue'
import NuxtLoading from './components/nuxt-loading.vue'

import '../assets/styles/normalize.css'

import '../assets/styles/variables.less'

import '../assets/styles/common.less'

import '../assets/styles/forms.less'


import _6f6c098b from '../layouts/default.vue'

const layouts = { "_default": _6f6c098b }



export default {
  head: {"title":"Surf | Open Leermaterialen","meta":[{"charset":"utf-8"},{"name":"viewport","content":"width=device-width, initial-scale=1"},{"name":"twitter:card","content":"summary_large_image"},{"hid":"description","name":"description","content":"Open Leermaterialen"},{"hid":"og:title","property":"og:title","content":"Surf | Open Leermaterialen"},{"hid":"og:description","property":"og:description","content":"Open Leermaterialen"},{"hid":"og:image","property":"og:image","content":"https:\u002F\u002Ffront-dev.surfcatalog.nl\u002F\u002Fsocial-image.jpg"},{"hid":"og:image:width","property":"og:image:width","content":"510"},{"hid":"og:image:height","property":"og:image:height","content":"298"},{"hid":"og:image:alt","property":"og:image:alt","content":"Open Leermaterialen"},{"hid":"og:type","property":"og:type","content":"article"}],"link":[{"rel":"icon","type":"image\u002Fx-icon","href":"\u002Ffavicon.ico"},{"rel":"icon","type":"image\u002Fpng","href":"\u002Ffavicon-16x16.png","sizes":"16x16"},{"rel":"icon","type":"image\u002Fpng","href":"\u002Ffavicon-32x32.png","sizes":"32x32"},{"rel":"icon","type":"image\u002Fpng","href":"\u002Ffavicon-70x70.png","sizes":"70x70"},{"rel":"stylesheet","href":"https:\u002F\u002Fuse.typekit.net\u002Feya4qgt.css"}],"style":[],"script":[{"src":"\u002F\u002Fwebstats.surf.nl\u002Fpiwik.js","body":true,"defer":true,"async":true}]},
  render(h, props) {
    const loadingEl = h('nuxt-loading', { ref: 'loading' })
    const layoutEl = h(this.layout || 'nuxt')
    const templateEl = h('div', {
      domProps: {
        id: '__layout'
      },
      key: this.layoutName
    }, [ layoutEl ])

    const transitionEl = h('transition', {
      props: {
        name: 'layout',
        mode: 'out-in'
      }
    }, [ templateEl ])

    return h('div',{
      domProps: {
        id: '__nuxt'
      }
    }, [
      loadingEl,
      transitionEl
    ])
  },
  data: () => ({
    layout: null,
    layoutName: ''
  }),
  beforeCreate () {
    Vue.util.defineReactive(this, 'nuxt', this.$options.nuxt)
  },
  created () {
    // Add this.$nuxt in child instances
    Vue.prototype.$nuxt = this
    // add to window so we can listen when ready
    if (typeof window !== 'undefined') {
      window.$nuxt = this
    }
    // Add $nuxt.error()
    this.error = this.nuxt.error
  },

  mounted () {
    this.$loading = this.$refs.loading
  },
  watch: {
    'nuxt.err': 'errorChanged'
  },

  methods: {

    errorChanged () {
      if (this.nuxt.err && this.$loading) {
        if (this.$loading.fail) this.$loading.fail()
        if (this.$loading.finish) this.$loading.finish()
      }
    },


    setLayout(layout) {
      if (!layout || !layouts['_' + layout]) {
        layout = 'default'
      }
      this.layoutName = layout
      this.layout = layouts['_' + layout]
      return this.layout
    },
    loadLayout(layout) {
      if (!layout || !layouts['_' + layout]) {
        layout = 'default'
      }
      return Promise.resolve(layouts['_' + layout])
    }

  },
  components: {
    NuxtLoading
  }
}
