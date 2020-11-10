<template>
  <div
    :class="{ selected: material.selected }"
    class="materials__item_wrapper tile__wrapper"
    @click="handleMaterialClick(material)"
  >
    <div class="materials__item_content">
      <div class="materials__item_main_info">
        <h3 class="materials__item_title">
          {{ material.title }}
        </h3>
        <div v-if="material.authors.length > 0" class="materials__item_author">
          {{ material.authors.join(', ') }}
        </div>
        <div
          v-if="material.publishers.length > 0"
          class="materials__item_publisher"
        >
          {{ material.publishers.join(', ') }}
        </div>
        <div class="materials__item_date">
          {{ material.date || null }}
        </div>
        <div
          v-if="itemsInLine === 1 && material.description"
          class="materials__item_description"
        >
          {{ material.description }}
        </div>
      </div>
      <div class="materials__item_subinfo">
        <div
          v-if="material.disciplines && material.disciplines.length"
          class="materials__item_disciplines"
        >
          <span
            v-for="discipline in material.disciplines.slice(0, 2)"
            :key="discipline"
            class="materials__item_discipline"
          >
            {{ titleTranslation(discipline, $i18n.locale) }}
            <span
              v-if="
                material.disciplines.length > 1 &&
                index < material.disciplines.length - 1
              "
            >,</span
            >
          </span>
          {{ material.disciplines.length < 3 ? '' : '...' }}
        </div>
        <div
          v-if="material.educationallevels && material.educationallevels.length"
          class="materials__item_educationallevels"
        >
          <span
            v-for="educationallevel in material.educationallevels.slice(0, 2)"
            class="materials__item_educationallevel"
            :key="educationallevel"
          >
            {{ educationallevel[$i18n.locale] }}
            <span
              v-if="
                material.educationallevels.length > 1 && index < material.educationallevels.length - 1
              "
            >,</span
            >
          </span>
          {{ material.educationallevels.length < 3 ? '' : '...' }}
        </div>
        <div v-if="material.format" class="materials__item_format">
          {{ $t(material.format) }}
        </div>
        <div
          v-if="
            material.keywords && material.keywords.length && itemsInLine === 1
          "
          class="materials__item_keywords"
        >
          <span
            v-for="keyword in material.keywords.slice(0, 2)"
            :key="keyword"
            class="materials__item_keyword"
          >
            {{ keyword }}
            <span
              v-if="
                material.keywords.length > 1 && index < material.keywords.length - 1
              "
            >,
            </span>
          </span>
          {{ material.keywords.length < 3 ? '' : '...' }}
        </div>
        <routerLink
          v-for="community in material.communities"
          class="materials__item_community_link"
          :key="`${community.id}`"
          :to="
            localePath({
              name: 'communities-community',
              params: { community: community.id }
            })
          "
          @click.native="$event.stopImmediatePropagation()"
        >
          {{ titleTranslation(community, $i18n.locale) }}
        </routerLink>
        <div class="materials__item_copyrights" :class="material.copyright"/>
      </div>
    </div>
    <footer class="materials__item_footer">
      <StarRating
        v-model="material.avg_star_rating"
        :counter="material.count_star_rating"
        :disabled="true"
        :dark-stars="true"
      />
      <div class="materials__item_actions">
        <div class="materials__item_applauds">
          <span>{{ material.applaud_count }}</span>
        </div>
        <a
          v-if="material.url"
          class="materials__item_external_link"
          target="_blank"
          :href="material.url"
        />
      </div>
    </footer>
  </div>
</template>

<script>
import StarRating from '../../StarRating/index'

export default {
  name: 'Material',
  components: {
    StarRating
  },
  props: {
    material: {
      type: Function,
      default: false
    },
    itemsInLine: {
      type: Number,
      default: 4
    },
    handleMaterialClick: {
      type: Function,
      params: 1,
      default: () => {}
    }
  }
}
</script>

<style src="./../Materials.component.less" scoped lang="less"></style>
