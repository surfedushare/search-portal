import Axios from 'axios'
import i18n from './i18n'

const baseURL = process.env.VUE_APP_BACKEND_URL + 'api/v1'
const axios = Axios.create({ baseURL })
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'x-csrftoken'

axios.interceptors.response.use(function(response) {
  if (response && response.data) {
    return response.data
  }

  return response
})

setLanguage(i18n.locale)

export function setLanguage(language) {
  axios.defaults.headers.common['Accept-Language'] = language
}

export default axios
