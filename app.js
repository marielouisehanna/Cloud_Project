const API_URL = 'https://nz7k6ytbsk.execute-api.us-east-1.amazonaws.com/prod';
let currentSessionId = null;

// Snow effect
function initSnowEffect() {
    const canvas = document.getElementById('snowCanvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    const snowflakes = [];
    const snowflakeCount = 150;
    
    class Snowflake {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.radius = Math.random() * 3 + 1;
            this.speed = Math.random() * 1 + 0.5;
            this.wind = Math.random() * 0.5 - 0.25;
            this.opacity = Math.random() * 0.6 + 0.4;
        }
        
        update() {
            this.y += this.speed;
            this.x += this.wind;
            
            if (this.y > canvas.height) {
                this.y = 0;
                this.x = Math.random() * canvas.width;
            }
            
            if (this.x > canvas.width) {
                this.x = 0;
            } else if (this.x < 0) {
                this.x = canvas.width;
            }
        }
        
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255, 255, 255, ${this.opacity})`;
            ctx.fill();
        }
    }
    
    for (let i = 0; i < snowflakeCount; i++) {
        snowflakes.push(new Snowflake());
    }
    
    function animateSnow() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        snowflakes.forEach(snowflake => {
            snowflake.update();
            snowflake.draw();
        });
        
        requestAnimationFrame(animateSnow);
    }
    
    animateSnow();
    
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
}

function addParticipant() {
    const form = document.getElementById('participantForm');
    const row = document.createElement('div');
    row.className = 'participant-row';
    row.innerHTML = `
        <div class="form-group">
            <label class="form-label">Name</label>
            <input type="text" placeholder="Enter name" class="name-input">
        </div>
        <div class="form-group">
            <label class="form-label">Email</label>
            <input type="email" placeholder="Enter email address" class="email-input">
        </div>
        <button class="btn-remove" onclick="this.closest('.participant-row').remove()">Remove</button>
    `;
    form.appendChild(row);
}

async function generateMatches() {
    const rows = document.querySelectorAll('.participant-row');
    const participants = [];
    
    rows.forEach(row => {
        const name = row.querySelector('.name-input').value.trim();
        const email = row.querySelector('.email-input').value.trim();
        
        if (name && email) {
            participants.push({ name, email });
        }
    });
    
    if (participants.length < 3) {
        showError('Please add at least 3 participants to generate matches');
        return;
    }

    const budgetRadio = document.querySelector('input[name="budget"]:checked');
    const budget = budgetRadio ? budgetRadio.value : '$20-$30';
    const isOrganizer = document.getElementById('organizerCheck').checked;
    
    document.getElementById('loading').style.display = 'block';
    document.getElementById('error').style.display = 'none';
    document.getElementById('results').style.display = 'none';
    
    try {
        const response = await fetch(`${API_URL}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                participants,
                budget,
                is_organizer: isOrganizer
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to generate matches');
        }
        
        currentSessionId = data.session_id;
        
        document.getElementById('loading').style.display = 'none';
        document.getElementById('results').style.display = 'block';
        
        let resultsHTML = `<strong>Session ID:</strong> ${data.session_id}<br><br>`;
        resultsHTML += `<strong>Budget Range:</strong> ${budget}<br><br>`;
        resultsHTML += `Your Secret Santa matches have been generated successfully!<br><br>`;
        resultsHTML += `<strong>Happy Holidays! 🎄🎁</strong>`;
        
        document.getElementById('resultsText').innerHTML = resultsHTML;
        
        if (data.email_status && data.email_status.length > 0) {
            displayEmailStatus(data.email_status);
        }
        
        if (isOrganizer) {
            document.getElementById('downloadSection').style.display = 'block';
        }
        
    } catch (error) {
        document.getElementById('loading').style.display = 'none';
        showError('Oops! Something went wrong. Please try again.');
        console.error('Error:', error);
    }
}

function displayEmailStatus(emailStatus) {
    const statusDiv = document.getElementById('emailStatus');
    const listDiv = document.getElementById('emailStatusList');
    
    let sent = 0;
    let failed = 0;
    
    let html = '';
    
    emailStatus.forEach(status => {
        const icon = status.status === 'sent' ? '✅' : '❌';
        const statusClass = status.status === 'sent' ? 'status-sent' : 'status-failed';
        
        if (status.status === 'sent') sent++;
        else failed++;
        
        html += `
            <div class="status-item">
                <span>${icon}</span>
                <span>${status.email}</span>
                <span class="${statusClass}">${status.status.toUpperCase()}</span>
            </div>
        `;
    });
    
    const summary = `<p style="margin-bottom: 15px;"><strong>${sent}/${emailStatus.length} emails sent successfully</strong>${failed > 0 ? `, ${failed} failed` : ''}</p>`;
    
    listDiv.innerHTML = summary + html;
    statusDiv.style.display = 'block';
}

async function downloadCSV() {
    if (!currentSessionId) {
        showError('No session ID found. Please generate matches first.');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/get-matches?session_id=${currentSessionId}`);
        
        if (!response.ok) {
            throw new Error('Failed to retrieve matches');
        }
        
        const data = await response.json();
        
        let csv = 'Giver Name,Giver Email,Receiver Name,Receiver Email,Budget\n';
        
        data.matches.forEach(match => {
            csv += `"${match.giver.name}","${match.giver.email}","${match.receiver.name}","${match.receiver.email}","${data.budget}"\n`;
        });
        
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `secret-santa-matches-${currentSessionId}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
    } catch (error) {
        showError('Failed to download matches. Please try again.');
        console.error('Error:', error);
    }
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initSnowEffect();
});