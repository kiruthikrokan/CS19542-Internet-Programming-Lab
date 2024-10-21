$(document).ready(function() {
    $('#loginForm').on('submit', function(event) {
        var username = $('#username').val();
        var password = $('#password').val();
        
        if (username === "" || password === "") {
            alert("Please fill in all fields");
            event.preventDefault();  // Prevent form submission
        }
    });
});
