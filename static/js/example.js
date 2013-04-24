function attach_example_fetch_events()
{
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

                    if($.trim(sent) == '')
                    {
                        // pass
                    }else{
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
                    }
             
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

                // url: "examples/" + ngramText,
                url: 'static/cultivate_relationships.json',
                type: "GET",
                dataType: "json",
            });
            exRequest.done(function(data){

                if(data.status)
                {
                    // get example successfully
                    // construct html element
                    var sent = data.sent[0];

                    if($.trim(sent) == '')
                    {
                        // pass
                    }else{
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
                    }
                
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
}