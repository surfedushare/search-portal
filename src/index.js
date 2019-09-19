import Vue from 'vue'
import { createRouter } from './router.js'
import NuxtChild from './components/nuxt-child.js'
import NuxtLink from './components/nuxt-link.js'
import NuxtError from '../layouts/error.vue'
import Nuxt from './components/nuxt.js'
import App from './App.js'
import { setContext, getLocation, getRouteData } from './utils'
import { createStore } from './store.js'

/* Plugins */
import nuxt_plugin_pluginseo_26e4ed71 from './nuxt-i18n/plugin.seo.js'
import nuxt_plugin_pluginrouting_3c9d9e30 from './nuxt-i18n/plugin.routing.js'
import nuxt_plugin_pluginmain_7147a387 from './nuxt-i18n/plugin.main.js'
import nuxt_plugin_axios_494a31c4 from './axios.js'
import nuxt_plugin_auth_6a7e4e1e from './plugins/auth'
import nuxt_plugin_vSelect_475ab648 from './plugins/vSelect'
import nuxt_plugin_infiniteScroll_049132f7 from './plugins/infiniteScroll'
import nuxt_plugin_axios_3566aa80 from './plugins/axios'
import nuxt_plugin_SocialSharing_3ab090d9 from './plugins/SocialSharing'
import nuxt_plugin_VueMasonry_21187416 from './plugins/VueMasonry'
import nuxt_plugin_VueClipboard_7da67946 from './plugins/VueClipboard'
import nuxt_plugin_veeValidate_1cb8e4d4 from './plugins/veeValidate'


// Component: <nuxt-child>
Vue.component(NuxtChild.name, NuxtChild);

// Component: <nuxt-link>
Vue.component(NuxtLink.name, NuxtLink);

// Component: <nuxt>`
Vue.component(Nuxt.name, Nuxt);

const defaultTransition = {"name":"page","mode":"out-in","appear":true,"appearClass":"appear","appearActiveClass":"appear-active","appearToClass":"appear-to"}

async function createApp (ssrContext) {
  const router = await createRouter(ssrContext);


  const store = createStore(ssrContext);
  // Add this.$router into store actions/mutations
  store.$router = router;



  // Create Root instance
  // here we inject the router and store to all child components,
  // making them available everywhere as `this.$router` and `this.$store`.
  const app = {
    router,
    store,
    nuxt: {
      defaultTransition,
      transitions: [ defaultTransition ],
      setTransitions (transitions) {
        if (!Array.isArray(transitions)) {
          transitions = [ transitions ]
        }
        transitions = transitions.map((transition) => {
          if (!transition) {
            transition = defaultTransition
          } else if (typeof transition === 'string') {
            transition = Object.assign({}, defaultTransition, { name: transition })
          } else {
            transition = Object.assign({}, defaultTransition, transition)
          }
          return transition
        });
        this.$options.nuxt.transitions = transitions;
        return transitions
      },
      err: null,
      dateErr: null,
      error (err) {
        err = err || null;
        app.context._errored = !!err;
        if (typeof err === 'string') err = { statusCode: 500, message: err };
        const nuxt = this.nuxt || this.$options.nuxt;
        nuxt.dateErr = Date.now();
        nuxt.err = err;
        // Used in lib/server.js
        if (ssrContext) ssrContext.nuxt.error = err;
        return err
      }
    },
    ...App
  };

  // Make app available into store via this.app
  store.app = app;

  const next = ssrContext ? ssrContext.next : location => app.router.push(location);
  // Resolve route
  let route;
  if (ssrContext) {
    route = router.resolve(ssrContext.url).route
  } else {
    const path = getLocation(router.options.base);
    route = router.resolve(path).route
  }

  // Set context to app.context
  await setContext(app, {
    route,
    next,
    error: app.nuxt.error.bind(app),
    store,
    payload: ssrContext ? ssrContext.payload : undefined,
    req: ssrContext ? ssrContext.req : undefined,
    res: ssrContext ? ssrContext.res : undefined,
    beforeRenderFns: ssrContext ? ssrContext.beforeRenderFns : undefined
  });

  const inject = function (key, value) {
    if (!key) throw new Error('inject(key, value) has no key provided');
    if (!value) throw new Error('inject(key, value) has no value provided');
    key = '$' + key;
    // Add into app
    app[key] = value;

    // Add into store
    store[key] = app[key];

    // Check if plugin not already installed
    const installKey = '__nuxt_' + key + '_installed__';
    if (Vue[installKey]) return;
    Vue[installKey] = true;
    // Call Vue.use() to install the plugin into vm
    Vue.use(() => {
      if (!Vue.prototype.hasOwnProperty(key)) {
        Object.defineProperty(Vue.prototype, key, {
          get () {
            return this.$root.$options[key]
          }
        })
      }
    })
  };


  if (process.client) {
    // Replace store state before plugins execution
    if (window.__NUXT__ && window.__NUXT__.state) {
      store.replaceState(window.__NUXT__.state)
    }
  }


  // Plugin execution

  if (typeof nuxt_plugin_pluginseo_26e4ed71 === 'function') await nuxt_plugin_pluginseo_26e4ed71(app.context, inject);
  if (typeof nuxt_plugin_pluginrouting_3c9d9e30 === 'function') await nuxt_plugin_pluginrouting_3c9d9e30(app.context, inject);
  if (typeof nuxt_plugin_pluginmain_7147a387 === 'function') await nuxt_plugin_pluginmain_7147a387(app.context, inject);
  if (typeof nuxt_plugin_axios_494a31c4 === 'function') await nuxt_plugin_axios_494a31c4(app.context, inject);
  if (typeof nuxt_plugin_plugin_fb59caba === 'function') await nuxt_plugin_plugin_fb59caba(app.context, inject);
  if (typeof nuxt_plugin_auth_6a7e4e1e === 'function') await nuxt_plugin_auth_6a7e4e1e(app.context, inject);
  if (typeof nuxt_plugin_vSelect_475ab648 === 'function') await nuxt_plugin_vSelect_475ab648(app.context, inject);
  if (typeof nuxt_plugin_infiniteScroll_049132f7 === 'function') await nuxt_plugin_infiniteScroll_049132f7(app.context, inject);
  if (typeof nuxt_plugin_axios_3566aa80 === 'function') await nuxt_plugin_axios_3566aa80(app.context, inject);
  if (typeof nuxt_plugin_SocialSharing_3ab090d9 === 'function') await nuxt_plugin_SocialSharing_3ab090d9(app.context, inject);
  if (typeof nuxt_plugin_VueMasonry_21187416 === 'function') await nuxt_plugin_VueMasonry_21187416(app.context, inject);
  if (typeof nuxt_plugin_VueClipboard_7da67946 === 'function') await nuxt_plugin_VueClipboard_7da67946(app.context, inject);
  if (typeof nuxt_plugin_veeValidate_1cb8e4d4 === 'function') await nuxt_plugin_veeValidate_1cb8e4d4(app.context, inject)

  return {
    app,
    router,
    store
  }
}

export { createApp, NuxtError }
