// Main JavaScript file for the fabric sample ordering system

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        if (!alert.querySelector('.btn-close')) {
            setTimeout(() => {
                alert.style.opacity = '0';
                setTimeout(() => {
                    alert.remove();
                }, 300);
            }, 5000);
        }
    });

    // Add smooth transitions for form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            // Add loading state to submit buttons
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton && !submitButton.disabled) {
                const originalText = submitButton.innerHTML;
                submitButton.dataset.originalText = originalText;
            }
        });
    });

    // Enhanced table row click handling for admin dashboard
    const tableRows = document.querySelectorAll('tr[data-request-id]');
    tableRows.forEach(row => {
        row.style.cursor = 'pointer';
        row.addEventListener('click', function(e) {
            // Don't navigate if clicking on action buttons
            if (e.target.closest('.btn') || e.target.closest('.dropdown')) {
                return;
            }
            
            const requestId = this.dataset.requestId;
            if (requestId) {
                window.location.href = `/admin/request/${requestId}`;
            }
        });

        // Add hover effect
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'var(--bs-secondary-bg)';
        });

        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });

    // Form validation improvements
    const validatedForms = document.querySelectorAll('.needs-validation');
    validatedForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Focus on first invalid field
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                }
            }
            form.classList.add('was-validated');
        });
    });

    // Smooth scroll for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href').substring(1);
            const target = document.getElementById(targetId);
            
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Auto-focus on first form field for better UX
    const firstFormField = document.querySelector('form input:not([type="hidden"]), form select, form textarea');
    if (firstFormField && !firstFormField.value) {
        firstFormField.focus();
    }

    // Add loading states for AJAX operations
    window.showLoadingState = function(element, loadingText = 'Loading...') {
        if (element.tagName === 'BUTTON') {
            element.disabled = true;
            element.dataset.originalText = element.innerHTML;
            element.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>${loadingText}`;
        }
    };

    window.hideLoadingState = function(element) {
        if (element.tagName === 'BUTTON') {
            element.disabled = false;
            if (element.dataset.originalText) {
                element.innerHTML = element.dataset.originalText;
            }
        }
    };

    // Utility function for showing toast notifications
    window.showToast = function(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 1055; min-width: 300px;';
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        document.body.appendChild(toast);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    };

    // Keyboard navigation improvements
    document.addEventListener('keydown', function(e) {
        // Escape key to close modals
        if (e.key === 'Escape') {
            const openModals = document.querySelectorAll('.modal.show');
            openModals.forEach(modal => {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            });
        }
    });

    // Print functionality for request details
    window.printRequest = function() {
        window.print();
    };

    // CSV export with loading state
    const csvExportButton = document.querySelector('a[href*="export_csv"]');
    if (csvExportButton) {
        csvExportButton.addEventListener('click', function() {
            showLoadingState(this, 'Exporting...');
            setTimeout(() => {
                hideLoadingState(this);
            }, 2000);
        });
    }
});

// Utility functions for status management
function getStatusColor(status) {
    switch (status.toLowerCase()) {
        case 'outstanding':
            return 'warning';
        case 'in progress':
            return 'info';
        case 'dispatched':
            return 'success';
        default:
            return 'secondary';
    }
}

// Enhanced error handling for fetch requests
window.handleFetchError = function(error) {
    console.error('Fetch error:', error);
    
    if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
        showToast('Network error. Please check your connection and try again.', 'danger');
    } else {
        showToast('An unexpected error occurred. Please try again.', 'danger');
    }
};

// Auto-save functionality for forms (optional)
window.enableAutoSave = function(formId, saveInterval = 30000) {
    const form = document.getElementById(formId);
    if (!form) return;

    setInterval(() => {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        // Save to localStorage
        localStorage.setItem(`autosave_${formId}`, JSON.stringify(data));
    }, saveInterval);

    // Restore from localStorage on page load
    const savedData = localStorage.getItem(`autosave_${formId}`);
    if (savedData) {
        try {
            const data = JSON.parse(savedData);
            Object.keys(data).forEach(key => {
                const field = form.querySelector(`[name="${key}"]`);
                if (field && !field.value) {
                    field.value = data[key];
                }
            });
        } catch (e) {
            console.warn('Failed to restore auto-saved data:', e);
        }
    }
};
