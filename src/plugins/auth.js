export default function({ store }) {
  if (store.api_token) {
    store.dispatch('authenticate', { token: store.api_token });
  } else {
    store.dispatch('getUser');
  }
}
