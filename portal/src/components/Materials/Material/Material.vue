<template>
  <div
    :class="{ selected: material.selected, stack: hasPart }"
    class="materials__item_wrapper tile__wrapper"
    @click="handleMaterialClick(material)"
  >
    <div class="materials__item_date">{{ formattedPublishedAt }}</div>
    <div class="materials__item_content">
      <div class="materials__item_main_info">
        <h3 class="materials__item_title" :class="{ truncate2: itemsInLine > 1 }">
          {{ material.title }}
        </h3>
        <StarRating
          v-model="material.avg_star_rating"
          :counter="material.count_star_rating"
          :disabled="true"
          :dark-stars="true"
        />
        <div class="materials__item_description truncate3" v-html="hightlightedSearchResult"></div>
      </div>

      <div class="materials__item_subinfo">
        <div class="materials__item_subinfo_row">
          <div
            v-if="material.educationallevels && material.educationallevels.length"
            class="materials__item_educationallevels"
          >
            <span
              v-for="(educationallevel, i) in material.educationallevels.slice(0, 2)"
              :key="i"
              class="materials__item_educationallevel"
            >
              {{ punctuate(educationallevel[$i18n.locale], i, material.educationallevels.length) }}
            </span>
          </div>

          <div v-if="hasPart" class="materials__item_set_count">
            {{ $tc("Materials", material.has_parts.length) }}
          </div>

          <div
            v-if="material.technical_type && material.technical_type !== 'unknown'"
            :class="`materials__item_format_kind materials__item_format_${material.technical_type}`"
          >
            {{ $t(material.technical_type) }}
          </div>
        </div>
      </div>
    </div>
    <footer class="materials__item_footer">
      <div class="materials__item_actions">
        <div v-if="hasPart" class="materials__item_tag">{{ $t("Set") }}</div>
      </div>
      <div v-if="material.authors.length > 0" class="materials__item_author">
        {{ material.authors.join(", ") }}
      </div>
      <div v-else class="materials__item_author_none">
        {{ $t("Authors-Unknown") }}
      </div>
    </footer>
  </div>
</template>

<script>
import StarRating from "../../StarRating/index";
import { formatDate } from "../../_helpers";
import DOMPurify from "dompurify";

export default {
  name: "Material",
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
      default: () => {},
    },
  },
  computed: {
    hasPart() {
      return this.material.has_parts.length > 0;
    },
    formattedPublishedAt() {
      return formatDate(this.material.published_at, this.$i18n.locale);
    },
    hightlightedSearchResult() {
      const description = this.material.highlight?.description
        ? this.material.highlight?.description[0]
        : this.material.highlight?.text
        ? this.material.highlight?.text[0]
        : this.material.description;
      return DOMPurify.sanitize(description);
    },
  },
  methods: {
    punctuate(word, index, len) {
      let punctuated = word;
      if (len > 1 && index < len - 1) {
        punctuated = punctuated + ", ";
      }
      if (index === 1 && len >= 3) {
        punctuated = punctuated + "...";
      }
      return punctuated;
    },
  },
};
</script>

<style lang="less" scoped>
@import "./../../../variables";
li:hover h3 {
  color: @green;
}
.truncate2 {
  height: 50px;
  line-height: 24px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  margin: 0 0 1em 0;
  overflow: hidden;
}
.truncate3 {
  line-height: 26px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  margin: 0 0 1em 0;
  overflow: hidden;
}

.materials {
  &__items {
    padding: 0;
    list-style: none;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(275px, 1fr));

    &.list {
      .materials__item_main_info {
        padding: 10px 20px 20px;
      }

      .materials__item_subinfo {
        display: grid;
        align-content: space-between;
        &_row {
          display: grid;
          grid-gap: 16px;
        }
      }
    }

    &.tile {
      .materials__item_content {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        &:hover {
          &.title {
            color: @green;
          }
        }
      }
    }
  }
  &__description {
    font-size: 20px;
    line-height: 1.15;
    margin: 1px 0 76px;
  }

  &__item {
    &_set {
      font-size: 14px;
      font-weight: 600;
    }

    &.select-delete {
      cursor: pointer;
    }

    &_wrapper {
      display: flex;
      flex-direction: column;
      cursor: pointer;
      height: auto;
    }

    &_content {
      grid-template-columns: 78% auto;
      display: grid;
    }

    &_main_info {
      padding: 10px 20px;
    }

    &_date {
      padding: 20px 0 0 20px;
      min-height: 48px;
    }

    &_subinfo {
      &_row {
        display: inline-flex;
        grid-gap: 8px;
        padding: 10px 10px 10px 20px;
      }
    }

    &_educationallevels {
      font-size: 16px;
      display: flex;
      flex-wrap: nowrap;
      align-items: center;
      gap: 0.4em;
      &:before {
        content: "";
        height: 18px;
        width: 18px;
        background: url("../../../assets/images/edulevel.svg") 0px 0px / contain no-repeat;
      }
    }

    &_set_count {
      font-size: 16px;
      display: flex;
      flex-wrap: nowrap;
      align-items: center;
      gap: 0.4em;
      &:before {
        content: "";
        height: 16px;
        width: 16px;
        background: url("../../../assets/images/docs.svg") 0px 0px / contain no-repeat;
      }
    }

    &_format {
      &_kind {
        font-size: 16px;
        display: flex;
        flex-wrap: nowrap;
        align-items: center;
        gap: 0.4em;
        &:before {
          content: "";
          height: 16px;
          width: 16px;
        }
      }
      &_app {
        &:before {
          background: url("../../../assets/images/app.svg") 0px 0px / contain no-repeat;
        }
      }
      &_document {
        &:before {
          background: url("../../../assets/images/doc.svg") 0px 0px / contain no-repeat;
        }
      }
      &_audio {
        &:before {
          background: url("../../../assets/images/audio.svg") 0px 0px / contain no-repeat;
        }
      }
      &_video {
        &:before {
          background: url("../../../assets/images/video.svg") 2px 0px / contain no-repeat;
        }
      }
      &_image {
        &:before {
          background: url("../../../assets/images/image.svg") 0px 0px / contain no-repeat;
        }
      }
      &_openaccess-textbook {
        &:before {
          background: url("../../../assets/images/open-text-book.svg") 0px 0px / contain no-repeat;
        }
      }
      &_presentation {
        &:before {
          background: url("../../../assets/images/presentation.svg") 0px 0px / contain no-repeat;
        }
      }
      &_spreadsheet {
        &:before {
          background: url("../../../assets/images/spreadsheet.png") 0px 0px / contain no-repeat;
        }
      }
      &_website {
        &:before {
          background: url("../../../assets/images/website.svg") 0px 0px / contain no-repeat;
        }
      }
    }

    &_footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 20px;
      background: @light-grey;
      flex-direction: row-reverse;
      height: 48px;
    }

    &_title {
      max-width: 100%;
      margin: 0 auto;
    }

    &_link {
      color: @dark-grey;
      text-decoration: none;

      &:hover {
        text-decoration: none;
      }
    }

    &_author {
      width: 100%;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      &_none {
        color: @dark-grey;
      }
    }

    &_tag {
      background: @green;
      border-radius: 8px;
      color: #fff;
      font-size: 14px;
      padding: 5px 10px;
      height: 30px;
    }

    &_actions {
      display: flex;
      align-items: center;
      min-width: fit-content;
    }

    &_description {
      padding: 16px 0 0;
      min-height: 96px;
      /deep/ em {
        background-color: @yellow;
        font-style: normal;
      }
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
