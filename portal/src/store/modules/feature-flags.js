import axios from "~/axios";

export default {
  state: {
    waffle_status: null,
  },
  getters: {
    isNewHeader(state) {
      const newHeader = state.waffle_status.flags["new-header"];
      return newHeader ? newHeader["is_active"] : false;
    },
  },
  actions: {
    async getFeatureFlags({ commit }) {
      const { data: waffle_status } = await axios.get("waffle_status");
      commit("GET_FEATURE_FLAGS", waffle_status);
    },
  },
  mutations: {
    GET_FEATURE_FLAGS(state, payload) {
      state.waffle_status = payload;
    },
  },
};
