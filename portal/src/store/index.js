import Vue from "vue";
import Vuex from "vuex";
import collections from "./modules/collections";
import communities from "./modules/communities";
import filterCategories from "./modules/filter-categories";
import headerMenu from "./modules/header-menu";
import materials from "./modules/materials";
import messages from "./modules/messages";
import statistic from "./modules/statistic";
import featureFlags from "./modules/feature-flags";
import user from "./modules/user";

Vue.use(Vuex);

const store = new Vuex.Store({
  modules: {
    user,
    filterCategories,
    communities,
    materials,
    collections,
    statistic,
    headerMenu,
    messages,
    featureFlags,
  },
});

export default store;
