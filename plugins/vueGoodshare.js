import Vue from 'vue';
import VueGoodshare from 'vue-goodshare';
import VueGoodshareLinkedin from 'vue-goodshare/src/providers/Linkedin.vue';
import VueGoodshareTwitter from 'vue-goodshare/src/providers/Twitter.vue';

Vue.component('vue-goodshare', VueGoodshare);
Vue.component('vue-goodshare-linkedin', VueGoodshareLinkedin);
Vue.component('vue-goodshare-twitter', VueGoodshareTwitter);
