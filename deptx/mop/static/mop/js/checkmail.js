var opts = {
	lines: 13, // The number of lines to draw
	length: 20, // The length of each line
	width: 10, // The line thickness
	radius: 30, // The radius of the inner circle
	corners: 1, // Corner roundness (0..1)
	rotate: 0, // The rotation offset
	direction: 1, // 1: clockwise, -1: counterclockwise
	color: '#000', // #rgb or #rrggbb or array of colors
	speed: 1, // Rounds per second
	trail: 60, // Afterglow percentage
	shadow: false, // Whether to render a shadow
	hwaccel: false, // Whether to use hardware acceleration
	className: 'spinner', // The CSS class to assign to the spinner
	zIndex: 2e9, // The z-index (defaults to 2000000000)
	top: 'auto', // Top position relative to parent in px
	left: 'auto', // Left position relative to parent in px
	position: 'relative',
};

var target;
var spinner;
var audioGotMail;

$(function() {
	target = document.getElementById('spinner');
	audioGotMail = document.createElement('audio');
	audioGotMail.setAttribute('src', NEW_MAIL_AUDIO );
	
});

window.setInterval(function(){
	mailfield = $('#checkmail');
	inboxfield = $('#inbox');
	
	spinner = new Spinner(opts).spin(target);
	mailfield.html('checking mail...');
	
	setTimeout(function(){
	
		$.ajax
		(
			{
		    	type: "POST",
		    	url: CHECK_MAIL_URL,
		    	data:
		    	{
		    		'test': 'success',
	    		},
	    		success: function(data)
	    		{
	      			if (data.new_mail==false) {
	      				mailfield.html('no new messages');
	      			}
	      			else {
	      				mailfield.html(data.total_unread + ' unread message(s)');
	      				inboxfield.val('inbox (' + data.total_unread + ')');
	      				audioGotMail.play();
	      			};
	      			spinner.stop();
	      			
	     		},
	    		error: function()
	    		{
	        		mailfield.html('error checking messages');
	        		spinner.stop();
				}
			}
		);
	
	},5000);
	
	
	
  
}, 10000);