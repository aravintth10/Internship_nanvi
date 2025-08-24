// Enhanced JavaScript for Person Profile Tracker

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all enhancements
    initializeFormEnhancements();
    initializeFileUpload();
    initializeSearchButton();
    initializeAnimations();
    initializeTooltips();
});

function initializeFormEnhancements() {
    // Add floating labels effect
    const formControls = document.querySelectorAll('.form-control, .form-select');
    
    formControls.forEach(control => {
        // Add focus effects
        control.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        control.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });
        
        // Add input validation feedback
        control.addEventListener('input', function() {
            validateField(this);
        });
    });
}

function initializeFileUpload() {
    const fileInput = document.getElementById('id_profile_photo');
    const uploadArea = document.querySelector('.file-upload-area');
    
    if (!fileInput || !uploadArea) return;
    
    // Enhanced drag and drop
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('dragover');
        this.style.borderColor = 'var(--primary-color)';
        this.style.background = 'rgba(99, 102, 241, 0.05)';
    });
    
    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.classList.remove('dragover');
        this.style.borderColor = 'var(--border-color)';
        this.style.background = 'var(--secondary-color)';
    });
    
    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });
    
    // File input change
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });
}

function handleFileSelect(file) {
    const uploadArea = document.querySelector('.file-upload-area');
    const fileInput = document.getElementById('id_profile_photo');
    
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    if (!allowedTypes.includes(file.type)) {
        showNotification('Please select a valid image file (JPG, PNG)', 'error');
        return;
    }
    
    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
        showNotification('File size must be less than 5MB', 'error');
        return;
    }
    
    // Update file input
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    fileInput.files = dataTransfer.files;
    
    // Update UI
    uploadArea.innerHTML = `
        <i class="fas fa-check-circle text-success"></i>
        <h5>File Selected</h5>
        <p class="text-success">${file.name}</p>
        <small class="text-muted">${(file.size / 1024 / 1024).toFixed(2)} MB</small>
    `;
    
    showNotification('File uploaded successfully!', 'success');
}

function initializeSearchButton() {
    const searchForm = document.getElementById('searchForm');
    const searchBtn = document.getElementById('searchBtn');
    
    if (!searchForm || !searchBtn) return;
    
    searchForm.addEventListener('submit', function(e) {
        // Show loading state
        const searchText = document.getElementById('searchText');
        const searchLoading = document.getElementById('searchLoading');
        
        if (searchText && searchLoading) {
            searchBtn.disabled = true;
            searchText.style.display = 'none';
            searchLoading.style.display = 'inline-block';
        }
        
        // Add loading overlay
        showLoadingOverlay();
    });
}

function initializeAnimations() {
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.profile-card, .platform-section').forEach(el => {
        observer.observe(el);
    });
}

function initializeTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function validateField(field) {
    const value = field.value.trim();
    const fieldName = field.name;
    
    // Remove existing validation classes
    field.classList.remove('is-valid', 'is-invalid');
    
    // Basic validation rules
    if (fieldName === 'name' && value.length < 2) {
        field.classList.add('is-invalid');
        showFieldError(field, 'Name must be at least 2 characters long');
    } else if (fieldName === 'primary_email' && value && !isValidEmail(value)) {
        field.classList.add('is-invalid');
        showFieldError(field, 'Please enter a valid email address');
    } else if (value) {
        field.classList.add('is-valid');
        hideFieldError(field);
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showFieldError(field, message) {
    // Remove existing error message
    hideFieldError(field);
    
    // Create error message element
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

function hideFieldError(field) {
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, 5000);
}

function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function showLoadingOverlay() {
    // Create loading overlay
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div class="loading-content">
            <div class="loading-spinner mb-3"></div>
            <h5>Searching Profiles...</h5>
            <p class="text-muted">This may take a few moments</p>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    // Remove overlay after a delay (in case of errors)
    setTimeout(() => {
        if (overlay.parentNode) {
            overlay.remove();
        }
    }, 30000);
}

// Add CSS for notifications
const notificationStyles = `
<style>
.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    padding: 1rem;
    z-index: 10000;
    transform: translateX(100%);
    transition: transform 0.3s ease;
    max-width: 400px;
}

.notification.show {
    transform: translateX(0);
}

.notification-content {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.notification-success {
    border-left: 4px solid var(--success-color);
}

.notification-error {
    border-left: 4px solid var(--danger-color);
}

.notification-warning {
    border-left: 4px solid var(--warning-color);
}

.notification-info {
    border-left: 4px solid var(--primary-color);
}

.notification-close {
    background: none;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    padding: 0.25rem;
    border-radius: 4px;
    transition: all 0.2s ease;
}

.notification-close:hover {
    background: rgba(0, 0, 0, 0.1);
    color: var(--text-primary);
}

.animate-in {
    animation: slideInUp 0.6s ease-out;
}

@keyframes slideInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.dragover {
    transform: scale(1.02);
    box-shadow: 0 0 0 2px var(--primary-color);
}

.focused .form-label {
    color: var(--primary-color);
    transform: translateY(-2px);
}

.is-valid {
    border-color: var(--success-color) !important;
    box-shadow: 0 0 0 0.2rem rgba(16, 185, 129, 0.25) !important;
}

.is-invalid {
    border-color: var(--danger-color) !important;
    box-shadow: 0 0 0 0.2rem rgba(239, 68, 68, 0.25) !important;
}

.invalid-feedback {
    display: block;
    color: var(--danger-color);
    font-size: 0.875rem;
    margin-top: 0.25rem;
}
</style>
`;

// Inject styles
document.head.insertAdjacentHTML('beforeend', notificationStyles);
