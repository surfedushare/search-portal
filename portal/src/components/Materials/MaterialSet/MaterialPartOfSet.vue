<template>
  <div>
    <h3 class="material__info_subttl">{{ $t('Part-of-set') }}</h3>
    <div class="material__info_part_of">
      <div class="material__info_main" @click="goToMaterial">
        <h3>
          {{ mainMaterial.title }}
          <i class="material__info_main_arrow"></i>
        </h3>
        <div v-if="mainMaterial.has_part" class="">
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
      //type: Object,
      //default: {}
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
        .dispatch('getMaterialByExternalId', { id: this.material.is_part_of })
        .then(result => (this.mainMaterial = result[0]))
    }
  },
  methods: {
    goToMaterial() {
      const route = this.$router.resolve(
        this.localePath({
          name: 'materials-id', // put your route information in
          params: { id: this.mainMaterial.external_id } // put your route information in
        })
      )
      window.location.assign(route.href)
    }
  }
}
</script>

<style src="../MaterialInfo/MaterialInfo.component.less" scoped lang="less" />
