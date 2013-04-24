var THRESHOLD = 5;
var AutoOnTopK = 3;

function _show_clustering_results(data)
{
	var cluster_container = $('#clusters-container');
	// cluster_container.html('');
	var k = 0;
	$.each(data, function(cidx, c){
		// get cluster label, e.g., relationship
		var members = c.data;
		// console.log('members',members);
		
		var cid = 'c' + (k).toString();
		if(k % 2 == 0)cluster_theme = 'cluster-even';
		else cluster_theme = 'cluster-odd';
		k++;

		// generate cluster tag
		var tag_container = $('<div/>').addClass('tag-container f small').attr('idx',cid).appendTo($('#cluster-tag-container'));
		var tag_status = $('<div/>').addClass('tag-status').appendTo(tag_container);

		$('<img/>').addClass('hide').attr('src','static/img/tag-on.png').appendTo(tag_status);
		$('<img/>').attr('src','static/img/tag-off.png').appendTo(tag_status);

		var tag_text = $('<div/>').addClass('tag-text').appendTo(tag_container);
		
		$('<span/>').text(c.tag).appendTo(tag_text);
		$('<span/>').addClass('tag-text-count').text('('+members.length.toString()+')').appendTo(tag_text);

		var cluster = $('<div/>').addClass('cluster hide').attr('id',cid).addClass(cluster_theme).appendTo(cluster_container);
		var cluster_label_container = $('<div/>').addClass('cluster-label-container').appendTo(cluster);
		var cluster_label_mask = $('<div/>').addClass('cluster-label-mask').appendTo(cluster_label_container);
		var cluster_label = $('<div/>').addClass('cluster-label').text(c.tag).appendTo(cluster_label_container);
		
		var entry_wrap = $('<div/>').addClass('entry-wrap').appendTo(cluster);


		$.each(members, function(i){
			// get all members
			ngram = members[i][0];
			count = members[i][1];
			percent = members[i][2];
			
			if(i >= THRESHOLD) {
				fold = 'fold-target hide';
			}else{
				fold = '';
			}

			var entry = $('<div/>').addClass('entry '+fold).appendTo(entry_wrap);

			var entry_ngram = $('<div/>').addClass('entry-ngram').html(ngram).appendTo(entry);
			var entry_count = $('<div/>').addClass('entry-count').text(count).appendTo(entry);
			var entry_percent = $('<div/>').addClass('entry-percent').text(percent).appendTo(entry);
			var entry_example = $('<div/>').addClass('entry-example').appendTo(entry);

			var example_btn_expand = $('<img/>').addClass('entry-example-btn-expand').attr('src','static/img/example-btn.png').appendTo(entry_example);
			var example_btn_shrink = $('<img/>').addClass('entry-example-btn-shrink hide').attr('src','static/img/example-btn-shrink.png').appendTo(entry_example);
		});

		// add the (more) item
		// console.log(entry_wrap.find('.entry').length);
		// console.log();
		if(entry_wrap.find('.entry').length >= THRESHOLD)
		{
			var more_wrap = $('<div/>').addClass('more-wrap').appendTo(cluster);
			$('<span/>').addClass('more-text').text('(more ' + entry_wrap.find('.fold-target').length.toString() + '...)').appendTo(more_wrap);
			$('<span/>').addClass('more-text hide').text('(less)').appendTo(more_wrap);
		}
	});

	// turn on top-3 cluster
	$.each($('.tag-container'), function(i, obj){
		if(i < AutoOnTopK)
		{
			obj.click();	
		}
	});
	
}

///
/// Handle the example expand/shrink events for traditional results
///
$('.item-example').find('img').live('click',function(){
	var item = $(this).parents('.item');
	var next = item.next();
	var ngramText = item.find('.item-ngram-text').text()

	if(!next.hasClass('item-example-container'))
	{
		$('#search-loading').find('img').show(0);

		var exRequest = $.ajax({
			url: "examples/" + ngramText,
			type: "GET",
			dataType: "json",
		});
		exRequest.done(function(data){
			if(data.status)
			{
				var sent = data.sent[0];
				var item_example = $('<tr/>').addClass('item-example-container hide');
				var item_example_container = $('<td/>').attr('colspan',4).appendTo(item_example);

				var quoteleft = $('<div/>').addClass('quoteleft').appendTo(item_example_container);
				$('<img/>').attr('src','static/img/quote-left.png').appendTo(quoteleft);

				$('<div/>').addClass('example-sent-new').html(sent).appendTo(item_example_container);

				var quoteright = $('<div/>').addClass('quoteright').appendTo(item_example_container);
				$('<img/>').attr('src','static/img/quote-right.png').appendTo(quoteright);	

				item.after(item_example);

				// toggle example
				item.find('.item-example').find('img').toggleClass('hide');
				item_example.toggleClass('hide');				
			}else{
				item.find('.item-example').find('img').remove();
			}
		});
		exRequest.complete(function(data){
			$('#search-loading').find('img').hide(0);

			if(data.readyState != 4)
			{
				// return false;
				
			}else{


			}
		});		
	}else
	{
		item.find('.item-example').find('img').toggleClass('hide');
		next.toggleClass('hide');
	}
});

///
/// Handle the example expand/shrink events for cluster results
///
$('.entry-example').find('img').live('click',function(){

	// console.log('trigger example.');

	var entry = $(this).parents('.entry');
	var next = entry.next();
	var ngramText = entry.find('.entry-ngram').text();

	// check if example fetched
	if(!next.hasClass('example-container'))
	{
		// not fetched, i.e., example not exists
		// fetch example
		// $.get()....
		$('#search-loading').find('img').show(0);
		var exRequest = $.ajax({

			url: "examples/" + ngramText,
			// url: 'static/cultivate_relationships.json',
			type: "GET",
			dataType: "json",
		});
		exRequest.done(function(data){

			if(data.status)
			{
				// get example successfully
				// construct html element
				var sent = data.sent[0];
				var example = $('<div/>').addClass('example-container hide');
				var quoteleft = $('<div/>').addClass('quoteleft-cluster').appendTo(example);
				$('<img/>').attr('src','static/img/quote-left.png').appendTo(quoteleft);

				var examplesent = $('<div/>').addClass('example-sent').html(sent).appendTo(example);

				var quoteright = $('<div/>').addClass('quoteright-cluster').appendTo(example);
				$('<img/>').attr('src','static/img/quote-right.png').appendTo(quoteright);	

				// insert the example
				entry.after(example);

				// toggle example
				entry.find('.entry-example').find('img').toggleClass('hide');
				example.toggleClass('hide');				
			}else{
				// 
				// no sent
				// 
				entry.find('.entry-example').find('img').remove();
			}
		});
		exRequest.complete(function(data){
			$('#search-loading').find('img').hide(0);
			if(data.readyState != 4){}
		});
		
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

