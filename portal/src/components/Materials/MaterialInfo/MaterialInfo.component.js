import { generateSearchMaterialsQuery, validateHREF } from "./../../_helpers";

import CollectionList from "../CollectionList/CollectionList";
import EnlargeableImage from "@diracleo/vue-enlargeable-image";
import Keywords from "~/components/Keywords";
import MaterialPartOfSet from "../MaterialSet/MaterialPartOfSet";
import MaterialSet from "../MaterialSet/MaterialSet";
import PopularList from "~/components/Communities/PopularList";
import { PublishStatus } from "~/utils";
import SaveRating from "~/components/Popup/SaveRating";
import StarRating from "~/components/StarRating";
import { isNil } from "lodash";
import { mapGetters } from "vuex";
import numeral from "numeral";

export default {
  name: "material-info",
  props: ["material", "communities", "collections"],
  components: {
    StarRating,
    PopularList,
    Keywords,
    SaveRating,
    MaterialSet,
    MaterialPartOfSet,
    CollectionList,
    EnlargeableImage,
  },
  mounted() {
    this.href = validateHREF(window.location.href);
    this.fetchSetMaterials();
  },
  data() {
    return {
      href: "",
      shared_link: false,
      isShow: false,
      is_loading_applaud: false,
      is_applauded: false,
      rating: false,
      rating_given: this.isMaterialRated(this.material.external_id),
      is_copied: false,
      setMaterials: [],
      formData: {
        page_size: 10,
        page: 1,
        filters: [],
        search_text: "",
      },
    };
  },
  methods: {
    fetchSetMaterials() {
      if (this.material.has_parts.length > 0) {
        this.$store
          .dispatch("getSetMaterials", {
            external_id: this.material.external_id,
          })
          .then((res) => (this.setMaterials = res.records));
      }
    },
    authorUrl(author) {
      if (this.material) {
        return this.generateSearchMaterialsQuery({
          ...this.formData,
          filters: {
            "authors.name.keyword": [author],
          },
        });
      }
    },
    publisherUrl(publisher) {
      if (this.material) {
        return this.generateSearchMaterialsQuery({
          ...this.formData,
          filters: {
            "publishers.keyword": [publisher],
          },
        });
      }
    },
    consortiumUrl(consortium) {
      if (this.material) {
        return this.generateSearchMaterialsQuery({
          ...this.formData,
          filters: {
            consortium: [consortium],
          },
        });
      }
    },
    generateSearchMaterialsQuery,
    /**
     * Show the popup "Save rating"
     */
    showPopupSaveRating() {
      this.isShow = true;
    },
    /**
     * Close the popup "Save rating"
     */
    closePopupSaveRating() {
      this.isShow = false;
    },
    /**
     * Check in sessionStorage if material has been rated by the current user"
     * @param external_id of material - String
     */
    isMaterialRated(materialId) {
      const ratings = sessionStorage.getItem("ratedMaterials");
      const parsedRatings = ratings !== null ? JSON.parse(ratings) : [];
      return parsedRatings.includes(materialId);
    },
    /**
     * Saving the applaud for material
     * @param material - Object
     */
    setApplaudMaterial(material) {
      this.is_loading_applaud = true;
      this.$store
        .dispatch("setApplaudMaterial", {
          external_id: material.external_id,
        })
        .then(() => {
          this.is_applauded = true;
          this.$store.dispatch("getMaterial", { id: this.$route.params.id }).then(() => {
            this.is_loading_applaud = false;
          });
        });
    },
  },
  computed: {
    ...mapGetters(["isAuthenticated"]),
    /**
     * Get formatted 'number_of_views'
     * @returns String
     */
    viewCount() {
      return numeral(this.material.view_count).format("0a");
    },
    publishedCollections() {
      return this.collections.filter((collection) => collection.publish_status === PublishStatus.PUBLISHED);
    },
  },
  watch: {
    /**
     * If the material changes, it is checked if the material has been rated
     */
    material: function () {
      const { material } = this;
      if (!isNil(material)) {
        this.rating_given = this.isMaterialRated(material.external_id);
      }
    },
  },
};
