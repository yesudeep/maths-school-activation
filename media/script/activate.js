jQuery(".btn-slide").click(function(){
	jQuery(".panel").slideToggle("slow");
});
jQuery("#cancel-button").click(function(){
  jQuery(".panel").fadeOut("slow");
});
jQuery("#activate-product-button").click(function(){
  jQuery(".panel").fadeOut("slow");
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
