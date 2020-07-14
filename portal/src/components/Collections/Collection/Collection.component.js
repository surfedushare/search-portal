import ShareCollection from '~/components/Popup/ShareCollection'
import DeleteCollection from '~/components/Popup/DeleteCollection'
import { validateHREF } from '~/components/_helpers'
import SwitchInput from '~/components/switch-input'
import InputWithCounter from '~/components/InputWithCounter'
import { PublishStatus } from '~/utils'

export default {
  name: 'collection',
  props: {
    collection: {
      default: {}
    },
    contenteditable: {
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
    ShareCollection,
    DeleteCollection,
    SwitchInput,
    InputWithCounter
  },
  mounted() {
    if (this.collection) {
      this.resetData()
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
    resetData() {
      const { collection } = this
      this.collectionTitle =
        this.$i18n.locale === 'nl' ? collection.title_nl : collection.title_en
    },
    deleteCollectionPopup() {
      this.isShowDeleteCollection = true
    },
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
    onSubmit() {
      if (this.$i18n.locale === 'nl') {
        this.$emit('onSubmit', { title_nl: this.collectionTitle })
      } else {
        this.$emit('onSubmit', { title_en: this.collectionTitle })
      }
    },
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
    showShareCollection() {
      this.isShowShareCollection = true
    },
    closeShareCollection() {
      this.isShowShareCollection = false
      if (this.isCopied) {
        this.closeSocialSharing('link')
      }
    }
  },
  watch: {
    search(search) {
      this.$emit('input', search)
    },
    contenteditable(isEditable) {
      if (!isEditable) {
        this.resetData()
      }
    },
    collection(collection) {
      if (collection) {
        this.resetData()
        this.setSocialCounters()
      }
    },
    '$i18n.locale': function() {
      this.resetData()
    }
  }
}
