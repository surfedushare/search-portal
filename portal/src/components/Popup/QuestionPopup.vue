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
          {{ $t("Question-popup-title") }}
        </h2>
        <div class="popup__subtext">
          {{ $t("Question-popup-subtext") }}
        </div>
        <v-form ref="form" v-model="valid" lazy-validation>
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
          <button :disabled="!valid" class="button" @click="sendForm">
            {{ $t("Question-popup-send") }}
          </button>
        </v-form>
      </slot>
    </Popup>
  </transition>
</template>

<script>
import axios from "~/axios";
import Popup from "~/components/Popup";
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
/deep/.v-input__slot {
  background-color: @grey !important;
  fieldset {
    border: none !important;
  }
}
/deep/textarea {
  border: none !important;
}
</style>
