"use strict";
/**
 * Jquery plugin for client-server form validations
 * API entry points are jQuery().validator() and jQuery().validate()
 * 
 */

(function($){
  /***************************************************************************\
  | Plugin Initialization (Private API)                                       |
  \***************************************************************************/
  /* Internal plugin registry */
  var plugin = {
    /** Set to true when it is safe to call bind() on selector strings */
    canbind: false,

    /** Registry of all validator contexts */
    registry: [],

    /** Default values for validator contexts */
    validator_defaults: {
      logsel: '', // default form log-panel selector
      formsel: 'form', // default form selector
      subsel: 'button[type="submit"]', // default form submit selector
      multibind: false, // Whether or not to apply multibind selectors
      logstatus: 'default' // Default log panel status
    },

    /** Enumeration of logging statuses */
    log_status: {
      info: 'info',
      warn: 'warning',
      good: 'success',
      error: 'danger',
      success: 'success',
      warning: 'warning'
    }
  };

  /**
   * Registers context configuration with plugin
   * @param context New context config
   */
  plugin.register = function(context){
    plugin.registry.push(context);
  };

  /**
   * Registers a binding between a callback and a selection of elements
   * @param Context configuration for binding
   * @param Element selector
   * @param Callback Validation code to be called on selector
   */
  plugin.bind = function(context, selector, callback){
    if (plugin.canbind){
      /* Can directly bind a callback to the given selector */
      var els = $(selector);
      var elnum = context.__multibind__ ? els.length : 1;
      for (var i=0; i<elnum; i++){
        var binding = {
          element: els[i],
          callback: callback,
          selector: selector
        };
        context.__binding__.push(binding);

        /* Bind element updates to check context */
        var elementChangeCallback = (function (ctx, bnd){
          return function(e){
            var res = bnd.callback(bnd.element);
            if (res){
              /* Error found, log it */
              plugin.log(ctx, res, plugin.log_status.error);
              plugin.lock(ctx);

            } else {
              /* Error not found, check other conditions */
              plugin.attempt_unlock(ctx);
            }
          };
        })(context, binding);

        $(binding.element).on('input', elementChangeCallback);
      }

    } else {
      /* Can't bind the callback yet */
      if (selector in context.__prebinding__){
        context.__prebinding__[selector].push(callback);
      } else {
        context.__prebinding__[selector] = [callback];
      }
    }
  };

  /**
   * Keeps submission locked
   */
  plugin.lock = function(context){
    var els = $(context.__subsel__);
    var elnum = context.__multibind__ ? els.length : 1;
    for (var i=0; i<elnum; i++){
      var el = $(els[i]);
      el.attr('disabled', 'true')
        .text("X")
        .removeClass('active')
        .addClass('disabled');
    }
  };

  /**
   * Attempts to unlock a form
   */
  plugin.attempt_unlock = function(context){
    /* Run over bindings */
    for (var b in context.__binding__){
      /* Evaluate callback on bound element */
      var binding = context.__binding__[b];
      var res = binding.callback(binding.element);
      if (res){
        /* Error encountered */
        plugin.log(context, res, plugin.log_status.error);
        plugin.lock(context);
        return;
      }
    }
    /* Check for prepost backend checking */
    if (context.__prepost__){
      plugin.log(context, 'Checking ...', plugin.log_status.warn);
      var sendData = {};
      var elInputs = $(context.__formsel__ +' input');
      elInputs.each(function (i, elIn){
        var $elIn = $(elIn);
        var elInType = $elIn.attr('type');
        var elInName = $elIn.attr('name');
        if (elInType !== 'hidden' && elInType !== 'password'){
          sendData[elInName] = encodeURIComponent($elIn.val());
        }
      });
      $.getJSON(context.__prepost__, sendData, function(data){
        if (data.status.toLowerCase() === 'error'){
          var msg = data.message || 'Form validation failed!';
          plugin.log(context, msg, plugin.log_status.error);

        } else {
          plugin.unlock(context);
        }
      });

    } else {
      plugin.unlock(context);
    }
  };

  /**
   * Unlocks a form
   */
  plugin.unlock = function(context){
    /* No errors encountered, unlock form */
    var els = $(context.__subsel__);
    var elnum = context.__multibind__ ? els.length : 1;
    for (var i=0; i<elnum; i++){
      var el = $(els[i]);
      var btnText = el.attr('data-text') || 'Submit';
      console.log(btnText);
      el.removeAttr('disabled')
        .text(btnText)
        .removeClass('disabled')
        .addClass('active');
    }
    plugin.log(context, 'Ready to Submit', plugin.log_status.success);
  };

  /**
   * Logs validator-specific message
   */
  plugin.log = function(context, message, errStat){
    if ('__logger__' in context){
      $(context.__logger__.children()[0]).text(message);

      if (errStat){
        /* Set alert status of logging element */
        if ('__logstatus__' in context){
          context.__logger__.removeClass('panel-'+ context.__logstatus__);
        }
        context.__logger__.addClass('panel-'+errStat);
        context.__logstatus__ = errStat;
      }

    } else {
      /* No bound logger element, just send message to console */
      var errPrefix = errStat ? "[info] " : "["+errStat+"] ";
      console.log(errPrefix + message);
    }
  };


  /***************************************************************************\
  | Validator Context (Public API)                                            |
  \***************************************************************************/
  plugin.generate_validator_context = function(template){
    /* Register new validation instance */
    var validator_context = {
      __logsel__: plugin.validator_defaults.logsel,
      __subsel__: plugin.validator_defaults.subsel,
      __formsel__: plugin.validator_defaults.formsel,
      __binding__: [],
      __prepost__: '',
      __subtext__: '',
      __multibind__: plugin.validator_defaults.multibind,
      __logstatus__: plugin.validator_defaults.logstatus,
      __prebinding__: {}
    };
    if (template){
      if (typeof(template) === 'string'){
        /* Interpet template strings as form selectors */
        validator_context.__formsel__ = template;

      } else {
        /* Interpret template objects as inheritable context */
        validator_context.__logsel__ = template.__logsel__ || '';
        validator_context.__formsel__ = template.__formsel__ || '';
        validator_context.__multibind__ = template.__multibind__ || '';
      }
    }
    plugin.register(validator_context);


    /**
     * Deferred binding for a list of fields
     * @param jqargs Object list of selector-callbacks for binding
     * @return Updated validator instance
     */
    validator_context.validate = (function(ctx){
      return function(jqargs){
        for (var selector in jqargs){
          plugin.bind(ctx, selector, jqargs[selector]);
        }
        return ctx;
      };
    })(validator_context);

    /**
     * Bind a logger for the current context
     * @param jqargs Selector for logging element(s)
     * @return Updated validator instance
     */
    validator_context.logger = (function(ctx){
      return function(jqargs){
        ctx.__logsel__ = jqargs;
        return ctx;
      };
    })(validator_context);

    /**
     * Turns on form multibinding
     * @return Updated validator instance
     */
    validator_context.multibind = (function(ctx){
      return function(jqargs){
        ctx.__multibind__ = true;
        return ctx;
      }
    })(validator_context);

    /**
     * Turns off form multibinding
     * @return Updated validator instance
     */
    validator_context.singlebind = (function(ctx){
      return function(jqargs){
        ctx.__multibind__ = false;
        return ctx;
      }
    })(validator_context);

    /**
     * Sets the ajax prepost checker
     */
    validator_context.prepost = (function(ctx){
      return function(jqargs){
        ctx.__prepost__ = jqargs;
        return ctx;
      }
    })(validator_context);

    /**
     * Sets form submission
     */
    validator_context.submit = (function(ctx){
      return function(jqargs){
        ctx.__subsel__ = jqargs;
        return ctx;
      };
    })(validator_context);

    return validator_context;
  };


  /* Bind validation generators to jquery */
  var congen = plugin.generate_validator_context;
  $.fn.validator = congen;
  $.fn.validate = congen('form').logger('.log-panel').validate;


  /***************************************************************************\
  | Document Loaded                                                           |
  \***************************************************************************/
  $(document).ready(function(){
    plugin.canbind = true;

    /* Re-bind deferred callbacks */
    for (var ir in plugin.registry){
      /* For contexts in registry */
      var context = plugin.registry[ir];

      /* Bind logging elements first */
      if (context.__logsel__){
        context.__logger__ = $(context.__logsel__);
      };

      /* Bind validation callbacks next */
      for (var selector in context.__prebinding__){
        /* For unbound callback list for each selector in context */
        var callbacks = context.__prebinding__[selector];
        for (var ic in callbacks){
          /* For callback in list of callbacks */
          plugin.bind(context, selector, callbacks[ic]);
        }
      }
      /* Clear out prebinding object */
      context.__prebinding__ = {};

      /* Apply first checks if no page-errors are baked in */
      if (!context.__logger__.hasClass('panel-danger')){
        plugin.attempt_unlock(context);
      }
    }
  });

})(jQuery);


function checkAlphaNumeric(x){
  var uname = $(x).val();
  if (! /^\w+$/.test(uname) ){
    return 'User name may only countain letters and numbers';
  }
}


/**
 * Checks to make sure password fields match eachother
 * @param password Password field jq element
 * @param repeat Optional password repeat field
 */
function checkPassword(password, repeat){
  var pass = $(password).val();
  if (pass === undefined){
    console.log("Warning, password checker passed undefined element");
    return '';
  }

  if (pass.length < 6){
    return 'Password must be at least six characters long';
  } else if (repeat !== undefined && pass !== $(repeat).val()) {
    return 'Password fields do not match';
  }
}


/**
 * Checks to make sure email address is okay
 */
function checkEmail(x){
  var v = $(x).val();
  if (v === undefined){
    console.log("Warning, email checker passed undefined element");
    return '';
  }

  if (v.length == 0){
    return ' ';
  } else if ( !/.+@.+/.test(v) ){
    return 'Invalid email address';
  }
}
