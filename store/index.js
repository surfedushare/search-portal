import Vue from 'vue'
import Vuex from 'vuex'

import filterCategories from './modules/filter-categories'
import communities from './modules/communities'
import materials from './modules/materials'
import themes from './modules/themes'

Vue.use(Vuex)

const store = () =>
  new Vuex.Store({
    modules: {
      filterCategories,
      communities,
      materials,
      themes
    }
  })
export default store
