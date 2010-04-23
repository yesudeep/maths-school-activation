
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
    jQuery.post('/activate', {data: JSON.stringify(activateProducts)}, function(data){
      if (data.url != ""){
        window.location = data.url;
      }
    }, 'json');
    e.preventDefault();
    e.stopPropagation();
    return false;    
  });
});
