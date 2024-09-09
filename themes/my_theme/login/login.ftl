<#import "template.ftl" as layout>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Login - My Custom Application</title>
    <link rel="stylesheet" href="resources/css/login.css">
</head>
<body>

    <div class="login-container">
        <div class="login-header">
            <img src="resources/img/logo.png" alt="Logo" class="logo">
            <h2>My Custom Application</h2>
            <h3>Sign in to your account</h3>
        </div>

        <div class="login-form">
            <form id="kc-form-login" action="http://localhost:8080/auth/realms/my-realm/protocol/openid-connect/auth" method="post">

                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" required>
                </div>

                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required>
                </div>

                <div class="form-group">
                    <input type="submit" value="Login" class="submit-btn">
                </div>

            </form>
        </div>

        <div class="login-footer">
            <a href="http://localhost:8080/auth/realms/my-realm/registrations">Register</a>
            <a href="http://localhost:8080/auth/realms/my-realm/forgot-credentials">Forgot Password?</a>
        </div>
    </div>

</body>
</html>

