import Vue from "vue";
import Vuex from "vuex";
import collections from "./modules/collections";
import communities from "./modules/communities";
import filterCategories from "./modules/filter-categories";
import headerMenu from "./modules/header-menu";
import headerSubMenu from "./modules/header-sub-menu";
import materials from "./modules/materials";
import messages from "./modules/messages";
import statistic from "./modules/statistic";
import themes from "./modules/themes";
import user from "./modules/user";

Vue.use(Vuex);

const store = new Vuex.Store({
  modules: {
    user,
    filterCategories,
    communities,
    materials,
    themes,
    collections,
    statistic,
    headerMenu,
    headerSubMenu,
    messages,
  },
});

export default store;
