'use strict'

/**
 * Insert panel
 */
function add_panel(button){
  /* Fetch panel to insert after */
  var prevBox = button.parentElement;

  /* Create inner content box */
  var newBox = document.createElement('div');
  newBox.className = prevBox.className;

  /* Create inner row div */
  var prevRow = prevBox.parentElement;
  var newRow = document.createElement('div');
  newRow.className = prevRow.className;
  newRow.appendChild(newBox);

  /* Create outer container div */
  var prevPanel = prevRow.parentElement;
  var newPanel = document.createElement('div')
  newPanel.className = prevPanel.className;
  newPanel.appendChild(newRow);

  /* Create panel elements */
  newBox.appendChild($('<h2>').text('Panel')[0]);
  var form = [{'type': 'text', 'label': 'Header:', 'name': 'header'}]
  newBox.appendChild(JQ_create_form(form)[0]);

  /* TODO: Add new panel button */
  /* TODO: Add form fields buton */
  /* TODO: Send page config back */

  $(prevPanel).after(newPanel);
}


/**
 * Creates form JQ element
 * @param form: list of description objects for form fields,
 *    'label': required name of label input label
 *    'type': optional type of input, defaults to text
 *    'name': optional name of input field, defaults to label
 * @return Root jquery object of form
 */
function JQ_create_form(form){
  /* Create initial form */
  var formEl = $('<form>')
    .addClass('form-horizontal')
    .append($('<div>')
      .addClass('form-group')
    );

  for (var i in form){
    console.log(i)
    var f = form[i];
    var ftype = f.type || 'text';
    var fname = f.name || f.label;
    formEl
      .append($('<label>')
        .addClass('col-sm-3 control-label')
        .append(f.label)
      ).append($('<div>')
        .addClass('col-sm-8')
        .append($('<input>')
          .addClass('form-control')
          .attr('name', fname)
          .attr('type', ftype)
      )
    );
  }
  return formEl;
}
