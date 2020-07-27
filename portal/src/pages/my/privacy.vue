<template>
  <section class="container main privacy">
    <HeaderBlock :title="$t('My-privacy')" />
    <div class="center_block">
      <div class="content">
        <div v-if="permissions.length" class="left-column">
          <div class="privacy__form">
            <form
              action="/"
              class="privacy__form_in"
              novalidate
              @submit.prevent="onSubmit"
            >
              <div class="privacy__form__column">
                <div
                  v-for="permission in permissions"
                  :key="permission.type"
                  class="privacy__form__row"
                >
                  <p class="privacy__form__label">
                    {{ permission[$i18n.locale].title }}
                  </p>
                  <div class="permission-container">
                    <div class="switch-container">
                      <switch-input
                        v-if="!permission.is_notification_only"
                        v-model="permission.is_allowed"
                      />
                    </div>
                    <div
                      class="description"
                      :class="{
                        'notification-only': permission.is_notification_only
                      }"
                    >
                      <p>
                        {{ permission[$i18n.locale].description }}
                        <router-link
                          :to="localePath(permission.more_info_route)"
                        >
                          {{ $t('more-info') }}
                        </router-link>
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="isSaved" class="success">
                &#10004; {{ $t('Data-saved') }}
              </div>
              <div class="privacy__form__buttons">
                <button
                  :disabled="isSubmitting"
                  type="submit"
                  class="button privacy__form__button"
                >
                  {{ submitButtonLabel }}
                </button>
                <button
                  class="button privacy__form__button cancel"
                  @click.prevent="$router.go(-1)"
                >
                  {{ $t('cancel-privacy-settings') }}
                </button>
              </div>
              <div class="warning">
                <span class="nota-bene">i</span>
                <p>{{ $t('remove-account-warning') }}</p>
              </div>
            </form>
          </div>
        </div>
        <div class="right-column">
          <div v-if="cookies">
            <p class="privacy__form__label">
              {{ cookies[$i18n.locale].title }}
            </p>
            <div class="description">
              <p>
                {{ cookies[$i18n.locale].description }} (<router-link
                  :to="localePath(cookies.more_info_route)"
                >
                  {{ $t('more-info') }} </router-link
                >)
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
    <CreateAccount
      v-if="showPopup"
      :user="user"
      :show-popup="showPopup"
      :close="closePopupCreateAccount"
    />
  </section>
</template>
<script>
import { isNil } from 'lodash'
import { mapGetters } from 'vuex'
import SwitchInput from '~/components/switch-input'
import CreateAccount from '~/components/Popup/CreateAccount'
import HeaderBlock from '~/components/HeaderBlock'

export default {
  components: {
    HeaderBlock,
    SwitchInput,
    CreateAccount
  },
  data() {
    const showPopup = !!this.$route.query.popup
    return {
      hasInitialCommunityPermission: null,
      isSaved: false,
      isSubmitting: false,
      permissionsKey: 0,
      showPopup
    }
  },
  computed: {
    ...mapGetters(['user', 'isAuthenticated']),
    permissions() {
      if (isNil(this.user) || isNil(this.user.permissions)) {
        return []
      }
      let permissions =
        this.user.permissions.filter(
          permission => !permission.is_notification_only
        ) || []
      if (!this.isAuthenticated) {
        permissions = permissions.filter(
          permission => !permission.is_after_login
        )
      }
      return permissions
    },
    cookies() {
      if (this.user && this.user.permissions) {
        return this.user.permissions.find(
          permission => permission.type === 'Cookies'
        )
      } else return false
    },
    submitButtonLabel() {
      if (
        this.$store.getters.hasGivenCommunityPermission !==
        this.hasInitialCommunityPermission
      ) {
        return this.$t('save-privacy-settings-and-logout')
      }
      return this.$t('save-privacy-settings')
    }
  },
  mounted() {
    this.hasInitialCommunityPermission = this.$store.getters.hasGivenCommunityPermission
  },
  methods: {
    onSubmit() {
      this.isSubmitting = true
      this.$store
        .dispatch('postUser')
        .then(() => {
          this.isSaved = true
          setTimeout(() => {
            this.isSaved = false
            if (
              this.$store.getters.hasGivenCommunityPermission !==
              this.hasInitialCommunityPermission
            ) {
              this.$store.dispatch('logout', { fully: true })
            }
          }, 1000)
        })
        .finally(() => {
          this.isSubmitting = false
        })
    },
    closePopupCreateAccount() {
      this.showPopup = false
    }
  }
}
</script>
<style lang="less">
@import './../../variables';

.privacy {
  width: 100%;
  padding: 0 0 60px;

  .center_block {
    display: flex;
    flex-direction: column;
  }

  .privacy-header {
    position: relative;
    display: block;

    background-image: url('/images/pictures/rawpixel-760027-unsplash.jpg');
    background-repeat: no-repeat;
    background-size: auto 100%;
    background-position-x: calc(100% - 30px);
    padding: 40px 0;

    @media @wide {
      padding: 50px 0;
      background-position-x: calc(100% - 50px);
    }

    @media @mobile {
      padding: 20px 0;
      background-position-x: calc(100% - 20px);
    }

    @media @small-mobile {
      background-size: 0;
    }
  }

  .left-column {
    width: calc(100% - 425px);
    padding: 0 80px 0 40px;

    @media @wide {
      width: calc(100% - 470px);
    }

    @media @tablet {
      padding: 0 40px;
    }

    @media @mobile {
      width: 100%;
      padding: 0 40px;
    }
  }

  .right-column {
    width: 425px;
    padding: 0 30px 0 2px;
    margin-top: 40px;

    @media @wide {
      width: 470px;
      padding: 0 50px 0 2px;
    }

    @media @mobile {
      margin-top: 0;
      width: 100%;
      padding: 0 40px;
      margin-bottom: 40px;
    }
  }

  .content {
    display: flex;
    width: 100%;

    @media @mobile {
      flex-direction: column;
    }
  }

  input:checked + .slider {
    background-color: #ffc300;
  }

  &__form {
    margin-bottom: 80px;

    @media @mobile {
      margin-bottom: 40px;
    }

    .permission-container {
      display: flex;
    }

    .switch-container {
      line-height: 75px;
    }

    .description {
      padding-left: 20px;
    }

    .description.notification-only {
      padding: 0;
    }

    &_in {
      display: flex;
      justify-content: space-between;
      flex-wrap: wrap;
    }

    &__column {
      width: 100%;
      padding: 0 0 40px;
    }

    &__row {
      clear: both;
      overflow: hidden;
      width: 100%;
      margin-bottom: 16px;
    }

    &__label {
      font-weight: bold;
      color: #353535;
      font-family: @second-font;
      display: block;
      margin-bottom: 8px;
    }

    &__buttons {
      display: flex;
      flex-direction: row;
      width: 100%;
      margin: 10px 0 20px;

      @media @small-mobile {
        flex-direction: column;
      }

      .success {
        display: block;
        margin-left: 20px;
        margin-bottom: 20px;
        color: #008800;
      }
    }
    &__button {
      padding: 13px 60px;

      @media @small-mobile {
        display: block !important;
      }

      &.cancel {
        color: @dark-blue !important;
        background-color: white !important;
        border: 2px solid @light-grey !important;
        box-sizing: border-box;
        -moz-box-sizing: border-box;
        -webkit-box-sizing: border-box;
        padding: 17px 23px;
        margin-left: 20px;

        @media @small-mobile {
          margin-left: 0;
          margin-top: 20px;
          display: block;
        }
      }
    }
    .warning {
      display: flex;
      flex-direction: row;
      .nota-bene {
        color: @red;
        font-weight: bold;
        border: 1px @red solid;
        justify-content: center;
        align-items: center;
        border-radius: 100%;
        text-align: center;
        display: flex;
        width: 20px;
        height: 20px;
        padding: 8px;
        margin-right: 10px;
      }
    }
  }
}
</style>
