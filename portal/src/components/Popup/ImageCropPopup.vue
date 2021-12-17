<template>
  <Popup v-if="isShow" :is-show="isShow" class="crop-popup" :close="closePopup">
    <vue-croppie
      ref="croppieRef"
      :boundary="{ width: 400, height: 300 }"
      :viewport="{ width: width, height: height }"
      :enable-resize="false"
      @result="result"
    >
    </vue-croppie>
    <button type="button" class="button crop" @click="cropImage()">
      {{ $t('Crop') }}
    </button>
  </Popup>
</template>
<script>
import Popup from '~/components/Popup'

export default {
  name: 'ImageCropPopup',
  components: {
    Popup,
  },
  props: {
    width: {
      type: Number,
      default: 100,
    },
    height: {
      type: Number,
      default: 50,
    },
    isShow: {
      type: Boolean,
      default: false,
    },
    image: {
      type: String,
      default: null,
    },
    crop: {
      type: Function,
      default: () => {},
    },
    close: {
      type: Function,
      default: () => {},
    },
  },
  watch: {
    image(image) {
      this.$refs.croppieRef.bind({
        url: image,
      })
    },
  },
  mounted() {
    if (this.image) {
      this.$refs.croppieRef.bind({
        url: this.image,
      })
    }
  },
  methods: {
    result(result) {
      this.$emit('crop', result)
      const reader = new FileReader()
      reader.onload = (e) => {
        this.$emit('preview', e.target.result)
        this.closePopup()
      }
      reader.readAsDataURL(result)
    },
    cropImage() {
      const options = {
        format: 'png',
        size: { width: this.width, height: this.height },
        type: 'blob',
      }
      this.$refs.croppieRef.result(options)
    },
    closePopup() {
      this.$emit('close')
    },
  },
}
</script>
<style lang="less">
.crop-popup {
  .popup__center {
    width: auto;
  }

  .croppie-container {
    padding: 0 20px;

    .cr-slider-wrap {
      width: 100%;

      input {
        width: 100%;
        padding: 0 20px;
      }
    }
  }

  button {
    width: auto;
    align-self: center;
  }
}
</style>
