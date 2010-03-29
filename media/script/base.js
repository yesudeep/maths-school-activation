jQuery(document).ready(function() {
	jQuery('input[title]').each(function() {
		if(jQuery(this).val() === '') {
			jQuery(this).val($(this).attr('title'));
		}

		jQuery(this).focus(function() {
			if(jQuery(this).val() === jQuery(this).attr('title')) {
				jQuery(this).val('').addClass('focused');
			}
		});

		jQuery(this).blur(function() {
			if(jQuery(this).val() === '') {
				jQuery(this).val(jQuery(this).attr('title')).removeClass('focused');
			}
		});
	});
});
