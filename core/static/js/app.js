// Dark/Light Mode Toggle Functionality
class ThemeManager {
    constructor() {
        this.init();
    }

    init() {
        // Get saved theme or default to system preference
        const savedTheme = localStorage.getItem('theme');
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const initialTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
        
        this.setTheme(initialTheme);
        this.bindEvents();
        
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('theme')) {
                this.setTheme(e.matches ? 'dark' : 'light');
            }
        });
    }

    bindEvents() {
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                this.setTheme(newTheme);
                localStorage.setItem('theme', newTheme);
            });
        }
    }

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        
        // Update toggle button icon and Bootstrap theme
        const themeToggle = document.getElementById('themeToggle');
        const icon = themeToggle?.querySelector('i');
        
        if (theme === 'dark') {
            document.documentElement.setAttribute('data-bs-theme', 'dark');
            if (icon) {
                icon.className = 'bi bi-sun-fill';
                themeToggle.setAttribute('title', 'التبديل للوضع الفاتح');
            }
        } else {
            document.documentElement.setAttribute('data-bs-theme', 'light');
            if (icon) {
                icon.className = 'bi bi-moon-fill';
                themeToggle.setAttribute('title', 'التبديل للوضع المظلم');
            }
        }
    }

    getCurrentTheme() {
        return document.documentElement.getAttribute('data-theme') || 'light';
    }
}

// Toast Notifications System
class ToastManager {
    constructor() {
        this.container = this.createContainer();
    }

    createContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '1055';
            document.body.appendChild(container);
        }
        return container;
    }

    show(message, type = 'success', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi bi-${this.getIcon(type)} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        data-bs-dismiss="toast"></button>
            </div>
        `;

        this.container.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast, { delay: duration });
        bsToast.show();

        // Remove from DOM after hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });

        return bsToast;
    }

    getIcon(type) {
        const icons = {
            success: 'check-circle-fill',
            error: 'exclamation-triangle-fill',
            warning: 'exclamation-triangle-fill',
            info: 'info-circle-fill'
        };
        return icons[type] || 'info-circle-fill';
    }
}

// Favorites Management
class FavoritesManager {
    constructor() {
        this.bindEvents();
    }

    bindEvents() {
        document.addEventListener('click', (e) => {
            if (e.target.closest('.favorite-btn')) {
                e.preventDefault();
                e.stopPropagation();
                this.toggleFavorite(e.target.closest('.favorite-btn'));
            }
        });
    }

    async toggleFavorite(button) {
        const productId = button.dataset.productId;
        
        if (!productId) return;

        try {
            const response = await fetch('/products/favorites/toggle/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ product_id: productId })
            });

            const data = await response.json();

            if (data.success) {
                this.updateFavoriteUI(button, data.is_favorite);
                this.updateFavoritesCount(data.favorites_count);
                
                // Show toast notification
                window.toastManager.show(
                    data.message,
                    data.is_favorite ? 'success' : 'info'
                );
            } else {
                window.toastManager.show(data.message || 'حدث خطأ', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            window.toastManager.show('حدث خطأ في الشبكة', 'error');
        }
    }

    updateFavoriteUI(button, isFavorite) {
        const icon = button.querySelector('i');
        if (icon) {
            if (isFavorite) {
                icon.className = 'bi bi-heart-fill text-danger';
                button.setAttribute('title', 'إزالة من المفضلة');
            } else {
                icon.className = 'bi bi-heart';
                button.setAttribute('title', 'إضافة للمفضلة');
            }
        }
    }

    updateFavoritesCount(count) {
        const badges = document.querySelectorAll('.favorites-count');
        badges.forEach(badge => {
            if (count > 0) {
                badge.textContent = count;
                badge.style.display = '';
            } else {
                badge.style.display = 'none';
            }
        });
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
               document.querySelector('meta[name=csrf-token]')?.content || '';
    }
}

// Initialize on DOM content loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme manager
    window.themeManager = new ThemeManager();
    
    // Initialize toast manager
    window.toastManager = new ToastManager();
    
    // Initialize favorites manager
    window.favoritesManager = new FavoritesManager();
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Export for use in other scripts
window.ThemeManager = ThemeManager;
window.ToastManager = ToastManager;
window.FavoritesManager = FavoritesManager;