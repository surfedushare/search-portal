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
          {{ $t('Delete-account') }}
        </h2>
        <div class="popup__subtext">
          {{ $t('Are-you-sure-you-want-to-delete-this-account') }}
        </div>
        <div>
          <div class="popup-content__actions">
            <button class="button" @click="deleteAccount">
              {{ $t('Yes-delete-it') }}
            </button>
          </div>
        </div>
      </slot>
    </Popup>
  </transition>
</template>

<script>
import Popup from '~/components/Popup'

export default {
  name: 'DeleteAccountPopup',
  components: {
    Popup,
  },
  props: {
    showPopup: {
      type: Boolean,
      default: false,
    },
    deleteAccount: {
      type: Function,
      default: () => {},
    },
    close: {
      type: Function,
      default: () => {},
    },
  },
}
</script>

<style
  src="./DeleteCollection/DeleteCollection.component.less"
  scoped
  lang="less"
/>
