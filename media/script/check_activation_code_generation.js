jQuery(function(){
  var formGenerateActivationCode = jQuery('#form-generate-activation-code');
  var fieldActivationCode = formGenerateActivationCode.find('input[name="activation_code"]');
  
  formGenerateActivationCode.ajaxForm({
    type: 'post',
    success: function(responseData){
      console.log(responseData);
      fieldActivationCode.val(responseData);
    }
  });
});
