const AssignmentComponent = {
    render: async (assignmentId) => {
        app.showLoading();
        let assignment;
        try {
            assignment = await api.getAssignmentDetails(assignmentId);
        } catch (error) {
            console.error('Error fetching assignment details:', error);
            assignment = { title: 'Unknown Assignment', description: 'No description available', due_date: 'Unknown' };
        }
        app.hideLoading();

        return `
            <div class="ui container">
                <div class="ui stackable grid">
                    <div class="sixteen wide column">
                        <h1 class="ui header">${assignment.title}</h1>
                        <div class="ui divider"></div>
                    </div>
                    <div class="twelve wide column">
                        <div class="ui segment">
                            <h3 class="ui header">Description</h3>
                            <p>${assignment.description}</p>
                        </div>
                        <form class="ui form">
                            <div class="field">
                                <label>Your Submission</label>
                                <textarea rows="4" name="submission"></textarea>
                            </div>
                            <button class="ui primary button" type="submit">Submit Assignment</button>
                        </form>
                    </div>
                    <div class="four wide column">
                        <div class="ui segment">
                            <h3 class="ui header">Assignment Information</h3>
                            <div class="ui list">
                                <div class="item">
                                    <i class="calendar icon"></i>
                                    <div class="content">
                                        Due Date: ${assignment.due_date}
                                    </div>
                                </div>
                            </div>
                        </div>
                        <a class="ui button" href="#/course/${assignment.course_id}">
                            <i class="arrow left icon"></i> Back to Course
                        </a>
                    </div>
                </div>
            </div>
        `;
    },

    afterRender: (assignmentId) => {
        document.querySelector('.ui.form').addEventListener('submit', async (event) => {
            event.preventDefault();
            app.showLoading();
            const submission = document.querySelector('textarea[name="submission"]').value;
            try {
                await api.submitAssignment(assignmentId, submission);
                alert('Assignment submitted successfully!');
                window.location.hash = `#/course/${assignment.course_id}`;
            } catch (error) {
                console.error('Submission error:', error);
                alert('Error submitting assignment. Please try again.');
            }
            app.hideLoading();
        });
    }
};