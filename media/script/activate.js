
jQuery(function(){
  var elements = {
    product: jQuery('#products a'),
    dialog_input_serial_number: jQuery('#dialog-input-serial-number'),
    dialog_input_serial_number_ok: jQuery('#dialog-input-serial-number .button-ok'),
    dialog_input_serial_number_cancel: jQuery('#dialog-input-serial-number .button-cancel')
  };
  
  elements.product.click(function(e){
  	elements.dialog_input_serial_number.slideToggle('slow');
  	e.preventDefault();
  	e.stopPropagation();
  	return false;
  });
  elements.dialog_input_serial_number_ok.click(function(e){
    elements.dialog_input_serial_number.fadeOut('slow');
    e.preventDefault();
    e.stopPropagation();
    return false;
  });
  elements.dialog_input_serial_number_cancel.click(function(e){
    elements.dialog_input_serial_number.fadeOut('slow');
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
