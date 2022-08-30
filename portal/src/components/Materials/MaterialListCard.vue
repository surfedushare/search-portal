<template>
  <v-card :ripple="false" :class="{ stack: hasPart }" @click="handleMaterialClick(material)">
    <v-row>
      <v-col class="mx-auto" md="9" sm="8">
        <v-card-text v-if="material.published_at" class="pb-0 date">{{ formattedPublishedAt }}</v-card-text>
        <v-card-title class="pt-4 mt-0 truncate2">{{ material.title }}</v-card-title>
        <v-card-text>
          <v-row align="center" class="mx-0">
            <StarRating
              v-model="material.avg_star_rating"
              :counter="material.count_star_rating"
              :disabled="true"
              :dark-stars="true"
            />
          </v-row>
          <v-row>
            <div class="mt-4 pl-4 description truncate3" v-html="hightlightedSearchResult"></div>
          </v-row>
        </v-card-text>
      </v-col>
      <v-col class="mt-14 pl-6" lg="3" md="3" sm="4">
        <v-container>
          <v-row
            v-if="material.lom_educational_levels && material.lom_educational_levels.length"
            class="educationallevels mt-0 mb-4"
          >
            <span v-for="(educationalLevel, i) in material.lom_educational_levels" :key="i" class="educationallevel">
              {{ punctuate(educationalLevel[$i18n.locale], i, material.lom_educational_levels.length) }}
            </span>
          </v-row>
          <v-row v-if="hasPart" class="set_count mb-4">
            {{ $tc("Materials", material.has_parts.length) }}
          </v-row>
          <v-row
            v-if="material.technical_type && material.technical_type !== 'unknown'"
            :class="`mt-4 format_kind format_${material.technical_type}`"
          >
            {{ $t(material.technical_type) }}
          </v-row>
        </v-container>
      </v-col>
    </v-row>
    <v-card-actions v-if="hasAuthors || hasPart">
      <v-chip v-if="hasPart">
        <span>{{ $t("Set") }}</span>
      </v-chip>
      <div v-if="hasAuthors" class="author">
        {{ material.authors.join(", ") }}
      </div>
    </v-card-actions>
  </v-card>
</template>

<script>
import StarRating from "../StarRating/index.vue";
import { formatDate } from "../_helpers";
import DOMPurify from "dompurify";

export default {
  name: "MaterialListCard",
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
    hasAuthors() {
      return this.material.authors.length > 0;
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
@import "./../../variables";
.v-card:hover .v-card__title {
  color: @green-hover-dark;
}
.v-card {
  border-radius: 12px;
  &__title {
    color: @green;
    font-weight: 700;
  }
}
&.stack {
  background: transparent url("../../assets/images/card-flip.svg") 100.2% -2px no-repeat;
}
.truncate2 {
  height: 64px;
  line-height: 24px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  margin: 0 0 1em 0;
  overflow: hidden;
  word-break: break-word;
}
.truncate3 {
  line-height: 24px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  margin: 0 0 1em 0;
  overflow: hidden;
}
.description {
  line-height: 22px;
  color: @black;
  /deep/ em {
    background-color: @yellow;
    font-style: normal;
  }
}
.v-card__actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background: @light-grey;
  flex-direction: row-reverse;
  height: 48px;
}
.author {
  width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  &_none {
    color: @dark-grey;
  }
}
.date {
  color: @dark-grey;
  font-weight: 700;
}
.v-chip {
  background: @green !important;
  color: #fff !important;
  min-width: fit-content !important;
  height: 30px !important;
}
.set_count {
  font-size: 16px;
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: 0.4em;
  &:before {
    content: "";
    height: 22px;
    width: 22px;
    background: url("../../assets/images/docs.svg") 0px 0px / contain no-repeat;
  }
}

.educationallevels {
  font-size: 16px;
  display: flex;
  flex-wrap: nowrap;
  align-items: flex-end;
  gap: 0.4em;
  margin-left: -14px;
  &:before {
    content: "";
    height: 28px;
    width: 28px;
    background: url("../../assets/images/edulevel.svg") 0px 0px / contain no-repeat;
  }
}
.format {
  &_kind {
    font-size: 16px;
    display: flex;
    flex-wrap: nowrap;
    align-items: center;
    gap: 0.4em;
    &:before {
      content: "";
      height: 24px;
      width: 24px;
    }
  }
  &_app {
    &:before {
      background: url("../../assets/images/app.svg") 0px 0px / contain no-repeat;
    }
  }
  &_document {
    &:before {
      background: url("../../assets/images/doc.svg") 0px 0px / contain no-repeat;
    }
  }
  &_audio {
    &:before {
      background: url("../../assets/images/audio.svg") 0px 0px / contain no-repeat;
    }
  }
  &_video {
    &:before {
      background: url("../../assets/images/video.svg") 2px 0px / contain no-repeat;
    }
  }
  &_image {
    &:before {
      background: url("../../assets/images/image.svg") 0px 0px / contain no-repeat;
    }
  }
  &_openaccess-textbook {
    &:before {
      background: url("../../assets/images/open-text-book.svg") 0px 0px / contain no-repeat;
    }
  }
  &_presentation {
    &:before {
      background: url("../../assets/images/presentation.svg") 0px 0px / contain no-repeat;
    }
  }
  &_spreadsheet {
    &:before {
      background: url("../../assets/images/spreadsheet.png") 0px 0px / contain no-repeat;
    }
  }
  &_website {
    &:before {
      background: url("../../assets/images/website.svg") 0px 0px / contain no-repeat;
    }
  }
}
</style>
