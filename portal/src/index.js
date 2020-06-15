import Vue from "vue";
import injector from "vue-inject";
Vue.use(injector);

import { createRouter } from "./router.js";
import App from "./App.vue";
import { setContext, getLocation } from "./utils";
import { createStore } from "./store.js";
import { createI18N } from "./i18n";

/* Plugins */
import nuxt_plugin_pluginrouting_3c9d9e30 from "./i18n/plugin.routing.js";
import nuxt_plugin_axios_494a31c4 from "./axios.js";
import nuxt_plugin_auth_6a7e4e1e from "./plugins/auth";
import nuxt_plugin_infiniteScroll_049132f7 from "./plugins/infiniteScroll";
import nuxt_plugin_axios_3566aa80 from "./plugins/axios";
import nuxt_plugin_SocialSharing_3ab090d9 from "./plugins/SocialSharing";
import nuxt_plugin_VueMasonry_21187416 from "./plugins/VueMasonry";
import nuxt_plugin_VueClipboard_7da67946 from "./plugins/VueClipboard";

const $log = injector.get("$log");

async function createApp(ssrContext) {
  const router = await createRouter(ssrContext);

  const store = createStore(ssrContext);
  // Add this.$router into store actions/mutations
  store.$router = router;

  const i18n = await createI18N();

  // Create Root instance
  // here we inject the router and store to all child components,
  // making them available everywhere as `this.$router` and `this.$store`.
  const app = {
    router,
    store,
    i18n,
    ...App
  };

  // Make app available into store via this.app
  store.app = app;
  // Make app available from anywhere through injector
  injector.constant("App", app);

  const next = location => app.router.push(location);

  // Resolve route
  let route;
  const path = getLocation(router.options.base);
  route = router.resolve(path).route;

  // Set context to app.context
  await setContext(app, {
    route,
    next,
    error: null,
    store,
    payload: ssrContext ? ssrContext.payload : undefined,
    req: ssrContext ? ssrContext.req : undefined,
    res: ssrContext ? ssrContext.res : undefined,
    beforeRenderFns: ssrContext ? ssrContext.beforeRenderFns : undefined
  });

  const inject = function(key, value) {
    if (!key) throw new Error("inject(key, value) has no key provided");
    if (!value) throw new Error("inject(key, value) has no value provided");
    key = "$" + key;
    // Add into app
    app[key] = value;

    // Add into store
    store[key] = app[key];

    // Check if plugin not already installed
    const installKey = "__nuxt_" + key + "_installed__";
    if (Vue[installKey]) return;
    Vue[installKey] = true;
    // Call Vue.use() to install the plugin into vm
    Vue.use(() => {
      if (!Vue.prototype.hasOwnProperty(key)) {
        Object.defineProperty(Vue.prototype, key, {
          get() {
            return this.$root.$options[key];
          }
        });
      }
    });
  };

  // Plugin execution

  if (typeof nuxt_plugin_pluginrouting_3c9d9e30 === "function")
    await nuxt_plugin_pluginrouting_3c9d9e30(app.context, inject);
  if (typeof nuxt_plugin_axios_494a31c4 === "function")
    await nuxt_plugin_axios_494a31c4(app.context, inject);
  if (typeof nuxt_plugin_auth_6a7e4e1e === "function")
    await nuxt_plugin_auth_6a7e4e1e(app.context, inject);
  if (typeof nuxt_plugin_infiniteScroll_049132f7 === "function")
    await nuxt_plugin_infiniteScroll_049132f7(app.context, inject);
  if (typeof nuxt_plugin_axios_3566aa80 === "function")
    await nuxt_plugin_axios_3566aa80(app.context, inject);
  if (typeof nuxt_plugin_SocialSharing_3ab090d9 === "function")
    await nuxt_plugin_SocialSharing_3ab090d9(app.context, inject);
  if (typeof nuxt_plugin_VueMasonry_21187416 === "function")
    await nuxt_plugin_VueMasonry_21187416(app.context, inject);
  if (typeof nuxt_plugin_VueClipboard_7da67946 === "function")
    await nuxt_plugin_VueClipboard_7da67946(app.context, inject);

  return {
    app,
    router,
    store
  };
}

export { createApp };
