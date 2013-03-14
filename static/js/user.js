
_LOGIN = false; // login or not
_USER = '';
_MSG = '';

function UserEvents()
{
    loginChecker(false);

    UserEventHandler();

    showLogin();

}

function showLogin(){ $('#login-linker').find('.underline-hover').click(); }
function showSignup(){ $('#signup-linker').find('.underline-hover').click(); }

function initForm() { 
    $('#login-email').focus(); 

    // clear password & email
    $('#login-table').find('input[type=password]').val('');
    $('#login-table').find('input[type=text]').val('');

    $('#login-msg').html('');
    $('.warning').removeClass('warning');
}


function loginChecker(PanelControl)
{
    $.get('/login').done(function(data){
        console.log(data);
        if(data.type == 'login')
        {
            _LOGIN = true;
            _MSG = data.msg;
            _USER = data.user;

            if(PanelControl == true)
            {
                hideUserPanel();
            }
        }else
        {
            _LOGIN = false;
            if (PanelControl == true)
            {
                showUserPanel();
            }
        }

        _changeTextByUserStatus();
    })
}


function emptyChecker(form, action)
{
    $.each(form[action], function(i){
        if($.trim($(form[action][i]).val()).length == 0){
            valid = false;
            $(form[action][i]).addClass('warning');
            return false;
        }else {
            valid = true
            $(form[action][i]).removeClass('warning');
            return true;
        }
    });
    return valid
}

function emailChecker()
{
    // valid email address?
    var emailRegex = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i;

    var msg = '';

    matched_format = emailRegex.test($('#login-email').val())

    // console.log(matched_format)

    if (!matched_format)
    {
        $('#login-email').addClass('warning');

        msg = 'Please enter valid <red>email address.</red>'
    }
    return msg;
}


function passwordChecker()
{
    // robustness

    // correctness
    var msg = '';
    if ($('#login-password').val() == $('#login-confirmpassword').val())
    {
        // valid = true;

    }else
    {
        // valid = false;

        msg = 'Please make sure your <red>passwords match.</red>'

        $('#login-password').addClass('warning');
        $('#login-confirmpassword').addClass('warning');
    }
    return msg;
}

// the right panel for login/signup
function showUserPanel()
{
    $('#login-mask').fadeIn(200, function(){
        $('#login-container').slideDown(600,function(){
            initForm();
        });
    });
    
}

function hideUserPanel()
{
    $('#login-container').delay(1000).slideUp(500, function(){
        // .delay(800).fadeIn(400);
        $('#login-mask').fadeOut(200);
    });
    
}

function UserEventHandler()
{
    $('#login-link').click(function(){
        console.log('# login-link trigger');
        if(!_LOGIN){
            initForm();
            showLogin();
            showUserPanel();

        }
    });

    $('#login-table').find('input').keyup(function(event){
        if(event.keyCode == 13)
        {
            var _target_btn;
            btns = $('#login-table').find('button');
            $.each(btns, function(i){
                if(!btns.eq(i).hasClass('hide'))
                {
                    _target_btn = btns.eq(i);
                }
                // consolo.log(btns.attr('style'))
            });
            _target_btn.click();
        }
    });

    $('#show-logout-text').click(function(){
        $.get('/logout', function(data){
            if(data.logout == true)
            {
                _LOGIN = false;
            }else{

            }
            _changeTextByUserStatus()
        });
    });


    $('#login-mask').click(function(){
        hideUserPanel();
    });

    // switch login/ signup mode
    $('#signup-linker').find('.underline-hover').click(function(e){
        $('.for-login').addClass('hide');
        $('.for-signup').removeClass('hide');
        // initForm();
    });
    $('#login-linker').find('.underline-hover').click(function(e){
        $('.for-signup').addClass('hide');
        $('.for-login').removeClass('hide');
        // initForm();
    });


    // <input> modified
    $('#login-wrap').find('input').keyup(function(e){
        if ($(this).val().length > 0){
            $(this).removeClass('warning');
        }
    });


    // login-btn or signup-btn button clicked
    $('#login-btn').click(function(){
        if(_formChecker('login')){
            $.post("/login", 
                { 
                    username: $('#login-email').val(), 
                    password: $('#login-password').val(),
                    utype: "email" 
                })
                .done(function(data) {
                    
                    $('#login-msg').html(data.msg);
                    console.log(data);

                    if(data.type == 'success')
                    {
                        loginChecker(true);
                    }

            });
        }
    });
    $('#signup-btn').click(function(){
        if(_formChecker('signup')){
            loading_img = '<img src="static/img/loading-equip.gif" />'
            $('#login-msg').html(loading_img);
            $.post("/signup", 
                { 
                    username: $('#login-email').val(), 
                    password: $('#login-password').val(),
                    utype: "email" 
                })
                .done(function(data) {
                    
                    $('#login-msg').html(data.msg);
                    console.log(data);

                    if(data.type == 'success')
                    {
                        loginChecker(true);
                    }
            });
        }
        
    });
}

function _changeTextByUserStatus()
{
    console.log(_LOGIN);

    if(_LOGIN)
    {
        $('#show-greeting-text').show(0);
        $('#show-logout-text').show(0); 
        $('#show-login-text').hide(0);       
    }else
    {
        $('#show-greeting-text').hide(0);
        $('#show-logout-text').hide(0); 
        $('#show-login-text').show(0);        
    }
}

function _formChecker(action)
{

    form = {
        'signup': ['#login-email', '#login-password', '#login-confirmpassword'],
        'login':  ['#login-email', '#login-password']
    }

    var valid = false;
    msg = ''

    if(action != 'signup' && action != 'login')
    {
        valid = false
    }else
    {
        if (emptyChecker(form, action))
        {
            error_msg = emailChecker();

            if(error_msg == '') 
            {
                if (action == 'signup')
                {
                    error_msg = passwordChecker();
                    if (error_msg == ''){ // passwords valid, ready for signup
                        valid = true;
                    }else{  // passwords unmatched
                        valid = false;
                    }
                }else{ // ready for login
                    valid = true;
                }
            }else{ // email error
                valid = false;
            }

            msg = error_msg;
        }
    }

    $('#login-msg').html(msg)

    return valid;
}


// function _login()
// {
//     console.log('# catch login event.');
// }

// function _signup()
// {
//     console.log('catch signup event.');
//     // $.post("/signup", 
//     //     { 
//     //         username: $('#login-email').val(), 
//     //         password: $('#login-password').val(),
//     //         utype: "email" 
//     //     })
//     //     .done(function(data) {
//     //         $('#login-msg').html(data.msg);
//     //         console.log(data);
//     // });
// }