import Axios from 'axios'
import i18n from './i18n'

// Axios.prototype cannot be modified
const axiosExtra = {
  setHeader(name, value, scopes = 'common') {
    for (let scope of Array.isArray(scopes) ? scopes : [scopes]) {
      if (!value) {
        delete this.defaults.headers[scope][name]
        return
      }
      this.defaults.headers[scope][name] = value
    }
  }
}

// Request helpers ($get, $post, ...)
for (let method of [
  'request',
  'delete',
  'get',
  'head',
  'options',
  'post',
  'put',
  'patch'
]) {
  axiosExtra['$' + method] = function() {
    return this[method].apply(this, arguments).then(res => res && res.data)
  }
}

const extendAxiosInstance = axios => {
  for (let key in axiosExtra) {
    axios[key] = axiosExtra[key].bind(axios)
  }
}

const baseURL = process.env.VUE_APP_BACKEND_URL + 'api/v1'
const axios = Axios.create({ baseURL })
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'x-csrftoken'

extendAxiosInstance(axios)
setLanguage(i18n.locale)

export function setLanguage(language) {
  axios.defaults.headers.common['Accept-Language'] = language
}

export default axios
