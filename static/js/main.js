// Personal Finance Tracker JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize dark mode
    initializeDarkMode();
    
    // Initialize tooltips and popovers
    initializeBootstrapComponents();
    
    // Initialize form validators
    initializeFormValidation();
    
    // Initialize number formatting
    initializeNumberFormatting();
    
    // Initialize auto-save for forms
    initializeAutoSave();
    
    console.log('Personal Finance Tracker initialized successfully');
}

// Dark Mode Functionality
function initializeDarkMode() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const htmlElement = document.documentElement;
    
    // Check for saved theme preference or default to light
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            const currentTheme = htmlElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            setTheme(newTheme);
        });
    }
}

function setTheme(theme) {
    const htmlElement = document.documentElement;
    const darkModeToggle = document.getElementById('darkModeToggle');
    
    htmlElement.setAttribute('data-bs-theme', theme);
    localStorage.setItem('theme', theme);
    
    if (darkModeToggle) {
        const icon = darkModeToggle.querySelector('i');
        if (theme === 'dark') {
            icon.className = 'bi bi-sun-fill';
            darkModeToggle.setAttribute('aria-label', 'Switch to light mode');
        } else {
            icon.className = 'bi bi-moon-fill';
            darkModeToggle.setAttribute('aria-label', 'Switch to dark mode');
        }
    }
}

// Bootstrap Components Initialization
function initializeBootstrapComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Form Validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// Number Formatting
function initializeNumberFormatting() {
    // Auto-format currency inputs
    const currencyInputs = document.querySelectorAll('input[type="number"][step="0.01"]');
    currencyInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            if (this.value) {
                const value = parseFloat(this.value);
                if (!isNaN(value)) {
                    this.value = value.toFixed(2);
                }
            }
        });
    });
    
    // Format numbers in tables
    const numberCells = document.querySelectorAll('.number-format');
    numberCells.forEach(function(cell) {
        const value = parseFloat(cell.textContent);
        if (!isNaN(value)) {
            cell.textContent = formatCurrency(value);
        }
    });
}

// Auto-save functionality for forms
function initializeAutoSave() {
    const autoSaveForms = document.querySelectorAll('.auto-save');
    
    autoSaveForms.forEach(function(form) {
        const formId = form.id;
        
        // Load saved data
        loadFormData(formId);
        
        // Save on input change
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(function(input) {
            input.addEventListener('input', function() {
                saveFormData(formId);
            });
        });
    });
}

// Utility Functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatNumber(number) {
    return new Intl.NumberFormat('en-US').format(number);
}

function formatPercentage(decimal) {
    return (decimal * 100).toFixed(2) + '%';
}

function saveFormData(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    localStorage.setItem(`form_${formId}`, JSON.stringify(data));
}

function loadFormData(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const savedData = localStorage.getItem(`form_${formId}`);
    if (!savedData) return;
    
    try {
        const data = JSON.parse(savedData);
        
        for (let [key, value] of Object.entries(data)) {
            const input = form.querySelector(`[name="${key}"]`);
            if (input) {
                input.value = value;
            }
        }
    } catch (e) {
        console.error('Error loading form data:', e);
    }
}

function clearFormData(formId) {
    localStorage.removeItem(`form_${formId}`);
}

// Chart Helper Functions
function createPieChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    const defaultOptions = {
        responsive: true,
        plugins: {
            legend: {
                position: 'bottom'
            }
        }
    };
    
    return new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: { ...defaultOptions, ...options }
    });
}

function createBarChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    const defaultOptions = {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function(value) {
                        return formatCurrency(value);
                    }
                }
            }
        }
    };
    
    return new Chart(ctx, {
        type: 'bar',
        data: data,
        options: { ...defaultOptions, ...options }
    });
}

function createLineChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    const defaultOptions = {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function(value) {
                        return formatCurrency(value);
                    }
                }
            }
        }
    };
    
    return new Chart(ctx, {
        type: 'line',
        data: data,
        options: { ...defaultOptions, ...options }
    });
}

// API Helper Functions
async function fetchAPI(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API fetch error:', error);
        showNotification('Error fetching data. Please try again.', 'error');
        throw error;
    }
}

// Notification System
function showNotification(message, type = 'info', duration = 5000) {
    const container = getNotificationContainer();
    
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification-toast`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    container.appendChild(notification);
    
    // Auto remove after duration
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
}

function getNotificationContainer() {
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1060';
        document.body.appendChild(container);
    }
    return container;
}

// Loading States
function showLoading(element) {
    if (typeof element === 'string') {
        element = document.getElementById(element);
    }
    
    if (element) {
        element.classList.add('loading');
        const spinner = document.createElement('div');
        spinner.className = 'spinner';
        spinner.id = 'loading-spinner';
        element.appendChild(spinner);
    }
}

function hideLoading(element) {
    if (typeof element === 'string') {
        element = document.getElementById(element);
    }
    
    if (element) {
        element.classList.remove('loading');
        const spinner = element.querySelector('#loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    }
}

// Modal Helpers
function openModal(modalId) {
    const modal = new bootstrap.Modal(document.getElementById(modalId));
    modal.show();
}

function closeModal(modalId) {
    const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
    if (modal) {
        modal.hide();
    }
}

// Date Helpers
function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US');
}

function getDateString(date = new Date()) {
    return date.toISOString().split('T')[0];
}

function addDays(date, days) {
    const result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
}

// Calculation Helpers
function calculateCompoundInterest(principal, rate, time, compound = 12) {
    return principal * Math.pow(1 + (rate / compound), compound * time);
}

function calculateLoanPayment(principal, rate, time) {
    const monthlyRate = rate / 12;
    const numberOfPayments = time * 12;
    
    if (rate === 0) {
        return principal / numberOfPayments;
    }
    
    return principal * (monthlyRate * Math.pow(1 + monthlyRate, numberOfPayments)) / 
           (Math.pow(1 + monthlyRate, numberOfPayments) - 1);
}

function calculateTaxBracket(income, brackets) {
    let tax = 0;
    let previousBracket = 0;
    
    for (const [limit, rate] of brackets) {
        if (income <= previousBracket) break;
        
        const taxableInBracket = Math.min(income, limit) - previousBracket;
        tax += taxableInBracket * rate;
        previousBracket = limit;
        
        if (income <= limit) break;
    }
    
    return tax;
}

// Export functions for use in other scripts
window.FinanceTracker = {
    formatCurrency,
    formatNumber,
    formatPercentage,
    showNotification,
    createPieChart,
    createBarChart,
    createLineChart,
    fetchAPI,
    calculateCompoundInterest,
    calculateLoanPayment,
    calculateTaxBracket,
    openModal,
    closeModal,
    showLoading,
    hideLoading
};