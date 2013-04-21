function _test_cluster()
{
	// get cluster data from wujc
	// $.each() ...
	// ...
	var getCluster = $.ajax({
  		url: "/static/test.json",
  		type: "get",
  		dataType: "json"
	});

	var cluster_container = $('#clusters-container');

	getCluster.done(function(data){

		
		$.each(data, function(cluster_type, c){
			// get cluster type, e.g., VN:cultivate $N
			
			var i = 0;
			$.each(c, function(cluster_label, memebers){
				// get cluster label, e.g., relationship

				i++;
				var cid = 'c' + (i).toString();

				if(i % 2 == 0)cluster_theme = 'cluster-even';
				else cluster_theme = 'cluster-odd';

				// generate cluster tag
				var tag_container = $('<div/>').addClass('tag-container f small tag-on').attr('idx',cid).appendTo($('#cluster-tag-container'));
				var tag_status = $('<div/>').addClass('tag-status').appendTo(tag_container);
				$('<img/>').attr('src','static/img/tag-on.png').appendTo(tag_status);
				$('<img/>').addClass('hide').attr('src','static/img/tag-off.png').appendTo(tag_status);
				$('<div/>').addClass('tag-text').text(cluster_label).appendTo(tag_container);

				var cluster = $('<div/>').addClass('cluster').attr('id',cid).addClass(cluster_theme).appendTo(cluster_container);

				console.log('Label:',cluster_label);
				var cluster_label_container = $('<div/>').addClass('cluster-label-container').appendTo(cluster);

				var cluster_label_mask = $('<div/>').addClass('cluster-label-mask').appendTo(cluster_label_container);
				var cluster_label = $('<div/>').addClass('cluster-label').text(cluster_label).appendTo(cluster_label_container);
				
				var entry_wrap = $('<div/>').addClass('entry-wrap').appendTo(cluster);
				$.each(memebers, function(i){
					// get all members
					ngram = memebers[i][0];
					count = memebers[i][1];
					percent = memebers[i][2];
					console.log('ngram:',ngram);
					console.log('count:',count);
					console.log('percent:',percent);
					
					var entry = $('<div/>').addClass('entry').appendTo(entry_wrap);

					var entry_ngram = $('<div/>').addClass('entry-ngram').html(ngram).appendTo(entry);
					var entry_count = $('<div/>').addClass('entry-count').text(count).appendTo(entry);
					var entry_percent = $('<div/>').addClass('entry-percent').text(percent).appendTo(entry);
					var entry_example = $('<div/>').addClass('entry-example').appendTo(entry);

					var example_btn_expand = $('<img/>').addClass('entry-example-btn-expand').attr('src','static/img/example-btn.png').appendTo(entry_example);
					var example_btn_shrink = $('<img/>').addClass('entry-example-btn-shrink hide').attr('src','static/img/example-btn-shrink.png').appendTo(entry_example);

					


					
				});

			});
			
		});
	});
	getCluster.fail(function(){});
	getCluster.always(function(){});


}

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

		var examplesent = $('<div/>').addClass('example-sent').html('Farmers should <strong>cultivate</strong> their <strong>crops</strong> to get a good harvest.').appendTo(example);
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
});

$('.tag-container').live('click',function(){
	$(this).find('.tag-status').find('img').toggleClass('hide');
	$(this).toggleClass('tag-on');

	var tag_on = $('.tag-on');
	$('.cluster').addClass('hide');

	$.each(tag_on, function(i){
		var idx = tag_on.eq(i).attr('idx');

		if(i % 2 == 0)cluster_theme = 'cluster-even';
		else cluster_theme = 'cluster-odd';

		$('#'+idx).removeClass('hide cluster-even cluster-odd').addClass(cluster_theme);

	})

	// var idx = $(this).attr('idx');
	// 
	// 
});

