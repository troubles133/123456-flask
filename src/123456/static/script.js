$(document).ready(function(){
    $('#registr_form').on('submit', function(e){
        e.preventDefault();
        
        $('.error-message').remove();
        
        let errors = [];
        let name = $('#name').val().trim();
        let email = $('#email').val().trim();
        let password = $('#password').val();
        let password2 = $('#password2').val();
        

        if(name === ''){
            errors.push('Введите имя');
            $('#name').css('border-color', 'red');
        } else {
            $('#name').css('border-color', '#ccc');
        }
        
        if(email === ''){
            errors.push('Введите email');
            $('#email').css('border-color', 'red');
        } else if(!isValidEmail(email)){
            errors.push('Введите корректный email');
            $('#email').css('border-color', 'red');
        } else {
            $('#email').css('border-color', '#ccc');
        }
        
        if(password === ''){
            errors.push('Введите пароль');
            $('#password').css('border-color', 'red');
        } else if(password.length < 6){
            errors.push('Пароль должен быть минимум 6 символов');
            $('#password').css('border-color', 'red');
        } else {
            $('#password').css('border-color', '#ccc');
        }
        
        if(password !== password2){
            errors.push('Пароли не совпадают');
            $('#password2').css('border-color', 'red');
        } else {
            $('#password2').css('border-color', '#ccc');
        }
        

        if(errors.length > 0){
            showErrors(errors);
            return;
        }
        

        $.ajax({
            method: "POST",
            url: "/ajax/registr",
            contentType: "application/json",
            data: JSON.stringify({
                name: name,
                email: email,
                password: password  // Отправляем обычный пароль, сервер сам его захэширует
            }),
            beforeSend: function() {
                $('button[type="submit"]').prop('disabled', true).text('Регистрация...');
            }
        })
        .done(function(response){
            if(response.code === 200){
                alert('Регистрация успешна! ID: ' + response.id);
                $('#registr_form')[0].reset();
                setTimeout(function(){
                    window.location.href = '/login';
                }, 1000);
            } else {
                showErrors([response.error || 'Ошибка регистрации']);
            }
        })
        .fail(function(xhr){
            let errorMsg = 'Ошибка сервера';
            if(xhr.responseJSON && xhr.responseJSON.error){
                errorMsg = xhr.responseJSON.error;
            }
            showErrors([errorMsg]);
        })
        .always(function(){
            $('button[type="submit"]').prop('disabled', false).text('Зарегистрироваться');
        });
    });
    

    function isValidEmail(email) {
        var re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return re.test(email);
    }
    

    function showErrors(errors) {
        $('.error-message').remove();
        errors.forEach(function(error) {
            $('#registr_form').prepend(
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
    

    $('#name, #email, #password, #password2').on('input', function(){
        $(this).css('border-color', '#ccc');
    });
});
