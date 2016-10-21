/* Validate login fields */
//jQuery().validate({
jQuery()
    .validator('#login-form')
    .logger('#login-log')
    .submit('#login-form button[type="submit"]')
    .validate
({
  '#login-name' : checkAlphaNumeric,
  '#login-passwd': checkPassword
});
