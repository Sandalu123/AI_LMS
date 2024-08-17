const DashboardComponent = {
    render: async () => {
        app.showLoading();
        let courses;
        try {
            courses = await api.getCourses();
        } catch (error) {
            console.error('Error fetching courses:', error);
            courses = [];
        }
        app.hideLoading();

        return `
            <div class="ui container">
                <div class="ui teal inverted segment">
                    <h2 class="ui header">
                        <i class="smile outline icon"></i>
                        <div class="content">
                            Your Mood Today: <span id="detectedMood">Analyzing...</span>
                            <div class="sub header" id="moodConfidence"></div>
                        </div>
                    </h2>
                    <button class="ui right floated button" id="cheerUpButton">Cheer Up!</button>
                    <div id="webcamPreviewContainer" style="position: absolute; top: 10px; right: 200px; width: 160px; height: 120px; overflow: hidden;">
                        <video id="webcamPreview" style="width: 100%; height: 100%; object-fit: cover; transform: scaleX(-1);" autoplay muted></video>
                    </div>
                </div>
                <div class="ui stackable grid">
                    <div class="sixteen wide column">
                        <h1 class="ui header">Dashboard</h1>
                        <div class="ui divider"></div>
                    </div>
                    <div class="twelve wide column">
                        <h2 class="ui header">My Courses</h2>
                        <div class="ui three stackable cards">
                            ${courses.map(course => `
                                <div class="ui card">
                                    <div class="content">
                                        <div class="header">${course.name}</div>
                                        <div class="meta">Instructor ID: ${course.instructor_id}</div>
                                    </div>
                                    <div class="extra content">
                                        <a class="ui button" href="#/course/${course.id}">View Course</a>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    <div class="four wide column">
                        <div class="ui segment">
                            <h3 class="ui header">Quick Links</h3>
                            <div class="ui vertical fluid menu">
                                <a class="item" id="createCourseLink">
                                    <i class="plus icon"></i> Create New Course
                                </a>
                                <a class="item" id="viewAssignmentsLink">
                                    <i class="tasks icon"></i> View All Assignments
                                </a>
                                <a class="item" id="logoutLink">
                                    <i class="sign out icon"></i> Logout
                                </a>
                            </div>
                        </div>
                        <div class="ui segment">
                            <h3 class="ui header">News Feed</h3>
                            <div class="ui relaxed divided list">
                                <div class="item">
                                    <i class="large newspaper middle aligned icon"></i>
                                    <div class="content">
                                        <a class="header">New Course Added: Advanced AI</a>
                                        <div class="description">Enroll now for the upcoming semester!</div>
                                    </div>
                                </div>
                                <div class="item">
                                    <i class="large announcement middle aligned icon"></i>
                                    <div class="content">
                                        <a class="header">Campus Event: Tech Fair</a>
                                        <div class="description">Join us next week for exciting tech demos!</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="ui segment">
                            <h3 class="ui header">Academic Calendar</h3>
                            <div class="ui list">
                                <div class="item">
                                    <i class="calendar icon"></i>
                                    <div class="content">
                                        <div class="header">Mid-term Exams</div>
                                        <div class="description">October 15-20, 2023</div>
                                    </div>
                                </div>
                                <div class="item">
                                    <i class="calendar icon"></i>
                                    <div class="content">
                                        <div class="header">Winter Break</div>
                                        <div class="description">December 20, 2023 - January 5, 2024</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- New Course Modal -->
            <div class="ui modal" id="newCourseModal">
                <i class="close icon"></i>
                <div class="header">Create New Course</div>
                <div class="content">
                    <form class="ui form">
                        <div class="field">
                            <label>Course Name</label>
                            <input type="text" name="courseName" placeholder="Enter course name">
                        </div>
                    </form>
                </div>
                <div class="actions">
                    <div class="ui approve button">Create</div>
                    <div class="ui cancel button">Cancel</div>
                </div>
            </div>

            <!-- Cheer Up Modal -->
            <div class="ui modal" id="cheerUpModal">
                <i class="close icon"></i>
                <div class="header">Cheer Up!</div>
                <div class="content">
                    <p>Here's a little motivation to brighten your day! 🌟🎉</p>
                    <p>Remember, every small step counts towards your big goals. Keep pushing forward! 💪😊</p>
                </div>
                <div class="actions">
                    <div class="ui positive button">Thanks!</div>
                </div>
            </div>

            <!-- All Assignments Modal -->
            <div class="ui modal" id="allAssignmentsModal">
                <i class="close icon"></i>
                <div class="header">All Assignments</div>
                <div class="content">
                    <div class="ui relaxed divided list" id="allAssignmentsList"></div>
                </div>
                <div class="actions">
                    <div class="ui cancel button">Close</div>
                </div>
            </div>

            <!-- Footer -->
            <div class="ui inverted vertical footer segment">
                <div class="ui container">
                    <div class="ui stackable inverted divided equal height stackable grid">
                        <div class="three wide column">
                            <h4 class="ui inverted header">About</h4>
                            <div class="ui inverted link list">
                                <a href="#" class="item">Contact Us</a>
                                <a href="#" class="item">Our Mission</a>
                                <a href="#" class="item">Privacy Policy</a>
                            </div>
                        </div>
                        <div class="three wide column">
                            <h4 class="ui inverted header">Services</h4>
                            <div class="ui inverted link list">
                                <a href="#" class="item">Online Courses</a>
                                <a href="#" class="item">Career Support</a>
                                <a href="#" class="item">Student Resources</a>
                            </div>
                        </div>
                        <div class="seven wide column">
                            <h4 class="ui inverted header">LMS - Learning Management System</h4>
                            <p>Empowering learners worldwide with cutting-edge educational technology and personalized learning experiences.</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    afterRender: async () => {

        await faceapi.nets.tinyFaceDetector.loadFromUri('/models');
        await faceapi.nets.faceExpressionNet.loadFromUri('/models');
        
        $('#createCourseLink').click(() => {
            $('#newCourseModal').modal('show');
        });

        $('#cheerUpButton').click(() => {
            $('#cheerUpModal').modal('show');
        });

        $('#viewAssignmentsLink').click(async () => {
            const assignments = await api.getAllAssignments();
            const assignmentList = assignments.map(assignment => `
                <div class="item">
                    <i class="large file middle aligned icon"></i>
                    <div class="content">
                        <a class="header" href="#/assignment/${assignment.id}">${assignment.title}</a>
                        <div class="description">Due: ${assignment.due_date}</div>
                    </div>
                </div>
            `).join('');
            $('#allAssignmentsList').html(assignmentList);
            $('#allAssignmentsModal').modal('show');
        });

        $('#logoutLink').click(() => {
            localStorage.removeItem('token');
            window.location.hash = '#/';
        });

        $('.ui.form').form({
            fields: {
                courseName: 'empty'
            },
            onSuccess: async (event, fields) => {
                event.preventDefault();
                try {
                    await api.createCourse(fields.courseName);
                    $('#newCourseModal').modal('hide');
                    app.router(); // Refresh the dashboard
                } catch (error) {
                    console.error('Error creating course:', error);
                }
            }
        });

        const startWebcam = async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                const video = document.getElementById('webcamPreview');
                video.srcObject = stream;

                // Start detecting faces and emotions
                video.addEventListener('play', () => {
                    setInterval(async () => {
                        const detections = await faceapi.detectSingleFace(video, new faceapi.TinyFaceDetectorOptions())
                            .withFaceExpressions();
                        if (detections) {
                            processDetections(detections);
                        }
                    }, 1000);
                });
            } catch (error) {
                console.error('Error accessing webcam:', error);
            }
        };

        const processDetections = (detections) => {
            const emotions = detections.expressions;
            const dominantEmotion = Object.keys(emotions).reduce((a, b) => emotions[a] > emotions[b] ? a : b);
            const confidence = emotions[dominantEmotion];

            updateMoodDisplay(dominantEmotion, confidence);

            // Log all emotions with confidence values
            console.log('Detected emotions:', emotions);
        };

        const updateMoodDisplay = (emotion, confidence) => {
            const moodElement = document.getElementById('detectedMood');
            const confidenceElement = document.getElementById('moodConfidence');

            moodElement.textContent = emotion;
            confidenceElement.textContent = `Confidence: ${(confidence * 100).toFixed(2)}%`;
        };

        // Start the webcam when the component is rendered
        startWebcam();
    }
};