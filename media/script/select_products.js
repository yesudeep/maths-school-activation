jQuery(function(){
  var elements = {
    productLinks: jQuery('#products a'),
    buttonActivate: jQuery('#button-activate'),
    dialogSubscription: jQuery('#dialog-subscription'),
    dialogNotification: jQuery('#dialog-notification'),
    buttonCancelSubscriptionPeriod: jQuery('#form-subscription-period .button-cancel'),
    buttonHideNotification: jQuery('#form-Notification .button-ok'),
    formSubscriptionPeriod: jQuery('#form-subscription-period'),
    fieldSubscriptionPeriod: jQuery('#form-subscription-period select[name="period"]')
  };
  
  var selectedClassName = 'selected';
  var subscriptionData = {
    products: {},
    period: 0
  };

  // Mark the clicked product as selected.
  elements.productLinks.click(function(e){
    var elem = jQuery(this);
    var selectedProductKey = elem.attr('id');
    
    if (elem.hasClass(selectedClassName)){
      elem.removeClass(selectedClassName);
      delete subscriptionData.products[selectedProductKey];
    } else {
      subscriptionData.products[selectedProductKey] = true;
      elem.addClass(selectedClassName);
    }
    
    var elem = jQuery(this);
    elements.dialogNotification.slideToggle('slow');
    e.preventDefault();
    e.stopPropagation();
  
  // Cancel hides the subscription period dialog.
  elements.buttonHideNotification.click(function(e){
    elements.dialogNotification.fadeOut('slow');
    e.preventDefault();
    e.stopPropagation();
    return false;
  });
    
    // Prevent default behavior and stop event bubbling.
    e.preventDefault();
    e.stopPropagation();
    return false;
  });

  // Show the activation subscription period dialog.
  elements.buttonActivate.click(function(e){
    var elem = jQuery(this);
    elements.dialogSubscription.slideToggle('slow');
    e.preventDefault();
    e.stopPropagation();
    return false;
  });
  
  // Cancel hides the subscription period dialog.
  elements.buttonCancelSubscriptionPeriod.click(function(e){
    elements.dialogSubscription.fadeOut('slow');
    e.preventDefault();
    e.stopPropagation();
    return false;
  });
  

  // Ok.  We've got all the information we need, send the data to the server.
  elements.formSubscriptionPeriod.submit(function(e){
    subscriptionData.period = parseInt(elements.fieldSubscriptionPeriod.val(), 10);      
    elements.dialogSubscription.fadeOut('slow');
    
    jQuery.post('/activate/select', {payload: JSON.stringify(subscriptionData)}, function(response){
      if (response.url && response.url != ""){
        window.location = response.url;
      }
    }, 'json');
    
    e.preventDefault();
    e.stopPropagation();
    return false;
  });
  
  
});

/*
jQuery(function(){
  var elements = {
    product: jQuery('#products a'),
    dialogInputSerialNumber: jQuery('#dialog-input-serial-number'),
    fieldSerialNumber: jQuery('#dialog-input-serial-number').find('input[name="serial-number"]'),
    //fieldMachineId: jQuery('#dialog-input-serial-number').find('input[name="machine-id"]'),
    dialogInputSerialNumberOK: jQuery('#dialog-input-serial-number .button-ok'),
    dialogInputSerialNumberCancel: jQuery('#dialog-input-serial-number .button-cancel'),
    formInputSerialNumber: jQuery('#form-input-serial-number'),
    buttonActivate: jQuery('#button-activate')
  };
  var selectedProductKey, activateProducts={};
  
  elements.product.click(function(e){
    var elem = jQuery(this);
    selectedProductKey = elem.attr('id');
    if (elem.hasClass('selected')){
      elem.removeClass('selected');
      delete activateProducts[selectedProductKey];
    } else {
    	elements.dialogInputSerialNumber.slideToggle('slow');      
    }
    elements.fieldSerialNumber.focus();
  	e.preventDefault();
  	e.stopPropagation();
  	return false;
  });
  
  elements.formInputSerialNumber.submit(function(e){
    var form = jQuery(this),
      serialNumberField = form.find('input[name="serial-number"]'),
      machineIdField = form.find('input[name="machine-id"]');
    activateProducts[selectedProductKey] = {
      serialNumber: serialNumberField.val(),
      machineId: machineIdField.val()
    };
    jQuery('#' + selectedProductKey).toggleClass('selected');
    elements.dialogInputSerialNumber.fadeOut('slow');
    serialNumberField.val("");
    machineIdField.val("");

    e.preventDefault();
    e.stopPropagation();
    return false;
  });
  
  elements.dialogInputSerialNumberCancel.click(function(e){
    elements.dialogInputSerialNumber.fadeOut('slow');
    e.preventDefault();
    e.stopPropagation();
    return false;
  });
  
  elements.buttonActivate.click(function(e){
    jQuery.post('/activate/select', {data: JSON.stringify(activateProducts)}, function(data){
      if (data.url != ""){
        window.location = data.url;
      }
    }, 'json');
    e.preventDefault();
    e.stopPropagation();
    return false;    
  });
});
*/
