<template>
  <div v-if="setMaterials.length > 0">
    <h3 class="material__info_subttl">
      <i class="set-icon large" />
      {{ $t("Parts") }}
    </h3>
    <h4>{{ $t("Learning-materials-in-set") }}</h4>
    <div class="material__info_set_table">
      <div class="row header">
        <span class="edusources-title">{{ $t("Title") }}</span>
        <span class="type">{{ $t("File-format") }}</span>
        <span class="link" />
      </div>
      <div
        v-for="setMaterial in setMaterials"
        :key="setMaterial.external_id"
        class="row"
        @click="onMaterialClick(setMaterial)"
      >
        <span class="edusources-title">{{ setMaterial.title }}</span>
        <span class="type">
          {{ setMaterial.technical_type !== "unknown" ? $t(setMaterial.technical_type) : "-" }}
        </span>
        <span class="link">
          <a v-if="setMaterial.url" class="external_link" target="_blank" :href="setMaterial.url" />
        </span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "MaterialSet",
  props: {
    setMaterials: {
      type: Array,
      default: () => [],
      required: true,
    },
  },
  methods: {
    onMaterialClick(material) {
      this.$router.push(
        this.localePath({
          name: "materials-id",
          params: { id: material.external_id },
        })
      );
    },
  },
};
</script>

<style src="../MaterialInfo/MaterialInfo.component.less" scoped lang="less" />
