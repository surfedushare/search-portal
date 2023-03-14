import axios from "~/axios";

export default {
  state: {
    config: null,
  },
  getters: {
    use_api_endpoint(state) {
      return state.config.use_api_endpoint;
    },
  },
  actions: {
    async getConfig({ commit }) {
      const { data: config } = await axios.get("/config");
      commit("SET_CONFIG", config);
    },
  },
  mutations: {
    SET_CONFIG(state, payload) {
      state.config = payload;
    },
  },
};
