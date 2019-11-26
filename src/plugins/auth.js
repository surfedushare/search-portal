export default function({ store }) {
  if (store.getters.api_token) {
    store.dispatch('authenticate', { token: store.getters.api_token });
  } else {
    store.dispatch('getUser');
  }
}
