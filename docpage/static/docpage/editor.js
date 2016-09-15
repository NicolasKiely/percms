'use strict'

/** Setup Module Namespace for docpage editor */
var ns = ns || {};
ns.docpage = {};

$(document).ready(function($){
  /* Attach add-panel function to initial button */
  $('#btn-add-panel').click(ns.docpage.cb.add_panel);

  /* Start off counting panels at header panel */
  var prevPanel = $('div.outer-content-box')[0]

  /* Read in page config */
  for (var p=0; p<originalPanels.length; p++){
    var panelSpec = originalPanels[p];

    /* Insert panel after last one */
    prevPanel = ns.docpage.misc.add_panel(prevPanel, panelSpec.header);

    /* Build component forms */
    var hrTerm = $(prevPanel).find('hr.component-term')
    var originalComps = panelSpec.components || [];
    for (var c=0; c<originalComps.length; c++){
      var compSpec = originalComps[c];
      /* Add component after previous */
      var prevComp = ns.docpage.misc.add_component(hrTerm, compSpec);
      hrTerm = $(prevComp).find('hr.component-term')
    }
  }
});



/**********************\
|* Callback Functions *|
\**********************/
var callback = {};


/** Submits docpage data back to server */
callback.submit = function(){
  /* Get page submission data */
  var data = ns.docpage.misc.gather_docpage_data();

  /* Set panel data to hidden form */
  $('#edit_panel_data').val(data);

  /* Submit form */
  document.forms.form_edit_header.submit();
  
};


/** Insert panel after element */
callback.add_panel = function (){
  /* Get panel containing this button */
  var prevBox = this.parentElement.parentElement
    .parentElement.parentElement;
  var prevPanel = prevBox.parentElement.parentElement;

  /* Insert panel */
  ns.docpage.misc.add_panel(prevPanel);
};


/** Callback for "Delete Panel" button */
callback.delete_panel = function(){
  var box = $(this).parent().parent().parent().parent();
  /* Remove box's panel */
  box.parent().parent().remove();
};


/** Callback function for adding component in panel */
callback.add_component = function(){
  /* Get component terminator immediately after this button */
  var component = $(this).parent().parent();
  var hr_term = component.siblings('hr.component-term')[0];

  /* Append new component form */
  ns.docpage.misc.add_component(hr_term);
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
  /* Get current component */
  var current = $(this).parent().parent().parent();
  /* Get list of components in this form */
  var components = current.parent().children('div.component-form')
  /* Get current component index. Make sure not first element */
  var i = components.index(current);
  if (i+1 >= components.size)
    return;
  /* Get next component and attach current to after */
  components.eq(i+1).after(current);
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
    var fvalue = f.value || '';
    var foptions = f.options || [];

    /* Create input element */
    var inputElement;
    if (ftype == 'textarea'){
      inputElement = $('<textarea>')
        .text(fvalue)
      ;
    } else if (ftype == 'select'){
      inputElement = $('<select>');
      for (var q=0; q<foptions.length; q++){
        var option = foptions[q];
        inputElement.append($('<option>')
          .attr('value', option[0])
          .text(option[1])
        );
      }
      inputElement.val(fvalue);
    } else {
      inputElement = $('<input>')
        .attr('type', ftype)
        .attr('value', fvalue)
      ;
    }

    /* Create input field and attach to form */
    formEl
      .append($('<label>')
        .addClass('col-sm-3 control-label')
        .append(f.label)
      )
      .append($('<div>')
          .addClass('col-sm-8')
          .append(inputElement
            .addClass('form-control')
            .attr('name', fname)
          )
        );

  }
  return formEl;
};


/** Creates form for editing docpage component */
jq.create_component_form = function(comp){
  comp = comp || {};
  var formFields = [
    {
      label: 'Field Type', name: 'view', value: comp.view,
      options: viewOptions, type: 'select'
    },
    {
      label: 'Data Model Type', name: 'model', value: comp.model,
      options: modelOptions, type: 'select'
    },
    {label: 'Source', name: 'source', value: comp.source, type:'textarea'}
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


/** Creates component terminator element */
jq.component_terminator = function(){
  return $('<hr>').addClass('component-term');
};



/** Creates the "Add Component" button in panels */
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


/** Creates "delete component" button */
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


/** Creates button for appending panels */
jq.add_panel_button = function(){
  return $('<div>')
    .addClass('col-lg-6')
    .append($('<button>')
      .click(ns.docpage.cb.add_panel)
      .addClass('btn btn-primary col-lg-12')
      .text('Add Panel')
    )
  ;
};


/** Creates button for deleting panels */
jq.delete_panel_button = function(){
  return $('<div>')
    .addClass('col-lg-6')
    .append($('<button>')
      .click(ns.docpage.cb.delete_panel)
      .addClass('btn btn-danger col-lg-12')
      .text('Delete Panel')
    )
  ;
};


/** Creates new panel */
jq.empty_panel = function(){
  /* Get initial header panel and use as prototype for panel */
  var protoPanel = $('div.outer-content-box')[0]
  var protoRow = protoPanel.childNodes[0];
  var protoBox = protoRow.childNodes[0];

  /* Create new panel */
  var newPanel = document.createElement('div');
  newPanel.className = protoPanel.className;

  /* Create new row */
  var newRow = document.createElement('div');
  newRow.className = protoRow.className;
  newPanel.appendChild(newRow);

  /* Create new content box */
  var newBox = document.createElement('div');
  newBox.className = protoBox.className;
  newRow.appendChild(newBox);

  return [newPanel, newRow, newBox];
};


ns.docpage.jq = jq;


/******************\
|* Misc Functions *|
\******************/
var misc = {};


/**
 * Creates and adds new panel after existing panel
 * @param prevPanel Existing panel div to insert after
 * @return Newly created panel (div)
 */
misc.add_panel = function(prevPanel, header){
  /* Create new panel */
  var panelSet = ns.docpage.jq.empty_panel();
  var newPanel = panelSet[0];
  var newBox = panelSet[2];
  header = header || '';

  /* Create panel elements */
  newBox.appendChild($('<h2>').text('Panel')[0]);
  var form = [{
    'label': 'Header:', 'name': 'header', 'type': 'text', 'value': header
  }];
  $(newBox)
    .append($('<div>')
      .addClass('container-fluid')
      .appendRow(ns.docpage.jq.create_form(form))
      .appendRow(ns.docpage.jq.add_component_button())
      .append(ns.docpage.jq.component_terminator())
    )
    .append($('<div>')
      .addClass('container-fluid')
      .appendRow([
        ns.docpage.jq.add_panel_button(),
        ns.docpage.jq.delete_panel_button()
      ])
    )
  ;

  /* Add it in */
  $(prevPanel).after(newPanel);

  return newPanel;
};


/**
 * Creates and adds new component after existing terminator
 * @param hrTerm Component terminator to add after
 * @param comp Optional component field values
 * @return Newly created component form
 */
misc.add_component = function(hrTerm, comp){
  var compForm = ns.docpage.jq.create_component_form(comp)
  $(hrTerm).parent().after(compForm);

  return compForm;
};


/**
 * Gathers up data in docpage editor fields
 * @return String representation of JSON docpage data
 *   [
 *     {
 *       'header': <panel header>,
 *       'components': [
 *          { <component field name>: <component field value>, ... }
 *       ], ...
 *     }, ...
 *   ]
 */
misc.gather_docpage_data = function(){
  /* Submission data */
  var panels = [];

  /* Loop over panels */
  var boxes = $('div.content-box');
  var box_len = boxes.size();
  for (var i=1; i<box_len; i++){
    var box = $(boxes[i]);    // Content box of panel
    var panel = {'components': []}; // Panel data

    /* Panel header */
    panel['header'] = box.find('input[name="header"]').val();

    /* Loop over components */
    var components = box.find('div.component-form div.row form');
    var component_len = components.size();
    for (var j=0; j<component_len; j++){
      var form = $(components[j]); // Component form
      var component = {}; // Component data

      /* Read value attributes from inputs */
      var form_inputs = form.find('input');
      var form_input_len = form_inputs.size();
      for (var k=0; k<form_input_len; k++){
        /* Map form to component */
        var input = form_inputs[k];
        component[input.name] = input.value;
      }

      /* Read text area input */
      var formAreas = form.find('textarea');
      var formAreasLen = formAreas.size();
      for (var k=0; k<formAreasLen; k++){
        var textArea = formAreas[k];
        component[textArea.name] = $(textArea).val();
      }

      /* Read select input */
      var selects = form.find('select');
      var selectsLen = selects.size();
      for (var k=0; k<selectsLen; k++){
        var select = selects[k];
        component[select.name] = $(select).val();
      }

      /* Add component data */
      panel.components.push(component);
    }

    /* Add panel data */
    panels.push(panel)
  }

  /* Return as string */
  return JSON.stringify(panels);
}


ns.docpage.misc = misc;
