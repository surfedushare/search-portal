<template>
  <div>
    <h3 class="material__info_subttl">
      <i class="set-icon large" />
      {{ $t('Parts') }}
    </h3>
    <h4>{{ $t('Learning-materials-in-set') }}</h4>
    <div class="material__info_set_table">
      <div class="row header">
        <span class="title">{{ $t('Title') }}</span>
        <span class="type">{{ $t('File-format') }}</span>
        <span class="level">{{ $t('Learning-levels') }}</span>
        <span class="link"></span>
      </div>
      <div
        v-for="(setMaterial, i) in setMaterials"
        :key="setMaterial.external_id"
        class="row"
      >
        <span class="title">{{ `${i + 1}. ${setMaterial.title}` }}</span>
        <span class="type">{{ setMaterial.format }}</span>
        <span class="level">
          {{
            setMaterial.educationallevels
              .slice(0, 2)
              .map(level => level[$i18n.locale])
              .join(', ')
          }}
        </span>
        <span class="link">
          <a
            v-if="setMaterial.url"
            class="external_link"
            target="_blank"
            :href="setMaterial.url"
          />
        </span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MaterialSet',
  props: {
    material: {
      //type: Array,
      //default: []
    }
  },
  data() {
    return {
      setMaterials: []
    }
  },
  mounted() {
    if (this.material.has_part.length > 0) {
      this.$store
        .dispatch('getSetMaterials', {
          external_id: this.material.external_id
        })
        .then(res => (this.setMaterials = res.records))
    }
  }
}
</script>

<style src="../MaterialInfo/MaterialInfo.component.less" scoped lang="less" />
