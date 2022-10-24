<template>
  <div>
    <header>
      <div class="center_block">
        <v-row class="header-content" no-gutters>
          <v-col v-if="communityData.translation.featured_image" class="col-2">
            <div class="community-logo" :style="{'background-image': `url(${communityData.translation.featured_image})`}"></div>
          </v-col>
          <v-col :class="(communityData.translation.featured_image) ? 'col-7' : 'col-9'" class="community-title">
            <h1>{{ communityData.translation.title }}</h1>
            <p v-html="sanitizedShortDescription"></p>
          </v-col>
          <v-col class="col-3">
            <button
              v-if="communityData.metadata.publisher"
              class="button community-search"
              data-test="community_search_link"
              @click="onCommunitySearch"
            >
              {{ $t("Show-all-materials", {count: communityData.metadata.materials_count}) }}
            </button>
          </v-col>
        </v-row>
        <v-row class="header-tabs">
          <v-tabs v-model="tabIndex" :color="$vuetify.theme.defaults.light.accent">
            <v-tab>{{ $t("collections") }} ({{ communityData.collections.length }})</v-tab>
            <v-tab>{{ $t("About-this-community") }}</v-tab>
          </v-tabs>
        </v-row>
      </div>
    </header>

    <div class="center_block">
      <v-row no-gutters>
        <v-col class="col-10">
          <v-tabs-items v-model="tabIndex">
            <v-tab-item>
              <Collections
                v-if="communityData.collections"
                :collections="communityData.collections"
                class="community__collections"
              >
              </Collections>
              <div v-else>
                {{ $t("No-collections") }}
              </div>
            </v-tab-item>
            <v-tab-item>
              <div class="community-description" v-html="sanitizedDescription"></div>
            </v-tab-item>
          </v-tabs-items>
        </v-col>
        <v-col class="col-2">
          <div class="community-info">
            <a v-if="communityData.translation.website_url" :href="communityData.translation.website_url" target="_blank">
              {{ $t("Visit-website") }}&nbsp;<v-icon x-small :color="$vuetify.theme.defaults.light.anchor">fa-arrow-up-right-from-square</v-icon>
            </a>
          </div>
        </v-col>
      </v-row>
    </div>

  </div>
</template>

<script>
import Collections from "~/components/Collections";
import DOMPurify from "dompurify";

export default {
  name: "CommunityDesktop",
  components: {
    Collections,
  },
  props: {
    communityData: {
      type: Object,
      default: () => ({}),
    },
    onCommunitySearch: {
      type: Function,
      default: () => {},
    },
  },
  data() {
    return {
      tabIndex: null,
      sanitizedDescription: DOMPurify.sanitize(this.communityData.translation.description),
      sanitizedShortDescription: DOMPurify.sanitize(this.communityData.translation.short_description)
    };
  },
};
</script>

<style lang="less" scoped>
@import url("../../variables");

@header-height: 140px;

header {
  height: 250px;
  background-color: @lighter-grey;
  padding-top: 32px;

  .header-content {
    height: @header-height;
  }

  .community-logo {
    width: @header-height;
    height: @header-height;
    background-position: left center;
    background-repeat: no-repeat;
    background-size: contain;
    background-color: @white;
  }

  .community-title h1 {
    margin: 0;
  }

  .header-tabs {
    margin-top: 30px;
  }

  .community-search.button {
    float: right;
  }
}

.community-description {
  padding: 20px;
}

.community-info {
  padding: 20px;
}

</style>
