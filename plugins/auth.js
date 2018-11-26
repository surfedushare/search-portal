export default function({ redirect, route, store }) {
  if (route.query && route.query.access_token) {
    store.dispatch('login', { token: route.query.access_token });
    redirect({ path: route.path });
  }
  const token = localStorage.getItem('surf_token');
  if (token) {
    store.dispatch('login', { token });
  }
}
