import Vue from 'vue';
import Vuex from 'vuex';

import user from './modules/user';
import filterCategories from './modules/filter-categories';
import communities from './modules/communities';
import materials from './modules/materials';
import themes from './modules/themes';
import filters from './modules/filters';
import collections from './modules/collections';
import statistic from './modules/statistic';
import headerMenu from './modules/header-menu';
import headerSubMenu from './modules/header-sub-menu';

Vue.use(Vuex);

const store = () =>
  new Vuex.Store({
    modules: {
      user,
      filterCategories,
      communities,
      materials,
      themes,
      filters,
      collections,
      statistic,
      headerMenu,
      headerSubMenu
    }
  });
export default store;
