$(document).ready(function(){
    $('#registr_form').on('submit', function(e){
        e.preventDefault();
        if($('#name').val().trim() ==''){
            err=1;
        }else{
            err=0;
        }
        alert(err);
        if($('#password').val() != $('#password2').val()){
            err=2;
            }
        else{
            err=0;
        }
        s.ajax({
            method: "POST",
            url:"/ajax/registr",
            contentType: "application/jdon",
            data: JSON.stringify({
                password: $('#password').val(),
                email: $('#email').val(),
                name: $('#name').val()
            })
        })
        .done(function(msg){
            alert("Data Saved:" + msg);
        });

        alert(err);
    })
});