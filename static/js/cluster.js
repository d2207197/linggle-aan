$('.entry-example').find('img').live('click',function(){

	// console.log('trigger example.');

	var entry = $(this).parents('.entry');
	var next = entry.next();
	// check if example fetched
	if(!next.hasClass('example-container'))
	{
		// not fetched, i.e., example not exists
		// fetch example
		// $.get()....

		// get example successfully
		// construct html element
		var example = $('<div/>').addClass('example-container hide');
		var quoteleft = $('<div/>').appendTo(example);
		$('<img/>').attr('src','static/img/quote-left.png').appendTo(quoteleft);

		var examplesent = $('<div/>').html('Farmers should <strong>cultivate</strong> their <strong>crops</strong> to get a good harvest.').appendTo(example);
		var quoteright = $('<div/>').appendTo(example);
		$('<img/>').attr('src','static/img/quote-right.png').appendTo(quoteright);	
		// insert the example
		entry.after(example);


		// toggle example
		entry.find('.entry-example').find('img').toggleClass('hide');
		example.toggleClass('hide');		
	}else
	{
		entry.find('.entry-example').find('img').toggleClass('hide');
		next.toggleClass('hide');
	}

	

})
