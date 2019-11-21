import axios from 'axios';


export default function({ $axios, store }) {
  $axios.interceptors.request.use(
    function(config) {
      // Do something before request is sent
      if (
        // (config.id && !validateID(config.id)) ||
        config.params &&
        typeof config.params !== 'object'
      ) {
        throw new axios.Cancel('Operation canceled.');
      } else {
        return config;
      }
    },
    function(error) {
      // Do something with request error
      return Promise.reject(error);
    }
  );
  $axios.onError(error => {
    const code = parseInt(error.response && error.response.status);
    if (code === 401) {
      store.dispatch('logout');
    }
  });
}
