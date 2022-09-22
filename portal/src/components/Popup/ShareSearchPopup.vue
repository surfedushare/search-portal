<template>
  <transition name="fade">
    <Popup v-if="isShow" :close="close" :is-show="isShow">
      <slot>
        <h2 class="popup__title">
          {{ $t("Share-search-popup-title") }}
        </h2>
        <v-form ref="form" v-model="valid"  lazy-validation>
          <v-row>
            <v-col>
              <v-text-field
                v-model="width"
                :rules="widthRules"
                :label="$t('Share-search-popup-width')"
                required
                outlined
              ></v-text-field>
            </v-col>
            <v-col>
              <v-text-field
                v-model="height"
                :rules="heightRules"
                :label="$t('Share-search-popup-height')"
                required
                outlined
              ></v-text-field>
            </v-col>
          </v-row>
          <v-select
            v-model="language"
            :items="[
              {'text': $t('nl'), 'value': 'nl'},
              {'text': $t('en'), 'value': 'en'}
            ]"
            :label="$t('Share-search-popup-language')"
            outlined
          ></v-select>
          <v-sheet
            color="grey lighten-4"
            height="96"
            width="100%"
            rounded="rounded"
          >
            <div class="iframe-code-block">{{ iframeCodeBlock }}</div>
          </v-sheet>
          <button @click.prevent="isShow = false" class="button">{{ $t("Share-search-popup-cancel") }}</button>
          <button @click.prevent="copyIframeCodeBlock" :disabled="!valid" type="submit" class="button">
            {{ $t("Share-search-popup-copy") }}
          </button>
        </v-form>
      </slot>
    </Popup>
  </transition>
</template>

<script>
import Popup from "~/components/Popup";

export default {
  name: "ShareSearchPopup",
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
    errors: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      isShow: this.showPopup,
      valid: true,
      width: "640",
      height: "480",
      language: "nl",
    }
  },
  watch: {
    showPopup(newValue) {
      this.isShow = newValue;
    }
  },
  computed: {
    widthRules() {
      return [
        (value) => !!value || this.$t("errors.fieldRequired"),
        (value) => !isNaN(value) || this.$t("errors.fieldValidNumber"),
      ];
    },
    heightRules() {
      return [
        (value) => !!value || this.$t("errors.fieldRequired"),
        (value) => !isNaN(value) || this.$t("errors.fieldValidNumber"),
      ];
    },
    iframeCodeBlock() {
      if(!this.valid) {
        return;
      }
      const width = this.width
      const height = this.height
      return `<iframe width="${width}" height="${height}" src="secret-chocolate-sauce"/>`
    }
  },
  methods: {
    async copyIframeCodeBlock() {
      if(!this.valid) {
        return;
      }
      await navigator.clipboard.writeText(this.iframeCodeBlock);
      this.isShow = false;
    }
  },
};
</script>
<style scoped lang="less">
@import "./../../variables";
html {
  height: 90vh;
  overflow: "hidden";
}

/deep/.v-input__slot {
  background-color: @grey !important;
  fieldset {
    border: none !important;
  }
}
/deep/textarea {
  border: none !important;
}
.iframe-code-block {
  padding: 10px;
}
.button {
  margin: 20px 20px 0 0;
}
</style>
