<template>
  <div>
    <h3 class="material__info_subttl">{{ $t('Part-of-set') }}</h3>
    <div class="blue-bar">
      <div class="content" @click="goToMaterial">
        <h3>
          {{ mainMaterial.title }}
          <i class="arrow"></i>
        </h3>
        <div v-if="mainMaterial.has_part">
          {{ $tc('Materials', mainMaterial.has_part.length) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MaterialPartOfSet',
  props: {
    material: {
      type: Object,
      default: null,
      required: false
    }
  },
  data() {
    return {
      mainMaterial: {}
    }
  },
  watch: {
    material: function() {
      this.updateMainMaterial()
    }
  },
  mounted() {
    this.updateMainMaterial()
  },
  methods: {
    goToMaterial() {
      this.$router.push(
        this.localePath({
          name: 'materials-id',
          params: { id: this.mainMaterial.external_id }
        })
      )
    },
    updateMainMaterial() {
      if (this.material.is_part_of !== null) {
        this.$store
          .dispatch('getMaterial', {
            params: { external_id: this.material.is_part_of }
          })
          .then(result => (this.mainMaterial = result[0]))
      }
    }
  }
}
</script>

<style src="../MaterialInfo/MaterialInfo.component.less" scoped lang="less" />
