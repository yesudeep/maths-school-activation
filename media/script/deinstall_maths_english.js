jQuery(function(){
    var elements = {
        formDeactivationEntryCodeByTimezone: jQuery('#form-deactivation-entry-code-by-timezone'),
        spanDeactivationEntryCode: jQuery('#deactivation-entry-code'),
        formMachineID: jQuery('#form-machine-id')
    };
    
    elements.formDeactivationEntryCodeByTimezone.ajaxForm({
        dataType: 'json',
        success: function(responseText){
            var deactivationEntryCode = responseText.deactivationEntryCode;
            var timezone = responseText.timezone;
            
            var fieldDeactivationEntryCode = elements.formMachineID.find('input[name="deactivation_entry_code"]');
            var fieldTimezone = elements.formMachineID.find('input[name="timezone"]');
            
            fieldTimezone.val(timezone);
            elements.spanDeactivationEntryCode.text(deactivationEntryCode);
            fieldDeactivationEntryCode.val(deactivationEntryCode);
        }
    });
    
    elements.formMachineID.validate();
});
