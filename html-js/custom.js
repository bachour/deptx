$(document).ready(function(){
    // show popup when you click on the link
    $('.show-popup').click(function(event){
        event.preventDefault(); // disable normal link function so that it doesn't refresh the page
        $('.overlay-bg').show(); //display your popup
        
        $.getJSON("https://dl.dropboxusercontent.com/u/17451725/PROV_Blood-1Kclean.json", function(json) {
       	   loadJSONProv(json);
       	   loadImages(initStage);
       	 });
    });

    // hide popup when user clicks on close button
   // $('.close-btn').click(function(){
   // 	$('.overlay-bg').hide(); // hide the overlay
    //});
    
    

});