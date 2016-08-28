/* Validate login fields */
//jQuery().validate({
jQuery()
    .validator('#login-form')
    .logger('#login-log')
    .submit('#login-form button[type="submit"]')
    .validate
({
  '#login-email' : checkEmail,
  '#login-passwd': checkPassword
});
