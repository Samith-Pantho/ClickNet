DELIMITER $$

CREATE DEFINER=`root`@`localhost` PROCEDURE CLICKKYC_GetAppSettingsByKeys (
    IN p_keys TEXT
)
BEGIN
    -- Convert comma-separated keys into a temporary table
    CREATE TEMPORARY TABLE temp_keys (key_name VARCHAR(255));

    WHILE LOCATE(',', p_keys) > 0 DO
        INSERT INTO temp_keys (key_name)
        VALUES (TRIM(SUBSTRING_INDEX(p_keys, ',', 1)));
        SET p_keys = SUBSTRING(p_keys FROM LOCATE(',', p_keys) + 1);
    END WHILE;

    IF LENGTH(TRIM(p_keys)) > 0 THEN
        INSERT INTO temp_keys (key_name) VALUES (TRIM(p_keys));
    END IF;

    -- Return matching app settings with PRIVACYLEVEL not equal to '3'
    SELECT a.KEY, a.VALUE
    FROM APP_SETTINGS a
    INNER JOIN temp_keys t ON UPPER(a.KEY) = UPPER(t.key_name)
    WHERE a.PRIVACYLEVEL != '3';

    DROP TEMPORARY TABLE IF EXISTS temp_keys;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE CLICKKYC_GetAllAppSettings()
BEGIN
    SELECT `KEY`, `VALUE` FROM APP_SETTINGS;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE CLICKKYC_InitializeTrackingId(
    IN p_phone_number VARCHAR(20),
    IN p_product_code VARCHAR(20)
)
BEGIN
    DECLARE v_tracking_id VARCHAR(100);
    DECLARE v_existing_tracking_id VARCHAR(50);
    DECLARE v_existing_status VARCHAR(30);
    DECLARE v_is_tax_id_verified BOOLEAN;
    DECLARE v_return_tracking_id VARCHAR(50);
    
    -- Check for most recent existing tracking ID with same phone and product code
    SELECT TRACKING_ID, STATUS, IS_TAX_ID_VERIFIED 
    INTO v_existing_tracking_id, v_existing_status, v_is_tax_id_verified
    FROM CUSTOMER_REGISTRATION
    WHERE PHONE_NUMBER = p_phone_number
      AND PRODUCT_CODE = p_product_code
    ORDER BY CREATE_DT DESC
    LIMIT 1;
    
    -- If no valid tracking ID or rejected/unverified, create a new one
    IF v_existing_tracking_id IS NULL OR 
       (v_existing_status = 'REJECTED' OR v_is_tax_id_verified = FALSE) THEN
        
        -- If unverified, mark it rejected
        IF v_existing_tracking_id IS NOT NULL AND v_is_tax_id_verified = FALSE THEN
            UPDATE CUSTOMER_REGISTRATION
            SET STATUS = 'REJECTED'
            WHERE TRACKING_ID = v_existing_tracking_id;
        END IF;
        
        -- Generate new tracking ID (max 50 chars)
        SET v_tracking_id = CONCAT(
            DATE_FORMAT(NOW(), '%Y%m%d%H%i%s'),
            LPAD(FLOOR(RAND() * 10000000000), 20, '0'),
            SUBSTRING(UUID(), 1, 19)
        );
        SET v_return_tracking_id = SUBSTRING(v_tracking_id, 1, 50);
        
        -- Insert new record
        INSERT INTO CUSTOMER_REGISTRATION (
            TRACKING_ID,
            PHONE_NUMBER,
            PRODUCT_CODE,
            CREATE_DT,
            STATUS
        ) VALUES (
            v_return_tracking_id,
            p_phone_number,
            p_product_code,
            NOW(),
            'INITIALIZED'
        );
        COMMIT;
    ELSE
        SET v_return_tracking_id = v_existing_tracking_id;
    END IF;
    
    -- Directly return only the tracking ID
    SELECT v_return_tracking_id AS tracking_id;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE CLICKKYC_GetTrackingData(
    IN p_tracking_id VARCHAR(50)
)
BEGIN
    SELECT 
        TRACKING_ID as tracking_id,
        NAME as name,
        TITLE as title,
        FIRST_NAME as first_name,
        MIDDLE_NAME as middle_name,
        LAST_NAME as last_name,
        SUFFIX as suffix,
        BIRTH_DATE as birth_date,
        TAX_ID as tax_id,
        TAX_ID_TYPE as tax_id_type,
		IS_TAX_ID_VERIFIED as is_tax_id_verified,
        ADDRESS_TYPE as address_type,
        LINE_1 as line_1,
        LINE_2 as line_2,
        LINE_3 as line_3,
        LINE_4 as line_4,
        CITY as city,
        STATE_CODE as state_code,
        ZIPCODE as zipcode,
        COUNTRY_CODE as country_code,
        EMAIL_ADDRESS as email_address,
        PHONE_NUMBER as phone_number,
        PRODUCT_CODE as product_code,
        BRANCH_CODE as branch_code,
        CUSTOMER_ID as customer_id,
        ACCOUNT_NUMBER as account_number,
        CREATE_BY as create_by,
        CREATE_DT as create_dt,
        STATUS as status,
        REJECT_REASON as reject_reason
    FROM CUSTOMER_REGISTRATION
    WHERE TRACKING_ID = p_tracking_id;
END$$
CREATE DEFINER=`root`@`localhost` PROCEDURE CLICKKYC_UpdateTrackingData(
    IN p_tracking_id VARCHAR(50),
    IN p_name VARCHAR(500),
    IN p_title VARCHAR(50),
    IN p_first_name VARCHAR(500),
    IN p_middle_name VARCHAR(500),
    IN p_last_name VARCHAR(500),
    IN p_suffix VARCHAR(50),
    IN p_birth_date DATE,
    IN p_tax_id VARCHAR(50),
    IN p_tax_id_type VARCHAR(50),
    IN p_is_tax_id_verified BOOLEAN,
    IN p_address_type VARCHAR(100),
    IN p_line_1 VARCHAR(500),
    IN p_line_2 VARCHAR(500),
    IN p_line_3 VARCHAR(500),
    IN p_line_4 VARCHAR(500),
    IN p_city VARCHAR(500),
    IN p_state_code VARCHAR(100),
    IN p_zipcode VARCHAR(200),
    IN p_country_code VARCHAR(100),
    IN p_email_address VARCHAR(500),
    IN p_phone_number VARCHAR(500),
    IN p_product_code VARCHAR(100),
    IN p_branch_code VARCHAR(100),
    IN p_customer_id VARCHAR(100),
    IN p_account_number VARCHAR(100),
    IN p_create_by VARCHAR(30),
    IN p_status VARCHAR(30),
    IN p_reject_reason VARCHAR(1000)
)
BEGIN
    DECLARE v_current_status VARCHAR(30);
    DECLARE v_current_name VARCHAR(500);
    DECLARE v_current_tax_id VARCHAR(100);
    DECLARE v_current_tax_id_type VARCHAR(100);
    DECLARE v_current_phone_number VARCHAR(200);
    DECLARE v_current_email_address VARCHAR(500);
    DECLARE v_current_product_code VARCHAR(100);
    DECLARE v_current_customer_id VARCHAR(100);
    DECLARE v_current_account_number VARCHAR(100);
    DECLARE v_new_status VARCHAR(30);

    -- Get current status and protected field values
    SELECT 
        STATUS, NAME, TAX_ID, TAX_ID_TYPE, PHONE_NUMBER, 
        EMAIL_ADDRESS, PRODUCT_CODE, CUSTOMER_ID, ACCOUNT_NUMBER
    INTO 
        v_current_status, v_current_name, v_current_tax_id, v_current_tax_id_type, 
        v_current_phone_number, v_current_email_address, v_current_product_code, 
        v_current_customer_id, v_current_account_number
    FROM CUSTOMER_REGISTRATION
    WHERE TRACKING_ID = p_tracking_id;

    -- Check if already processed or rejected
    IF v_current_status IN ('PROCESSED', 'REJECTED') THEN
        SET v_new_status = v_current_status;
    ELSE
        -- Determine the new status based on tax ID verification
        IF p_is_tax_id_verified IS NOT NULL AND p_is_tax_id_verified = FALSE THEN
            SET v_new_status = 'REJECTED';
        ELSE
            -- Original status determination logic
            IF (p_customer_id IS NOT NULL AND p_account_number IS NOT NULL) OR 
               (v_current_customer_id IS NOT NULL AND v_current_account_number IS NOT NULL) OR
               ((v_current_customer_id IS NOT NULL OR p_customer_id IS NOT NULL) AND 
                (v_current_account_number IS NOT NULL OR p_account_number IS NOT NULL)) THEN
                SET v_new_status = 'PROCESSED';
            ELSE
                -- Use the provided status if none of the above conditions are met
                SET v_new_status = COALESCE(p_status, v_current_status);
            END IF;
        END IF;

        -- Update the record
        UPDATE CUSTOMER_REGISTRATION
        SET
            -- Protected fields can only be updated if currently NULL
            NAME = CASE WHEN v_current_name IS NULL THEN p_name ELSE v_current_name END,
            TAX_ID = CASE WHEN v_current_tax_id IS NULL THEN p_tax_id ELSE v_current_tax_id END,
            TAX_ID_TYPE = CASE WHEN v_current_tax_id_type IS NULL THEN p_tax_id_type ELSE v_current_tax_id_type END,
            IS_TAX_ID_VERIFIED = p_is_tax_id_verified,
            PHONE_NUMBER = CASE WHEN v_current_phone_number IS NULL THEN p_phone_number ELSE v_current_phone_number END,
            EMAIL_ADDRESS = CASE WHEN v_current_email_address IS NULL THEN p_email_address ELSE v_current_email_address END,
            PRODUCT_CODE = CASE WHEN v_current_product_code IS NULL THEN p_product_code ELSE v_current_product_code END,
            CUSTOMER_ID = CASE WHEN v_current_customer_id IS NULL THEN p_customer_id ELSE v_current_customer_id END,
            ACCOUNT_NUMBER = CASE WHEN v_current_account_number IS NULL THEN p_account_number ELSE v_current_account_number END,

            -- Always updatable fields
            TITLE = p_title,
            FIRST_NAME = p_first_name,
            MIDDLE_NAME = p_middle_name,
            LAST_NAME = p_last_name,
            SUFFIX = p_suffix,
            BIRTH_DATE = p_birth_date,
            ADDRESS_TYPE = p_address_type,
            LINE_1 = p_line_1,
            LINE_2 = p_line_2,
            LINE_3 = p_line_3,
            LINE_4 = p_line_4,
            CITY = p_city,
            STATE_CODE = p_state_code,
            ZIPCODE = p_zipcode,
            COUNTRY_CODE = p_country_code,
            BRANCH_CODE = p_branch_code,
            CREATE_BY = p_create_by,
            REJECT_REASON = p_reject_reason,
            STATUS = v_new_status
        WHERE TRACKING_ID = p_tracking_id;
        COMMIT;
    END IF;

    -- Return the final status
    SELECT v_new_status AS result;

END$$

DELIMITER ;


