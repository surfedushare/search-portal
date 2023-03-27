<template>
  <v-footer bottom class="bg-gray-lighter">
    <div class="wrapper mx-auto">
      <div class="links">
        <v-btn plain @click="openUseLink('/over-edusources')">{{ $t("footer.about") }}</v-btn>
        <v-btn plain @click="openUseLink('/instellingen')">{{ $t("footer.institutions") }}</v-btn>
        <v-btn plain @click="openUseLink('/privacy')">{{ $t("footer.privacy") }}</v-btn>
      </div>
      <NewLanguageSwitch class="main-header__language_switch" />
      <div class="logos">
        <a @click="openUseLink('/over-edusources#copyright')"><div class="ccby"></div></a>
        <a href="https://www.surf.nl" target="_blank"><div class="surf-logo"></div></a>
      </div>
    </div>
  </v-footer>
</template>

<script>
import { mapGetters } from "vuex";
import NewLanguageSwitch from "./NewLanguageSwitch";

export default {
  name: "NewMainFooter",
  components: {
    NewLanguageSwitch,
  },
  props: [],
  data() {
    return {
      showQuestionPopup: false,
    };
  },
  computed: {
    ...mapGetters(["use_api_endpoint"]),
  },
  methods: {
    openUseLink(link) {
      window.open(`${this.use_api_endpoint}${link}`, "_self");
    },
  },
};
</script>

<style lang="less" scoped>
@import "./../variables";
.v-footer {
  margin-top: 48px;
}

.v-footer .wrapper {
  display: flex;
  flex-direction: row;
  max-width: 1296px;
  justify-content: space-between;
  align-items: flex-end;
  width: 100%;
  @media @mobile {
    flex-direction: column;
    justify-content: flex-start;
    align-items: flex-start;
    min-height: 250px;
  }
}

.v-footer .links {
  display: flex;
  flex-direction: column;
  align-content: flex-start;
  align-items: flex-start;
  width: 240px;
  @media @mobile {
    flex-direction: column;
    align-items: flex-start;
  }
}

.v-footer .links .v-btn {
  text-transform: none;
  height: 24px;
  color: @green;
  font-weight: 600;
  font-size: 14px !important;
  line-height: 18px !important;
  margin-left: -17px;
}

.v-footer .logos {
  display: flex;
  align-self: center;
  @media @mobile {
    align-self: end;
  }
}

.v-footer .logos .surf-logo {
  height: 36px;
  align-self: center;
  content: url("data:image/svg+xml,%3Csvg id='Laag_1' xmlns='http://www.w3.org/2000/svg' version='1.1' x='0' y='0' height='100%25' viewBox='0 0 100 52' xml:space='preserve'%3E%3Cpath id='a_1_' d='M92.4 31.4c4.2 0 7.6 3.5 7.6 7.8v5c0 4.3-3.4 7.8-7.6 7.8H80.9c-4.2 0-7.6-3.5-7.6-7.8v-3.1c0-5.4-4.3-9.7-9.5-9.7H9.5c-5.3 0-9.5-4.3-9.5-9.7v-12C0 4.3 4.3 0 9.5 0h54.3c5.3 0 9.5 4.3 9.5 9.7v12c0 5.4 4.3 9.7 9.5 9.7h9.6z' /%3E%3Cpath d='M60.6 17.8c1 0 1.5-.5 1.5-1.5s-.5-1.6-1.5-1.6h-3.8v-3h6c1 0 1.5-.5 1.5-1.6 0-1-.5-1.5-1.5-1.5h-7.6c-1 0-1.6.5-1.6 1.6v11c0 1.1.5 1.6 1.6 1.6 1 0 1.6-.5 1.6-1.6v-3.5c0 .1 3.8.1 3.8.1zm-12.5-.3c1.4-.7 2.2-2.1 2.2-3.9 0-2.9-2.1-5-5.1-5h-4.5c-1 0-1.6.5-1.6 1.6v11c0 1.1.5 1.6 1.6 1.6 1 0 1.6-.5 1.6-1.6v-2.9H45l1.6 3.4c.3.7.7 1 1.3 1 .8 0 1.8-.6 1.8-1.5 0-.3-.1-.6-.2-.9l-1.4-2.8zm-3.3-2h-2.7v-3.8h2.7c1.2 0 2.2.6 2.2 1.9 0 1.3-1 1.9-2.2 1.9zm-12.7.8c0 2.2-1.3 3.5-3.1 3.5s-3.1-1.3-3.1-3.5v-6.2c0-1.1-.5-1.6-1.6-1.6-1 0-1.6.5-1.6 1.6v6.2c0 4.1 2.7 6.7 6.3 6.7 3.6 0 6.3-2.6 6.3-6.7v-6.2c0-1.1-.5-1.6-1.6-1.6-1 0-1.6.5-1.6 1.6v6.2zM14.2 20c-1.2 0-2.1-.3-2.7-.5-.5-.2-.9-.3-1.4-.3-.9 0-1.4.6-1.4 1.5 0 1.5 3 2.3 5.6 2.3 3.1 0 5.5-1.7 5.5-4.3 0-2.4-1.6-3.5-3.3-4.1l-2.6-.8c-1.1-.3-1.6-.6-1.6-1.3 0-.7 1.1-1.1 2-1.1 1.1 0 1.9.3 2.5.5.4.1.8.3 1.3.3.8 0 1.3-.6 1.3-1.5 0-1.5-2.7-2.3-5.1-2.3-3 0-5.2 1.7-5.2 4.2 0 2.1 1.5 3.3 3.1 3.8l2.3.7c1.2.4 2.1.7 2.1 1.4-.2 1-1.4 1.5-2.4 1.5z' fill='%23fff' /%3E%3C/svg%3E");
}

.v-footer .logos .ccby {
  height: 22px;
  align-self: top;
  margin-right: 10px;
  content: url("data:image/svg+xml,%3Csvg width='56' height='24' viewBox='0 0 56 24' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11.9672 0C8.67959 0 5.78652 1.21668 3.55083 3.48494C1.24925 5.81909 0 8.84394 0 11.9998C0 15.189 1.2163 18.148 3.51788 20.4492C5.81947 22.7508 8.81099 24 11.9672 24C15.1231 24 18.1809 22.7508 20.548 20.4166C22.7837 18.2139 23.9671 15.2878 23.9671 11.9998C23.9671 8.7451 22.7837 5.78652 20.5151 3.51788C18.2139 1.2163 15.2549 0 11.9672 0ZM11.9998 2.1698C14.696 2.1698 17.096 3.18882 18.9697 5.06325C20.8108 6.90399 21.7969 9.33697 21.7969 11.9998C21.7969 14.6956 20.8434 17.0631 19.0026 18.8712C17.0627 20.7779 14.5642 21.7973 11.9998 21.7973C9.40286 21.7973 6.96988 20.7782 5.09582 18.9038C3.22176 17.0297 2.1698 14.5642 2.1698 11.9998C2.1698 9.40286 3.22176 6.93731 5.09582 5.02993C6.93693 3.15625 9.30403 2.1698 11.9998 2.1698Z' fill='black'/%3E%3Cpath d='M11.8455 10.0057C11.1677 8.7697 10.0112 8.2778 8.66884 8.2778C6.71488 8.2778 5.15967 9.65996 5.15967 11.9994C5.15967 14.3786 6.62173 15.7214 8.73511 15.7214C10.0911 15.7214 11.2476 14.9769 11.8853 13.8473L10.3967 13.0896C10.0643 13.8867 9.55911 14.1264 8.92142 14.1264C7.81796 14.1264 7.31281 13.2093 7.31281 11.9994C7.31281 10.7903 7.73844 9.87278 8.92142 9.87278C9.24026 9.87278 9.87833 10.0455 10.2506 10.8433L11.8455 10.0057Z' fill='black'/%3E%3Cpath d='M18.7679 10.0057C18.0901 8.7697 16.9336 8.2778 15.5912 8.2778C13.6372 8.2778 12.082 9.65996 12.082 11.9994C12.082 14.3786 13.5441 15.7214 15.6575 15.7214C17.0135 15.7214 18.17 14.9769 18.8077 13.8473L17.3191 13.0896C16.9866 13.8867 16.4815 14.1264 15.8438 14.1264C14.7403 14.1264 14.2352 13.2093 14.2352 11.9994C14.2352 10.7903 14.6608 9.87278 15.8438 9.87278C16.1626 9.87278 16.8007 10.0455 17.1729 10.8433L18.7679 10.0057Z' fill='black'/%3E%3Cg clip-path='url(%23clip0_804_9047)'%3E%3Cpath d='M43.6626 -1.01725e-05C37.1821 0.164052 31.9673 5.47997 31.9673 12C31.9673 18.624 37.3433 24 43.9673 24C50.5913 24 55.9673 18.624 55.9673 12C55.9673 5.37597 50.5913 -1.01725e-05 43.9673 -1.01725e-05C43.8633 -1.01725e-05 43.7651 -0.00293986 43.6626 -1.01725e-05ZM43.6509 2.06249C43.7578 2.05956 43.8604 2.06249 43.9673 2.06249C49.4531 2.06249 53.9048 6.51415 53.9048 12C53.9048 17.4858 49.4531 21.9375 43.9673 21.9375C38.4814 21.9375 34.0298 17.4858 34.0298 12C34.0298 6.62108 38.313 2.23241 43.6509 2.06249Z' fill='black'/%3E%3Cpath d='M45.7017 5.97656C45.7017 6.93311 44.9253 7.71094 43.9673 7.71094C43.0093 7.71094 42.2329 6.93311 42.2329 5.97656C42.2329 5.01855 43.0093 4.24219 43.9673 4.24219C44.9253 4.24219 45.7017 5.01855 45.7017 5.97656Z' fill='black'/%3E%3Cpath d='M42.1729 19.7578H45.7617V13.9922H46.8472C46.8472 13.9922 46.8457 9.8701 46.8472 9.22117C46.8457 9.04979 46.8618 8.70994 46.6143 8.46092C46.3652 8.21336 46.0298 8.22801 45.854 8.22801C45.6768 8.22947 42.2578 8.22947 42.0806 8.22801C41.9048 8.22801 41.5693 8.21336 41.3203 8.46092C41.0728 8.70994 41.0889 9.04979 41.0874 9.22117C41.0889 9.8701 41.0874 13.9922 41.0874 13.9922H42.1729V19.7578Z' fill='black'/%3E%3C/g%3E%3Cdefs%3E%3CclipPath id='clip0_804_9047'%3E%3Crect width='24' height='24' fill='white' transform='translate(31.9673)'/%3E%3C/clipPath%3E%3C/defs%3E%3C/svg%3E%0A");
}
</style>
