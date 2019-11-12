<template>
  <div>
    <div class="main_block">
      <MainHeader />
      <nuxt/>
      <MainFooter />
    </div>
    <nuxt-loading ref="loading"></nuxt-loading>
  </div>
</template>

<style lang="less">
  @import 'styles/normalize.css';

  @import '../assets/styles/variables.less';

  @import 'styles/common.less';

  @import 'styles/forms.less';
</style>

<script>

import Vue from 'vue'

import MainHeader from './../components/MainHeader';
import MainFooter from './../components/MainFooter';
import NuxtLoading from './components/nuxt-loading.vue'

//import _6f6c098b from '../layouts/default.vue'
//const layouts = { "_default": _6f6c098b };


export default {
  components: {
    MainHeader,
    MainFooter,
    NuxtLoading
  },
  // mounted() {
  //
  // },
  // render(h, props) {
  //   const loadingEl = h('nuxt-loading', { ref: 'loading' });
  //   const layoutEl = h(this.layout || 'nuxt');
  //   const templateEl = h('div', {
  //     domProps: {
  //       id: '__layout'
  //     },
  //     key: this.layoutName
  //   }, [ layoutEl ]);
  //
  //   const transitionEl = h('transition', {
  //     props: {
  //       name: 'layout',
  //       mode: 'out-in'
  //     }
  //   }, [ templateEl ]);
  //
  //   return h('div',{
  //     domProps: {
  //       id: '__nuxt'
  //     }
  //   }, [
  //     loadingEl,
  //     transitionEl
  //   ])
  // },
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
    this.$store.dispatch('getFilterCategories');
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

    this.$store.dispatch('getThemes');
  },

  methods: {

    setLayout() {  // previously received a layout
      return 'default';
      // if (!layout || !layouts['_' + layout]) {
      //   layout = 'default'
      // }
      // this.layoutName = layout;
      // this.layout = layouts['_' + layout];
      // return this.layout
    }
    // loadLayout(layout) {
    //   if (!layout || !layouts['_' + layout]) {
    //     layout = 'default'
    //   }
    //   return Promise.resolve(layouts['_' + layout])
    // }

  }
}
</script>
