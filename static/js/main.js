document.addEventListener('DOMContentLoaded', function() {
    // Enable tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Enable popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
    
    // Auto fade out for flash messages
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            const alert = new bootstrap.Alert(message);
            alert.close();
        }, 5000);
    });
    
    // Star rating display
    document.querySelectorAll('.star-rating').forEach(container => {
        const rating = parseFloat(container.dataset.rating);
        let stars = '';
        
        // Full stars
        for (let i = 1; i <= Math.floor(rating); i++) {
            stars += '<i class="fas fa-star"></i>';
        }
        
        // Half stars
        if (rating % 1 >= 0.5) {
            stars += '<i class="fas fa-star-half-alt"></i>';
        }
        
        // Empty stars
        for (let i = Math.ceil(rating); i < 5; i++) {
            stars += '<i class="far fa-star"></i>';
        }
        
        container.innerHTML = stars;
    });
    
    // Filter form submission (fields search)
    const filterForm = document.getElementById('filter-form');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            // Remove empty fields to keep URL clean
            const inputs = this.querySelectorAll('input, select');
            inputs.forEach(input => {
                if (!input.value) {
                    input.disabled = true;
                }
            });
        });
    }
});
