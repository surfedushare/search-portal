<template>
  <div>
    <button type="button" class="feedback button" @click="togglePopup">
      <span class="button-text">
        <span class="inner">Feedback</span>
      </span>
    </button>
    <FeedbackPopup
      v-if="showPopup"
      :show-popup="showPopup"
      :close="togglePopup"
    />
  </div>
</template>

<script>
import FeedbackPopup from '../Popup/Feedback/FeedbackPopup'
export default {
  name: 'Feedback',
  components: {
    FeedbackPopup,
  },
  data() {
    return {
      showPopup: false,
    }
  },
  methods: {
    togglePopup() {
      this.showPopup = !this.showPopup
    },
  },
}
</script>

<style lang="less" scoped>
@import './../../variables';
.feedback {
  position: fixed;
  right: 0;
  top: 75%;
  background-color: @green;
  color: white;
  padding: 23px 17px;
  max-height: none;

  &:hover {
    background-color: @green-hover !important;
    color: white !important;
  }

  .button-text {
    writing-mode: tb-rl;
    display: flex;
    align-items: center;
    justify-content: flex-end;

    .inner {
      transform: rotate(180deg);
      transition: transform 1s ease-in-out;
    }
  }
}
</style>
