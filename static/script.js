
document.addEventListener('DOMContentLoaded', function() {
   
    initializeAnimations();
    initializeFormHandling();
    initializeSearchFunctionality();
    initializeTaskActions();
    
   
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});


function initializeAnimations() {
    
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
   
    document.querySelectorAll('.stat-card, .feature-card, .task-card, .action-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
}


function initializeFormHandling() {
   
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelection);
    }
    
   
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', validateForm);
    });
}


function handleFileSelection(event) {
    const file = event.target.files[0];
    if (file) {
        // Validate file type
        if (!file.type.startsWith('image/')) {
            showNotification('Please select an image file.', 'error');
            event.target.value = '';
            return;
        }
        
        // Validate file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            showNotification('File size must be less than 10MB.', 'error');
            event.target.value = '';
            return;
        }
        
        // Show preview
        showFilePreview(file);
    }
}

// Show file preview
function showFilePreview(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const preview = document.getElementById('uploadPreview');
        const previewImage = document.getElementById('previewImage');
        const fileName = document.getElementById('fileName');
        const uploadArea = document.getElementById('fileUploadArea');
        const uploadBtn = document.getElementById('uploadBtn');
        
        if (preview && previewImage && fileName && uploadArea && uploadBtn) {
            previewImage.src = e.target.result;
            fileName.textContent = file.name;
            uploadArea.style.display = 'none';
            preview.style.display = 'block';
            uploadBtn.disabled = false;
            
           
            preview.style.animation = 'slideIn 0.5s ease';
        }
    };
    reader.readAsDataURL(file);
}


function initializeSearchFunctionality() {
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        // Add debounced search
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(this.value);
            }, 300);
        });
    }
}

// Perform search
function performSearch(query) {
    if (query.length < 2) return;
    
    // Highlight search results
    const taskCards = document.querySelectorAll('.task-card');
    taskCards.forEach(card => {
        const title = card.querySelector('.task-title');
        const description = card.querySelector('.task-description');
        
        if (title || description) {
            const text = (title ? title.textContent : '') + ' ' + (description ? description.textContent : '');
            if (text.toLowerCase().includes(query.toLowerCase())) {
                card.style.border = '2px solid #967BB6';
                card.style.boxShadow = '0 0 20px rgba(150, 123, 182, 0.3)';
            } else {
                card.style.border = '1px solid rgba(150, 123, 182, 0.1)';
                card.style.boxShadow = '0 8px 30px rgba(150, 123, 182, 0.1)';
            }
        }
    });
}

// Initialize task actions
function initializeTaskActions() {
    // Task completion toggle
    document.querySelectorAll('.task-card').forEach(card => {
        const completeBtn = card.querySelector('.btn-success');
        if (completeBtn) {
            completeBtn.addEventListener('click', function(e) {
                e.preventDefault();
                const taskId = card.dataset.taskId;
                if (taskId) {
                    markTaskComplete(taskId, card);
                }
            });
        }
    });
}

// Mark task as complete
function markTaskComplete(taskId, cardElement) {
    if (confirm('Mark this task as complete?')) {
        // Show loading state
        const btn = cardElement.querySelector('.btn-success');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
        btn.disabled = true;
        
        // Submit form
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/tasks/complete';
        
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'task_id';
        input.value = taskId;
        
        form.appendChild(input);
        document.body.appendChild(form);
        
        // Add success animation before submit
        cardElement.style.animation = 'completeTask 0.5s ease';
        
        setTimeout(() => {
            form.submit();
        }, 500);
    }
}

// Form validation
function validateForm(event) {
    const form = event.target;
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    if (!isValid) {
        event.preventDefault();
        showNotification('Please fill in all required fields.', 'error');
    }
    
    return isValid;
}

// Show field error
function showFieldError(field, message) {
    clearFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    errorDiv.style.color = '#C62828';
    errorDiv.style.fontSize = '0.85rem';
    errorDiv.style.marginTop = '0.25rem';
    
    field.parentNode.appendChild(errorDiv);
    field.style.borderColor = '#FF6B6B';
}

// Clear field error
function clearFieldError(field) {
    const errorDiv = field.parentNode.querySelector('.field-error');
    if (errorDiv) {
        errorDiv.remove();
    }
    field.style.borderColor = '#E6E6FA';
}

// Show notification
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : type === 'success' ? 'check-circle' : 'info-circle'}"></i>
            <span>${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    // Style notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        z-index: 10000;
        max-width: 400px;
        border-left: 4px solid ${type === 'error' ? '#FF6B6B' : type === 'success' ? '#66BB6A' : '#967BB6'};
        animation: slideInRight 0.3s ease;
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        }
    }, 5000);
}

// Enhanced drag and drop functionality
function initializeDragAndDrop() {
    const dropZones = document.querySelectorAll('.file-upload-area');
    
    dropZones.forEach(zone => {
        zone.addEventListener('dragover', handleDragOver);
        zone.addEventListener('dragleave', handleDragLeave);
        zone.addEventListener('drop', handleDrop);
    });
}

function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        const fileInput = e.currentTarget.querySelector('input[type="file"]');
        if (fileInput) {
            fileInput.files = files;
            fileInput.dispatchEvent(new Event('change'));
        }
    }
}

// Initialize drag and drop if on upload page
if (document.querySelector('.file-upload-area')) {
    initializeDragAndDrop();
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100%);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100%);
        }
    }
    
    @keyframes completeTask {
        0% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
        100% {
            transform: scale(1);
        }
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .notification-close {
        background: none;
        border: none;
        color: #6B6B8A;
        cursor: pointer;
        padding: 0.25rem;
        border-radius: 50%;
        transition: all 0.3s ease;
    }
    
    .notification-close:hover {
        background: #F0E6FF;
        color: #4A4A6A;
    }
`;

document.head.appendChild(style);

// Export functions for global use
window.markComplete = function(taskId) {
    if (confirm('Mark this task as complete?')) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/tasks/complete';
        
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'task_id';
        input.value = taskId;
        
        form.appendChild(input);
        document.body.appendChild(form);
        form.submit();
    }
};

window.deleteTask = function(taskId) {
    if (confirm('Are you sure you want to delete this task? This action cannot be undone.')) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/tasks/delete';
        
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'task_id';
        input.value = taskId;
        
        form.appendChild(input);
        document.body.appendChild(form);
        form.submit();
    }
};

window.editTask = function(taskId) {
    const taskCard = document.querySelector(`[data-task-id="${taskId}"]`);
    if (!taskCard) return;
    
    const title = taskCard.querySelector('.task-title').textContent;
    const date = taskCard.querySelector('.task-date').textContent.trim().split(' ')[1];
    const priority = taskCard.querySelector('.task-priority').textContent.trim();
    const status = taskCard.querySelector('.task-status').textContent.trim();
    
    // Populate modal
    const editTaskId = document.getElementById('editTaskId');
    const editTitle = document.getElementById('editTitle');
    const editDate = document.getElementById('editDate');
    const editPriority = document.getElementById('editPriority');
    const editStatus = document.getElementById('editStatus');
    
    if (editTaskId) editTaskId.value = taskId;
    if (editTitle) editTitle.value = title;
    if (editDate) editDate.value = date;
    if (editPriority) editPriority.value = priority;
    if (editStatus) editStatus.value = status;
    
    // Show modal
    const modal = document.getElementById('editModal');
    if (modal) {
        modal.style.display = 'block';
        modal.style.animation = 'slideIn 0.3s ease';
    }
};

window.closeModal = function() {
    const modal = document.getElementById('editModal');
    if (modal) {
        modal.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            modal.style.display = 'none';
        }, 300);
    }
};

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('editModal');
    if (event.target == modal) {
        closeModal();
    }
};
