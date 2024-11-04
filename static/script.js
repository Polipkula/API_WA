document.addEventListener('DOMContentLoaded', function() {
    loadPosts();

    const form = document.getElementById('create-post-form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        createPost();
    });
});

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

function createPost() {
    const content = document.getElementById('content').value;
    const author = document.getElementById('author').value;

    fetch('/api/blog', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            content: content,
            author: author
        })
    })
    .then(response => response.json())
    .then(() => {
        loadPosts();
        document.getElementById('create-post-form').reset();
    });
}

function deletePost(id) {
    fetch(`/api/blog/${id}`, {
        method: 'DELETE'
    })
    .then(() => loadPosts());
}
