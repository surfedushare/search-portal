export default function({ route, store }) {
  route.meta.matomo = {
    userId: [
      'setUserId',
      store.state.user && store.state.user.user
        ? store.state.user.user.id
        : 'anonymous'
    ]
  };
}
