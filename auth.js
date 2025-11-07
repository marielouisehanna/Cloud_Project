// Cognito Configuration - UPDATE THESE VALUES AFTER TERRAFORM APPLY
const COGNITO_CONFIG = {
    UserPoolId: 'us-east-1_D2zHEN9Hx',  // Updated from your terraform output
    ClientId: '6jufqgov4mbkisfvq0ngh09ago',  // Updated from your terraform output
    Region: 'us-east-1'
};

const poolData = {
    UserPoolId: COGNITO_CONFIG.UserPoolId,
    ClientId: COGNITO_CONFIG.ClientId
};

const userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);

// Check if user is logged in on page load
document.addEventListener('DOMContentLoaded', function() {
    checkAuthStatus();
});

function checkAuthStatus() {
    const cognitoUser = userPool.getCurrentUser();
    
    if (cognitoUser != null) {
        cognitoUser.getSession(function(err, session) {
            if (err) {
                showLoggedOut();
                return;
            }
            if (session.isValid()) {
                cognitoUser.getUserAttributes(function(err, attributes) {
                    if (err) {
                        console.error(err);
                        return;
                    }
                    const email = attributes.find(attr => attr.Name === 'email').Value;
                    showLoggedIn(email);
                });
            } else {
                showLoggedOut();
            }
        });
    } else {
        showLoggedOut();
    }
}

function showLoggedIn(email) {
    document.getElementById('loggedOut').style.display = 'none';
    document.getElementById('loggedIn').style.display = 'block';
    document.getElementById('userEmail').textContent = email;
    
    // Show the form sections
    document.getElementById('participantSection').style.display = 'block';
}

function showLoggedOut() {
    document.getElementById('loggedOut').style.display = 'block';
    document.getElementById('loggedIn').style.display = 'none';
    
    // Hide the form sections until logged in
    document.getElementById('participantSection').style.display = 'none';
}

function showSignup() {
    const email = prompt('Enter your email:');
    const password = prompt('Enter password (min 8 chars, with uppercase, lowercase, number, symbol):');
    
    if (!email || !password) return;
    
    const attributeList = [
        new AmazonCognitoIdentity.CognitoUserAttribute({
            Name: 'email',
            Value: email
        })
    ];
    
    userPool.signUp(email, password, attributeList, null, function(err, result) {
        if (err) {
            alert('Signup failed: ' + err.message);
            return;
        }
        alert('Signup successful! Please check your email for verification code.');
        const code = prompt('Enter the verification code from your email:');
        if (code) {
            confirmSignup(email, code);
        }
    });
}

function confirmSignup(email, code) {
    const userData = {
        Username: email,
        Pool: userPool
    };
    
    const cognitoUser = new AmazonCognitoIdentity.CognitoUser(userData);
    
    cognitoUser.confirmRegistration(code, true, function(err, result) {
        if (err) {
            alert('Verification failed: ' + err.message);
            return;
        }
        alert('Email verified! You can now login.');
    });
}

function showLogin() {
    const email = prompt('Enter your email:');
    const password = prompt('Enter your password:');
    
    if (!email || !password) return;
    
    const authenticationData = {
        Username: email,
        Password: password
    };
    
    const authenticationDetails = new AmazonCognitoIdentity.AuthenticationDetails(authenticationData);
    
    const userData = {
        Username: email,
        Pool: userPool
    };
    
    const cognitoUser = new AmazonCognitoIdentity.CognitoUser(userData);
    
    cognitoUser.authenticateUser(authenticationDetails, {
        onSuccess: function(result) {
            alert('Login successful!');
            checkAuthStatus();
        },
        onFailure: function(err) {
            alert('Login failed: ' + err.message);
        }
    });
}

function logout() {
    const cognitoUser = userPool.getCurrentUser();
    if (cognitoUser) {
        cognitoUser.signOut();
        showLoggedOut();
        alert('Logged out successfully!');
    }
}

// Get current user's JWT token for API calls
function getAuthToken(callback) {
    const cognitoUser = userPool.getCurrentUser();
    
    if (cognitoUser != null) {
        cognitoUser.getSession(function(err, session) {
            if (err) {
                callback(null);
                return;
            }
            callback(session.getIdToken().getJwtToken());
        });
    } else {
        callback(null);
    }
}