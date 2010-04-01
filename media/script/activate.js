
jQuery(function(){
  var elements = {
    product: jQuery('#products a'),
    dialogInputSerialNumber: jQuery('#dialog-input-serial-number'),
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
    jQuery.post('/activate', activateProducts, function(data){
      console.log(data);
    });
    e.preventDefault();
    e.stopPropagation();
    return false;    
  });
});

/*jQuery(function(){
  var elements = {
    products: jQuery('#products'),
    product: jQuery('#products a'),
    input_serial_number: jQuery('#input-serial-number')
  };
  
  var activate_products = {},
      currentProductId = 0;

  elements.product.click(function(e){
    var elem = jQuery(this),
        content = elements.input_serial_number,
        currentProductId = elem.attr('id');
    content.modal({});
    e.stopPropagation();
    e.preventDefault();
    return false;
  });
  
  jQuery('#simplemodal-container form.input-serial-number').live('submit', function(e){    
    var form = jQuery(this),
      serialNumber = form.find('input[name="serial-number"]').val(),
      machineId = form.find('input[name="machine-id"]').val();

    activate_products[currentProductId] = {
      serialNumber: serialNumber,
      machineId: machineId
    };
    console.log(activate_products);
    jQuery('#' + currentProductId).toggleClass('selected');
    jQuery.modal.close();
    return false;
  });
});
*/
