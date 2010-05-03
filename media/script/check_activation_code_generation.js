jQuery(function(){
  var formGenerateActivationCode = jQuery('#form-generate-activation-code');
  var fieldActivationCode = formGenerateActivationCode.find('input[name="activation_code"]');
  
    
  formGenerateActivationCode.submit(function(e){
    var form = jQuery(this);  
    jQuery.post('/_at/check/activation/code/', form.serialize(), function(responseData, status){
      form.find('input[name="activation_code"]').val(responseData);
    }, 'json');
    return false;
  });
  
});
