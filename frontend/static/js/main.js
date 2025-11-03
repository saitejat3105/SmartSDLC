// Check authentication
function checkAuth() {
    const token = localStorage.getItem('token');
    const publicPages = ['/', '/register-page'];
    
    if (!token && !publicPages.includes(window.location.pathname)) {
        window.location.href = '/';
        return false;
    }
    return true;
}

// Fetch with authentication
async function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem('token');
    
    if (!token) {
        window.location.href = '/';
        throw new Error('No authentication token');
    }

    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };

    const response = await fetch(url, { ...options, headers });

    if (response.status === 401) {
        localStorage.removeItem('token');
        window.location.href = '/';
        throw new Error('Authentication failed');
    }

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response;
}

// Logout function
function logout() {
    localStorage.removeItem('token');
    window.location.href = '/';
}

// Initialize auth check
if (window.location.pathname !== '/' && window.location.pathname !== '/register-page') {
    checkAuth();
}