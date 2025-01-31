// js/app.js
document.addEventListener('DOMContentLoaded', () => {
    fetch('/api/jobs')  // Adjust the URL as needed
        .then(response => response.json())
        .then(data => {
            const jobListings = document.getElementById('job-listings');
            data.forEach(job => {
                const jobItem = document.createElement('div');
                jobItem.innerHTML = `<h2>${job.title}</h2><p>${job.description}</p>`;
                jobListings.appendChild(jobItem);
            });
        })
        .catch(error => console.error('Error fetching jobs:', error));
});

function toggleForm() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    loginForm.classList.toggle('hidden');
    registerForm.classList.toggle('hidden');
}

// Optionally, handle form submission
document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();
    // Add login handling logic here
    alert('Login form submitted!');
});

document.getElementById('registerForm').addEventListener('submit', function(event) {
    event.preventDefault();
    // Add registration handling logic here
    alert('Register form submitted!');
});
<script src="js/app.js"></script>
