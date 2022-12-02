// This file is here to be able to load Sentry preloaded.
// Sentry itself doesn't seem to provide a default export that webpack requires.
// Apart from providing the export default we configure the Sentry instance.

import * as Sentry from "@sentry/browser";

if (process.env.VUE_APP_USE_SENTRY) {
  Sentry.init({
    dsn: `${window.location.protocol}//21fab3e788584cbe999f20ea1bb7e2df@${window.location.host}/sentry/2964956`,
    beforeSend(event) {
      if (window.location.host !== "edusources.nl") {
        return event;
      }
      if (event.user) {
        delete event.user;
      }
      if (event.request && event.request.headers && event.request.headers["User-Agent"]) {
        delete event.request.headers["User-Agent"];
      }
      return event;
    },
  });
}

export default Sentry;
