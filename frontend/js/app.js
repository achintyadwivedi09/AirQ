/**
 * App Bootstrap — initializes sidebar, mobile nav, and router.
 */
(function() {
    'use strict';

    // Wait for DOM
    document.addEventListener('DOMContentLoaded', init);

    function init() {
        setupSidebar();
        setupOverlay();
        checkBackendHealth();
        Router.init();
    }

    // ── Sidebar / Mobile Nav ────────────────────
    function setupSidebar() {
        const hamburger = document.getElementById('hamburger');
        const sidebar = document.getElementById('sidebar');
        const closeBtn = document.getElementById('sidebar-close');

        if (hamburger) {
            hamburger.addEventListener('click', () => {
                sidebar.classList.add('open');
                getOverlay().classList.add('active');
            });
        }
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                sidebar.classList.remove('open');
                getOverlay().classList.remove('active');
            });
        }
    }

    function setupOverlay() {
        // Create overlay element if not exists
        let overlay = document.querySelector('.sidebar-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'sidebar-overlay';
            document.body.appendChild(overlay);
        }
        overlay.addEventListener('click', () => {
            document.getElementById('sidebar')?.classList.remove('open');
            overlay.classList.remove('active');
        });
    }

    function getOverlay() {
        return document.querySelector('.sidebar-overlay') || document.createElement('div');
    }

    // ── Backend Health Check ────────────────────
    async function checkBackendHealth() {
        const statusDot = document.querySelector('#data-status .status-dot');
        const statusText = document.querySelector('#data-status .status-text');
        const topbarBadge = document.getElementById('topbar-badge');

        try {
            await API.healthCheck();
            if (statusDot) { statusDot.className = 'status-dot online'; }
            if (statusText) { statusText.textContent = 'Backend Online'; }
            if (topbarBadge) { topbarBadge.innerHTML = '<span class="badge badge-real">● Online</span>'; }
        } catch {
            if (statusDot) { statusDot.className = 'status-dot offline'; }
            if (statusText) { statusText.textContent = 'Backend Offline'; }
            if (topbarBadge) { topbarBadge.innerHTML = '<span class="badge badge-fallback">○ Offline</span>'; }
        }
    }
})();
