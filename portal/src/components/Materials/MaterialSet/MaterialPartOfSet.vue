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
          {{ $tc('Materials', mainMaterial.has_part.length + 1) }}
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
  mounted() {
    if (this.material.is_part_of !== null) {
      this.$store
        .dispatch('getMaterial', {
          params: { external_id: this.material.is_part_of }
        })
        .then(result => (this.mainMaterial = result[0]))
    }
  },
  methods: {
    goToMaterial() {
      const route = this.$router.resolve(
        this.localePath({
          name: 'materials-id',
          params: { id: this.mainMaterial.external_id }
        })
      )
      window.location.assign(route.href)
    }
  }
}
</script>

<style src="../MaterialInfo/MaterialInfo.component.less" scoped lang="less" />
