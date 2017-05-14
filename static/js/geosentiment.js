$(document).ready(function(){

	$('#search').on('click', function(){

		if($('#searchbar').val() == ''){

       	   alert("Since you left the searchbar blank, we'll pick a random word for you");
        }

		$('#loader-wrapper').css('display', 'block');

	})
})