export default function({ store }) {
  const token = localStorage.getItem('surf_token');
  if (token) {
    store.dispatch('authenticate', { token });
  }
}
