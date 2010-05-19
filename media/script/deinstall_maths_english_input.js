jQuery(function(){
    
    jQuery.validator.addMethod("deactivation_code", function(deactivation_code, element) {
        deactivation_code = deactivation_code.replace(/\s+/g, ""); 
    	
    	return this.optional(element) || deactivation_code.length == 10 &&
    		deactivation_code.match(/^\d{10}$/);
    }, "Invalid code.");


    var elements = {
        formInputDeactivationCodes: jQuery('#form-input-deactivation-codes')
    };
    
    elements.formInputDeactivationCodes.validate();
});
