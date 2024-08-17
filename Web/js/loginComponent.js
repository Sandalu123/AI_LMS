const LoginComponent = {
    render: async () => {
        return `
            <div class="ui middle aligned center aligned grid" style="height: 100vh;">
                <div class="column" style="max-width: 450px;">
                    <h2 class="ui teal image header">
                        <img src="https://semantic-ui.com/examples/assets/images/logo.png" class="image">
                        <div class="content">
                            Log-in to your account
                        </div>
                    </h2>
                    <form class="ui large form">
                        <div class="ui stacked segment">
                            <div class="field">
                                <div class="ui left icon input">
                                    <i class="user icon"></i>
                                    <input type="text" name="username" placeholder="Username">
                                </div>
                            </div>
                            <div class="field">
                                <div class="ui left icon input">
                                    <i class="lock icon"></i>
                                    <input type="password" name="password" placeholder="Password">
                                </div>
                            </div>
                            <div class="ui fluid large teal submit button">Login</div>
                        </div>
                        <div class="ui error message"></div>
                    </form>
                    <div class="ui message">
                        New to us? <a href="#">Sign Up</a>
                    </div>
                </div>
            </div>
        `;
    },

    afterRender: () => {
        $('.ui.form').form({
            fields: {
                username: 'empty',
                password: 'empty'
            },
            onSuccess: async (event, fields) => {
                event.preventDefault();
                app.showLoading();
                try {
                    const response = await api.login(fields.username, fields.password);
                    if (response.access_token) {
                        localStorage.setItem('token', response.access_token);
                        window.location.hash = '#/dashboard';
                    } else {
                        $('.ui.form').form('add errors', ['Invalid username or password']);
                    }
                } catch (error) {
                    console.error('Login error:', error);
                    $('.ui.form').form('add errors', ['An error occurred. Please try again.']);
                }
                app.hideLoading();
            }
        });
    }
};