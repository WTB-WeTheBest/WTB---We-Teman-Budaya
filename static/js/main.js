// Main JavaScript file for Garuda

// Toggle mobile menu
function toggleMobileMenu() {
    const mobileMenu = document.getElementById('mobileMenu');
    mobileMenu.classList.toggle('hidden');
}

// Toggle user dropdown
function toggleDropdown() {
    const dropdown = document.getElementById('userDropdown');
    dropdown.classList.toggle('hidden');
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const dropdown = document.getElementById('userDropdown');
    const dropdownButton = event.target.closest('button[onclick="toggleDropdown()"]');
    
    if (dropdown && !dropdownButton && !dropdown.contains(event.target)) {
        dropdown.classList.add('hidden');
    }
});

// Logout function
async function logout() {
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (refreshToken) {
        try {
            await fetch('/api/logout/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ refresh: refreshToken })
            });
        } catch (error) {
            console.error('Logout error:', error);
        }
    }
    
    // Clear tokens from localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    
    // Redirect to home
    window.location.href = '/';
}

// Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// API request helper with JWT token
async function apiRequest(url, options = {}) {
    const token = localStorage.getItem('access_token');
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
            ...(token && { 'Authorization': `Bearer ${token}` })
        }
    };
    
    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(url, mergedOptions);
        
        // If token is expired, try to refresh
        if (response.status === 401 && token) {
            const refreshed = await refreshToken();
            if (refreshed) {
                // Retry the original request with new token
                mergedOptions.headers['Authorization'] = `Bearer ${localStorage.getItem('access_token')}`;
                return await fetch(url, mergedOptions);
            } else {
                // Refresh failed, redirect to login
                window.location.href = '/login/';
                return;
            }
        }
        
        return response;
    } catch (error) {
        console.error('API request error:', error);
        throw error;
    }
}

// Refresh JWT token
async function refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (!refreshToken) {
        return false;
    }
    
    try {
        const response = await fetch('/api/token/refresh/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ refresh: refreshToken })
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access);
            return true;
        }
    } catch (error) {
        console.error('Token refresh error:', error);
    }
    
    return false;
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-md shadow-lg z-50 ${
        type === 'success' ? 'bg-green-100 text-green-700 border border-green-400' :
        type === 'error' ? 'bg-red-100 text-red-700 border border-red-400' :
        'bg-blue-100 text-blue-700 border border-blue-400'
    }`;
    
    notification.innerHTML = `
        ${message}
        <button onclick="this.parentElement.remove()" class="float-right ml-4 text-lg font-bold">&times;</button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    // Add fade-in animation to main content
    const main = document.querySelector('main');
    if (main) {
        main.classList.add('fade-in');
    }
    
    // Add hover effects to cards
    const cards = document.querySelectorAll('.bg-white.rounded-lg.shadow-md');
    cards.forEach(card => {
        card.classList.add('hover-scale');
    });
});