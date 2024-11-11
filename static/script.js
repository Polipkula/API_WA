document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const logoutButton = document.getElementById('logout-button');
    const createPostForm = document.getElementById('create-post-form');
    const blogSection = document.getElementById('blog-section');

    // Initially hide sections
    createPostForm.style.display = 'none';
    blogSection.style.display = 'none';
    logoutButton.style.display = 'none';

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

    checkLoginStatus(); // Check login status on load and adjust UI
    loadPosts();
});

function checkLoginStatus() {
    fetch('/api/check-session', { method: 'GET' })
        .then(response => response.json())
        .then(data => {
            if (data.logged_in) {
                // Show post creation form and logout button
                document.getElementById('create-post-form').style.display = 'block';
                document.getElementById('logout-button').style.display = 'block';
                document.getElementById('login-form').style.display = 'none';
                document.getElementById('register-form').style.display = 'none';
            } else {
                // Show login and register forms
                document.getElementById('create-post-form').style.display = 'none';
                document.getElementById('logout-button').style.display = 'none';
                document.getElementById('login-form').style.display = 'block';
                document.getElementById('register-form').style.display = 'block';
            }
        });
}

function loginUser() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    })
        .then(response => response.json())
        .then(data => {
            if (data.message === 'Login successful') {
                checkLoginStatus();
                loadPosts();
            } else {
                alert(data.message || 'Login failed');
            }
        });
}

function registerUser() {
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;

    fetch('/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    })
        .then(response => response.json())
        .then(data => {
            alert(data.message || 'Registration failed');
        });
}

function logoutUser() {
    fetch('/logout', { method: 'POST' })
        .then(() => {
            checkLoginStatus();
            loadPosts();
        });
}

function createPost() {
    const content = document.getElementById('content').value;

    fetch('/api/blog', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content })
    })
        .then(response => response.json())
        .then(() => {
            loadPosts();
            document.getElementById('create-post-form').reset();
        });
}

function loadPosts() {
    fetch('/api/blog')
        .then(response => response.json())
        .then(posts => {
            const postsDiv = document.getElementById('blog-posts');
            postsDiv.innerHTML = '';
            posts.forEach(post => {
                const postDiv = document.createElement('div');
                postDiv.classList.add('post');
                postDiv.innerHTML = `
                    <p>${post.content}</p>
                    <small>By ${post.author} on ${new Date(post.created_at).toLocaleString()}</small>
                `;
                postsDiv.appendChild(postDiv);
            });
        });
}
