/*
 * Javascript interaction for the recurrence widget.	
 */
$(document).ready(function(){	
	
	// frequency options
	var NEVER = -1,
		YEARLY = 0,
		MONTHLY = 1,
		WEEKLY = 2,
		DAILY = 3;
	
	/////////////
	// Functions
	/////////////
	
	/*
	 * Functions to run when script is first run.
	 */
	function initialize(){
		$('.recurrence-widget .recurrence-byweekday li label, .recurrence-widget .recurrence-bymonth li label').each(function(index, element){
			updateCheckboxStyles(this);
		});
		
		$('.recurrence-widget select.freq').change();
	}
	
	/* Update fields that are shown/hidden based on recurrence frequency value.
	 * 
	 * param obj: the object inside the recurrence widget.  This can be any
	 *      object as long as it's inside a recurrence widget.
	 */
	function updateFields(obj){
		
		// This is the parent recurrence widget container
		var parentContainer = $(obj).closest('.recurrence-widget');
		
		// Initialize widget with correct fields shown based on freq value.
		var freq = parentContainer.find('.freq:first').val();
		
		// Hide all fields except for frequency field
		parentContainer.find('.recurrence-field').hide();
		parentContainer.find('.recurrence-freq').show();
		
		if (freq != NEVER){
			parentContainer.find('.recurrence-interval, .recurrence-ending').show();
		}
		
		if (freq == YEARLY){
			parentContainer.find('.recurrence-byyearday, .recurrence-bymonth').show();
			parentContainer.find('.interval-lbl:first').text('years');
		} else if (freq == MONTHLY){
			parentContainer.find('.recurrence-bymonth, .recurrence-bymonthday, .recurrence-byweekday').show();
			parentContainer.find('.interval-lbl:first').text('months');
		} else if (freq == WEEKLY){
			parentContainer.find('.recurrence-byweekday').show();
			parentContainer.find('.interval-lbl:first').text('weeks');
		} else if (freq == DAILY){
			parentContainer.find('.interval-lbl:first').text('days');
		} else {
			// Do nothing, everything is already hidden or it's an unhandled 
			// frequency option choice.
		}
	}
	
	/*
	 * Update the checkbox styles when an item is selected.
	 * 
	 * obj: the label being clicked
	 */
	function updateCheckboxStyles(obj){
		var $checkbox = $(obj).find('input[type="checkbox"]:first');
		
		if ($checkbox.is(':checked')){
			$(obj).addClass('selected');
		} else {
			$(obj).removeClass('selected');
		}
	}
	
	//////////////////////
	// Add event listeners
	//////////////////////
	
	// When the frequency changes, update the field shown
	$('.recurrence-widget select.freq').on('change', function(e){
		updateFields($(this));
	});
	
	// Put the focus on the correct inputs for the frequency ending
	$('.recurrence-widget .recurrence-ending').on('change focus', '[type="radio"]', function(e){
		var $this = $(this),
			id = $this.attr('id'),
			parent = $this.parent(),
			input = parent.find('label[for="' + id + '"] input'),
			input_value = input.val(),
			container = parent.closest('.recurrence-ending'),
		    val = $this.val(),
		    clear_input = 'count';
		
		input.focus();
		
		
		// Clear both nested labels
		container.find('label input').val('')
		
		// Reset value
		input.val(input_value);
		
	}).on('focus', 'label input', function(e){
		// Make sure the radio is checked for this input
		
		$(this).closest('div').find('input[type="radio"]').click();
	});
	
	// Event listener for updating label classes when selecting weekdays or months
	$('.recurrence-widget .recurrence-byweekday, .recurrence-widget .recurrence-bymonth').on('click', 'li label', function(e){
		updateCheckboxStyles(this);
	});
	
	initialize();
});