// Nura AI Dashboard JavaScript

class Dashboard {
    constructor() {
        this.charts = {};
        this.animationSpeed = 300;
        this.init();
    }

    init() {
        this.initializeCharts();
        this.initializeAnimations();
        this.initializeInteractions();
        this.startPerformanceUpdates();
    }

    initializeCharts() {
        // Performance Trends Chart
        const performanceCtx = document.getElementById('performanceChart');
        if (performanceCtx) {
            this.createPerformanceChart(performanceCtx);
        }

        // Subject Performance Chart (for teacher dashboard)
        const subjectCtx = document.getElementById('subjectPerformanceChart');
        if (subjectCtx) {
            this.createSubjectChart(subjectCtx);
        }
    }

    createPerformanceChart(ctx) {
        const chartData = this.getChartData(ctx);
        
        this.charts.performance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Quiz Scores',
                    data: chartData.scores,
                    borderColor: '#4f46e5',
                    backgroundColor: 'rgba(79, 70, 229, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#4f46e5',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#4f46e5',
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: false,
                        callbacks: {
                            label: function(context) {
                                return `Score: ${context.parsed.y}%`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#64748b'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            color: '#64748b',
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                elements: {
                    point: {
                        hoverBackgroundColor: '#4f46e5'
                    }
                }
            }
        });
    }

    createSubjectChart(ctx) {
        const chartData = this.getSubjectChartData(ctx);
        
        this.charts.subjects = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: chartData.labels,
                datasets: [{
                    data: chartData.scores,
                    backgroundColor: [
                        '#4f46e5',
                        '#10b981',
                        '#f59e0b',
                        '#ef4444',
                        '#8b5cf6',
                        '#06b6d4'
                    ],
                    borderWidth: 0,
                    hoverBorderWidth: 2,
                    hoverBorderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            color: '#64748b'
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#4f46e5',
                        borderWidth: 1,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(context) {
                                return `${context.label}: ${context.parsed}%`;
                            }
                        }
                    }
                },
                cutout: '60%'
            }
        });
    }

    getChartData(ctx) {
        // Extract data from data attributes or global variables
        const labels = [];
        const scores = [];
        
        // This would be populated from the template data
        if (window.performanceData) {
            window.performanceData.recent_quizzes.forEach(quiz => {
                labels.push(new Date(quiz.date).toLocaleDateString());
                scores.push(quiz.score);
            });
        }
        
        return { labels, scores };
    }

    getSubjectChartData(ctx) {
        const labels = [];
        const scores = [];
        
        if (window.subjectData) {
            Object.entries(window.subjectData).forEach(([subject, data]) => {
                labels.push(subject);
                scores.push(data.average_score);
            });
        }
        
        return { labels, scores };
    }

    initializeAnimations() {
        // Animate progress bars
        this.animateProgressBars();
        
        // Animate counters
        this.animateCounters();
        
        // Animate cards on scroll
        this.initializeScrollAnimations();
    }

    animateProgressBars() {
        const progressBars = document.querySelectorAll('.progress-bar');
        
        progressBars.forEach(bar => {
            const width = bar.style.width || bar.getAttribute('aria-valuenow') + '%';
            bar.style.width = '0%';
            
            setTimeout(() => {
                bar.style.transition = 'width 1s ease-in-out';
                bar.style.width = width;
            }, 100);
        });
    }

    animateCounters() {
        const counters = document.querySelectorAll('[data-count]');
        
        counters.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-count'));
            const duration = 2000;
            const step = target / (duration / 16);
            let current = 0;
            
            const timer = setInterval(() => {
                current += step;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                counter.textContent = Math.floor(current);
            }, 16);
        });
    }

    initializeScrollAnimations() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        }, {
            threshold: 0.1
        });

        document.querySelectorAll('.card, .benefit-item, .feature-card').forEach(el => {
            observer.observe(el);
        });
    }

    initializeInteractions() {
        // Performance card hover effects
        this.initializeCardHovers();
        
        // Subject filter functionality
        this.initializeFilters();
        
        // Refresh data functionality
        this.initializeRefresh();
    }

    initializeCardHovers() {
        const performanceCards = document.querySelectorAll('.traffic-light .card');
        
        performanceCards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-5px)';
                card.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.15)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0)';
                card.style.boxShadow = '';
            });
        });
    }

    initializeFilters() {
        const filterButtons = document.querySelectorAll('[data-filter]');
        
        filterButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const filter = button.getAttribute('data-filter');
                this.filterContent(filter);
                
                // Update active state
                filterButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
            });
        });
    }

    filterContent(filter) {
        const items = document.querySelectorAll('[data-category]');
        
        items.forEach(item => {
            const category = item.getAttribute('data-category');
            if (filter === 'all' || category === filter) {
                item.style.display = 'block';
                item.classList.add('fade-in');
            } else {
                item.style.display = 'none';
            }
        });
    }

    initializeRefresh() {
        const refreshButton = document.getElementById('refreshData');
        
        if (refreshButton) {
            refreshButton.addEventListener('click', () => {
                this.refreshDashboardData();
            });
        }
    }

    refreshDashboardData() {
        const refreshButton = document.getElementById('refreshData');
        const originalText = refreshButton.innerHTML;
        
        refreshButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Refreshing...';
        refreshButton.disabled = true;
        
        // Simulate data refresh
        setTimeout(() => {
            this.updateCharts();
            this.updateProgressBars();
            
            refreshButton.innerHTML = originalText;
            refreshButton.disabled = false;
            
            this.showNotification('Dashboard data refreshed successfully!', 'success');
        }, 2000);
    }

    updateCharts() {
        Object.values(this.charts).forEach(chart => {
            chart.update('active');
        });
    }

    updateProgressBars() {
        this.animateProgressBars();
    }

    startPerformanceUpdates() {
        // Auto-refresh data every 5 minutes
        setInterval(() => {
            this.refreshDashboardData();
        }, 300000);
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
        `;
        
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    // Utility methods
    formatNumber(num) {
        return new Intl.NumberFormat().format(num);
    }

    formatPercentage(num) {
        return `${Math.round(num)}%`;
    }

    formatDate(date) {
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }
}

// Teacher Dashboard specific functionality
class TeacherDashboard extends Dashboard {
    constructor() {
        super();
        this.initializeTeacherFeatures();
    }

    initializeTeacherFeatures() {
        this.initializeStudentModals();
        this.initializeAlerts();
        this.initializeClassManagement();
    }

    initializeStudentModals() {
        const studentLinks = document.querySelectorAll('[data-student-id]');
        
        studentLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const studentId = link.getAttribute('data-student-id');
                this.loadStudentDetails(studentId);
            });
        });
    }

    loadStudentDetails(studentId) {
        const modal = document.getElementById('studentDetailsModal');
        const content = document.getElementById('studentDetailsContent');
        
        content.innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin fa-2x"></i></div>';
        
        fetch(`/api/performance/${studentId}`)
            .then(response => response.json())
            .then(data => {
                this.renderStudentDetails(data, content);
            })
            .catch(error => {
                console.error('Error loading student data:', error);
                content.innerHTML = '<div class="alert alert-danger">Error loading student data</div>';
            });
        
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
    }

    renderStudentDetails(data, container) {
        const html = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Recent Performance</h6>
                    <canvas id="studentPerformanceChart" width="400" height="200"></canvas>
                </div>
                <div class="col-md-6">
                    <h6>Subject Breakdown</h6>
                    ${Object.entries(data.subject_proficiency).map(([subject, score]) => `
                        <div class="mb-3">
                            <div class="d-flex justify-content-between">
                                <span>${subject}</span>
                                <span class="badge bg-${score >= 80 ? 'success' : score >= 60 ? 'warning' : 'danger'}">
                                    ${score.toFixed(1)}%
                                </span>
                            </div>
                            <div class="progress mt-1">
                                <div class="progress-bar bg-${score >= 80 ? 'success' : score >= 60 ? 'warning' : 'danger'}" 
                                     style="width: ${score}%"></div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        container.innerHTML = html;
        
        // Create student performance chart
        const ctx = document.getElementById('studentPerformanceChart');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.recent_quizzes.map(q => this.formatDate(q.date)),
                datasets: [{
                    label: 'Quiz Scores',
                    data: data.recent_quizzes.map(q => q.score),
                    borderColor: '#4f46e5',
                    backgroundColor: 'rgba(79, 70, 229, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    initializeAlerts() {
        const alertItems = document.querySelectorAll('.alert[data-student-id]');
        
        alertItems.forEach(alert => {
            alert.addEventListener('click', () => {
                const studentId = alert.getAttribute('data-student-id');
                this.loadStudentDetails(studentId);
            });
        });
    }

    initializeClassManagement() {
        const classActions = document.querySelectorAll('[data-class-action]');
        
        classActions.forEach(action => {
            action.addEventListener('click', (e) => {
                e.preventDefault();
                const actionType = action.getAttribute('data-class-action');
                this.handleClassAction(actionType);
            });
        });
    }

    handleClassAction(actionType) {
        switch (actionType) {
            case 'export-data':
                this.exportClassData();
                break;
            case 'send-feedback':
                this.openFeedbackModal();
                break;
            case 'generate-report':
                this.generateClassReport();
                break;
        }
    }

    exportClassData() {
        this.showNotification('Exporting class data...', 'info');
        // Implementation for data export
    }

    openFeedbackModal() {
        // Implementation for feedback modal
    }

    generateClassReport() {
        this.showNotification('Generating class report...', 'info');
        // Implementation for report generation
    }
}

// Initialize dashboard based on user role
document.addEventListener('DOMContentLoaded', function() {
    const isTeacher = document.body.classList.contains('teacher-dashboard');
    
    if (isTeacher) {
        window.dashboard = new TeacherDashboard();
    } else {
        window.dashboard = new Dashboard();
    }
});

// Export for use in other scripts
window.Dashboard = Dashboard;
window.TeacherDashboard = TeacherDashboard;
