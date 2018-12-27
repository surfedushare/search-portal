const pkg = require('./package');

module.exports = {
  mode: 'spa',

  env: {
    logoutURL:
      process.env.LOGOUT_URL || 'https://engine.test.surfconext.nl/logout'
  },

  /**
   * Headers of the page
   */
  head: {
    title: 'Surf | Open Leermaterialen',
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      {
        hid: 'description',
        name: 'description',
        content: 'Open Leermaterialen'
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
        href: 'https://fonts.googleapis.com/css?family=Source+Sans+Pro'
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
    }
  ],

  /**
   * Nuxt.js modules
   */
  modules: [
    // Doc: https://github.com/nuxt-community/axios-module#usage
    '@nuxtjs/axios',
    [
      'nuxt-i18n',
      {
        locales: [
          {
            code: 'en',
            iso: 'en-US',
            file: 'en/surf-en.json'
          },
          {
            code: 'nl-NL',
            iso: 'nl-NL',
            file: 'nl-NL/surf-nl-NL.json'
          }
        ],
        defaultLocale: 'nl-NL',
        vueI18n: {
          fallbackLocale: 'nl-NL'
        },
        lazy: true,
        langDir: 'static/locales/'
      }
    ]
  ],
  /**
   * Axios module configuration
   */
  axios: {
    // See https://github.com/nuxt-community/axios-module#options
    headers: { Pragma: 'no-cache' },
    baseURL: 'https://surf.stg.mqd.me/api/v1/'
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
