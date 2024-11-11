document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const logoutButton = document.getElementById('logout-button');
    const createPostForm = document.getElementById('create-post-form');
    const blogSection = document.getElementById('blog-section');

    // Hide forms initially
    createPostForm.style.display = 'none';
    blogSection.style.display = 'none';
    logoutButton.style.display = 'none';

    // Attach event listeners
    loginForm.addEventListener('submit', function (event) {
        event.preventDefault();
        loginUser();
    });

    registerForm.addEventListener('submit', function (event) {
        event.preventDefault();
        registerUser();
    });

    logoutButton.addEventListener('click', function () {
        logoutUser();
    });

    if (createPostForm) {
        createPostForm.addEventListener('submit', function (event) {
            event.preventDefault();
            createPost();
        });
    }

    // Initial check for user session
    checkLoginStatus();
    loadPosts();
});

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
                alert('Login successful');
                checkLoginStatus();
            } else {
                alert(data.message || 'Login failed');
            }
        })
        .catch(error => console.error('Error:', error));
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
        })
        .catch(error => console.error('Error:', error));
}

function logoutUser() {
    fetch('/logout', { method: 'POST' })
        .then(() => {
            alert('Logged out successfully');
            checkLoginStatus();
        })
        .catch(error => console.error('Error:', error));
}

function createPost() {
    const content = document.getElementById('content').value;

    fetch('/api/blog', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content })
    })
        .then(response => response.json())
        .then(data => {
            if (data.message === 'Post created successfully') {
                alert('Post created successfully');
                loadPosts();
                document.getElementById('create-post-form').reset();
            } else {
                alert(data.message || 'Failed to create post');
            }
        })
        .catch(error => console.error('Error:', error));
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
        })
        .catch(error => console.error('Error:', error));
}

function checkLoginStatus() {
    fetch('/api/check-session')
        .then(response => response.json())
        .then(data => {
            const loginForm = document.getElementById('login-form');
            const registerForm = document.getElementById('register-form');
            const logoutButton = document.getElementById('logout-button');
            const blogSection = document.getElementById('blog-section');
            const createPostForm = document.getElementById('create-post-form');

            if (data.logged_in) {
                loginForm.style.display = 'none';
                registerForm.style.display = 'none';
                logoutButton.style.display = 'block';
                blogSection.style.display = 'block';
                createPostForm.style.display = 'block';
            } else {
                loginForm.style.display = 'block';
                registerForm.style.display = 'block';
                logoutButton.style.display = 'none';
                blogSection.style.display = 'none';
                createPostForm.style.display = 'none';
            }
        })
        .catch(error => console.error('Error:', error));
}
