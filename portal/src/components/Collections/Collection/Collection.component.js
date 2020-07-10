import _ from 'lodash'
import EditableContent from '~/components/EditableContent'
import ShareCollection from '~/components/Popup/ShareCollection'
import DeleteCollection from '~/components/Popup/DeleteCollection'
import { validateHREF } from '~/components/_helpers'
import SwitchInput from '~/components/switch-input'
import { PublishStatus } from '~/utils'

export default {
  name: 'collection',
  props: {
    collection: {
      default: {}
    },
    contentEditable: {
      default: false
    },
    setEditable: {
      default: false
    },
    submitting: {
      default: false
    },
    changeViewType: {
      default: false
    },
    'items-in-line': {
      default: 4
    }
  },
  components: {
    EditableContent,
    ShareCollection,
    DeleteCollection,
    SwitchInput
  },
  mounted() {
    const { collection } = this
    if (!_.isEmpty(collection)) {
      const title = this.$i18n.locale === 'nl' ? collection.title_nl : collection.title_en
      this.setCollectionTitle(title)
      this.setSocialCounters()
    }
    this.href = validateHREF(window.location.href)
  },
  data() {
    return {
      href: '',
      collectionTitle: null,
      search: {},
      isShowDeleteCollection: false,
      isShowShareCollection: false,
      isCopied: false
    }
  },
  computed: {
    isPublished: {
      get() {
        return this.collection.publish_status === PublishStatus.PUBLISHED
      },
      set(value) {
        this.collection.publish_status = value
          ? PublishStatus.PUBLISHED
          : PublishStatus.DRAFT
      }
    }
  },
  methods: {
    setCollectionTitle(title) {
      if (title) {
        this.collectionTitle = title
      }
    },
    /**
     * Trigger on the change collection title
     */
    onChangeTitle() {
      if (this.$refs.title) {
        this.setCollectionTitle(this.$refs.title.innerText)
      }
    },
    /**
     * Reset changed data
     */
    resetData() {
      const title = this.$i18n.locale === 'nl' ? collection.title_nl : collection.title_en
      this.setCollectionTitle(title)
    },
    /**
     * Deleting collection by id
     */
    deleteCollectionPopup() {
      this.isShowDeleteCollection = true
    },
    /**
     * Deleting collection by id
     */
    deleteCollection() {
      this.$store
        .dispatch('deleteMyCollection', this.collection.id)
        .then(() => {
          if (window.history.length > 1) {
            this.$router.go(-1)
          } else {
            this.$router.push(this.localePath({ name: 'my-communities' }))
          }
        })
    },
    closeDeleteCollection() {
      this.isShowDeleteCollection = false
    },
    /**
     * Saving the collection
     */
    onSubmit() {
      this.$emit('onSubmit', { title: this.collectionTitle })
    },
    /**
     * Set counters value for share buttons
     */
    setSocialCounters() {
      const interval = setInterval(() => {
        this.$nextTick().then(() => {
          const { collection } = this
          const { social_counters } = this.$refs
          const linkedIn = social_counters.querySelector('#linkedin_counter')

          if (
            collection &&
            collection.sharing_counters &&
            social_counters &&
            linkedIn
          ) {
            const share = collection.sharing_counters.reduce(
              (prev, next) => {
                prev[next.sharing_type] = next
                return prev
              },
              {
                linkedin: {
                  counter_value: 0
                },
                twitter: {
                  counter_value: 0
                },
                link: {
                  counter_value: 0
                }
              }
            )

            if (share.linkedin) {
              social_counters.querySelector('#linkedin_counter').innerText =
                share.linkedin.counter_value
            }
            if (share.twitter) {
              social_counters.querySelector('#twitter_counter').innerText =
                share.twitter.counter_value
            }
            if (share.link) {
              social_counters.querySelector('#url_counter').innerText =
                share.link.counter_value
            }
            if (linkedIn) {
              clearInterval(interval)
            }
          }
        })
      }, 200)
    },
    /**
     * Event close social popups
     * @param type - String - social type
     */
    closeSocialSharing(type) {
      this.$store
        .dispatch('setCollectionSocial', {
          id: this.$route.params.id,
          params: {
            shared: type
          }
        })
        .then(() => {
          this.setSocialCounters()
        })
    },
    /**
     * Show the popup "Share collection"
     */
    showShareCollection() {
      this.isShowShareCollection = true
    },
    /**
     * Close the popup "Share collection"
     */
    closeShareCollection() {
      this.isShowShareCollection = false
      if (this.isCopied) {
        this.closeSocialSharing('link')
      }
    }
  },
  watch: {
    /**
     * Watcher on the search field
     * @param search - String
     */
    search(search) {
      this.$emit('input', search)
    },
    /**
     * Watcher on the contentEditable field
     * @param isEditable - Boolean
     */
    contentEditable(isEditable) {
      if (!isEditable) {
        this.resetData()
      }
    },
    /**
     * Watcher on the collection object
     * @param collection - Object
     */
    collection(collection) {
      if (!_.isEmpty(collection)) {
        const title = this.$i18n.locale === 'nl' ? collection.title_nl : collection.title_en
        this.setCollectionTitle(title)
        this.setSocialCounters()
      }
    }
  }
}
