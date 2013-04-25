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
	// check_style();
}

function attach_cluster_tag_event()
{
	$('.tag-container').live('click',function(){

		$(this).find('.tag-status').find('img').toggleClass('hide');
		$(this).toggleClass('tag-on');

		var tag_on = $('.tag-on');
		$('.cluster').addClass('hide');

		$.each(tag_on, function(i){
			var idx = tag_on.eq(i).attr('idx');

			if(i % 2 == 0)cluster_theme = 'cluster-even';
			else cluster_theme = 'cluster-odd';

			var isMacLike = navigator.userAgent.match(/(Mac|iPhone|iPod|iPad)/i)?true:false;

			if(isMacLike)cluster_theme = cluster_theme + '-apple';
			$('#'+idx).removeClass('hide cluster-even cluster-odd cluster-even-apple cluster-odd-apple').addClass(cluster_theme);
		})
	});
}

