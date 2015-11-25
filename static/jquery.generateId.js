;(function($) {
	$.generateId = function() {
		return arguments.callee.prefix + arguments.callee.count++;
	};
	$.generateId.prefix = 'jq$';
	$.generateId.count = 0;

	$.fn.generateId = function() {
		return this.each(function() {
			this.id = $.generateId();
		});
	};
})(jQuery);