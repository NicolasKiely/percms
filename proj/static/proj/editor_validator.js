/* Validate project header */

function checkAboutField(x){
  var about = $(x).val();
  if (!(about=='' || about%1===0)){
    return 'Error, invalid id of docpage id for project description';
  }
}


jQuery()
  .validator('#form_edit_header')
  .logger('#log_edit_header')
  .submit('#form_edit_header button[type="submit"]')
  .validate
({
  '#edit_about': checkAboutField
});
