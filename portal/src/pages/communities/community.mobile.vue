<template>
  <div>

    <header>
      <v-row>
        <v-col class="col-8 community-title">
          <h1>{{ communityData.translation.title }}</h1>
        </v-col>
        <v-col class="col-4">
          <div
            v-if="communityData.translation.featured_image" :src="communityData.translation.featured_image"
            class="community-logo"
            :style="{'background-image': `url(${communityData.translation.featured_image})`}"
          ></div>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <p>{{ communityData.translation.short_description }}</p>
        </v-col>
      </v-row>
      <v-row justify="center">
        <v-col class="community-search-button">
          <button
            v-if="communityData.metadata.publisher"
            class="button"
            data-test="community_search_link"
            @click="onCommunitySearch"
          >
            {{ $t("Show-all-materials", {count: communityData.metadata.materials_count}) }}
          </button>
        </v-col>
      </v-row>
      <v-row>
        <div class="community-website">
          <a v-if="communityData.translation.website_url" :href="communityData.translation.website_url" target="_blank">
            {{ $t("Visit-website") }}&nbsp;
            <v-icon x-small :color="$vuetify.theme.defaults.light.anchor">fa-arrow-up-right-from-square</v-icon>
          </a>
        </div>
      </v-row>
    </header>

    <div class="center_block">
      <h3>{{ $t("collections") }} ({{ communityData.collections.length }})</h3>
      <Collections
        v-if="communityData.collections"
        :collections="communityData.collections"
        class="community__collections"
      >
      </Collections>
      <div v-else>
        {{ $t("No-collections") }}
      </div>
      <h3>{{ $t("About-the-community") }}</h3>
      <div class="community-description" v-html="sanitizedDescription"></div>
      <h3 v-if="communityData.translation.website_url">{{ $t("Contact") }}</h3>
      <div v-if="communityData.translation.website_url" class="community-website">
        <a :href="communityData.translation.website_url" target="_blank">
          {{ $t("Visit-website") }}&nbsp;<v-icon x-small :color="$vuetify.theme.defaults.light.anchor">fa-arrow-up-right-from-square</v-icon>
        </a>
      </div>
    </div>

  </div>
</template>

<script>
import Collections from "~/components/Collections";
import DOMPurify from "dompurify";

export default {
  name: "CommunityMobile",
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
      sanitizedDescription: DOMPurify.sanitize(this.communityData.translation.description),
    };
  }
};
</script>

<style lang="less" scoped>
@import url("../../variables");

header {
  padding: 20px;
  background-color: @lighter-grey;

  .community-logo {
    width: 100px;
    height: 100px;
    float: right;
    background-position: left center;
    background-repeat: no-repeat;
    background-size: contain;
    background-color: @white;
  }

  .community-search-button {
    text-align: center;
  }

}

.community-website {
  width: 100%;
  text-align: center;
  margin: 20px auto 25px;
}

h3 {
  margin-top: 30px;
}

</style>
