document.addEventListener('DOMContentLoaded', function() {
    // Get payment method elements
    const paymentMethodRadios = document.querySelectorAll('input[name="metode"]');
    const paymentMethodDetails = document.querySelectorAll('.payment-method-details');
    
    // Only proceed if we're on the payment page
    if (paymentMethodRadios.length === 0) {
        return;
    }
    
    // Show/hide payment details when method changes
    paymentMethodRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            const selectedMethod = this.value;
            
            // Hide all details first
            paymentMethodDetails.forEach(detail => {
                detail.classList.add('d-none');
            });
            
            // Show the details for selected method
            const selectedDetails = document.querySelector(`.payment-method-details[data-method="${selectedMethod}"]`);
            if (selectedDetails) {
                selectedDetails.classList.remove('d-none');
            }
        });
    });
    
    // Trigger change event for pre-selected method
    const checkedRadio = document.querySelector('input[name="metode"]:checked');
    if (checkedRadio) {
        checkedRadio.dispatchEvent(new Event('change'));
    }
    
    // Payment form validation
    const paymentForm = document.getElementById('payment-form');
    if (paymentForm) {
        paymentForm.addEventListener('submit', function(e) {
            const selectedMethod = document.querySelector('input[name="metode"]:checked');
            
            if (!selectedMethod) {
                e.preventDefault();
                alert('Silakan pilih metode pembayaran.');
                return false;
            }
            
            // For demonstration purposes, we'll just show a loading indicator
            const submitButton = this.querySelector('button[type="submit"]');
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Memproses...';
            submitButton.disabled = true;
        });
    }
    
    // Countdown timer (for demo purposes when payment is pending)
    const countdownElement = document.getElementById('payment-countdown');
    if (countdownElement) {
        let timeLeft = 900; // 15 minutes in seconds
        
        const countdownTimer = setInterval(function() {
            timeLeft--;
            
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            
            countdownElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
            if (timeLeft <= 0) {
                clearInterval(countdownTimer);
                countdownElement.textContent = '00:00';
                document.getElementById('payment-expired-alert').classList.remove('d-none');
                document.getElementById('payment-button').classList.add('d-none');
            }
        }, 1000);
    }
});
