jQuery(function(){
    var elements = {
        formDeinstallationEntryCodeByTimezone: jQuery('#form-deinstallation-entry-code-by-timezone'),
        deinstallationEntryCode: jQuery('#deinstallation-entry-code')
    };
    
    elements.formDeinstallationEntryCodeByTimezone.ajaxForm({
        dataType: 'json',
        success: function(responseText){
           elements.deinstallationEntryCode.text(responseText.deactivationEntryCode);
        }
    });
});