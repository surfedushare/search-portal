import validate from 'uuid-validate';

/**
 * formatting date
 * @param str - String
 * @param format - String
 * @returns {*} - formatted date
 */
export const formatDate = (str, format) => {
  if (str) {
    const d = new Date(str);
    let curr_date = d.getDate();
    let curr_month = d.getMonth() + 1;
    const curr_year = d.getFullYear();
    format = format ? format.toUpperCase() : 'DD/MM/YYYY';
    curr_date = curr_date < 10 ? '0' + curr_date : curr_date;
    curr_month = curr_month < 10 ? '0' + curr_month : curr_month;
    const mapObj = {
      DD: curr_date,
      MM: curr_month,
      YYYY: curr_year
    };

    return format.replace(/DD|MM|YYYY/gi, matched => {
      return mapObj[matched];
    });
  }

  return false;
};

/**
 * Validate ID
 * @param str
 * @returns {Boolean}
 */
export const validateID = str => {
  return validate(str, 4) || validateBASE64(str);
};

/**
 * Validate ID string
 * @param str
 * @returns {Boolean}
 */
export const validateIDString = str => {
  return str && typeof str === 'string';
};

/**
 * Validate base64
 * @param str
 * @returns {boolean}
 */
export const validateBASE64 = str => {
  try {
    window.atob(str);

    return true;
  } catch (e) {
    // something failed
    // if you want to be specific and only catch the error which means
    // the base 64 was invalid, then check for 'e.code === 5'.
    // (because 'DOMException.INVALID_CHARACTER_ERR === 5')

    return false;
  }
};

/**
 * Validate search
 * @param obj
 * @returns {*|boolean}
 */
export const validateSearch = obj => {
  return obj && typeof obj === 'object';
};

/**
 * Validate params
 * @param obj
 * @returns {*|boolean}
 */
export const validateParams = obj => {
  return obj && typeof obj === 'object';
};

export function decodeAuthor(material) {
  let elem = document.createElement('textarea');
  elem.innerHTML = material.author;
  material.author = elem.value;
}
