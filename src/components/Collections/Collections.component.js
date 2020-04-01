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
  components: { Spinner },
  methods: {
    getCommunityDetail(community, language, detail) {
      let communityDetails = _.find(community.community_details, {language_code: language.toUpperCase()});
      return communityDetails[detail] || null
    }
  }
};
