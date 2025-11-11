// Training Manager - Interactive Scripts
// Анимации и интерактивность для Flask шаблонов

document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Fade-in animation for page elements
    const animateElements = document.querySelectorAll('[data-animate]');
    animateElements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        setTimeout(() => {
            el.style.transition = 'all 0.5s ease-out';
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // 2. Radio button animations with ripple effect
    const radioLabels = document.querySelectorAll('input[type="radio"] + div');
    radioLabels.forEach(label => {
        label.addEventListener('click', function(e) {
            // Create ripple effect
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = e.clientX - rect.left - size/2 + 'px';
            ripple.style.top = e.clientY - rect.top - size/2 + 'px';
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });

    // 3. Form validation with smooth error messages
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input[required], select[required]');
        
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateInput(this);
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('error')) {
                    validateInput(this);
                }
            });
        });
    });

    function validateInput(input) {
        const parent = input.parentElement;
        let errorMsg = parent.querySelector('.error-message');
        
        if (!input.validity.valid) {
            input.classList.add('error');
            if (!errorMsg) {
                errorMsg = document.createElement('p');
                errorMsg.className = 'error-message text-red-500 text-sm mt-1';
                parent.appendChild(errorMsg);
            }
            errorMsg.textContent = getErrorMessage(input);
            errorMsg.style.animation = 'slideDown 0.3s ease-out';
        } else {
            input.classList.remove('error');
            if (errorMsg) {
                errorMsg.style.animation = 'slideUp 0.3s ease-out';
                setTimeout(() => errorMsg.remove(), 300);
            }
        }
    }

    function getErrorMessage(input) {
        if (input.validity.valueMissing) {
            return 'Это поле обязательно';
        }
        if (input.validity.typeMismatch) {
            return 'Неверный формат';
        }
        if (input.validity.tooShort) {
            return 'Слишком короткое значение';
        }
        return 'Неверное значение';
    }

    // 4. Button press animation
    const buttons = document.querySelectorAll('button, .btn');
    buttons.forEach(button => {
        button.addEventListener('mousedown', function() {
            this.style.transform = 'scale(0.97)';
        });
        
        button.addEventListener('mouseup', function() {
            this.style.transform = 'scale(1)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });

    // 5. Auto-hide flash messages
    const flashMessages = document.querySelectorAll('.fixed.top-4 > div');
    flashMessages.forEach(msg => {
        setTimeout(() => {
            msg.style.animation = 'slideUp 0.3s ease-out';
            setTimeout(() => msg.remove(), 300);
        }, 5000);
    });

    // 6. Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
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

    // 7. Input focus animations
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.style.transform = 'scale(1.01)';
            this.parentElement.style.transition = 'transform 0.2s ease-out';
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.style.transform = 'scale(1)';
        });
    });

    // 8. Card hover effects
    const cards = document.querySelectorAll('.bg-white.rounded-3xl, .bg-white.rounded-2xl');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s ease-out';
            this.style.transform = 'translateY(-4px)';
            this.style.boxShadow = '0 20px 40px -10px rgba(0,0,0,0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '';
        });
    });

    // 9. Loading state for forms
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = `
                    <svg class="animate-spin h-5 w-5 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                `;
            }
        });
    });

    // 10. Number input formatting
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('input', function() {
            // Remove non-numeric characters
            this.value = this.value.replace(/[^0-9.]/g, '');
        });
    });

    // 11. Add smooth page transition effect
    window.addEventListener('beforeunload', function() {
        document.body.style.opacity = '0';
        document.body.style.transition = 'opacity 0.3s ease-out';
    });

    // 12. Prevent double form submission
    forms.forEach(form => {
        let isSubmitting = false;
        form.addEventListener('submit', function(e) {
            if (isSubmitting) {
                e.preventDefault();
                return false;
            }
            isSubmitting = true;
        });
    });

    // ========== WORKOUT PAGE FUNCTIONALITY ==========
    
    // Initialize workout timer if on workout page
    const workoutTimer = document.getElementById('workout-timer');
    if (workoutTimer) {
        const startTime = new Date(workoutTimer.getAttribute('data-start-time'));
        
        function updateTimer() {
            const now = new Date();
            const diff = Math.floor((now - startTime) / 1000);
            const minutes = Math.floor(diff / 60);
            const seconds = diff % 60;
            workoutTimer.textContent = 
                `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        }
        
        setInterval(updateTimer, 1000);
        updateTimer();
    }

    // Auto-save workout sets
    let saveTimeout;
    const SAVE_DELAY = 1000; // 1 second delay after input
    
    function saveSet(setId) {
        const row = document.querySelector(`tr[data-set-id="${setId}"]`);
        if (!row) return;
        
        const weight = row.querySelector('.weight-input').value;
        const reps = row.querySelector('.reps-input').value;
        const isCompleted = row.querySelector('.completed-checkbox').checked;

        fetch(`/workouts/set/${setId}/update`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                weight: weight ? parseFloat(weight) : null,
                reps: reps ? parseInt(reps) : null,
                is_completed: isCompleted
            })
        })
        .then(response => response.json())
        .then(data => {
            // Visual feedback
            row.style.backgroundColor = '#f0fdf4';
            setTimeout(() => {
                row.style.backgroundColor = '';
            }, 300);
        })
        .catch(error => console.error('Error saving set:', error));
    }

    // Event listeners for workout inputs
    document.querySelectorAll('.weight-input, .reps-input').forEach(input => {
        input.addEventListener('input', function() {
            const setId = this.getAttribute('data-set-id');
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => saveSet(setId), SAVE_DELAY);
        });
        
        input.addEventListener('blur', function() {
            const setId = this.getAttribute('data-set-id');
            clearTimeout(saveTimeout);
            saveSet(setId);
        });
    });

    // Completed checkbox handlers
    document.querySelectorAll('.completed-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const setId = this.getAttribute('data-set-id');
            saveSet(setId);
            
            const row = this.closest('tr');
            if (this.checked) {
                row.classList.add('opacity-60');
            } else {
                row.classList.remove('opacity-60');
            }
        });
    });

    // Toggle exercise notes
    window.toggleNotes = function(exerciseId) {
        const textarea = document.getElementById(`notes-${exerciseId}`);
        if (textarea) {
            textarea.classList.toggle('hidden');
            if (!textarea.classList.contains('hidden')) {
                textarea.focus();
            }
        }
    };

    // Confirm before leaving unfinished workout
    const workoutPage = document.querySelector('[data-workout-completed]');
    if (workoutPage) {
        const isFinished = workoutPage.getAttribute('data-workout-completed') === 'true';
        
        window.addEventListener('beforeunload', function(e) {
            if (!isFinished) {
                e.preventDefault();
                e.returnValue = '';
            }
        });
    }

    // Confirm workout finish if not all sets completed
    const finishForm = document.getElementById('finish-form');
    if (finishForm) {
        finishForm.addEventListener('submit', function(e) {
            const allSetsCompleted = Array.from(document.querySelectorAll('.completed-checkbox'))
                .filter(cb => {
                    const setLabel = cb.closest('tr').querySelector('.inline-flex');
                    return setLabel && !setLabel.textContent.includes('W'); // Exclude warmup
                })
                .every(cb => cb.checked);
            
            if (!allSetsCompleted) {
                const confirmed = confirm('Not all working sets are marked as completed. Finish workout anyway?');
                if (!confirmed) {
                    e.preventDefault();
                }
            }
        });
    }
});

// Add CSS animations dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideUp {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(-10px);
        }
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(59, 130, 246, 0.3);
        transform: scale(0);
        animation: rippleEffect 0.6s ease-out;
        pointer-events: none;
    }
    
    @keyframes rippleEffect {
        to {
            transform: scale(2);
            opacity: 0;
        }
    }
    
    input.error, select.error {
        border-color: #ef4444 !important;
        animation: shake 0.3s ease-out;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
`;
document.head.appendChild(style);
