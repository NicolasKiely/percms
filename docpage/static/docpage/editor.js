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
      .addClass('container-fluid')
      .appendRow(ns.docpage.jq.create_form(form))
      .appendRow(ns.docpage.jq.add_component_button())
      .append(ns.docpage.jq.component_terminator())
    )
  ;

  /* TODO: Add new panel button */
  /* TODO: Send page config back */

  $(prevPanel).after(newPanel);
};


/** Callback function for adding component in panel */
callback.add_component = function(){
  /* Get component terminator immediately after this button */
  var component = $(this).parent().parent();
  var hr_term = component.siblings('hr.component-term')[0];

  /* Append new component form */
  $(hr_term).parent().after(ns.docpage.jq.create_component_form());
};


/** Callback function for deleting component */
callback.delete_component = function(){
  /* Get component root dom node and delete */
  var component = $(this).parent().parent().parent();
  component.remove()
};


/** Moves component up in panel */
callback.move_component_up = function(){
  /* Get current component */
  var current = $(this).parent().parent().parent();
  /* Get list of components in this form */
  var components = current.parent().children('div.component-form')
  /* Get current component index. Make sure not first element */
  var i = components.index(current);
  if (i<=0)
    return;
  /* Get preceeding component and attach current to before */
  components.eq(i-1).before(current);

};


/** Moves component down in panel */
callback.move_component_down = function(){
  console.log('Moving component down');
};


ns.docpage.cb = callback;



/***********************\
|* Jquery Constructors *|
\***********************/
var jq = {};

/** Similar to jquery's append() function, but wraps div.row around node */
$.fn.appendRow = function(children){
  this
    .append($('<div>')
      .addClass('row')
      .append(children)
    )
  ;
  return this;
};


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
    .addClass('container-fluid component-form')
    .appendRow($('<h3>').addClass('text-center').text('Component'))
    .appendRow(ns.docpage.jq.create_form(formFields))
    .append($('<br>'))
    .appendRow([
      ns.docpage.jq.add_component_button(),
      ns.docpage.jq.delete_component_button(),
      ns.docpage.jq.component_down_button(),
      ns.docpage.jq.component_up_button()
    ])
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
      .click(ns.docpage.cb.delete_component)
      .addClass('btn btn-danger')
      .text('Delete Component')
    )
  ;
};


/** Creates up arrow button for component*/
jq.component_up_button = function(){
  return $('<div>')
    .addClass('pull-right')
    .append($('<button>')
      .click(ns.docpage.cb.move_component_up)
      .addClass('btn btn-primary')
      .append($('<span>')
        .addClass('glyphicon glyphicon-arrow-up')
      )
    )
  ;
};


/** Creates down arrow button for component*/
jq.component_down_button = function(){
  return $('<div>')
    .addClass('pull-right')
    .append($('<button>')
      .click(ns.docpage.cb.move_component_down)
      .addClass('btn btn-primary')
      .append($('<span>')
        .addClass('glyphicon glyphicon-arrow-down')
      )
    )
  ;
};



ns.docpage.jq = jq;
