document.addEventListener('DOMContentLoaded', function() {
    loadPosts();

    // Form submission for creating a post
    const form = document.getElementById('create-post-form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        createPost();
    });

    // Form submission for login
    const loginForm = document.getElementById('login-form');
    loginForm.addEventListener('submit', function(event) {
        event.preventDefault();
        login();
    });

    // Form submission for registration
    const registerForm = document.getElementById('register-form');
    registerForm.addEventListener('submit', function(event) {
        event.preventDefault();
        register();
    });
});

// Load all blog posts
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
                    <h3>Author: ${post.author}</h3>
                    <p>${post.content}</p>
                    <p><small>${new Date(post.created_at).toLocaleString()}</small></p>
                    <button onclick="deletePost(${post.id})">Delete</button>
                `;
                postsDiv.appendChild(postDiv);
            });
        });
}

// Create a new blog post
function createPost() {
    const content = document.getElementById('content').value;
    fetch('/api/blog', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            content: content
        })
    })
    .then(response => response.json())
    .then(() => {
        loadPosts();
        document.getElementById('create-post-form').reset();
    });
}

// Delete a blog post
function deletePost(id) {
    fetch(`/api/blog/${id}`, {
        method: 'DELETE'
    })
    .then(() => loadPosts());
}

// Login function
function login() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Login successful') {
            loadPosts();
        } else {
            alert('Login failed');
        }
    });
}

// Register function
function register() {
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;

    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'User registered successfully') {
            alert('Registration successful');
        } else {
            alert('Registration failed');
        }
    });
}

// Logout function
function logout() {
    fetch('/logout', { method: 'POST' })
        .then(() => {
            loadPosts();
        });
}
