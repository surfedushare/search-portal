export const PublishStatus = {
  // NB: this enum has a hard copy in the API
  DRAFT: 0,
  REVIEW: 1,
  PUBLISHED: 2,
}

// Imported from vue-router
export function getLocation(base, mode) {
  var path = window.location.pathname
  if (mode === 'hash') {
    return window.location.hash.replace(/^#\//, '')
  }
  if (base && path.indexOf(base) === 0) {
    path = path.slice(base.length)
  }
  return (path || '/') + window.location.search + window.location.hash
}
