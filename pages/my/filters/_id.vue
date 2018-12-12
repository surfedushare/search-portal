
<template>
  <section class="container main collections my_filter">
    <div
      class="center_block">
      <div
        v-if="data"
        class="my_filter__info" >
        <div class="my_filter__info_title">
          <BreadCrumbs
            :items="[
              {title:'Profiel', url: '/my/'},
              {title:`Mijn selecties`, url: `/my/filters/`},
              {title:`Selectie`, url: `/my/filters/${data.id}`}]"/>
          <h2 class="my_filter__info_ttl">{{ data.title }}</h2>
          <p class="my_filter__info_subttl">{{ data.materials_count }} resultaten</p>
        </div>
        <div class="my_filter__info_filter">
          <div class="my_filter__info_filter__edit">
            <a
              class="my_filter__info_filter__link"
              href="#"
            >
              Bewerken
            </a>
          </div>
          <div class="my_filter__info_filter__delete">
            <a
              href="#"
              class="my_filter__info_filter__link"
            >
              Verwijderen
            </a>
          </div>
          <div class="my_filter__info_filter__button">
            <a
              href="#"
              class="button"
            >
              Opslaan
            </a>
          </div>
        </div>
      </div>
      <masonry
        :cols="{default: 4, 1000: 3, 700: 2, 400: 1}"
        :gutter="{default: '60px', 700: '15px'}"
      >
        <div
          v-for="category in all_filters"
          v-if="!category.hide"
          :key="category.external_id"
          class="filter-categories__item"
        >
          <h4
            class="filter-categories__item_title"
          >
            {{ category.title }}
          </h4>
          <ul class="filter-categories__subitems">
            <li
              v-for="filter in category.items"
              :key="filter.external_id"
              class="filter-categories__subitem"
            >
              <input
                :id="filter.external_id"
                :value="filter.external_id"
                type="checkbox"
                @change="onChange($event, filter)"
              >
              <label :for="filter.external_id">{{ filter.title }} ({{ filter.count }})</label>
            </li>
          </ul>
        </div>
      </masonry>
    </div>
  </section>
</template>

<script>
import { mapGetters } from 'vuex';
import BreadCrumbs from '~/components/BreadCrumbs';

export default {
  components: {
    BreadCrumbs
  },
  data() {
    return {
      checked_filter: [],
      data: null
    };
  },
  computed: {
    ...mapGetters([
      'active_filter',
      'materials',
      'filters',
      'filter_categories',
      'user',
      'isAuthenticated'
    ]),
    all_filters() {
      const { materials, filter_categories } = this;
      if (materials && filter_categories) {
        const { results } = filter_categories;
        const { filters } = materials;

        return filters.map(category => {
          const current_filter = results.find(
            filter => filter.external_id === category.external_id
          );
          return {
            ...category,
            ...current_filter,
            items: category.items.map(item => {
              const current_item = current_filter.items.find(
                filter => filter.external_id === item.external_id
              );

              return {
                ...item,
                ...current_item
              };
            })
          };
        });
      }

      return false;
    }
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
      this.getData();
    }
  },
  methods: {
    getData() {
      this.$store.dispatch('searchMaterials', {
        return_records: false,
        search_text: []
      });

      this.$store
        .dispatch('getDetailFilter', {
          id: this.$route.params.id
        })
        .then(data => {
          this.data = data;
        });

      this.$store.dispatch('getFilterCategories');
    },
    onChange($event, filter) {
      if ($event.target.checked) {
        this.data.items.push({
          category_item_id: filter.external_id
        });
        this.data.materials_count += filter.count;
      } else {
        this.data.items = this.data.items.filter(
          item => item.category_item_id !== filter.external_id
        );
        this.data.materials_count -= filter.count;
      }
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
<style src="./../../../components/FilterCategories/FilterCategories.component.less" scoped lang="less">
</style>
