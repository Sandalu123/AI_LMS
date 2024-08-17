const app = {
    init: () => {
        app.router();
        window.addEventListener('hashchange', app.router);
    },

    router: async () => {
        const hash = window.location.hash.slice(1) || '/';
        let pageContent = '';
        let params = {};

        if (hash.startsWith('/course/')) {
            params.id = hash.split('/')[2];
        } else if (hash.startsWith('/assignment/')) {
            params.id = hash.split('/')[2];
        }

        switch(true) {
            case hash === '/':
                pageContent = await LoginComponent.render();
                break;
            case hash === '/dashboard':
                pageContent = await DashboardComponent.render();
                break;
            case hash.startsWith('/course/'):
                pageContent = await CourseComponent.render(params.id);
                break;
            case hash.startsWith('/assignment/'):
                pageContent = await AssignmentComponent.render(params.id);
                break;
            default:
                pageContent = `
                    <div class="ui container">
                        <div class="ui middle aligned center aligned grid" style="height: 100vh;">
                            <div class="column">
                                <h1 class="ui header">
                                    <i class="exclamation triangle icon"></i>
                                    404 - Page Not Found
                                </h1>
                                <p>The page you're looking for doesn't exist.</p>
                                <a class="ui button" href="#/">
                                    <i class="home icon"></i> Go to Login
                                </a>
                            </div>
                        </div>
                    </div>
                `;
        }

        document.querySelector('#app').innerHTML = pageContent;

        // Call afterRender method if it exists
        if (hash === '/' && LoginComponent.afterRender) {
            LoginComponent.afterRender();
        } else if (hash === '/dashboard' && DashboardComponent.afterRender) {
            DashboardComponent.afterRender();
        } else if (hash.startsWith('/course/') && CourseComponent.afterRender) {
            CourseComponent.afterRender(params.id);
        } else if (hash.startsWith('/assignment/') && AssignmentComponent.afterRender) {
            AssignmentComponent.afterRender(params.id);
        }
    },

    showLoading: () => {
        document.getElementById('loadingScreen').classList.remove('hidden');
    },

    hideLoading: () => {
        document.getElementById('loadingScreen').classList.add('hidden');
    }
};

document.addEventListener('DOMContentLoaded', app.init);