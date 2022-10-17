<template>
  <section class="edusources-container main">
    <div v-if="!communityData.translation && isReady">
      <error status-code="404" message-key="community-not-found" />
    </div>
    <CommunityDesktop
      v-else-if="communityData.translation && !$vuetify.breakpoint.mobile"
      :community-data="communityData"
      :on-community-search="goToCommunitySearch"
    />
    <CommunityMobile
      v-else-if="communityData.translation && $vuetify.breakpoint.mobile"
      :community-data="communityData"
      :on-community-search="goToCommunitySearch"
    />
  </section>
</template>

<script>
import { mapGetters } from "vuex";
import Error from "~/components/error";
import { CONSORTIUM_CATEGORY_FILTER_FIELD } from "~/constants";
import { generateSearchMaterialsQuery } from "@/components/_helpers";
import PageMixin from "~/pages/page-mixin";
import CommunityDesktop from "@/pages/communities/community.desktop";
import CommunityMobile from "@/pages/communities/community.mobile";

export default {
  name: "Community",
  components: {
    Error,
    CommunityDesktop,
    CommunityMobile,
  },
  mixins: [PageMixin],
  computed: {
    ...mapGetters(["user"]),
    communityData() {
      return {
        collections: this.$store.getters.getPublicCollections(this.user),
        metadata: this.$store.getters.getCommunityInfo(this.user) || null,
        translation: this.$store.getters.getCommunityTranslation(this.user, this.$i18n.locale),
      };
    },
  },
  created() {
    const { community } = this.$route.params;
    this.pageLoad = this.$store.dispatch("getCommunity", community);
    this.$store.dispatch("getCommunityCollections", community);
  },
  metaInfo() {
    const defaultTitle = this.$root.$meta().title;
    return {
      title: this.communityData.translation ? this.communityData.translation.title || defaultTitle : defaultTitle,
    };
  },
  methods: {
    goToCommunitySearch() {
      const searchData = {
        search_text: "",
        filters: { [CONSORTIUM_CATEGORY_FILTER_FIELD]: [this.community_info.publisher] },
        page_size: 10,
        page: 1,
      };
      const searchRoute = generateSearchMaterialsQuery(searchData, "materials-search");
      this.$router.push(searchRoute);
    },
  },
};
</script>
