<template>
  <div v-if="material">
    <div class="green-bar part-of-set">
      <div class="content" @click="goToMaterial">
        <h3>
          {{ material.title }}
          <i class="arrow" />
        </h3>
        <div v-if="material.has_parts">
          {{ $tc('Materials', material.has_parts.length) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MaterialPartOfSet',
  props: {
    parentId: {
      type: String,
      default: null,
      required: true,
    },
  },
  data() {
    return {
      material: null,
    }
  },
  mounted() {
    this.updateMaterial()
  },
  methods: {
    goToMaterial() {
      this.$router.push(
        this.localePath({
          name: 'materials-id',
          params: { id: this.parentId },
        })
      )
    },
    updateMaterial() {
      if (!this.parentId) {
        return
      }
      this.$store
        .dispatch('getMaterial', {
          params: { external_id: this.parentId },
        })
        .then((result) => {
          return (this.material = result[0])
        })
    },
  },
}
</script>

<style src="../MaterialInfo/MaterialInfo.component.less" scoped lang="less" />
