CREATE TABLE IF NOT EXISTS APP_SETTINGS
(
    `KEY`        VARCHAR(255)  NOT NULL PRIMARY KEY,
    DESCRIPTION  VARCHAR(3000) NULL,
    PRIVACYLEVEL VARCHAR(1)    NULL,
    VALUE        VARCHAR(5000) NOT NULL
);

INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('CREDENTIALS_SENDING_PROCESS', 'Send credentials via SMS/EMAIL/BOTH', '2', 'EMAIL');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('SMS_USER_REGISTREATION_BODY', 'SMS body for registered users', '1', 'Dear user,

Thank you for using ClickKYC

You have opened your account successfully.
Account Information:
Customer ID: *_customerId_*
Account Number: *_account_number_*


For support, contact our helpdesk.

Regards,
ClickKYC Service');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('EMAIL_USER_REGISTREATION_BODY', 'Email body for registered users', '1', '<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Account Opened</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
  <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 20px; border: 1px solid #dddddd;">
    <p>Dear user,</p>

    <p>Thank you for using <strong>ClickKYC</strong>.</p>

    <p>You have successfully opened your account.</p>

    <h3>Account Information</h3>
    <p>
      <span style="font-size: 18px; font-weight: bold; color: #007BFF;">Customer ID:</span>
      <span style="font-size: 18px; font-weight: bold; color: #007BFF;">_customerId_</span><br>

      <span style="font-size: 18px; font-weight: bold; color: #28a745;">Account Number:</span>
      <span style="font-size: 18px; font-weight: bold; color: #28a745;">_account_number_</span>
    </p>

    <p>For any support or assistance, feel free to contact our helpdesk.</p>

    <p>Regards,<br>
    <strong>ClickKYC Service</strong></p>
  </div>
</body>
</html>
');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('IS_ENABLE_LOG_INSERT', 'Enable DB logging', '1', 'True');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('ADD_LOG_IN_FILE_OR_DB', 'Log location: FILE/DB/BOTH', '1', 'FILE');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('OTP_EXPIRY_MINUTES', 'OTP expiry in minutes', '1', '5');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('OTP_LENGTH', 'OTP length', '1', '6');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('OTP_TYPE', 'OTP type (NUMERIC/ALPHA_NUMARIC/NON_ALPHA_NUMARIC/)', '1', 'NUMERIC');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('ACCESS_TOKEN_TIME', 'JWT token expiry (minutes)', '1', '60');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('APPLICATION_DEVELOPMENT_MODE', 'App running in development mode', '2', 'True');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('SMS_VERIFICATION_BODY', 'SMS body for OTP', '1', 'Your ClickNet verification code is _code_');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('EMAIL_VERIFICATION_BODY', 'Email body for OTP', '1', '<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <title>OTP Verification</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
  <div style="max-width: 600px; margin: auto; background-color: #fff; padding: 20px; border: 1px solid #ddd;">

    <p>Thank you for using <strong>ClickKYC</strong>.</p>

    <p>
      <span style="font-size: 18px; font-weight: bold; color: #28a745;">OTP:</span>
      <span style="font-size: 18px; font-weight: bold; color: #28a745;">_code_</span>
    </p>

    <p>Please enter this code in the application to verify your identity. This code will expire in <strong>5 minutes</strong>.</p>
    <p>If you did not request this, please ignore this email or contact our support team immediately.</p>

    <p>Regards,<br />
      <strong>ClickKYC Service</strong></p>
  </div>
</body>
</html>');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('JWT_SECRET_KEY', 'JWT signing key', '3', 'xxxxx');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('DIDIT_WORKFLOW_ID', 'Didit Workflow ID for Custom EKYC', '3', 'xxxxx');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('DIDIT_API_KEY', 'Didit API Key', '3', 'xxxxx');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('DIDIT_CALLBACK_URL', 'Didit Callback/redirect URL', '3', 'http://https://8af82b6acdf4.ngrok-free.app/callback?data=_data_');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('DIDIT_WEBHOOK_SECRET', 'Didit webhook secret key for checking signature', '3', 'xxxxx');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('CUSTOMER_PHOTO_PATH', 'Customer Pictures path', '1', 'C:\\ClickKYC\\Customer_Kyc_Pictures\\');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('FERNET_SECRET_KEY', 'Fernet SecretKey for image encryption', '3', 'xxxxx');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('GOOGLE_RECAPTCHA_SITE_KEY', 'Google reCAPTCHA site key', '2', 'xxxxx');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('GOOGLE_RECAPTCHA_SECRET_KEY', 'Google reCAPTCHA secret key', '3', 'xxxxx');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('ENCRYPTION_FIXED_KEY', 'Fixed key for encryption', '3', 'xxxxx');
INSERT INTO APP_SETTINGS (`KEY`, DESCRIPTION, PRIVACYLEVEL, VALUE) VALUES ('DIDIT_WEBHOOK_KEY', 'KYC Webhook Key', '3', 'xxxxx');