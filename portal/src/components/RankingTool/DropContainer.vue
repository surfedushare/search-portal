<template>
  <div>
    <h3>{{ title }}</h3>
    <draggable
      :list="list"
      group="rankingtool"
      :move="move"
      class="dropzone"
      :data-id-attr="identifier"
    >
      <div
        v-for="material in list"
        :key="material.external_id"
        class="material-container"
      >
        <Material
          :material="material"
          :handle-material-click="handleMaterialClick"
        />
      </div>
    </draggable>
  </div>
</template>
<script>
import draggable from 'vuedraggable'
import Material from '~/components/Materials/Material/Material'

export default {
  components: {
    draggable,
    Material
  },
  props: {
    title: {
      type: String,
      default: ''
    },
    identifier: {
      type: String,
      default: ''
    },
    move: {
      type: Function,
      default: () => {}
    },
    list: {
      type: Array,
      default: () => []
    }
  },
  methods: {
    handleMaterialClick() {
      console.log('click')
    }
  }
}
</script>
<style scoped>
.dropzone {
  border: 1px dashed #ccc;
  padding: 20px;
  border-radius: 10px;
  margin: 10px 0 20px 0;
}

.material-container {
  margin-bottom: 20px;
}

.material-container:last-child {
  margin-bottom: 0;
}
</style>
