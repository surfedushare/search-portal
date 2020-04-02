import _ from 'lodash';
import Spinner from './../Spinner';

export default {
  name: 'collections',
  props: {
    collections: {
      default: false
    },
    'items-in-line': {
      type: Number,
      default: 4
    },
    loading: {
      type: Boolean,
      default: false
    },
    editableContent: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      selection: []
    }
  },
  components: { Spinner },
  methods: {
    getCommunityDetail(community, language, detail) {
      let communityDetails = _.find(community.community_details, {language_code: language.toUpperCase()});
      return communityDetails[detail] || null
    },
    selectCollection(collection) {
      collection.selected = !collection.selected;
      if (this.selection.indexOf(collection.id) === -1) {
        this.selection.push(collection.id);
      } else {
        this.selection = this.selection.filter(
          item => item !== collection.id
        );
      }
      this.$emit('input', this.selection);
      this.$forceUpdate();
    }
  }
};
