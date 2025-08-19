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
    
    // Initialize new managers
    window.liveSearchManager = new LiveSearchManager();
    window.carouselManager = new CarouselManager();
    window.announcementManager = new AnnouncementManager();
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Live Search Manager
class LiveSearchManager {
    constructor() {
        this.searchInput = document.getElementById('globalSearchInput');
        this.searchResults = document.getElementById('searchResults');
        this.debounceTimer = null;
        this.isLoading = false;
        
        if (this.searchInput) {
            this.init();
        }
    }
    
    init() {
        // Bind search input events
        this.searchInput.addEventListener('input', (e) => {
            this.debounceSearch(e.target.value.trim());
        });
        
        this.searchInput.addEventListener('focus', () => {
            if (this.searchInput.value.trim().length >= 2) {
                this.searchResults.classList.remove('d-none');
            }
        });
        
        // Hide results when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-wrapper')) {
                this.searchResults.classList.add('d-none');
            }
        });
        
        // Handle Enter key for full search
        this.searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                const query = this.searchInput.value.trim();
                if (query) {
                    window.location.href = `/products/?q=${encodeURIComponent(query)}`;
                }
            }
        });
    }
    
    debounceSearch(query) {
        clearTimeout(this.debounceTimer);
        
        if (query.length < 2) {
            this.searchResults.classList.add('d-none');
            return;
        }
        
        this.debounceTimer = setTimeout(() => {
            this.performSearch(query);
        }, 300);
    }
    
    async performSearch(query) {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoadingState();
        
        try {
            const response = await fetch(`/products/api/live-search/?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            this.displayResults(data.results);
            this.searchResults.classList.remove('d-none');
        } catch (error) {
            console.error('Search error:', error);
            this.showErrorState();
        } finally {
            this.isLoading = false;
        }
    }
    
    displayResults(results) {
        if (results.length === 0) {
            this.searchResults.innerHTML = `
                <div class="p-3 text-center text-muted">
                    <i class="bi bi-search me-2"></i>
                    لا توجد نتائج للبحث
                </div>
            `;
            return;
        }
        
        let html = '';
        results.forEach(product => {
            const stockBadge = product.is_available 
                ? '<span class="badge bg-success me-2">متوفر</span>'
                : '<span class="badge bg-secondary me-2">غير متوفر</span>';
                
            html += `
                <div class="search-result-item" onclick="window.location.href='${product.url}'">
                    <div class="d-flex align-items-center">
                        <img src="${product.image_url}" alt="${product.name}" class="search-result-image me-3">
                        <div class="flex-grow-1">
                            <div class="fw-semibold mb-1">${product.name}</div>
                            <div class="small text-muted mb-1">${product.brand}</div>
                            <div class="d-flex align-items-center">
                                ${stockBadge}
                                <span>${product.price_html}</span>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        if (results.length >= 8) {
            html += `
                <div class="p-3 text-center border-top">
                    <a href="/products/?q=${encodeURIComponent(this.searchInput.value.trim())}" 
                       class="btn btn-outline-primary btn-sm">
                        عرض كل النتائج
                        <i class="bi bi-arrow-left me-1"></i>
                    </a>
                </div>
            `;
        }
        
        this.searchResults.innerHTML = html;
    }
    
    showLoadingState() {
        this.searchResults.innerHTML = `
            <div class="p-3 text-center">
                <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                جاري البحث...
            </div>
        `;
        this.searchResults.classList.remove('d-none');
    }
    
    showErrorState() {
        this.searchResults.innerHTML = `
            <div class="p-3 text-center text-danger">
                <i class="bi bi-exclamation-triangle me-2"></i>
                حدث خطأ في البحث
            </div>
        `;
    }
}

// Enhanced Carousel Manager with auto-advance
class CarouselManager {
    constructor() {
        this.carousels = document.querySelectorAll('.product-carousel');
        this.autoAdvanceInterval = 6000; // 6 seconds
        this.intervals = new Map();
        
        if (this.carousels.length > 0) {
            this.init();
        }
    }
    
    init() {
        this.carousels.forEach(carousel => {
            const wrapper = carousel.closest('.product-carousel-wrapper');
            const prevBtn = wrapper?.querySelector('.carousel-btn-prev');
            const nextBtn = wrapper?.querySelector('.carousel-btn-next');
            
            if (prevBtn && nextBtn) {
                this.setupCarousel(carousel, prevBtn, nextBtn);
            }
        });
    }
    
    setupCarousel(carousel, prevBtn, nextBtn) {
        const carouselId = carousel.id;
        let currentIndex = 0;
        const items = carousel.children;
        const totalItems = items.length;
        const itemsToShow = this.getItemsToShow();
        const maxIndex = Math.max(0, totalItems - itemsToShow);
        
        if (totalItems <= itemsToShow) {
            prevBtn.style.display = 'none';
            nextBtn.style.display = 'none';
            return;
        }
        
        // Navigation functions
        const goToIndex = (index) => {
            currentIndex = Math.max(0, Math.min(index, maxIndex));
            const translateX = -(currentIndex * (100 / itemsToShow));
            carousel.style.transform = `translateX(${translateX}%)`;
            
            // Update button states
            prevBtn.disabled = currentIndex === 0;
            nextBtn.disabled = currentIndex === maxIndex;
        };
        
        const goNext = () => {
            if (currentIndex < maxIndex) {
                goToIndex(currentIndex + 1);
            } else {
                // Seamless loop - go back to start
                goToIndex(0);
            }
        };
        
        const goPrev = () => {
            if (currentIndex > 0) {
                goToIndex(currentIndex - 1);
            } else {
                // Go to end for seamless loop
                goToIndex(maxIndex);
            }
        };
        
        // Event listeners
        nextBtn.addEventListener('click', goNext);
        prevBtn.addEventListener('click', goPrev);
        
        // Auto-advance functionality
        const startAutoAdvance = () => {
            this.intervals.set(carouselId, setInterval(goNext, this.autoAdvanceInterval));
        };
        
        const stopAutoAdvance = () => {
            const interval = this.intervals.get(carouselId);
            if (interval) {
                clearInterval(interval);
                this.intervals.delete(carouselId);
            }
        };
        
        // Pause on hover/focus
        carousel.addEventListener('mouseenter', stopAutoAdvance);
        carousel.addEventListener('mouseleave', startAutoAdvance);
        carousel.addEventListener('focusin', stopAutoAdvance);
        carousel.addEventListener('focusout', startAutoAdvance);
        
        // Manual control stops auto-advance temporarily
        [prevBtn, nextBtn].forEach(btn => {
            btn.addEventListener('click', () => {
                stopAutoAdvance();
                setTimeout(startAutoAdvance, this.autoAdvanceInterval * 2); // Resume after 12s
            });
        });
        
        // Touch/drag support for mobile
        this.addTouchSupport(carousel, goNext, goPrev, stopAutoAdvance, startAutoAdvance);
        
        // Initialize
        goToIndex(0);
        startAutoAdvance();
    }
    
    addTouchSupport(carousel, goNext, goPrev, stopAutoAdvance, startAutoAdvance) {
        let startX = 0;
        let startY = 0;
        let isDragging = false;
        
        carousel.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
            isDragging = false;
            stopAutoAdvance();
        }, { passive: true });
        
        carousel.addEventListener('touchmove', (e) => {
            if (!isDragging) {
                const deltaX = Math.abs(e.touches[0].clientX - startX);
                const deltaY = Math.abs(e.touches[0].clientY - startY);
                isDragging = deltaX > deltaY && deltaX > 10;
            }
        }, { passive: true });
        
        carousel.addEventListener('touchend', (e) => {
            if (isDragging) {
                const endX = e.changedTouches[0].clientX;
                const deltaX = startX - endX;
                
                if (Math.abs(deltaX) > 50) {
                    if (deltaX > 0) {
                        goNext();
                    } else {
                        goPrev();
                    }
                }
            }
            setTimeout(startAutoAdvance, 1000);
        }, { passive: true });
    }
    
    getItemsToShow() {
        const width = window.innerWidth;
        if (width < 768) return 1;
        if (width < 992) return 2;
        if (width < 1200) return 3;
        return 4;
    }
}

// Announcement Banner Manager
class AnnouncementManager {
    constructor() {
        this.banner = document.getElementById('announcementBanner');
        this.dismissBtn = document.getElementById('dismissAnnouncement');
        
        if (this.banner && this.dismissBtn) {
            this.init();
        }
    }
    
    init() {
        // Check if banner was previously dismissed
        const dismissed = localStorage.getItem('announcement_dismissed');
        const dismissedTime = localStorage.getItem('announcement_dismissed_time');
        
        // Show banner if not dismissed or dismissed more than 24 hours ago
        const shouldShow = !dismissed || 
            (dismissedTime && Date.now() - parseInt(dismissedTime) > 24 * 60 * 60 * 1000);
        
        if (shouldShow) {
            this.showBanner();
        }
        
        // Handle dismiss
        this.dismissBtn.addEventListener('click', () => {
            this.dismissBanner();
        });
    }
    
    showBanner() {
        this.banner.style.display = 'block';
        
        // Adjust navbar if needed
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            navbar.style.marginBottom = '0';
        }
    }
    
    dismissBanner() {
        this.banner.style.display = 'none';
        localStorage.setItem('announcement_dismissed', 'true');
        localStorage.setItem('announcement_dismissed_time', Date.now().toString());
        
        // Restore navbar margin
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            navbar.style.marginBottom = '';
        }
    }
}

// Export for use in other scripts
window.ThemeManager = ThemeManager;
window.ToastManager = ToastManager;
window.FavoritesManager = FavoritesManager;
window.LiveSearchManager = LiveSearchManager;
window.CarouselManager = CarouselManager;
window.AnnouncementManager = AnnouncementManager;