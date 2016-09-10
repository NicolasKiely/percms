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
    .append($('<div>')
      .addClass('row')
      .append(ns.docpage.jq.create_form(form))
    )
    .append($('<div>')
      .addClass('row')
      .append(ns.docpage.jq.add_component_button())
    )
    .append(ns.docpage.jq.component_terminator())
  ;

  /* TODO: Add new panel button */
  /* TODO: Send page config back */

  $(prevPanel).after(newPanel);
};


/**
 * Callback function for adding component in panel
 */
callback.add_component = function(){
  /* Get component terminator immediately after this button */
  var hr_term = $(this).parent().parent().siblings('hr.component-term')[0];

  /* Append new component form */
  $(hr_term).after(ns.docpage.jq.create_component_form());
};


ns.docpage.cb = callback;



/***********************\
|* Jquery Constructors *|
\***********************/
var jq = {};


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
};


/**
 * Creates form for editing docpage component
 * @return Root jquery object of form
 */
jq.create_component_form = function(){
  var formFields = [
    {'label': 'Field Type', 'name': 'view'},
    {'label': 'Data Model Type', 'name': 'model'},
    {'label': 'Source', 'name': 'source'}
  ];
  return $('<div>')
    .addClass('container-fluid')
    .append($('<div>')
      .addClass('row')
      .append($('<h3>').text('Component'))
    )
    .append($('<div>')
      .addClass('row')
      .append(ns.docpage.jq.create_form(formFields))
    )
    .append($('<br>'))
    .append($('<div>')
      .addClass('row')
      .append(ns.docpage.jq.add_component_button())
      .append(ns.docpage.jq.delete_component_button())
    )
    .append(ns.docpage.jq.component_terminator())
  ;
};


/**
 * Creates component terminator element
 * @return Root jquery object of <hr>
 */
jq.component_terminator = function(){
  return $('<hr>').addClass('component-term');
};


/**
 * Creates the "Add Component" button in panels
 * @return Root jquery ovject of button
 */
jq.add_component_button = function(){
  return $('<div>')
    .addClass('col-lg-2')
    .append($('<button>')
      .click(ns.docpage.cb.add_component)
      .addClass('btn btn-primary')
      .text('Add Component')
    )
  ;
}


/**
 * Creates "delete component" button
 * @return Root jquery object of <button>
 */
jq.delete_component_button = function(){
  return $('<div>')
    .addClass('col-lg-2')
    .append($('<button>')
      .addClass('btn btn-primary')
      .text('Delete Component')
    )
  ;
};


ns.docpage.jq = jq;
