// import axios from 'axios';
export default () => {
  return new Promise(function(resolve) {
    var xhr = new XMLHttpRequest();

    xhr.open('GET', process.env.VUE_APP_LOCALES_URL + 'en/surf-en.json', false);
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.send();

    if (xhr.status !== 200) {
      console.log(xhr.status + ': ' + xhr.statusText);
    } else {
      // console.log(xhr.responseText);
      return resolve(JSON.parse(xhr.responseText));
    }

    // axios
    //   .get('https://surf.stg.mqd.me/static/locales/en/surf-en.json')
    //   .then(response => {
    //     return resolve(response.data);
    //   });
  });
};
