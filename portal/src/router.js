import Collection from "~/pages/collection";
import Communities from "~/pages/communities/communities";
import Community from "~/pages/communities/community";
const CommunityEdit = () => import(/* webpackChunkName: "rich-text-editor" */ "~/pages/communities/community-edit");
import Home from "~/pages/index";
import HowDoesItWork from "~/pages/how-does-it-work";
import InfoPage from "~/pages/info";
import Material from "~/pages/material";
import Privacy from "~/pages/privacy";
import Router from "vue-router";
import Search from "~/pages/search";
import Vue from "vue";
import VueMeta from "vue-meta";
import axios from "~/axios";
import injector from "vue-inject";
import { isEqual } from "lodash";
import { localePath } from "~/i18n/plugin.routing";
import store from "~/store";

const $log = injector.get("$log");

Vue.use(Router);
Vue.use(VueMeta);

const scrollBehavior = function (to, from, savedPosition) {
  if (savedPosition) {
    return savedPosition;
  }

  // Do not scroll to the top when only GET parameters change
  if (from && to.name === from.name && isEqual(to.params, from.params)) {
    return;
  }

  return { x: 0, y: 0 };
};

export default new Router({
  mode: "history",
  base: "/",
  linkActiveClass: "router-link-active",
  linkExactActiveClass: "router-link-exact-active",
  scrollBehavior,
  routes: [
    {
      path: "/en/how-does-it-work",
      component: HowDoesItWork,
      name: "how-does-it-work___en",
    },
    {
      path: "/hoe-werkt-het",
      component: HowDoesItWork,
      name: "how-does-it-work___nl",
    },
    {
      path: "/en/communities",
      component: Communities,
      name: "communities___en",
    },
    {
      path: "/communitys",
      component: Communities,
      name: "communities___nl",
    },
    {
      path: "/communities",
      component: Communities,
      name: "communities-legacy___nl",
    },
    {
      path: "/en/materials/search",
      component: Search,
      name: "materials-search___en",
      meta: {
        noAutoTrack: true,
      },
    },
    {
      path: "/materialen/zoeken",
      component: Search,
      name: "materials-search___nl",
      meta: {
        noAutoTrack: true,
      },
    },
    {
      path: "/en/my/collection/:id",
      component: Collection,
      name: "my-collection___en",
      meta: {
        editable: true,
      },
    },
    {
      path: "/mijn/collectie/:id",
      component: Collection,
      name: "my-collection___nl",
      meta: {
        editable: true,
      },
    },
    {
      path: "/en/my/community/:community",
      component: CommunityEdit,
      name: "my-community___en",
    },
    {
      path: "/mijn/community/:community",
      component: CommunityEdit,
      name: "my-community___nl",
    },
    {
      path: "/en/my/privacy",
      component: Privacy,
      name: "my-privacy___en",
    },
    {
      path: "/mijn/privacy",
      component: Privacy,
      name: "my-privacy___nl",
    },
    {
      path: "/en/materials/:id",
      component: Material,
      name: "materials-id___en",
    },
    {
      path: "/materialen/:id",
      component: Material,
      name: "materials-id___nl",
    },
    {
      path: "/en/collections/:id?",
      component: Collection,
      name: "collections-id___en",
      meta: {
        editable: false,
      },
    },
    {
      path: "/collecties/:id?",
      component: Collection,
      name: "collections-id___nl",
      meta: {
        editable: false,
      },
    },
    {
      path: "/en/communities/:community",
      component: Community,
      name: "communities-community___en",
    },
    {
      path: "/communitys/:community",
      component: Community,
      name: "communities-community___nl",
    },
    {
      path: "/communities/:community",
      component: Community,
      name: "communities-community-legacy___nl",
    },
    {
      path: "/en/privacy",
      component: InfoPage,
      name: "privacy___en",
      meta: {
        title_translation_key: "title-privacy-info",
        html_translation_key: "html-privacy-info",
      },
    },
    {
      path: "/privacy",
      component: InfoPage,
      name: "privacy___nl",
      meta: {
        title_translation_key: "title-privacy-info",
        html_translation_key: "html-privacy-info",
      },
    },
    {
      path: "/en/institutions",
      component: InfoPage,
      name: "institutions___en",
      meta: {
        title_translation_key: "title-institutions-info",
        html_translation_key: "html-institutions-info",
      },
    },
    {
      path: "/instellingen",
      component: InfoPage,
      name: "institutions___nl",
      meta: {
        title_translation_key: "title-institutions-info",
        html_translation_key: "html-institutions-info",
      },
    },
    {
      path: "/en/",
      component: Home,
      name: "index___en",
    },
    {
      path: "/",
      component: Home,
      name: "index___nl",
    },
    {
      path: "/login/permissions",
      beforeEnter(to, from, next) {
        let authFlowToken = to.query.partial_token || null;
        store.commit("AUTH_FLOW_TOKEN", authFlowToken);
        next(localePath({ name: "my-privacy", query: { popup: 1 } }));
      },
    },
    {
      path: "/login/success",
      beforeEnter(to, from, next) {
        axios
          .get("users/obtain-token/")
          .then((response) => {
            let token = response.token || response.data.token;
            store
              .dispatch("authenticate", { token: token })
              .then(() => {
                next(to.query.continue || "/");
              })
              .catch((error) => {
                $log.warn("Unable to login due to error during store 'login' dispatch");
                $log.error(error);
                next("/");
              });
          })
          .catch((error) => {
            $log.warn("Unable to login due to error during obtaining a token");
            $log.error(error);
            next("/");
          });
      },
    },
  ],
  fallback: false,
});
