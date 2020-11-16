<template>
  <div>
    <h3 class="material__info_subttl">
      <i class="set-icon large"/>
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
      <div v-for="(setMaterial, i) in setMaterials" class="row">
        <span class="title">{{ `${i + 1}. ${setMaterial.title}` }}</span>
        <span class="type">{{ setMaterial.format }}</span>
        <span class="level">
          <span
            class="level"
            v-for="(level, i) in setMaterial.educationallevels.slice(0, 2)"
            :key="i"
          >
            {{
              addComma(
                level[$i18n.locale],
                i,
                setMaterial.educationallevels.length
              )
            }}
          </span>
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
  name: 'Set',
  props: {
    setMaterials: {
      type: Array,
      default: []
    }
  },
  methods: {
    addComma(word, index, len) {
      if (len > 1 && index < len - 1) {
        return word + ', '
      } else {
        return word
      }
    }
  }
}

</script>

<style src="../MaterialInfo/MaterialInfo.component.less" scoped lang="less"></style>
