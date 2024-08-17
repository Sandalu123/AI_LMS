const API_BASE_URL = 'http://localhost:5000';

const api = {
    login: async (username, password) => {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
            credentials: 'include'
        });
        return await response.json();
    },

    getCourses: async () => {
        const response = await fetch(`${API_BASE_URL}/courses`, {
            headers: { 
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });
        return await response.json();
    },

    createCourse: async (name, instructorId) => {
        const response = await fetch(`${API_BASE_URL}/courses`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ name, instructor_id: instructorId })
        });
        return await response.json();
    },

    // New methods
    getCourseDetails: async (courseId) => {
        const response = await fetch(`${API_BASE_URL}/courses/${courseId}`, {
            headers: { 
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });
        return await response.json();
    },

    getCourseAssignments: async (courseId) => {
        const response = await fetch(`${API_BASE_URL}/courses/${courseId}/assignments`, {
            headers: { 
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });
        return await response.json();
    },

    getAssignmentDetails: async (assignmentId) => {
        const response = await fetch(`${API_BASE_URL}/assignments/${assignmentId}`, {
            headers: { 
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });
        return await response.json();
    },

    submitAssignment: async (assignmentId, submission) => {
        const response = await fetch(`${API_BASE_URL}/submissions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            credentials: 'include',
            body: JSON.stringify({ assignment_id: assignmentId, content: submission })
        });
        return await response.json();
    },
    getAllAssignments: async () => {
        // For now, return dummy data
        return [
            { id: 1, title: 'Math Assignment 1', due_date: '2023-06-15' },
            { id: 2, title: 'Physics Lab Report', due_date: '2023-06-20' },
            { id: 3, title: 'English Essay', due_date: '2023-06-25' },
        ];
    },

    getAIGeneratedContent: async (courseId) => {
        // For now, return dummy data
        return [
            { title: 'Introduction to the Course', description: 'This course covers the fundamental principles of...' },
            { title: 'Key Concepts', description: 'The main concepts you will learn in this course include...' },
            { title: 'Study Tips', description: 'To succeed in this course, make sure to...' },
        ];
    },

    getChatbotResponse: async (courseId, message) => {
        // For now, return a dummy response
        return `Thank you for your question about the course. Here's a response: ${message}`;
    },

    uploadDocument: async (courseId, formData) => {
        console.log(formData.get('file'))
        const response = await fetch(`${API_BASE_URL}/api/upload_document/${courseId}`, {
            method: 'POST',
            credentials: 'include',
            body: formData
        });
        return response.json();
    },

    listDocuments: async (courseId) => {
        const response = await fetch(`${API_BASE_URL}/api/list_documents/${courseId}`);
        const data = await response.json();
        return data.documents;
    },

    downloadDocument: async (courseId, filename) => {
        window.location.href = `${API_BASE_URL}/api/download_document/${courseId}/${filename}`;
    }
};