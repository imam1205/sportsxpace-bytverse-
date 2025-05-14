document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const dateInput = document.getElementById('tanggal_booking');
    const startTimeInput = document.getElementById('jam_booking_mulai');
    const endTimeInput = document.getElementById('jam_booking_selesai');
    const timeSlotsContainer = document.getElementById('time-slots-container');
    const fieldIdInput = document.getElementById('field_id');
    
    // Only proceed if we're on the booking page
    if (!dateInput || !timeSlotsContainer) {
        return;
    }
    
    const fieldId = window.location.pathname.split('/').pop();
    
    // Initialize date picker with min date of today
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    dateInput.min = `${yyyy}-${mm}-${dd}`;
    
    // When date changes, fetch available slots
    dateInput.addEventListener('change', function() {
        fetchAvailability();
    });
    
    // Function to fetch availability for selected date
    function fetchAvailability() {
        const selectedDate = dateInput.value;
        
        if (!selectedDate) {
            return;
        }
        
        timeSlotsContainer.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
        
        fetch(`/customer/field/${fieldId}/check-availability?date=${selectedDate}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                renderTimeSlots(data);
            })
            .catch(error => {
                console.error('Error fetching availability:', error);
                timeSlotsContainer.innerHTML = '<div class="alert alert-danger">Gagal memuat ketersediaan jadwal. Silakan coba lagi.</div>';
            });
    }
    
    // Function to render time slots
    function renderTimeSlots(data) {
        timeSlotsContainer.innerHTML = '';
        
        if (!data.operating_hours) {
            timeSlotsContainer.innerHTML = '<div class="alert alert-warning">Informasi jam operasional tidak tersedia.</div>';
            return;
        }
        
        const openHour = parseInt(data.operating_hours.open.split(':')[0]);
        const closeHour = parseInt(data.operating_hours.close.split(':')[0]);
        
        // Create time slots - we'll create 1-hour slots for simplicity
        const slotDuration = 60; // in minutes
        const slotsContainer = document.createElement('div');
        slotsContainer.className = 'row';
        
        // Convert booked slots to easily checkable format
        const bookedSlots = data.booked_slots.map(slot => {
            return {
                start: slot.start,
                end: slot.end
            };
        });
        
        // Create hourly slots
        for (let hour = openHour; hour < closeHour; hour++) {
            const startTime = `${hour.toString().padStart(2, '0')}:00`;
            const endTime = `${(hour + 1).toString().padStart(2, '0')}:00`;
            
            // Check if this slot is booked
            const isBooked = bookedSlots.some(slot => {
                const slotStart = slot.start;
                const slotEnd = slot.end;
                
                // Check if this hour overlaps with a booking
                return (startTime >= slotStart && startTime < slotEnd) || 
                       (endTime > slotStart && endTime <= slotEnd) ||
                       (startTime <= slotStart && endTime >= slotEnd);
            });
            
            // Create the time slot element
            const slotCol = document.createElement('div');
            slotCol.className = 'col-md-3 col-6 mb-3';
            
            const slot = document.createElement('div');
            slot.className = `time-slot ${isBooked ? 'booked' : 'available'}`;
            slot.dataset.start = startTime;
            slot.dataset.end = endTime;
            slot.innerHTML = `${startTime} - ${endTime}`;
            
            if (!isBooked) {
                slot.addEventListener('click', function() {
                    selectTimeSlot(this);
                });
            }
            
            slotCol.appendChild(slot);
            slotsContainer.appendChild(slotCol);
        }
        
        timeSlotsContainer.appendChild(slotsContainer);
        
        // Add helper message
        const helperMessage = document.createElement('div');
        helperMessage.className = 'mt-3 text-muted small';
        helperMessage.innerHTML = `
            <div class="d-flex align-items-center mb-2">
                <div class="time-slot available me-2" style="width: 20px; height: 20px;"></div>
                <span>Tersedia</span>
            </div>
            <div class="d-flex align-items-center">
                <div class="time-slot booked me-2" style="width: 20px; height: 20px;"></div>
                <span>Sudah dipesan</span>
            </div>
        `;
        timeSlotsContainer.appendChild(helperMessage);
    }
    
    // Function to handle time slot selection
    function selectTimeSlot(slot) {
        // Remove selected class from all slots
        document.querySelectorAll('.time-slot.selected').forEach(el => {
            el.classList.remove('selected');
        });
        
        // Add selected class to this slot
        slot.classList.add('selected');
        
        // Update form inputs
        startTimeInput.value = slot.dataset.start;
        endTimeInput.value = slot.dataset.end;
    }
    
    // Initialize if date is already set
    if (dateInput.value) {
        fetchAvailability();
    }
});
