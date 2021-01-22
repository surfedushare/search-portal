<template>
  <div class="switch-input">
    <span v-if="label" class="label">{{ label }}&nbsp;&nbsp;</span>
    <label class="switch">
      <input v-model="internalValue" type="checkbox" />
      <span class="slider round" />
    </label>
  </div>
</template>

<script>
export default {
  name: 'SwitchInput',
  props: {
    label: {
      type: String,
      default: ''
    },
    value: Boolean
  },
  data() {
    return {
      internalValue: this.value
    }
  },
  watch: {
    internalValue(input) {
      this.$emit('input', input)
    }
  }
}
</script>
<style lang="less">
@import '../variables';

.switch-input {
  display: flex;
  color: white;
  align-items: center;
}

span.label {
  margin-right: 10px;
}

.switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 34px;
}

/* Hide default HTML checkbox */
.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

/* The slider */
.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  -webkit-transition: 0.4s;
  transition: 0.4s;
}

.slider:before {
  position: absolute;
  content: '';
  height: 26px;
  width: 26px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  -webkit-transition: 0.4s;
  transition: 0.4s;
}

input:checked + .slider {
  background-color: @green-hover;
}

input:checked + .slider:before {
  -webkit-transform: translateX(26px);
  -ms-transform: translateX(26px);
  transform: translateX(26px);
}

/* Rounded sliders */
.slider.round {
  border-radius: 34px;
}

.slider.round:before {
  border-radius: 50%;
}
</style>
