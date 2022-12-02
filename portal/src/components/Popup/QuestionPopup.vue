<template>
  <transition name="fade">
    <Popup v-if="showPopup" :close="close" :is-show="showPopup">
      <slot>
        <h2 class="popup__title">
          {{ $t("Question-popup-title") }}
        </h2>
        <div class="popup__subtext" v-html="getSubText()" />
        <v-form ref="form" v-model="valid" class="popup-form" lazy-validation @submit.prevent="sendForm">
          <v-text-field
            v-model="name"
            :rules="nameRules"
            :label="$t('Question-popup-name')"
            required
            outlined
          ></v-text-field>
          <v-text-field
            v-model="email"
            :rules="emailRules"
            :label="$t('Question-popup-email')"
            required
            outlined
          ></v-text-field>
          <v-textarea
            v-model="message"
            :rules="messageRules"
            :label="$t('Question-popup-message')"
            required
            outlined
          ></v-textarea>
          <button :disabled="!valid" type="submit" class="button">{{ $t("Question-popup-send") }}</button>
        </v-form>
      </slot>
    </Popup>
  </transition>
</template>

<script>
import axios from "~/axios";
import Popup from "~/components/Popup";
import DOMPurify from "dompurify";
export default {
  name: "QuestionPopup",
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
  data: () => ({
    valid: true,
    name: "",
    email: "",
    message: "",
  }),
  computed: {
    nameRules() {
      return [(v) => !!v || this.$t("errors.fieldRequired")];
    },
    emailRules() {
      return [
        (v) => !!v || this.$t("errors.fieldRequired"),
        (v) => /.+@.+\..+/.test(v) || this.$t("errors.fieldValidEmail"),
      ];
    },
    messageRules() {
      return [(v) => !!v || this.$t("errors.fieldRequired")];
    },
  },
  methods: {
    getSubText() {
      const subText = this.$i18n.t("html-Question-popup-subtext");
      return DOMPurify.sanitize(subText);
    },
    async sendForm() {
      const valid = await this.$refs.form.validate();
      if (valid) {
        const currentUrl = window.location.pathname;
        await axios.post("contact/", {
          name: this.name,
          subject: "Vraag",
          email: this.email,
          message: this.message,
          current_url: currentUrl,
        });
        this.close();
      }
    },
  },
};
</script>
<style scoped lang="less">
@import "./../../variables";
html {
  height: 90vh;
  overflow: "hidden";
}
.popup-form {
  overflow-y: scroll;
}

/deep/.v-input__slot {
  background-color: @light-grey !important;
  fieldset {
    border: none !important;
  }
}
/deep/textarea {
  border: none !important;
}
</style>
