jQuery(function(){
  var elements = {
    products: jQuery('#products'),
    product: jQuery('#products a')
  };
  
  var activate_products = [];
  
  elements.product.click(function(e){
    
    
    
    jQuery(this).toggleClass('selected');
    e.stopPropagation();
    e.preventDefault();
    return false;
  });
});