import { isString, map, isEmpty, keys, isNil } from 'lodash'
import injector from 'vue-inject'
import i18n from '~/i18n/index'

const $timeout = injector.get('$timeout')

const DEFAULT_MESSAGES = {
  info: [],
  error: [],
}

function assertMessageLevel(level) {
  if (!DEFAULT_MESSAGES[level]) {
    throw Error('Assert: unknown message level ' + level)
  }
}

export default {
  state: {
    messages: DEFAULT_MESSAGES,
    timeout: null,
  },
  getters: {
    getMessagesContent(state) {
      // We load the Nuxt app, because we'll need the i18n object to translate messages
      return (level) => {
        assertMessageLevel(level)
        return map(state.messages[level], (msg) => {
          return i18n.t(msg)
        }).join(' ')
      }
    },
    getLevelIcon() {
      return (level) => {
        assertMessageLevel(level)
        return level === 'error' ? 'fa-exclamation-triangle' : 'fa-info-circle'
      }
    },
    getMessageLevels(state) {
      return keys(state.messages)
    },
    hasMessages(state) {
      return (level) => {
        assertMessageLevel(level)
        return !isEmpty(state.messages[level])
      }
    },
  },
  mutations: {
    ADD_MESSAGE(state, { level, message, sticky }) {
      // Check input
      assertMessageLevel(level)
      if (!isString(message)) {
        throw Error('Message should be a string not ' + typeof message)
      }
      sticky = isNil(sticky) ? level === 'error' : sticky

      // Invalidate and create timeout for message removal
      if (!isNil(state.timeout)) {
        clearTimeout(state.timeout)
        state.timeout = null
      }
      if (!sticky) {
        state.timeout = $timeout(() => {
          this.commit('CLEAR_MESSAGES', level)
          state.timeout = null
        }, 2000)
      }

      // Add a message if it's not already there
      if (state.messages[level].indexOf(message) < 0) {
        state.messages[level].push(message)
      }
    },
    CLEAR_MESSAGES(state, level) {
      assertMessageLevel(level)
      state.messages[level] = []
    },
  },
}
