'use strict'

/** Setup Module Namespace for docpage editor */
var ns = ns || {};
ns.docpage = {};



/**********************\
|* Callback Functions *|
\**********************/
var callback = {};

/**
 * Insert panel after element
 */
callback.add_panel = function (button){
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
  $(newBox)
    .append(ns.docpage.jq.create_form(form))
    .append(ns.docpage.jq.panel_add_field_button())
    .append($('<hr>'));

  /* TODO: Add new panel button */
  /* TODO: Add form fields buton */
  /* TODO: Send page config back */

  $(prevPanel).after(newPanel);
};


/**
 * Callback function for adding component in panel
 */
callback.add_component = function(){
  var btn = $(this);
  console.log(btn.parent().parent());
}


ns.docpage.cb = callback;



/***********************\
|* Jquery Constructors *|
\***********************/
var jq = {};


/**
 * Creates the "Add Component" button in panels
 * @return Root jquery ovject of button
 */
jq.panel_add_field_button = function(){
  return $('<div>')
    .append($('<button>')
      .click(ns.docpage.cb.add_component)
      .addClass('btn btn-primary')
      .text('Add Component')
    );
}


/**
 * Creates form JQ element
 * @param form: list of description objects for form fields,
 *    'label': required name of label input label
 *    'type': optional type of input, defaults to text
 *    'name': optional name of input field, defaults to label
 * @return Root jquery object of form
 */
jq.create_form = function (form){
  /* Create initial form */
  var formEl = $('<form>')
    .addClass('form-horizontal')
    .append($('<div>')
      .addClass('form-group')
    );

  for (var i in form){
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

ns.docpage.jq = jq;
