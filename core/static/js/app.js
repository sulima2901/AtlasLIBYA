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
    
    // Initialize search manager
    window.searchManager = new SearchManager();
    
    // Initialize announcement manager
    window.announcementManager = new AnnouncementManager();
    
    // Initialize carousel manager
    window.carouselManager = new CarouselManager();
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Live Search Functionality
class SearchManager {
    constructor() {
        this.searchInput = null;
        this.searchResults = null;
        this.searchTimeout = null;
        this.init();
    }

    init() {
        this.searchInput = document.getElementById('homeSearch');
        this.searchResults = document.getElementById('searchResults');
        
        if (this.searchInput && this.searchResults) {
            this.bindEvents();
        }
    }

    bindEvents() {
        this.searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            
            clearTimeout(this.searchTimeout);
            
            if (query.length < 2) {
                this.hideResults();
                return;
            }
            
            this.searchTimeout = setTimeout(() => {
                this.performSearch(query);
            }, 300);
        });
        
        // Hide results when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-container')) {
                this.hideResults();
            }
        });
        
        // Handle search button click
        const searchBtn = this.searchInput.parentElement.querySelector('.search-btn');
        if (searchBtn) {
            searchBtn.addEventListener('click', () => {
                this.redirectToSearch();
            });
        }
        
        // Handle enter key
        this.searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                this.redirectToSearch();
            }
        });
    }

    async performSearch(query) {
        try {
            const response = await fetch(`/api/search/?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            this.displayResults(data.results || []);
        } catch (error) {
            console.error('Search error:', error);
            this.hideResults();
        }
    }

    displayResults(results) {
        if (results.length === 0) {
            this.searchResults.innerHTML = `
                <div class="search-result-item text-center text-muted">
                    <i class="bi bi-search me-2"></i>لا توجد نتائج
                </div>
            `;
        } else {
            this.searchResults.innerHTML = results.map(product => `
                <div class="search-result-item d-flex align-items-center" onclick="window.location.href='/products/${product.slug}/'">
                    <img src="${product.image || '/static/core/no-image.png'}" alt="${product.name}" class="search-result-image me-3">
                    <div class="flex-grow-1">
                        <div class="fw-semibold">${product.name}</div>
                        <div class="text-muted small">${product.price} د.ل</div>
                    </div>
                </div>
            `).join('');
        }
        
        this.showResults();
    }

    showResults() {
        this.searchResults.style.display = 'block';
    }

    hideResults() {
        this.searchResults.style.display = 'none';
    }

    redirectToSearch() {
        const query = this.searchInput.value.trim();
        if (query) {
            window.location.href = `/products/?q=${encodeURIComponent(query)}`;
        }
    }
}

// Announcement Banner Manager
class AnnouncementManager {
    constructor() {
        this.init();
    }

    init() {
        // Restore dismissed state from localStorage
        const dismissed = localStorage.getItem('announcement-dismissed');
        if (dismissed) {
            const banner = document.getElementById('announcementBanner');
            if (banner) {
                banner.style.display = 'none';
            }
        }

        // Handle dismiss button
        document.addEventListener('click', (e) => {
            if (e.target.closest('.announcement-banner .btn-close')) {
                localStorage.setItem('announcement-dismissed', 'true');
            }
        });
    }
}

// Enhanced Carousel Manager
class CarouselManager {
    constructor() {
        this.carousels = new Map();
        this.init();
    }

    init() {
        // Find all carousels and initialize them
        document.querySelectorAll('.product-carousel').forEach(carousel => {
            this.initCarousel(carousel);
        });
    }

    initCarousel(carouselElement) {
        const carouselId = carouselElement.id;
        if (!carouselId) return;

        const config = {
            element: carouselElement,
            currentIndex: 0,
            autoAdvance: true,
            interval: 6000,
            direction: 'rtl', // RTL support
            touchStartX: 0,
            touchEndX: 0,
            isAnimating: false,
            intervalId: null
        };

        // Store config
        this.carousels.set(carouselId, config);

        // Setup carousel
        this.setupCarousel(config);
        this.bindCarouselEvents(config);
        this.startAutoAdvance(config);
    }

    setupCarousel(config) {
        const { element } = config;
        const cards = element.querySelectorAll('.product-card-modern');
        
        if (cards.length === 0) return;

        // Clone first and last cards for infinite scroll
        const firstCard = cards[0].cloneNode(true);
        const lastCard = cards[cards.length - 1].cloneNode(true);
        
        element.appendChild(firstCard);
        element.insertBefore(lastCard, cards[0]);

        // Update total cards count
        config.totalCards = cards.length;
        config.currentIndex = 1; // Start from actual first card (after cloned last)
        
        this.updateCarouselPosition(config, false);
    }

    bindCarouselEvents(config) {
        const { element } = config;
        const carouselId = element.id;

        // Navigation buttons
        const prevBtn = document.querySelector(`[data-carousel="${carouselId}"].carousel-btn-prev`);
        const nextBtn = document.querySelector(`[data-carousel="${carouselId}"].carousel-btn-next`);

        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.prevSlide(config));
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.nextSlide(config));
        }

        // Touch/drag support
        element.addEventListener('touchstart', (e) => {
            config.touchStartX = e.touches[0].clientX;
        });

        element.addEventListener('touchend', (e) => {
            config.touchEndX = e.changedTouches[0].clientX;
            this.handleTouch(config);
        });

        // Mouse drag support
        let isDragging = false;
        let startX = 0;
        let currentX = 0;

        element.addEventListener('mousedown', (e) => {
            isDragging = true;
            startX = e.clientX;
            element.style.cursor = 'grabbing';
        });

        element.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            currentX = e.clientX;
        });

        element.addEventListener('mouseup', (e) => {
            if (!isDragging) return;
            isDragging = false;
            element.style.cursor = 'grab';
            
            const diffX = startX - e.clientX;
            if (Math.abs(diffX) > 50) {
                if (diffX > 0) {
                    this.nextSlide(config);
                } else {
                    this.prevSlide(config);
                }
            }
        });

        // Pause on hover/focus
        element.addEventListener('mouseenter', () => this.pauseAutoAdvance(config));
        element.addEventListener('mouseleave', () => this.startAutoAdvance(config));
        element.addEventListener('focusin', () => this.pauseAutoAdvance(config));
        element.addEventListener('focusout', () => this.startAutoAdvance(config));
    }

    handleTouch(config) {
        const touchDiff = config.touchStartX - config.touchEndX;
        
        if (Math.abs(touchDiff) > 50) {
            if (touchDiff > 0) {
                this.nextSlide(config);
            } else {
                this.prevSlide(config);
            }
        }
    }

    nextSlide(config) {
        if (config.isAnimating) return;
        
        config.currentIndex++;
        this.updateCarouselPosition(config, true);
        
        // Handle infinite loop
        if (config.currentIndex > config.totalCards) {
            setTimeout(() => {
                config.currentIndex = 1;
                this.updateCarouselPosition(config, false);
            }, 300);
        }
    }

    prevSlide(config) {
        if (config.isAnimating) return;
        
        config.currentIndex--;
        this.updateCarouselPosition(config, true);
        
        // Handle infinite loop
        if (config.currentIndex < 1) {
            setTimeout(() => {
                config.currentIndex = config.totalCards;
                this.updateCarouselPosition(config, false);
            }, 300);
        }
    }

    updateCarouselPosition(config, animate = true) {
        const { element, currentIndex } = config;
        const cardWidth = element.querySelector('.product-card-modern')?.offsetWidth || 300;
        const translateX = -currentIndex * cardWidth;
        
        if (animate) {
            config.isAnimating = true;
            element.style.transition = 'transform 0.3s ease-in-out';
            setTimeout(() => {
                config.isAnimating = false;
            }, 300);
        } else {
            element.style.transition = 'none';
        }
        
        element.style.transform = `translateX(${translateX}px)`;
    }

    startAutoAdvance(config) {
        this.pauseAutoAdvance(config);
        
        if (config.autoAdvance) {
            config.intervalId = setInterval(() => {
                this.nextSlide(config);
            }, config.interval);
        }
    }

    pauseAutoAdvance(config) {
        if (config.intervalId) {
            clearInterval(config.intervalId);
            config.intervalId = null;
        }
    }

    // Public method to pause all carousels
    pauseAll() {
        this.carousels.forEach(config => this.pauseAutoAdvance(config));
    }

    // Public method to resume all carousels
    resumeAll() {
        this.carousels.forEach(config => this.startAutoAdvance(config));
    }
}

// Export for use in other scripts
window.ThemeManager = ThemeManager;
window.ToastManager = ToastManager;
window.FavoritesManager = FavoritesManager;
window.SearchManager = SearchManager;
window.AnnouncementManager = AnnouncementManager;
window.CarouselManager = CarouselManager;