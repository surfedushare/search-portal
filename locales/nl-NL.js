// import axios from 'axios';
export default () => {
  return new Promise(function(resolve) {
    var xhr = new XMLHttpRequest();

    xhr.open('GET', process.env.VUE_APP_LOCALES_URL + 'nl-NL/surf-nl-NL.json', false);
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.send();

    if (xhr.status !== 200) {
      console.log(xhr.status + ': ' + xhr.statusText);
    } else {
      return resolve(JSON.parse(xhr.responseText));
    }

    // axios
    //   .get('https://surf.stg.mqd.me/static/locales/nl-NL/surf-nl-NL.json')
    //   .then(response => {
    //     return resolve(response.data);
    //   });
  });
};
