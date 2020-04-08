import { isString, map } from 'lodash'
import injector from 'vue-inject'


const $log = injector.get('$log');


export default {
  state: {
    messages: {
      info: [],
      error: []
    },
  },
  getters: {
    getMessagesContent(state) {
      // We load the Nuxt app, because we'll need the i18n object to translate messages
      const app = injector.get('App');
      return (level) => {
        if (!state.messages[level]) {
          $log.warn('Unkown message level for getMessagesContent: ' + level);
          return ''
        }
        return map(state.messages[level], (msg) => { return app.i18n.t(msg) }).join(" ")
      }
    }
  },
  mutations: {
    ADD_MESSAGE(state, {level, message}) {
      if(!state.messages[level]) {
        $log.warn('Unkown message level for ADD_MESSAGE: ' + level);
        return
      }
      if(!isString(message)) {
        $log.warn('Message should be a string not ' + typeof message);
        return
      }
      state.messages[level].push(message)
    },
    CLEAR_MESSAGES(state, level) {
      if(!state.messages[level]) {
        $log.warn('Unkown message level for CLEAR_MESSAGES: ' + level);
        return
      }
      state.messages[level] = []
    }
  }
};
