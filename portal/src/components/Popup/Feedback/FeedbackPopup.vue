<template>
  <transition name="fade">
    <Popup
      v-if="showPopup"
      :close="close"
      :is-show="showPopup"
      class="popup-content"
    >
      <slot>
        <h2 class="popup__title">
          {{ $t('Give-feedback') }}
        </h2>
        <div class="popup__subtext">
          {{ $t('Give-feedback-subtext') }}
        </div>
        <div>
          <textarea
            v-model="message"
            rows="4"
            class="input textarea"
          />
          <div class="popup-content__actions">
            <button class="button" @click="sendFeedback">
              {{ $t('Send-feedback') }}
            </button>
          </div>
        </div>
      </slot>
    </Popup>
  </transition>
</template>

<script>
import axios from '~/axios'
import Popup from '~/components/Popup'
export default {
  name: 'FeedbackPopup',
  components: {
    Popup,
  },
  props: {
    showPopup: {
      type: Boolean,
      default: false,
    },
    close: {
      type: Function,
      default: () => {},
    },
  },
  data() {
    return {
      message: null,
    }
  },
  methods: {
    async sendFeedback() {
      if (this.message.trim().length > 0) {
        const currentUrl = window.location.pathname
        await axios.post('feedback/', {
          feedback: this.message,
          current_url: currentUrl,
        })
      }
      this.close()
    },
  },
}
</script>
<style
  src="../DeleteCollection/DeleteCollection.component.less"
  scoped
  lang="less"
/>
