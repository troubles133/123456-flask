$(document).ready(function(){
    $('#login_form').on('submit', function(e){
        e.preventDefault();
        
        
        $('.error-message').remove();
        
        let email = $('#email').val().trim();
        let password = $('#password').val();
        let errors = [];
        
        
        if(email === ''){
            errors.push('Введите email');
            $('#email').css('border-color', 'red');
        } else {
            $('#email').css('border-color', '#ccc');
        }
        
        if(password === ''){
            errors.push('Введите пароль');
            $('#password').css('border-color', 'red');
        } else {
            $('#password').css('border-color', '#ccc');
        }
        
        if(errors.length > 0){
            showErrors(errors);
            return;
        }
        
        
        $.ajax({
            method: "POST",
            url: "/ajax/login",
            contentType: "application/json",
            data: JSON.stringify({
                email: email,
                password: password
            }),
            beforeSend: function() {
                $('button[type="submit"]').prop('disabled', true).text('Вход...');
            }
        })
        .done(function(response){
            if(response.code === 200){
                alert('Добро пожаловать, ' + response.username + '!');
                window.location.href = '/dashboard';
            } else {
                showErrors([response.error || 'Ошибка при входе']);
            }
        })
        .fail(function() {
            showErrors(['Ошибка сервера. Попробуйте позже.']);
        })
        .always(function() {
            $('button[type="submit"]').prop('disabled', false).text('Войти');
        });
    });
    
    function showErrors(errors) {
        $('.error-message').remove();
        errors.forEach(function(error) {
            $('#login_form').prepend(
                $('<div>')
                    .addClass('error-message')
                    .css({
                        'background-color': '#f8d7da',
                        'color': '#721c24',
                        'padding': '10px',
                        'margin-bottom': '15px',
                        'border-radius': '4px',
                        'border': '1px solid #f5c6cb'
                    })
                    .text(error)
            );
        });
    }
    
    $('#email, #password').on('input', function(){
        $(this).css('border-color', '#ccc');
    });
});