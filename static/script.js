document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const logoutButton = document.getElementById('logout-button');
    const createPostForm = document.getElementById('create-post-form');
    const blogSection = document.getElementById('blog-section');

    loginForm.addEventListener('submit', function (event) {
        event.preventDefault();
        loginUser();
    });

    registerForm.addEventListener('submit', function (event) {
        event.preventDefault();
        registerUser();
    });

    logoutButton.addEventListener('click', logoutUser);

    createPostForm.addEventListener('submit', function (event) {
        event.preventDefault();
        createPost();
    });

    checkLoginStatus();
});

function checkLoginStatus() {
    fetch('/api/check-session')
        .then(response => response.json())
        .then(data => {
            if (data.logged_in) {
                document.getElementById('login-form').style.display = 'none';
                document.getElementById('register-form').style.display = 'none';
                document.getElementById('logout-button').style.display = 'block';
                document.getElementById('blog-section').style.display = 'block';
            } else {
                document.getElementById('login-form').style.display = 'block';
                document.getElementById('register-form').style.display = 'block';
                document.getElementById('logout-button').style.display = 'none';
                document.getElementById('blog-section').style.display = 'none';
            }
        });
}
