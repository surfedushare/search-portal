<template>
  <section class="container main privacy">
    <div class="center_block">
      <div class="privacy__info">
        <img
          src="/images/pictures/rawpixel-760027-unsplash.jpg"
          srcset="
            /images/pictures/rawpixel-760027-unsplash@2x.jpg 2x,
            /images/pictures/rawpixel-760027-unsplash@3x.jpg 3x
          "
          class="privacy__info_bg"
        />
        <h2 class="privacy__info_ttl">
          {{ $t('My-privacy') }}
        </h2>
      </div>
      <div v-if="permissions.length" class="privacy__form">
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
                    {{ permission[$i18n.locale].description }} (<router-link
                      :to="localePath(permission.more_info_route)"
                    >
                      {{ $t('more-info') }} </router-link
                    >)
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div class="privacy__form__buttons">
            <button
              :disabled="is_submitting"
              type="submit"
              class="button privacy__form__button"
            >
              {{ $t('save') }}
            </button>
            <div v-if="is_saved" class="success">
              &#10004; {{ $t('Data-saved') }}
            </div>
          </div>
        </form>
      </div>
    </div>
  </section>
</template>

<script>
import { isNil } from 'lodash'
import { mapGetters } from 'vuex'
import SwitchInput from '~/components/switch-input'

export default {
  components: {
    SwitchInput
  },
  data() {
    return {
      is_saved: false,
      is_submitting: false,
      permissionsKey: 0
    }
  },
  computed: {
    ...mapGetters(['user', 'isAuthenticated']),
    permissions() {
      if (isNil(this.user) || isNil(this.user.permissions)) {
        return []
      }
      return this.user.permissions
    }
  },
  methods: {
    onSubmit() {
      this.is_submitting = true
      this.$store
        .dispatch('postUser')
        .then(() => {
          this.is_saved = true
          setTimeout(() => {
            this.is_saved = false
            let authFlowToken = this.$store.getters.auth_flow_token
            if (!isNil(authFlowToken)) {
              let backendUrl = process.env.VUE_APP_BACKEND_URL
              this.$store.commit('AUTH_FLOW_TOKEN', null)
              window.location =
                backendUrl +
                'complete/surf-conext/?partial_token=' +
                authFlowToken
            }
          }, 1000)
        })
        .finally(() => {
          this.is_submitting = false
        })
    }
  }
}
</script>
<style lang="less">
@import './../../variables';

.privacy {
  width: 100%;
  padding: 80px 0 60px;

  @media @mobile {
    padding-top: 60px;
  }

  &__info {
    padding: 50px 30px;
    margin: 0 0 80px;
    border-radius: 20px;
    background-color: rgba(244, 244, 244, 0.9);
    position: relative;
    border-radius: 20px;

    &_bg {
      position: absolute;
      right: 26px;
      top: -51px;
      width: 40%;
      border-radius: 21px;

      @media @mobile {
        display: none;
      }
    }
    &_ttl {
      position: relative;
    }
  }
  &__form {
    margin-bottom: 146px;

    .permission-container {
      display: flex;
      align-items: center;
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
      width: 100%%;
      padding-right: 30px;
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
      width: 100%;
      margin: 10px 0 0;

      .success {
        display: inline-block;
        margin-left: 20px;
        color: #008800;
      }
    }
    &__button {
      padding: 13px 60px;
    }
  }
}
</style>
