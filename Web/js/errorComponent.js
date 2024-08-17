const ErrorComponent = {
    render: async () => {
        return `
            <div class="ui container">
                <div class="ui middle aligned center aligned grid" style="height: 100vh;">
                    <div class="column">
                        <h1 class="ui header">
                            <i class="exclamation triangle icon"></i>
                            404 - Page Not Found
                        </h1>
                        <p>The page you're looking for doesn't exist.</p>
                        <a class="ui button" href="#/dashboard">
                            <i class="home icon"></i> Go to Dashboard
                        </a>
                    </div>
                </div>
            </div>
        `;
    },

    afterRender: () => {
        // Any additional JavaScript for the error page
    }
};