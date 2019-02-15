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
  return validate(str, 4);
};
