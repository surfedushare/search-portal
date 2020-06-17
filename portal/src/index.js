import Vue from 'vue';
import injector from 'vue-inject';

import { createRouter } from './router.js';
import App from './App.vue';
import { setContext, getLocation } from './utils';
import { createStore } from './store.js';
import { createI18N } from './i18n';

import SocialSharing from 'vue-social-sharing';
import VueClipboard from 'vue-clipboard2';
import VueMasonry from 'vue-masonry-css';
import InfiniteScroll from 'vue-infinite-scroll';
import pluginRouting from './i18n/plugin.routing.js';
import axios from './axios.js';

Vue.use(injector);
Vue.use(SocialSharing);
Vue.use(VueClipboard);
Vue.use(VueMasonry);
Vue.use(InfiniteScroll);

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

  store.app = app;
  // Make app available from anywhere through injector
  injector.constant('App', app);

  const next = location => app.router.push(location);

  // Resolve route
  const path = getLocation(router.options.base);
  const route = router.resolve(path).route;

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

  pluginRouting(app.context);

  const axiosInstance = axios(app.context);

  // TODO: This should be replaced by modules (import)
  store.$axios = axiosInstance;
  app.$axios = axiosInstance;
  Vue.prototype.$axios = axiosInstance;

  if (store.getters.api_token) {
    store.dispatch('authenticate', { token: store.getters.api_token });
  } else {
    store.dispatch('getUser');
  }

  return {
    app,
    router,
    store
  };
}

export { createApp };
