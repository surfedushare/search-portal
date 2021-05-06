<template>
  <div
    :class="{ selected: material.selected, stack: hasPart }"
    class="materials__item_wrapper tile__wrapper"
    @click="handleMaterialClick(material)"
  >
    <div class="materials__item_set-wrapper">
      <span v-if="hasPart" class="materials__item_set">
        {{ $t('Set') }}
      </span>
    </div>
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
        <div v-if="hasPart" class="materials__item_set_count">
          {{ $tc('Materials', material.has_parts.length) }}
        </div>
        <div
          v-if="itemsInLine === 1 && material.description"
          class="materials__item_description"
        >
          {{ material.description }}
        </div>
      </div>
      <div class="materials__item_subinfo">
        <div>
          <div
            v-if="material.disciplines && material.disciplines.length"
            class="materials__item_disciplines"
          >
            <span
              v-for="(discipline, i) in material.disciplines.slice(0, 2)"
              :key="i"
              class="materials__item_discipline"
            >
              {{
                punctuate(
                  titleTranslation(discipline, $i18n.locale),
                  i,
                  material.disciplines.length
                )
              }}
            </span>
          </div>
          <div
            v-if="
              material.educationallevels && material.educationallevels.length
            "
            class="materials__item_educationallevels"
          >
            <span
              v-for="(educationallevel, i) in material.educationallevels.slice(
                0,
                2
              )"
              :key="i"
              class="materials__item_educationallevel"
            >
              {{
                punctuate(
                  educationallevel[$i18n.locale],
                  i,
                  material.educationallevels.length
                )
              }}
            </span>
          </div>
          <div
            v-if="material.format && material.format !== 'unknown'"
            class="materials__item_format"
          >
            {{ $t(material.format) }}
          </div>
          <div
            v-if="
              material.keywords && material.keywords.length && itemsInLine === 1
            "
            class="materials__item_keywords"
          >
            <span
              v-for="(keyword, i) in material.keywords.slice(0, 2)"
              :key="keyword"
              class="materials__item_keyword"
            >
              {{ punctuate(keyword, i, material.keywords.length) }}
            </span>
          </div>
          <routerLink
            v-for="community in material.communities"
            :key="`${community.id}`"
            :to="
              localePath({
                name: 'communities-community',
                params: { community: community.id }
              })
            "
            class="materials__item_community_link"
            @click.native="$event.stopImmediatePropagation()"
          >
            {{ titleTranslation(community, $i18n.locale) }}
          </routerLink>
        </div>
        <div class="materials__item_copyrights" :class="material.copyright" />
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
      type: Object,
      default: null,
      required: false
    },
    index: {
      type: Number,
      default: 0
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
  },
  computed: {
    hasPart() {
      return this.material.has_parts.length > 0
    }
  },
  methods: {
    punctuate(word, index, len) {
      let punctuated = word
      if (len > 1 && index < len - 1) {
        punctuated = punctuated + ', '
      }
      if (index === 1 && len >= 3) {
        punctuated = punctuated + '...'
      }
      return punctuated
    }
  }
}
</script>

<style src="./../Materials.component.less" scoped lang="less"></style>
