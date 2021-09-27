<template>
  <transition name="fade">
    <Popup
      v-if="showPopup"
      :close="close"
      :is-show="showPopup"
      class="popup-content"
    >
      <slot>
        <h2 class="popup__title">{{ $t('View-materials') }}</h2>
        <div>
          <a
            v-for="(file, ix) in material.files"
            :key="ix"
            :href="file.url"
            class="button button--full-width material__grey_block-btn"
            target="_blank"
            >{{ file.title }}</a
          >
        </div>
      </slot>
    </Popup>
  </transition>
</template>

<script>
import Popup from '~/components/Popup'

export default {
  name: 'SelectDownloadPopup',
  components: {
    Popup
  },
  props: {
    showPopup: {
      type: Boolean,
      default: false
    },
    close: {
      type: Function,
      default: () => {}
    },
    material: {
      type: Object,
      default: null
    }
  }
}
</script>
<style scoped lang="less">
.button {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;

  margin-bottom: 15px;
  background-image: url('/images/open-link-black.svg');
  background-position: 17px 15px;
  background-repeat: no-repeat;
  background-size: 25px 25px;
  padding: 19px 23px 19px 62px;
}
</style>
