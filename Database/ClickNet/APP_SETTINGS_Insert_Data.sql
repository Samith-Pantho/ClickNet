CREATE TABLE IF NOT EXISTS APP_SETTINGS
(
    `KEY`        VARCHAR(255)  NOT NULL PRIMARY KEY,
    DESCRIPTION  VARCHAR(3000) NULL,
    PRIVACYLEVEL VARCHAR(1)    NULL,
    VALUE        VARCHAR(5000) NOT NULL
);

INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('ACCESS_TOKEN_TIME', 'JWT token expiry (minutes)', '1', '60');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('ADD_LOG_IN_FILE_OR_DB', 'Log location: FILE/DB/BOTH', '1', 'FILE');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('APPLICATION_DEVELOPMENT_MODE', 'App running in development mode', '2', 'True');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('AUTO_GENARATED_PASSWORD', 'Enable auto-generated password', '2', 'True');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('AUTO_SET_USER_ID_AT_SIGNUP', 'Auto assign user ID', '2', 'True');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('AUTO_SET_USER_ID_TYPE_AT_SIGNUP', 'Auto assign ID type at signup : CIF/CIF_NON_ZERO/MOBILE/MOBILE_CIF/MOBILE_CIF_NON_ZERO', '2', 'CIF');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('AUTO_USER_ACTIVATION_AFTER_FORGET_PASSWORD', 'Auto activate user after reset', '2', 'True');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('CLICKNET_SENDER_EMAIL', 'Sender email for ClickNet', '3', 'xxxxx@gmail.com');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('CLICKNET_SENDER_EMAIL_PASS', 'Sender email password', '3', 'xxxxx');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('CREDENTIALS_SENDING_PROCESS', 'Send credentials via SMS/EMAIL/BOTH', '2', 'EMAIL');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('DEFAULT_AUTHENTICATION_TYPE', 'Default login method : SMS/EMAIL/BOTH', '1', 'EMAIL');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('DOB_VERIFICATION_MENDATORY_AT_FORGET_PASSWORD', 'Require DOB at password reset', '2', 'True');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('DOB_VERIFICATION_MENDATORY_AT_FORGET_USERID', 'Require DOB at user ID recovery', '2', 'True');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('EMAIL_USER_FORGET_PASSWORD_BODY', 'Email body for forgot password', '1', '<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Credentials Changed</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
  <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 20px; border: 1px solid #dddddd;">
    <p>Dear <strong>_userId_</strong>,</p>

    <p>Thank you for using <strong>ClickNet</strong>.</p>

    <p>You have successfully changed your credentials.</p>

    <h3>New Credentials</h3>
    <p>
      <span style="font-size: 18px; font-weight: bold; color: #007BFF;">User ID:</span>
      <span style="font-size: 18px; font-weight: bold; color: #007BFF;">_userId_</span><br>

      <span style="font-size: 18px; font-weight: bold; color: #28a745;">Password:</span>
      <span style="font-size: 18px; font-weight: bold; color: #28a745;">_password_</span>
    </p>

    <p>For any support or assistance, feel free to contact our helpdesk.</p>

    <p>Regards,<br>
    <strong>ClickNet Service</strong></p>
  </div>
</body>
</html>
');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('EMAIL_USER_FORGET_USERID_BODY', 'Email body for forgot user ID', '1', '
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Credentials</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
  <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 20px; border: 1px solid #dddddd;">
    <p>Dear <strong>_userId_</strong>,</p>

    <p>Thank you for using <strong>ClickNet</strong>.</p>

    <h3>Your Credentials</h3>
    <p>
      <span style="font-size: 18px; font-weight: bold; color: #007BFF;">User ID:</span>
      <span style="font-size: 18px; font-weight: bold; color: #007BFF;">_userId_</span><br>

    <p>For any support or assistance, feel free to contact our helpdesk.</p>

    <p>Regards,<br>
    <strong>ClickNet Service</strong></p>
  </div>
</body>
</html>
');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('EMAIL_USER_SIGNUP_BODY', 'Email body for signup', '1', '
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <title>Account Created</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
  <div style="max-width: 600px; margin: auto; background-color: #fff; padding: 20px; border: 1px solid #ddd;">
    <p>Dear <strong>_userId_</strong>,</p>

    <p>Thank you for registering with <strong>ClickNet</strong>.</p>

    <p>Your account has been successfully created. Please find your login credentials:</p>

    <h3>Account Credentials</h3>
    <p>
      <span style="font-size: 18px; font-weight: bold; color: #007BFF;">User ID:</span>
      <span style="font-size: 18px; font-weight: bold; color: #007BFF;">_userId_</span><br />

      <span style="font-size: 18px; font-weight: bold; color: #28a745;">Password:</span>
      <span style="font-size: 18px; font-weight: bold; color: #28a745;">_password_</span>
    </p>

    <p><em>Note: Please change your password immediately after your first login for security purposes.</em></p>

    <p>For any support or assistance, feel free to contact our helpdesk.</p>

    <p>Regards,<br />
      <strong>ClickNet Service</strong></p>
  </div>
</body>
</html>
');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('EMAIL_VERIFICATION_BODY', 'Email body for OTP', '1', '<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <title>OTP Verification</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
  <div style="max-width: 600px; margin: auto; background-color: #fff; padding: 20px; border: 1px solid #ddd;">

    <p>Thank you for using <strong>ClickNet</strong>.</p>

    <p>
      <span style="font-size: 18px; font-weight: bold; color: #28a745;">OTP:</span>
      <span style="font-size: 18px; font-weight: bold; color: #28a745;">_code_</span>
    </p>

    <p>Please enter this code in the application to verify your identity. This code will expire in <strong>5 minutes</strong>.</p>
    <p>If you did not request this, please ignore this email or contact our support team immediately.</p>

    <p>Regards,<br />
      <strong>ClickNet Service</strong></p>
  </div>
</body>
</html>');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('ENABLE_LICENCE_CHECKING', 'Enable or disable license validation', '2', 'False');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('ENCRYPTION_FIXED_KEY', 'Fixed key for encryption', '3', 'xxxxx');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('FORGET_PASSWORD_FAILED_ATTEMPTS_LIMIT', 'Limit for forget password attempts', '1', '3');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('FORGET_USERID_FAILED_ATTEMPTS_LIMIT', 'Limit for forget user ID attempts', '1', '3');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('IS_ENABLE_LOG_INSERT', 'Enable DB logging', '1', 'True');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('JWT_SECRET_KEY', 'JWT signing key', '3', 'xxxxx');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('LOGIN_AFTER_OTP_VERIFICATION', 'Enforce OTP verification before login', '2', 'False');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('LOGIN_WRONG_PASSWORD_ATTEMPT_LIMIT', 'Max wrong attempts before lock', '1', '5');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('MOBILE_MENDATORY_AT_FORGET_PASSWORD', 'Require mobile for password reset', '2', 'True');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('MOBILE_MENDATORY_AT_FORGET_USERID', 'Require mobile at user ID recovery', '2', 'True');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('NOTIFICATIONS_SENDING_PROCESS', 'Enable background notifications : SMS/EMAIL/BOTH', '2', 'EMAIL');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('OTP_EXPIRY_MINUTES', 'OTP expiry in minutes', '1', '5');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('OTP_LENGTH', 'OTP length', '1', '6');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('OTP_TYPE', 'OTP type (NUMERIC/ALPHA_NUMARIC/NON_ALPHA_NUMARIC/)', '1', 'NUMERIC');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('PASSWORD_EXPIRY_DAYS', 'Password will be Expired after N Days', '1', '30');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('PASSWORD_POLICY_MAX_PASSWORD_LENGTH', 'Max password length', '1', '16');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('PASSWORD_POLICY_MAX_SAME_PASSWORD_REUSE_COUNT', 'Max reused password count', '1', '5');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('PASSWORD_POLICY_MIN_ALPHA_NUMERIC_CHAR_COUNT', 'Min alphanumeric count', '1', '6');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('PASSWORD_POLICY_MIN_CAPITAL_CHAR_COUNT', 'Min capital letters', '1', '1');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('PASSWORD_POLICY_MIN_NON_ALPHA_NUMERIC_CHAR_COUNT', 'Min special characters in password', '1', '1');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('PASSWORD_POLICY_MIN_NUMBER_COUNT', 'Min digits', '1', '1');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('PASSWORD_POLICY_MIN_PASSWORD_LENGTH', 'Min password length', '1', '8');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('PASSWORD_POLICY_MIN_SMALL_CHAR_COUNT', 'Min small letters', '1', '1');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('PASSWORD_POLICY_SAME_PASSWORD_REPEAT_ALLOWED_AFTER_DAYS', 'Repeat password after N days', '1', '30');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('PASSWORD_POLICY_SUCCESSIVE_SAME_CHAR_ALLOEWD_COUNT', 'Max successive characters allowed', '1', '3');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('RESTRICT_SAME_MOBILE_NO_AT_SIGNUP', 'Restrict duplicate mobile at signup', '1', 'True');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('RESTRICT_SPECIAL_CHARACTERS_FOR_PASSWORD', 'Allow/disallow special characters', '1', '$-----#-----€');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('SMS_USER_FORGET_PASSWORD_BODY', 'SMS body for forgot password', '1', 'Dear *_userId_*,

Thank you for using 

Your credentials have been changed successfully.
Your new login credentials:
User ID: *_userId_*
Password: *_password_*

Note: Please change your password immediately after your first login for security.

For support, contact our helpdesk.

Regards,
ClickNet Service');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('SMS_USER_FORGET_USERID_BODY', 'SMS body for forgot user ID', '1', 'Dear *_userId_*,

Thank you for using 

Your credentials:
User ID: *_userId_*

Note: Please change your password immediately after your first login for security.

For support, contact our helpdesk.

Regards,
ClickNet Service');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('SMS_USER_SIGNUP_BODY', 'SMS body for signup', '1', 'Dear *_userId_*,

Thank you for registering with 

Your account has been created successfully.
Your login credentials:
User ID: *_userId_*
Password: *_password_*

Note: Please change your password immediately after your first login for security.

For support, contact our helpdesk.

Regards,
ClickNet Service');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('SMS_VERIFICATION_BODY', 'SMS body for OTP', '1', 'Your ClickNet verification code is _code_');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('SYSTEM_DOWN', 'System maintenance mode toggle', '1', 'False');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('SYSTEM_DOWN_MSG', 'System maintenance message', '1', 'System is under maintenance.');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('TAXID_MENDATORY_AT_FORGET_PASSWORD', 'Require Tax ID at password reset', '2', 'True');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('TAXID_MENDATORY_AT_FORGET_USERID', 'Require Tax ID at user ID recovery', '2', 'True');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('TWILIO_ACCOUNT_SID', 'Twilio account SID', '3', 'xxxxx');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('TWILIO_AUTH_TOKEN', 'Twilio auth token', '3', 'xxxxx');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('TWILIO_MOBILE_NUMBER', 'Twilio sender number', '3', 'xxxxx');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('CUSTOMER_PHOTO_PATH', 'Customer Profile Pictures path', '1', 'C:\\ClickNet\\Customer_Profile_Pictures\\');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('OPENAI_API_KEY', 'OpenAI Api SecretKey', '3', 'xxxxx');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('EMAIL_USER_FUND_TRANSFER_BODY', 'Email body for fund transfer', '1', '
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <title>Payment Confirmation</title>
  <style>
    body {
      font-family: Arial, sans-serif; 
      background-color: #f9f9f9; 
      padding: 20px;
      color: #333;
    }
    .container {
      max-width: 600px; 
      margin: auto; 
      background-color: #fff; 
      padding: 25px; 
      border: 1px solid #ddd; 
      border-radius: 8px;
      box-shadow: 0 2px 6px rgb(0 0 0 / 0.1);
    }
    h3 {
      color: #007BFF;
      border-bottom: 2px solid #007BFF;
      padding-bottom: 8px;
    }
    .detail-row {
      background: #f1f8ff;
      border-radius: 6px;
      padding: 15px 20px;
      margin-bottom: 15px;
      display: flex;
      justify-content: space-between;
      font-weight: 600;
      color: #0d47a1;
      box-shadow: inset 0 0 5px rgba(0, 123, 255, 0.2);
    }
    .label {
      flex: 1;
    }
    .value {
      flex: 1;
      text-align: right;
      color: #0056b3;
      word-break: break-word;    
      overflow-wrap: anywhere;   
      white-space: normal;       
    }
    p.note {
      font-style: italic;
      color: #555;
      margin-top: 25px;
    }
  </style>
</head>
<body>
  <div class="container">
    <p>Dear <strong>_userId_</strong>,</p>

    <p>We are pleased to inform you that your payment has been <strong style="color: #28a745;">successfully processed</strong>.</p>

    <h3>Payment Details</h3>

    <div class="detail-row">
      <div class="label">Amount:</div>
      <div class="value">_amount_ _currency_</div>
    </div>
    <div class="detail-row">
      <div class="label">From Account:</div>
      <div class="value">_fromAccount_</div>
    </div>
    <div class="detail-row">
      <div class="label">To Account:</div>
      <div class="value">_toAccount_</div>
    </div>
    <div class="detail-row">
      <div class="label">Purpose:</div>
      <div class="value">_purpose_</div>
    </div>
    <div class="detail-row">
      <div class="label">TXID:</div>
      <div class="value">_transactionId_</div>
    </div>

    <p>If you did not authorize this transaction or have any questions, please contact our support immediately.</p>

    <p>Thank you for banking with us.</p>

    <p>Regards,<br />
       <strong>ClickNet Service Team</strong></p>
  </div>
</body>
</html>
');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('SMS_USER_FUND_TRANSFER_BODY', 'SMS body for fund transfer', '1', 'Dear *_userId_*,

Your ClickNet Fund Transfer is Successful!

Transaction ID: *_transactionId_*
Amount: _amount_  _currency_
From: _fromAccount_
To: _toAccount_
Purpose: _purpose_

If you did not authorize this, contact our helpdesk immediately.

Thank you for banking with ClickNet!');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('FERNET_SECRET_KEY', 'Fernet SecretKey for image encryption', '3', 'xxxxx');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('GOOGLE_RECAPTCHA_SITE_KEY', 'Google reCAPTCHA site key', '2', 'xxxxx');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('GOOGLE_RECAPTCHA_SECRET_KEY', 'Google reCAPTCHA secret key', '3', 'xxxxx');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('ORS_API_KEY', 'OpenStreetMap API key', '2', 'xxxxx');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('STRIPE_SECRET_KEY', 'Stripe API secret key', '3', 'xxxxx');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('STRIPE_PUBLISHABLE_KEY', 'Stripe publishable key for websit', '2', 'xxxxx');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('STRIPE_CALLBACK_SUCCESS_URL', 'Stripe redirect url to website if payment success', '2', 'http://localhost:3000/addmoneycallback?data=_data_');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('STRIPE_CALLBACK_CANCEL_URL', 'Stripe redirect url to website if payment cancel', '2', 'http://localhost:3000/addmoneycallback?data=_data_');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('STRIPE_WEBHOOK_SECRET', 'Stripe secret key for webhook', '3', 'xxxxx');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('API_WEBHOOK_KEY', 'Secret key for API webhook', '3', 'xxxxx');