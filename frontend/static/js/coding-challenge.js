let problems = [];
let currentProblem = null;
let userStats = null;

// Load problems on page load
async function loadProblems() {
    try {
        const response = await fetchWithAuth('/api/problems');
        problems = await response.json();
        displayProblems();
    } catch (error) {
        console.error('Error loading problems:', error);
    }
}

function displayProblems() {
    const listDiv = document.getElementById('problemsList');
    listDiv.innerHTML = problems.map(problem => `
        <div class="problem-item" onclick="selectProblem(${problem.id})" id="problem-${problem.id}">
            <strong>${problem.title}</strong>
            <span class="difficulty ${problem.difficulty.toLowerCase()}">${problem.difficulty}</span>
            <p style="color: #6b7280; margin-top: 5px; font-size: 14px;">${problem.description.substring(0, 80)}...</p>
        </div>
    `).join('');
}

function selectProblem(id) {
    currentProblem = problems.find(p => p.id === id);
    
    // Update UI
    document.querySelectorAll('.problem-item').forEach(item => {
        item.classList.remove('active');
    });
    document.getElementById(`problem-${id}`).classList.add('active');
    
    // Show problem detail
    document.getElementById('noProblemSelected').style.display = 'none';
    document.getElementById('problemDetail').style.display = 'block';
    
    document.getElementById('problemTitle').textContent = currentProblem.title;
    document.getElementById('problemDifficulty').textContent = currentProblem.difficulty;
    document.getElementById('problemDifficulty').className = `difficulty ${currentProblem.difficulty.toLowerCase()}`;
    document.getElementById('problemDescription').textContent = currentProblem.description;
    
    // Set language
    document.getElementById('languageSelect').value = currentProblem.language.toLowerCase();
    
    // Clear previous results
    document.getElementById('codeEditor').value = '';
    document.getElementById('testResults').innerHTML = '';
}

async function runCode() {
    if (!currentProblem) {
        alert('Please select a problem first');
        return;
    }

    const code = document.getElementById('codeEditor').value;
    const language = document.getElementById('languageSelect').value;

    if (!code.trim()) {
        alert('Please write some code first');
        return;
    }

    const resultsDiv = document.getElementById('testResults');
    resultsDiv.innerHTML = '<p style="text-align: center; color: var(--primary);">Running tests...</p>';

    try {
        const response = await fetchWithAuth('/api/execute-code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                code: code,
                language: language,
                problem_id: currentProblem.id
            })
        });

        const data = await response.json();
        displayResults(data);
        
        // Reload stats
        loadStats();
    } catch (error) {
        resultsDiv.innerHTML = `<p style="color: var(--danger);">Error: ${error.message}</p>`;
    }
}

function displayResults(data) {
    const resultsDiv = document.getElementById('testResults');
    
    const allPassed = data.all_passed;
    const statusColor = allPassed ? 'var(--success)' : 'var(--danger)';
    const statusText = allPassed ? '✅ All tests passed!' : '❌ Some tests failed';
    
    let html = `<h3 style="color: ${statusColor}; margin-bottom: 15px;">${statusText}</h3>`;
    
    data.results.forEach((result, index) => {
        const testClass = result.passed ? 'passed' : 'failed';
        const icon = result.passed ? '✅' : '❌';
        
        html += `
            <div class="test-case ${testClass}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <strong>Test Case ${index + 1}</strong>
                    <span>${icon}</span>
                </div>
                <p><strong>Input:</strong> ${result.input}</p>
                <p><strong>Expected:</strong> ${result.expected}</p>
                <p><strong>Your Output:</strong> ${result.actual || 'No output'}</p>
                ${result.error ? `<p style="color: var(--danger);"><strong>Error:</strong> ${result.error}</p>` : ''}
            </div>
        `;
    });
    
    resultsDiv.innerHTML = html;
}

// Load user stats
async function loadStats() {
    try {
        const response = await fetchWithAuth('/api/user-stats');
        userStats = await response.json();
        displayCharts();
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function displayCharts() {
    if (!userStats) return;

    // Problems solved chart (Pie)
    const ctx1 = document.getElementById('problemsChart');
    if (ctx1) {
        new Chart(ctx1, {
            type: 'pie',
            data: {
                labels: ['Passed', 'Failed'],
                datasets: [{
                    data: [userStats.passed, userStats.failed],
                    backgroundColor: ['#10b981', '#ef4444'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: {
                                size: 14
                            }
                        }
                    },
                    title: {
                        display: true,
                        text: 'Problems Solved',
                        font: {
                            size: 18
                        }
                    }
                }
            }
        });
    }

    // Difficulty distribution chart (Doughnut)
    const ctx2 = document.getElementById('difficultyChart');
    if (ctx2) {
        const difficultyData = userStats.difficulty_stats;
        new Chart(ctx2, {
            type: 'doughnut',
            data: {
                labels: ['Easy', 'Medium', 'Hard'],
                datasets: [{
                    data: [
                        difficultyData.Easy || 0,
                        difficultyData.Medium || 0,
                        difficultyData.Hard || 0
                    ],
                    backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: {
                                size: 14
                            }
                        }
                    },
                    title: {
                        display: true,
                        text: 'Problems by Difficulty',
                        font: {
                            size: 18
                        }
                    }
                }
            }
        });
    }
}

// Initialize
loadProblems();
loadStats();