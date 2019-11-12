export default function({ redirect, route, store }) {
  const token = localStorage.getItem('surf_token');
  if (token) {
    store.dispatch('login', { token });
  }
}
