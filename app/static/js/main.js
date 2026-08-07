// ========================
// Main JavaScript — Employee System
// ========================

document.addEventListener('DOMContentLoaded', function () {
    initSidebar();
    initAlertDismiss();
    initCounterAnimations();
    initTooltips();
    setActiveNav();
});

// ========================
// Sidebar Toggle (Mobile)
// ========================
function initSidebar() {
    const toggleBtn = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            if (overlay) overlay.classList.toggle('active');
        });
    }
    if (overlay) {
        overlay.addEventListener('click', () => {
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
        });
    }
}

// ========================
// Auto-Dismiss Alerts
// ========================
function initAlertDismiss() {
    document.querySelectorAll('.alert[data-dismiss]').forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            alert.style.transition = 'all 0.4s ease';
            setTimeout(() => alert.remove(), 400);
        }, 4000);
    });

    document.querySelectorAll('.alert .alert-close').forEach(btn => {
        btn.addEventListener('click', () => {
            const alert = btn.closest('.alert');
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        });
    });
}

// ========================
// Counter Animations
// ========================
function initCounterAnimations() {
    const counters = document.querySelectorAll('[data-counter]');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    });
    counters.forEach(el => observer.observe(el));
}

function animateCounter(el) {
    const target = parseFloat(el.dataset.counter);
    const duration = 1200;
    const start = performance.now();
    const isDecimal = target % 1 !== 0;

    function update(now) {
        const elapsed = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - elapsed, 3);
        const value = target * eased;
        el.textContent = isDecimal ? value.toFixed(1) : Math.round(value).toLocaleString('en-IN');
        if (elapsed < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}

// ========================
// Active Nav Item
// ========================
function setActiveNav() {
    const path = window.location.pathname;
    document.querySelectorAll('.sidebar-nav .nav-link').forEach(link => {
        const href = link.getAttribute('href');
        if (href && path.startsWith(href) && href !== '/') {
            link.classList.add('active');
        }
    });
}

// ========================
// Tooltips (Simple)
// ========================
function initTooltips() {
    document.querySelectorAll('[title]').forEach(el => {
        el.addEventListener('mouseenter', showTooltip);
        el.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const text = e.currentTarget.getAttribute('title');
    if (!text) return;
    e.currentTarget.setAttribute('data-title', text);
    e.currentTarget.removeAttribute('title');
    const tooltip = document.createElement('div');
    tooltip.className = 'custom-tooltip';
    tooltip.textContent = text;
    tooltip.style.cssText = `
        position: fixed; background: #1a237e; color: white;
        padding: 6px 12px; border-radius: 6px; font-size: 12px;
        pointer-events: none; z-index: 9999; white-space: nowrap;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    `;
    document.body.appendChild(tooltip);
    const rect = e.currentTarget.getBoundingClientRect();
    tooltip.style.top = `${rect.top - tooltip.offsetHeight - 8}px`;
    tooltip.style.left = `${rect.left + rect.width / 2 - tooltip.offsetWidth / 2}px`;
    e.currentTarget._tooltip = tooltip;
}

function hideTooltip(e) {
    const title = e.currentTarget.getAttribute('data-title');
    if (title) e.currentTarget.setAttribute('title', title);
    if (e.currentTarget._tooltip) {
        e.currentTarget._tooltip.remove();
        delete e.currentTarget._tooltip;
    }
}

// ========================
// Confirm Dialogs
// ========================
function confirmAction(message, formId) {
    if (confirm(message)) {
        document.getElementById(formId).submit();
    }
    return false;
}

// ========================
// Format Currency (INR)
// ========================
function formatINR(amount) {
    return '₹ ' + parseFloat(amount).toLocaleString('en-IN', {
        minimumFractionDigits: 2, maximumFractionDigits: 2
    });
}

// ========================
// Date Range Picker Helper
// ========================
function calculateLeaveDays(fromId, toId, resultId) {
    const from = document.getElementById(fromId);
    const to = document.getElementById(toId);
    const result = document.getElementById(resultId);
    if (!from || !to || !result) return;

    function update() {
        if (!from.value || !to.value) { result.textContent = '—'; return; }
        const fromDate = new Date(from.value);
        const toDate = new Date(to.value);
        if (toDate < fromDate) { result.textContent = 'Invalid range'; return; }
        let days = 0;
        let cur = new Date(fromDate);
        while (cur <= toDate) {
            if (cur.getDay() !== 0 && cur.getDay() !== 6) days++;
            cur.setDate(cur.getDate() + 1);
        }
        result.textContent = days + (days === 1 ? ' day' : ' days');
    }
    from.addEventListener('change', update);
    to.addEventListener('change', update);
}
