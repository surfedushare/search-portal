<template>
  <div
    :class="{ selected: material.selected, stack: hasPart }"
    class="materials__item_wrapper tile__wrapper"
    @click="handleMaterialClick(material)"
  >
    <div class="materials__item_date">{{ formattedPublishedAt || null }}</div>
    <div class="materials__item_content">
      <div class="materials__item_main_info">
        <h3 class="materials__item_title">{{ material.title }}</h3>
        <StarRating
          v-model="material.avg_star_rating"
          :counter="material.count_star_rating"
          :disabled="true"
          :dark-stars="true"
        />
        <div
          class="materials__item_description"
          v-html="hightlightedSearchResult"
        ></div>
      </div>

      <div class="materials__item_subinfo">
        <div
          v-if="material.educationallevels && material.educationallevels.length"
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

        <div v-if="hasPart" class="materials__item_set_count">
          {{ $tc("Materials", material.has_parts.length) }}
        </div>

        <div
          v-if="
            material.technical_type && material.technical_type !== 'unknown'
          "
          :class="`materials__item_format_${material.technical_type}`"
        >
          {{ $t(material.technical_type) }}
        </div>
      </div>
    </div>
    <footer class="materials__item_footer">
      <div v-if="material.authors.length > 0" class="materials__item_author">
        {{ material.authors.join(", ") }}
      </div>
      <div class="materials__item_actions">
        <div class="materials__item_tag">
          <span v-if="hasPart">{{ $t("Set") }}</span>
        </div>
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
        justify-content: space-around;
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
    }

    &_content {
      flex: 1;
      display: flex;
    }

    &_main_info {
      padding: 10px 20px;
    }

    &_date {
      padding: 20px 0 0 20px;
    }

    &_subinfo {
      display: grid;
      font-size: 14px;
      margin: 20px;
      grid-template-columns: auto auto auto;
    }

    &_educationallevel {
      padding-right: 10px;
      &:before {
        content: "";
        display: inline-block;
        vertical-align: middle;
        width: 18px;
        height: 18px;
        background: url("../../../assets/images/edulevel.svg") 50% 50% / contain
          no-repeat;
      }
    }

    &_set_count {
      &:before {
        content: "";
        display: inline-block;
        vertical-align: middle;
        width: 18px;
        height: 18px;
        background: url("../../../assets/images/docs.svg") 50% 50% / contain
          no-repeat;
      }
    }

    &_format {
      &_app {
        &:before {
          content: "";
          display: inline-block;
          vertical-align: middle;
          width: 18px;
          height: 18px;
          background: url("../../../assets/images/app.svg") 50% 50% / contain
            no-repeat;
        }
      }
      &_document {
        &:before {
          content: "";
          display: inline-block;
          vertical-align: middle;
          width: 18px;
          height: 18px;
          background: url("../../../assets/images/doc.svg") 50% 50% / contain
            no-repeat;
        }
      }
      &_audio {
        &:before {
          content: "";
          display: inline-block;
          vertical-align: middle;
          width: 18px;
          height: 18px;
          background: url("../../../assets/images/audio.svg") 50% 50% / contain
            no-repeat;
        }
      }
      &_image {
        &:before {
          content: "";
          display: inline-block;
          vertical-align: middle;
          width: 18px;
          height: 18px;
          background: url("../../../assets/images/image.svg") 50% 50% / contain
            no-repeat;
        }
      }
      &_openaccess-textbook {
        &:before {
          content: "";
          display: inline-block;
          vertical-align: middle;
          width: 18px;
          height: 18px;
          background: url("../../../assets/images/open-text-book.svg") 50% 50% /
            contain no-repeat;
        }
      }
      &_presentation {
        &:before {
          content: "";
          display: inline-block;
          vertical-align: middle;
          width: 18px;
          height: 18px;
          background: url("../../../assets/images/presentation.svg") 50% 50% /
            contain no-repeat;
        }
      }
      &_spreadsheet {
        &:before {
          content: "";
          display: inline-block;
          vertical-align: middle;
          width: 18px;
          height: 18px;
          background: url("../../../assets/images/spreadsheet.png") 50% 50% /
            contain no-repeat;
        }
      }
      &_website {
        &:before {
          content: "";
          display: inline-block;
          vertical-align: middle;
          width: 18px;
          height: 18px;
          background: url("../../../assets/images/website.svg") 50% 50% /
            contain no-repeat;
        }
      }
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

    &_author {
      width: 100%;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    &_tag {
      background: @green;
      border-radius: 4px;
      color: #fff;
      font-size: 1.1em;
      padding: 0 10px;
    }

    &_actions {
      display: flex;
      align-items: center;
      min-width: fit-content;
    }

    &_description {
      padding: 16px 0 0;
      /deep/ em {
        background-color: yellow;
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
