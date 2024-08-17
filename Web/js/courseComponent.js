const CourseComponent = {
    render: async (courseId) => {
        app.showLoading();
        let course;
        let assignments;
        try {
            course = await api.getCourseDetails(courseId);
            assignments = await api.getCourseAssignments(courseId);
        } catch (error) {
            console.error('Error fetching course details:', error);
            course = { name: 'Unknown Course', instructor_id: 'Unknown' };
            assignments = [];
        }
        app.hideLoading();

        return `
            <div class="ui container">
                <div class="ui stackable grid">
                    <div class="sixteen wide column">
                        <h1 class="ui header">${course.name}</h1>
                        <div class="ui divider"></div>
                    </div>
                    <div class="twelve wide column">
                        <h2 class="ui header">Assignments</h2>
                        <div class="ui relaxed divided list">
                            ${assignments.map(assignment => `
                                <div class="item">
                                    <i class="large file middle aligned icon"></i>
                                    <div class="content">
                                        <a class="header" href="#/assignment/${assignment.id}">${assignment.title}</a>
                                        <div class="description">${assignment.description || 'No description available'}</div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    <div class="four wide column">
                        <div class="ui segment">
                            <h3 class="ui header">Course Information</h3>
                            <div class="ui list">
                                <div class="item">
                                    <i class="user icon"></i>
                                    <div class="content">
                                        Instructor ID: ${course.instructor_id}
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="ui two buttons" style="margin-bottom: 1em;">
                            <button class="ui primary button" id="aiTutorButton">
                                <i class="robot icon"></i> AI Tutor
                            </button>
                            <a class="ui button" href="#/dashboard">
                                <i class="arrow left icon"></i> Back
                            </a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- AI Tutor Modal -->
            <div class="ui modal" id="aiTutorModal">
                <i class="close icon"></i>
                <div class="header">AI Tutor</div>
                <div class="content">
                    <div class="ui top attached tabular menu">
                        <a class="item active" data-tab="content">AI Generated Content</a>
                        <a class="item" data-tab="chatbot">Chatbot</a>
                    </div>
                    <div class="ui bottom attached tab segment active" data-tab="content">
                        <div class="ui cards" id="aiGeneratedContent"></div>
                    </div>
                    <div class="ui bottom attached tab segment" data-tab="chatbot">
                        <div class="ui comments" id="chatMessages" style="max-height: 300px; overflow-y: auto;"></div>
                        <form class="ui reply form">
                            <div class="field">
                                <div class="ui fluid action input">
                                    <input type="text" id="chatInput" placeholder="Ask a question...">
                                    <button class="ui primary labeled icon button" type="submit">
                                        <i class="icon edit"></i> Send
                                    </button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        `;
    },

    afterRender: (courseId) => {
        $('#aiTutorButton').click(async () => {
            const content = await api.getAIGeneratedContent(courseId);
            const contentHtml = content.map(item => `
                <div class="card">
                    <div class="content">
                        <div class="header">${item.title}</div>
                        <div class="description">${item.description}</div>
                    </div>
                </div>
            `).join('');
            $('#aiGeneratedContent').html(contentHtml);
            
            $('.menu .item').tab();
            $('#aiTutorModal').modal('show');
        });

        $('.ui.reply.form').submit(async (event) => {
            event.preventDefault();
            const message = $('#chatInput').val();
            if (message.trim()) {
                const response = await api.getChatbotResponse(courseId, message);
                $('#chatMessages').append(`
                    <div class="comment">
                        <div class="content">
                            <a class="author">You</a>
                            <div class="metadata">
                                <span class="date">Just now</span>
                            </div>
                            <div class="text">${message}</div>
                        </div>
                    </div>
                    <div class="comment">
                        <div class="avatar">
                            <i class="robot icon"></i>
                        </div>
                        <div class="content">
                            <a class="author">AI Tutor</a>
                            <div class="metadata">
                                <span class="date">Just now</span>
                            </div>
                            <div class="text">${response}</div>
                        </div>
                    </div>
                `);
                $('#chatInput').val('');
                const chatMessages = document.getElementById('chatMessages');
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        });
    }
};