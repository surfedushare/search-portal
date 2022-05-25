<template>
  <div
    :class="{ selected: material.selected, stack: hasPart }"
    class="materials__item_wrapper tile__wrapper"
    @click="handleMaterialClick(material)"
  >
    <div class="materials__item_set-wrapper">
      <span v-if="hasPart" class="materials__item_set">{{ $t('Set') }}</span>
    </div>
    <div class="materials__item_content">
      <div class="materials__item_main_info">
        <h3 class="materials__item_title">{{ material.title }}</h3>
        <div
          v-if="material.authors.length > 0"
          class="materials__item_author"
        >{{ material.authors.join(', ') }}</div>
        <div
          v-if="material.publishers.length > 0"
          class="materials__item_publisher"
        >{{ material.publishers.join(', ') }}</div>
        <div class="materials__item_date">{{ formattedPublishedAt || null }}</div>
        <div
          v-if="hasPart"
          class="materials__item_set_count"
        >{{ $tc('Materials', material.has_parts.length) }}</div>
        <div
          v-if="itemsInLine === 1 && material.description"
          class="materials__item_description"
        >{{ material.description }}</div>
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
            v-if="
              material.technical_type && material.technical_type !== 'unknown'
            "
            class="materials__item_format"
          >{{ $t(material.technical_type) }}</div>
          <div
            v-if="
              material.keywords && material.keywords.length && itemsInLine === 1
            "
            class="materials__item_keywords"
          >
            <span
              v-for="(keyword, i) in material.keywords.slice(0, 2)"
              :key="keyword + '_' + i"
              class="materials__item_keyword"
            >{{ punctuate(keyword, i, material.keywords.length) }}</span>
          </div>
          <routerLink
            v-for="community in material.communities"
            :key="`${community.id}`"
            :to="
              localePath({
                name: 'communities-community',
                params: { community: community.id },
              })
            "
            class="materials__item_community_link"
            @click.native="$event.stopImmediatePropagation()"
          >{{ titleTranslation(community, $i18n.locale) }}</routerLink>
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
import { formatDate } from '../../_helpers'

export default {
  name: 'Material',
  components: {
    StarRating,
  },
  props: {
    material: {
      type: Object,
      default: null,
      required: false,
    },
    index: {
      type: Number,
      default: 0,
    },
    itemsInLine: {
      type: Number,
      default: 4,
    },
    handleMaterialClick: {
      type: Function,
      params: 1,
      default: () => { },
    },
  },
  computed: {
    hasPart() {
      return this.material.has_parts.length > 0
    },
    formattedPublishedAt() {
      return formatDate(this.material.published_at, this.$i18n.locale)
    },
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
    },
  },
}
</script>

<style lang="less" scoped>
@import "./../../../variables";
.materials {
  &__items {
    padding: 0;
    list-style: none;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(275px, 1fr));
    grid-gap: 1rem;

    &.list {
      grid-template-columns: repeat(auto-fit, minmax(100%, 1fr));
      .materials__item_main_info {
        flex: 1;
        padding: 10px 20px 20px;
      }

      .materials__item_subinfo {
        padding: 10px 20px 20px;
        width: 230px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
      }
    }

    &.tile {
      .materials__item_content {
        flex-direction: column;
        justify-content: space-between;
      }
    }
  }
  &__description {
    font-size: 20px;
    line-height: 1.15;
    margin: 1px 0 76px;
  }

  &__item {
    list-style: none;
    background-color: #fff;
    font-size: 16px;
    line-height: 1.44;

    &_set-wrapper {
      padding: 10px 0 0 20px;
    }

    &_set {
      display: inline-flex;
      background-color: @light-grey;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 14px;
      align-items: center;

      &:before {
        content: "";
        display: inline-flex;
        vertical-align: middle;
        width: 13px;
        height: 13px;
        margin-right: 6px;
        background: url("../../../assets/images/icon-set.svg") 50% 50% no-repeat;
        background-size: contain;
      }
    }

    &_set_count {
      display: flex;
      margin-top: 10px;
      align-items: center;
      font-size: 14px;

      &:before {
        content: "";
        display: inline-flex;
        vertical-align: middle;
        width: 13px;
        height: 13px;
        margin-right: 6px;
        background: url("../../../assets/images/icon-materials.svg") 50% 50% no-repeat;
        background-size: contain;
      }
    }

    &.select-delete {
      cursor: pointer;
    }

    &_wrapper {
      display: flex;
      flex-direction: column;
      cursor: pointer;
    }

    &_content {
      flex: 1;
      display: flex;
    }

    &_main_info {
      padding: 10px 20px;
    }

    &_date {
      margin-top: 10px;
    }

    &_subinfo {
      padding: 0 20px 20px 20px;
    }

    &_footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 20px;
      background: @light-grey;
    }

    &_title {
      line-height: 1.2;
    }

    &_link {
      color: @dark-grey;
      text-decoration: none;

      &:hover {
        text-decoration: none;
      }
    }

    &_community_link {
      font-weight: bold;
      text-decoration: none;
      font-family: @second-font;
      position: relative;
      z-index: 1;

      &:hover {
        color: @black;
      }
    }

    &_author {
      font-weight: bold;

      .materials__item--items-in-line-1 & {
        font-weight: bold;
        display: inline-block;
      }
    }

    &_applauds {
      background: @green url("../../../assets/images/clap_white.svg") 2px 50% no-repeat;
      background-size: 20px 20px;
      height: 25px;
      border-radius: 4px;
      color: #fff;
      font-size: 16px;
      font-weight: bold;
      min-width: 58px;
      padding-left: 23px;
      font-size: 1.1em;
    }

    &_external_link {
      background: @yellow url("../../../assets/images/open-link-black.svg") 50% 50% no-repeat;
      background-size: 20px 20px;
      margin: 0 0 0 7px;
      display: inline-block;
      width: 35px;
      height: 25px;
      border-radius: 4px;
      overflow: hidden;
      color: transparent;
      position: relative;
      z-index: 1;

      &:hover {
        background-color: @orange-hover;
      }
    }

    &_copyrights {
      &.cc-by,
      &.cc-by-30,
      &.cc-by-40 {
        background: url("../../../assets/images/cc-black.svg") no-repeat 0 0,
          url("../../../assets/images/by-black.svg") no-repeat 23px 0;
        background-size: contain;
      }
      &.cc-by-nc,
      &.cc-by-nc-30,
      &.cc-by-nc-40 {
        background: url("../../../assets/images/cc-black.svg") no-repeat 0 0,
          url("../../../assets/images/by-black.svg") no-repeat 23px 0,
          url("../../../assets/images/nc-black.svg") no-repeat 46px 0;
        background-size: contain;
      }
      &.cc-by-nc-sa,
      &.cc-by-nc-sa-30,
      &.cc-by-nc-sa-40 {
        background: url("../../../assets/images/cc-black.svg") no-repeat 0 0,
          url("../../../assets/images/by-black.svg") no-repeat 23px 0,
          url("../../../assets/images/nc-black.svg") no-repeat 46px 0,
          url("../../../assets/images/sa-black.svg") no-repeat 69px 0;
        background-size: contain;
      }
      &.cc-by-nd,
      &.cc-by-nd-30,
      &.cc-by-nd-40 {
        background: url("../../../assets/images/cc-black.svg") no-repeat 0 0,
          url("../../../assets/images/by-black.svg") no-repeat 23px 0,
          url("../../../assets/images/nd-black.svg") no-repeat 46px 0;
        background-size: contain;
      }
      &.cc-by-sa,
      &.cc-by-sa-30,
      &.cc-by-sa-40 {
        background: url("../../../assets/images/cc-black.svg") no-repeat 0 0,
          url("../../../assets/images/by-black.svg") no-repeat 23px 0,
          url("../../../assets/images/sa-black.svg") no-repeat 46px 0;
        background-size: contain;
      }
      &.yes,
      &.cc-by-nc-nd,
      &.cc-by-nc-nd-30,
      &.cc-by-nc-nd-40 {
        background: url("../../../assets/images/cc-black.svg") no-repeat 0 0,
          url("../../../assets/images/by-black.svg") no-repeat 23px 0,
          url("../../../assets/images/nc-black.svg") no-repeat 46px 0,
          url("../../../assets/images/nd-black.svg") no-repeat 69px 0;
        background-size: contain;
      }
      height: 20px;
      margin: 6px 0px 3px;
      width: 100%;
      display: block;
      background-size: contain;
    }

    &_actions {
      display: flex;
      align-items: center;
    }

    &_description {
      padding: 16px 0 0;
    }
  }

  &__bookmark {
    width: 24px;
    height: 39px;
    position: absolute;
    right: 17px;
    top: -3px;
    overflow: hidden;
    color: transparent;
    background: url("../../../assets/images/label.svg") 50% 0 no-repeat;
  }
}
</style>
