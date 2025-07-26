// Nura AI Quiz Engine JavaScript

class Quiz {
    constructor(options) {
        this.totalQuestions = options.totalQuestions;
        this.timeLimit = options.timeLimit; // in minutes
        this.questions = options.questions;
        this.currentQuestion = 1;
        this.answers = {};
        this.timer = null;
        this.timeRemaining = this.timeLimit * 60; // convert to seconds
        this.isSubmitted = false;
        
        this.elements = {
            form: document.getElementById('quizForm'),
            timer: document.getElementById('timer'),
            timeLeft: document.getElementById('time-left'),
            currentQuestion: document.getElementById('current-question'),
            progressBar: document.getElementById('progress-bar'),
            answeredCount: document.getElementById('answered-count'),
            remainingCount: document.getElementById('remaining-count'),
            prevBtn: document.getElementById('prev-btn'),
            nextBtn: document.getElementById('next-btn'),
            submitBtn: document.getElementById('submit-btn'),
            questionCards: document.querySelectorAll('.question-card'),
            questionNavs: document.querySelectorAll('.question-nav'),
            submitModal: document.getElementById('submitModal'),
            modalAnswered: document.getElementById('modal-answered'),
            confirmSubmit: document.getElementById('confirm-submit')
        };
    }

    init() {
        this.bindEvents();
        this.startTimer();
        this.updateUI();
        this.loadSavedAnswers();
        this.showQuestion(1);
    }

    bindEvents() {
        // Navigation buttons
        this.elements.prevBtn.addEventListener('click', () => this.previousQuestion());
        this.elements.nextBtn.addEventListener('click', () => this.nextQuestion());
        
        // Question navigation
        this.elements.questionNavs.forEach(nav => {
            nav.addEventListener('click', (e) => {
                const questionNum = parseInt(nav.getAttribute('data-question'));
                this.showQuestion(questionNum);
            });
        });
        
        // Form submission
        this.elements.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.showSubmitModal();
        });
        
        // Submit button
        this.elements.submitBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.showSubmitModal();
        });
        
        // Confirm submit
        this.elements.confirmSubmit.addEventListener('click', () => {
            this.submitQuiz();
        });
        
        // Answer selection
        this.elements.form.addEventListener('change', (e) => {
            if (e.target.type === 'radio') {
                console.log('Radio changed:', e.target.name, '=', e.target.value);
                this.saveAnswer(e.target);
                this.updateVisualSelection(e.target);
                this.updateAnsweredStatus();
            }
        });
        
        // Handle clicks on form-check divs to select radio buttons
        this.elements.form.addEventListener('click', (e) => {
            const formCheck = e.target.closest('.form-check');
            if (formCheck) {
                const radio = formCheck.querySelector('input[type="radio"]');
                if (radio && e.target !== radio) {
                    radio.checked = true;
                    radio.dispatchEvent(new Event('change', { bubbles: true }));
                    this.updateVisualSelection(radio);
                }
            }
        });
        
        // Update visual selection when radio buttons change
        this.elements.form.addEventListener('change', (e) => {
            if (e.target.type === 'radio') {
                this.updateVisualSelection(e.target);
            }
        });
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (!this.isSubmitted) {
                this.handleKeyboardNavigation(e);
            }
        });
        
        // Page visibility change (pause timer when tab is not active)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseTimer();
            } else {
                this.resumeTimer();
            }
        });
        
        // Prevent accidental page refresh
        window.addEventListener('beforeunload', (e) => {
            if (!this.isSubmitted) {
                e.preventDefault();
                e.returnValue = 'Are you sure you want to leave? Your quiz progress will be lost.';
            }
        });
    }

    startTimer() {
        this.updateTimerDisplay();
        
        this.timer = setInterval(() => {
            this.timeRemaining--;
            this.updateTimerDisplay();
            
            // Warning when 5 minutes left
            if (this.timeRemaining === 300) {
                this.showTimeWarning();
            }
            
            // Auto-submit when time is up
            if (this.timeRemaining <= 0) {
                this.timeUp();
            }
        }, 1000);
    }

    pauseTimer() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
    }

    resumeTimer() {
        if (!this.timer && this.timeRemaining > 0 && !this.isSubmitted) {
            this.startTimer();
        }
    }

    updateTimerDisplay() {
        const minutes = Math.floor(this.timeRemaining / 60);
        const seconds = this.timeRemaining % 60;
        const timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        if (this.elements.timer) {
            this.elements.timer.textContent = timeString;
        }
        
        if (this.elements.timeLeft) {
            this.elements.timeLeft.textContent = timeString;
        }
        
        // Change timer color when time is running low
        if (this.timeRemaining <= 300) { // 5 minutes
            this.elements.timer.style.color = '#ef4444';
        } else if (this.timeRemaining <= 600) { // 10 minutes
            this.elements.timer.style.color = '#f59e0b';
        }
    }

    showTimeWarning() {
        this.showNotification('⚠️ Only 5 minutes remaining!', 'warning', 5000);
    }

    timeUp() {
        this.pauseTimer();
        this.showNotification('⏰ Time\'s up! Submitting your quiz...', 'info', 3000);
        
        setTimeout(() => {
            this.submitQuiz();
        }, 3000);
    }

    showQuestion(questionNum) {
        if (questionNum < 1 || questionNum > this.totalQuestions) {
            return;
        }
        
        // Hide all questions
        this.elements.questionCards.forEach(card => {
            card.style.display = 'none';
        });
        
        // Show target question
        const targetCard = document.querySelector(`[data-question="${questionNum}"]`);
        if (targetCard) {
            targetCard.style.display = 'block';
            targetCard.classList.add('slide-in');
        }
        
        this.currentQuestion = questionNum;
        this.updateNavigationButtons();
        this.updateProgressBar();
        this.updateQuestionNavigation();
        this.updateUI();
        
        // Scroll to top
        window.scrollTo(0, 0);
    }

    previousQuestion() {
        if (this.currentQuestion > 1) {
            this.showQuestion(this.currentQuestion - 1);
        }
    }

    nextQuestion() {
        if (this.currentQuestion < this.totalQuestions) {
            this.showQuestion(this.currentQuestion + 1);
        }
    }

    updateNavigationButtons() {
        // Previous button
        this.elements.prevBtn.disabled = this.currentQuestion === 1;
        
        // Next/Submit button
        if (this.currentQuestion === this.totalQuestions) {
            this.elements.nextBtn.style.display = 'none';
            this.elements.submitBtn.style.display = 'inline-block';
        } else {
            this.elements.nextBtn.style.display = 'inline-block';
            this.elements.submitBtn.style.display = 'none';
        }
    }

    updateProgressBar() {
        const progress = (this.currentQuestion / this.totalQuestions) * 100;
        this.elements.progressBar.style.width = `${progress}%`;
    }

    updateQuestionNavigation() {
        this.elements.questionNavs.forEach(nav => {
            const questionNum = parseInt(nav.getAttribute('data-question'));
            
            // Remove all status classes
            nav.classList.remove('current', 'answered');
            
            // Add current class
            if (questionNum === this.currentQuestion) {
                nav.classList.add('current');
            }
            
            // Add answered class
            if (this.isQuestionAnswered(questionNum)) {
                nav.classList.add('answered');
            }
        });
    }

    updateUI() {
        if (this.elements.currentQuestion) {
            this.elements.currentQuestion.textContent = this.currentQuestion;
        }
        
        const answeredCount = this.getAnsweredCount();
        
        if (this.elements.answeredCount) {
            this.elements.answeredCount.textContent = answeredCount;
        }
        
        if (this.elements.remainingCount) {
            this.elements.remainingCount.textContent = this.totalQuestions - answeredCount;
        }
    }

    saveAnswer(input) {
        const questionId = input.name.replace('question_', '');
        this.answers[questionId] = input.value;
        
        // Save to localStorage as backup
        localStorage.setItem('quiz_answers', JSON.stringify(this.answers));
    }

    loadSavedAnswers() {
        const saved = localStorage.getItem('quiz_answers');
        if (saved) {
            try {
                this.answers = JSON.parse(saved);
                
                // Restore form values
                Object.entries(this.answers).forEach(([questionId, answer]) => {
                    const input = document.querySelector(`input[name="question_${questionId}"][value="${answer}"]`);
                    if (input) {
                        input.checked = true;
                    }
                });
            } catch (e) {
                console.error('Error loading saved answers:', e);
            }
        }
    }

    isQuestionAnswered(questionNum) {
        const questionCard = document.querySelector(`[data-question="${questionNum}"]`);
        if (!questionCard) return false;
        
        const inputs = questionCard.querySelectorAll('input[type="radio"]');
        return Array.from(inputs).some(input => input.checked);
    }

    getAnsweredCount() {
        let count = 0;
        for (let i = 1; i <= this.totalQuestions; i++) {
            if (this.isQuestionAnswered(i)) {
                count++;
            }
        }
        return count;
    }

    updateAnsweredStatus() {
        this.updateUI();
        this.updateQuestionNavigation();
    }

    showSubmitModal() {
        const answeredCount = this.getAnsweredCount();
        
        if (this.elements.modalAnswered) {
            this.elements.modalAnswered.textContent = answeredCount;
        }
        
        const modal = new bootstrap.Modal(this.elements.submitModal);
        modal.show();
    }

    submitQuiz() {
        if (this.isSubmitted) return;
        
        this.isSubmitted = true;
        this.pauseTimer();
        
        // Ensure all radio buttons are properly in the form before submission
        const radioButtons = this.elements.form.querySelectorAll('input[type="radio"]:checked');
        console.log('Submitting quiz with checked radios:');
        radioButtons.forEach(radio => {
            console.log(`${radio.name}: ${radio.value}`);
        });
        
        // Clear saved data
        localStorage.removeItem('quiz_answers');
        
        // Show loading state
        this.showLoadingState();
        
        // Create a new form with the data and submit it
        const submitForm = document.createElement('form');
        submitForm.method = 'POST';
        submitForm.action = this.elements.form.action;
        
        // Add all checked radio buttons as hidden inputs
        radioButtons.forEach(radio => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = radio.name;
            input.value = radio.value;
            submitForm.appendChild(input);
        });
        
        document.body.appendChild(submitForm);
        submitForm.submit();
    }

    showLoadingState() {
        const submitButton = this.elements.confirmSubmit;
        const originalText = submitButton.innerHTML;
        
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Submitting...';
        submitButton.disabled = true;
        
        // Disable all form inputs
        const inputs = this.elements.form.querySelectorAll('input, button');
        inputs.forEach(input => {
            input.disabled = true;
        });
    }

    handleKeyboardNavigation(e) {
        switch (e.key) {
            case 'ArrowLeft':
                e.preventDefault();
                this.previousQuestion();
                break;
            case 'ArrowRight':
                e.preventDefault();
                this.nextQuestion();
                break;
            case 'Enter':
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    this.showSubmitModal();
                }
                break;
            case '1':
            case '2':
            case '3':
            case '4':
            case '5':
            case '6':
            case '7':
            case '8':
            case '9':
                if (e.altKey) {
                    e.preventDefault();
                    const questionNum = parseInt(e.key);
                    if (questionNum <= this.totalQuestions) {
                        this.showQuestion(questionNum);
                    }
                }
                break;
        }
    }

    showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            animation: slideInRight 0.3s ease-out;
        `;
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        }, duration);
    }

    updateVisualSelection(radio) {
        // Remove selection from all options in the same question
        const questionName = radio.name;
        const allOptionsInQuestion = document.querySelectorAll(`input[name="${questionName}"]`);
        
        allOptionsInQuestion.forEach(opt => {
            const formCheck = opt.closest('.form-check');
            if (formCheck) {
                formCheck.classList.remove('selected');
            }
        });
        
        // Add selection to the current option
        const currentFormCheck = radio.closest('.form-check');
        if (currentFormCheck && radio.checked) {
            currentFormCheck.classList.add('selected');
        }
    }

    // Analytics methods
    getQuizStats() {
        return {
            totalQuestions: this.totalQuestions,
            answeredQuestions: this.getAnsweredCount(),
            currentQuestion: this.currentQuestion,
            timeRemaining: this.timeRemaining,
            timeElapsed: (this.timeLimit * 60) - this.timeRemaining,
            completionPercentage: (this.getAnsweredCount() / this.totalQuestions) * 100
        };
    }

    // Method to track user behavior
    trackInteraction(action, data = {}) {
        const event = {
            action,
            timestamp: new Date().toISOString(),
            currentQuestion: this.currentQuestion,
            timeRemaining: this.timeRemaining,
            ...data
        };
        
        // Store interactions for analytics
        const interactions = JSON.parse(localStorage.getItem('quiz_interactions') || '[]');
        interactions.push(event);
        localStorage.setItem('quiz_interactions', JSON.stringify(interactions));
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
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
    
    .slide-in {
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
`;
document.head.appendChild(style);

// Export for global use
window.Quiz = Quiz;
