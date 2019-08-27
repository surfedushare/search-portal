const pkg = require('./package');
const config = require('./config');

const prodBaseUrl =
  process.env.PROD_URL ||
  (config && config.PROD_URL) ||
  'https://surfcatalog-stage.firebaseapp.com';

module.exports = {
  mode: 'spa',

  router: {
    middleware: 'matomo'
  },

  env: {
    logoutURL:
      (config && config.LOGOUT_URL) ||
      'https://engine.test.surfconext.nl/logout',
    prodBaseUrl,
    localesURL: process.env.LOCALES_URL || (config && config.LOCALES_URL)
  },

  /**
   * Headers of the page
   */
  head: {
    title: 'SURF | Open Leermaterialen',
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { name: 'twitter:card', content: 'summary_large_image' },
      {
        hid: 'description',
        name: 'description',
        content: 'Open Leermaterialen'
      },
      {
        hid: 'og:title',
        property: 'og:title',
        content: 'SURF | Open Leermaterialen'
      },
      {
        hid: 'og:description',
        property: 'og:description',
        content: 'Open Leermaterialen'
      },
      {
        hid: 'og:image',
        property: 'og:image',
        content: prodBaseUrl + '/social-image.jpg'
      },
      {
        hid: 'og:image:width',
        property: 'og:image:width',
        content: '510'
      },
      {
        hid: 'og:image:height',
        property: 'og:image:height',
        content: '298'
      },
      {
        hid: 'og:image:alt',
        property: 'og:image:alt',
        content: 'Open Leermaterialen'
      },
      {
        hid: 'og:type',
        property: 'og:type',
        content: 'article'
      }
    ],
    link: [
      { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
      {
        rel: 'icon',
        type: 'image/png',
        href: '/favicon-16x16.png',
        sizes: '16x16'
      },
      {
        rel: 'icon',
        type: 'image/png',
        href: '/favicon-32x32.png',
        sizes: '32x32'
      },
      {
        rel: 'icon',
        type: 'image/png',
        href: '/favicon-70x70.png',
        sizes: '70x70'
      },
      {
        rel: 'stylesheet',
        href: 'https://use.typekit.net/eya4qgt.css'
      }
    ]
  },

  /**
   * Customize the progress-bar color
   */
  loading: { color: '#0077c8' },

  /**
   * Global CSS
   */
  css: [
    '@/assets/styles/normalize.css',
    '@/assets/styles/variables.less',
    '@/assets/styles/common.less',
    '@/assets/styles/forms.less'
  ],

  /**
   * Plugins to load before mounting the App
   */
  plugins: [
    {
      src: '~/plugins/auth',
      ssr: false
    },
    {
      src: '~/plugins/vSelect',
      ssr: false
    },
    {
      src: '~/plugins/infiniteScroll',
      ssr: false
    },
    {
      src: '~/plugins/axios',
      ssr: false
    },
    {
      src: '~/plugins/SocialSharing',
      ssr: false
    },
    {
      src: '~/plugins/VueMasonry',
      ssr: false
    },
    {
      src: '~/plugins/VueClipboard',
      ssr: false
    },
    {
      src: '~/plugins/veeValidate',
      ssr: false
    }
  ],

  /**
   * Nuxt.js modules
   */
  modules: [
    // Doc: https://github.com/pimlie/nuxt-matomo
    ['nuxt-matomo', { matomoUrl: '//webstats.surf.nl/', siteId: 54, blockLoading: false }],

    // Doc: https://github.com/nuxt-community/axios-module#usage
    '@nuxtjs/axios',
    [
      'nuxt-i18n',
      {
        locales: [
          {
            code: 'en',
            iso: 'en-US',
            file: 'en.js'
          },
          {
            code: 'nl',
            iso: 'nl-NL',
            file: 'nl-NL.js'
          }
        ],
        defaultLocale: 'nl',
        vueI18n: {
          fallbackLocale: 'nl'
        },
        lazy: true,
        langDir: 'locales/'
      }
    ]
  ],
  /**
   * Axios module configuration
   */
  axios: {
    // See https://github.com/nuxt-community/axios-module#options
    headers: { Pragma: 'no-cache' },
    baseURL: (config && config.BASE_URL) || 'https://surf.stg.mqd.me/api/v1/'
  },

  /**
   * Build configuration
   */
  build: {
    /**
     * You can extend webpack config here
     * @param config
     * @param ctx
     */
    extend(config, ctx) {
      // Run ESLint on save
      if (ctx.isDev && ctx.isClient) {
        config.module.rules.push({
          enforce: 'pre',
          test: /\.(js|vue)$/,
          loader: 'eslint-loader',
          exclude: /(node_modules)/
        });
      }
    }
  }
};
