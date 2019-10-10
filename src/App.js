import Vue from 'vue'
import NuxtLoading from './components/nuxt-loading.vue'

import '../assets/styles/normalize.css'

import '../assets/styles/variables.less'

import '../assets/styles/common.less'

import '../assets/styles/forms.less'


import _6f6c098b from '../layouts/default.vue'

const layouts = { "_default": _6f6c098b };



export default {
  render(h, props) {
    const loadingEl = h('nuxt-loading', { ref: 'loading' });
    const layoutEl = h(this.layout || 'nuxt');
    const templateEl = h('div', {
      domProps: {
        id: '__layout'
      },
      key: this.layoutName
    }, [ layoutEl ]);

    const transitionEl = h('transition', {
      props: {
        name: 'layout',
        mode: 'out-in'
      }
    }, [ templateEl ]);

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
    layoutName: '',
    loginEnabled: false
  }),
  beforeCreate () {
    Vue.util.defineReactive(this, 'nuxt', this.$options.nuxt);
  },
  created () {
    // Add this.$nuxt in child instances
    Vue.prototype.$nuxt = this;
    // add to window so we can listen when ready
    if (typeof window !== 'undefined') {
      window.$nuxt = this
    }
    // Add $nuxt.error()
    this.error = this.nuxt.error
  },

  mounted () {
    this.$loading = this.$refs.loading;

    let self = this;
    function keyUp(event) {
      if (event.keyCode === 73 && event.ctrlKey) {
        self.loginEnabled = !self.loginEnabled;
      }
    }
    window.document.onkeyup = keyUp;
  },
  watch: {
    'nuxt.err': 'errorChanged'
  },

  methods: {

    errorChanged () {
      if (this.nuxt.err && this.$loading) {
        if (this.$loading.fail) this.$loading.fail();
        if (this.$loading.finish) this.$loading.finish()
      }
    },


    setLayout(layout) {
      if (!layout || !layouts['_' + layout]) {
        layout = 'default'
      }
      this.layoutName = layout;
      this.layout = layouts['_' + layout];
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
