
<template>
  <section class="container main collections my_filter">
    <div
      class="center_block">
      <div
        v-if="active_filter"
        class="my_filter__info" >
        <div class="my_filter__info_title">
          <BreadCrumbs
            :items="[
              {title:'Profiel', url: '/my/'},
              {title:`Mijn selecties`, url: `/my/filters/`},
              {title:`Selectie`, url: `/my/filters/${active_filter.id}`}]"/>
          <h2 class="my_filter__info_ttl">{{ active_filter.title }}</h2>
          <p class="my_filter__info_subttl">{{ active_filter.materials_count }} resultaten</p>
        </div>
        <div class="my_filter__info_filter">
          <div class="my_filter__info_filter__edit">
            <a
              class="my_filter__info_filter__link"
              href="#" >Bewerken</a>
          </div>
          <div class="my_filter__info_filter__delete">
            <a
              href="#"
              class="my_filter__info_filter__link">Verwijderen</a>
          </div>
          <div class="my_filter__info_filter__button">
            <a
              href="#"
              class="button">Opslaan</a>
          </div>
        </div>
      </div>
      <div class="my_filter__list">
        <div class="my_filter__list_item">
          <div class="my_filter__list_title">Leerniveau</div>
          <!--<pre>{{ active_filter }}</pre>-->
          <FilterCategories
            :full-filter="true"
          />
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { mapGetters } from 'vuex';
import BreadCrumbs from '~/components/BreadCrumbs';
import FilterCategories from '~/components/FilterCategories';

export default {
  components: {
    BreadCrumbs,
    FilterCategories
  },
  computed: {
    ...mapGetters(['active_filter', 'user', 'isAuthenticated'])
  },
  watch: {
    isAuthenticated(isAuthenticated) {
      if (isAuthenticated) {
        this.getData();
      }
    }
  },
  mounted() {
    if (this.isAuthenticated) {
      console.log(this.$route.params.id, this.isAuthenticated);
      this.getData();
    }
  },
  methods: {
    getData() {
      this.$store
        .dispatch('searchMaterials', {
          return_records: false,
          search_text: []
        })
        .then(filters => {
          console.log(115623, filters);
          this.$store.commit('SET_FILTERS', filters);
          this.$store.dispatch('getDetailFilter', {
            id: this.$route.params.id
          });
        });
    }
  }
};
</script>

<style lang="less">
@import './../../../assets/styles/variables';
.my_filter {
  width: 100%;
  padding: 101px 0 47px;

  &__info {
    padding: 59px 45px 95px 103px;
    margin: 0 0 113px;
    border-radius: 20px;
    position: relative;
    display: flex;
    justify-content: space-between;
    background: url('./../../../assets/images/filters.svg') 54px 96px no-repeat;
    background-size: 30px;

    .bread-crumbs {
      margin-bottom: 0;
    }
    &:before {
      content: '';
      min-width: 100%;
      position: absolute;
      background-color: rgba(244, 244, 244, 0.9);
      right: 0;
      left: 0;
      top: 0;
      bottom: 0;
      border-radius: 20px;
      z-index: -1;
    }
    &_ttl {
      padding: 0 0 8px;
      position: relative;
    }
    &_subttl {
      padding: 0 0 7px;
      font-size: 20px;
      line-height: 1.15;
      font-family: @main-font;
      position: relative;
    }
    &_title {
      display: inline-block;
      vertical-align: top;
      min-width: 50%;
    }

    &_filter {
      width: 45%;
      display: flex;
      margin: 0;
      padding-top: 15px;
      align-items: center;
      justify-content: flex-end;
      &__link {
        font-weight: bold;
        padding-left: 30px;
        position: relative;
        font-size: 16px;
        font-family: @second-font;
      }
      &__edit {
        a {
          background: url('./../../../assets/images/edit.svg') no-repeat 0 50%;
          background-size: 30px;
        }
      }
      &__delete {
        margin-left: 32px;
        a {
          background: url('./../../../assets/images/trash.svg') no-repeat 0 50%;
          background-size: 30px;
        }
      }
      &__button {
        margin-left: 50px;
        a {
          padding: 13px 60px;
        }
      }
    }
  }
  &__add {
    display: flex;
    justify-content: flex-end;
    margin-bottom: -55px;
    &__link {
      padding: 13px 43px 13px 51px;
      background-image: url('./../../../assets/images/plus-black.svg');
      background-position: 10px 50%;
      background-repeat: no-repeat;
      background-size: 24px;
    }
  }
}
</style>
