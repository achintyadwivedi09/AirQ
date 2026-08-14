/**
 * Client-side Hash Router — handles #/path navigation.
 * Each route maps to a page renderer function.
 */
const Router = (() => {
    const routes = {
        '/dashboard': () => Pages.dashboard(getContainer()),
        '/live':      () => Pages.live(getContainer()),
        '/cities':    () => Pages.cities(getContainer()),
        '/city':      (params) => Pages.cityDetail(getContainer(), params.id),
        '/history':   () => Pages.history(getContainer()),
        '/forecast':  () => Pages.forecast(getContainer()),
        '/alerts':    () => Pages.alerts(getContainer()),
        '/sensors':   () => Pages.sensors(getContainer()),
        '/about':     () => Pages.about(getContainer()),
    };

    function getContainer() {
        return document.getElementById('page-container');
    }

    function navigate(path) {
        window.location.hash = path;
    }

    function reload() {
        handleRoute();
    }

    function handleRoute() {
        const hash = window.location.hash.slice(1) || '/dashboard';
        const parts = hash.split('/').filter(Boolean);

        // Update active nav link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            const page = link.dataset.page;
            if (page === parts[0] || (parts[0] === 'city' && page === 'cities')) {
                link.classList.add('active');
            }
        });

        // Close mobile sidebar
        document.getElementById('sidebar')?.classList.remove('open');
        document.querySelector('.sidebar-overlay')?.classList.remove('active');

        // Scroll to top
        window.scrollTo(0, 0);

        // Route matching
        const path = '/' + parts[0];

        if (path === '/city' && parts[1]) {
            routes['/city']({ id: parts[1] });
        } else if (routes[path]) {
            routes[path]();
        } else {
            // Default to dashboard
            routes['/dashboard']();
        }
    }

    function init() {
        window.addEventListener('hashchange', handleRoute);
        // Set default route if none
        if (!window.location.hash) {
            window.location.hash = '#/dashboard';
        } else {
            handleRoute();
        }
    }

    return { init, navigate, reload, handleRoute };
})();
