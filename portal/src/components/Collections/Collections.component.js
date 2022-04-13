import CollectionCard from "./CollectionCard/CollectionCard";
import Spinner from "./../Spinner";

export default {
  name: "collections",
  components: { Spinner, CollectionCard },
  props: {
    collections: {
      default: false,
    },
    "items-in-line": {
      type: Number,
      default: 4,
    },
    loading: {
      type: Boolean,
      default: false,
    },
  },
};
