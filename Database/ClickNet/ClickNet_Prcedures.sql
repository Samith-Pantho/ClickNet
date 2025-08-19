DELIMITER $$


CREATE DEFINER=`root`@`localhost` PROCEDURE CLICKNET_GetPendingOTP(
    IN p_user_id VARCHAR(25), 
    IN p_cust_id VARCHAR(20),
    IN p_from_acct VARCHAR(500), 
    IN p_from_branch VARCHAR(6),
    IN p_to_acct VARCHAR(500), 
    IN p_to_branch VARCHAR(12),
    IN p_to_bank_id VARCHAR(6),
    IN p_to_routing_numb VARCHAR(9),
    IN p_amount_ccy DECIMAL(17,4),
    IN p_amount_lcy DECIMAL(17,4), 
    IN p_cutoff_time DATETIME)
BEGIN
    SELECT *
    FROM CUSTOMER_OTP
    WHERE LOWER(TRIM(USER_ID)) = LOWER(TRIM(p_user_id))
      AND CUST_ID = p_cust_id
      AND FROM_ACCOUNT_NO = p_from_acct
      AND FROM_BRANCH_ID = p_from_branch
      AND TO_ACCOUNT_NO = p_to_acct
      AND TO_BRANCH_ID = p_to_branch
      AND TO_BANK_ID = p_to_bank_id
      AND TO_ROUTING_NUMB = p_to_routing_numb
      AND ROUND(AMOUNT_CCY, 4) = ROUND(p_amount_ccy, 4)
      AND ROUND(AMOUNT_LCY, 4) = ROUND(p_amount_lcy, 4)
      AND OTP_VERIFIED_AT IS NULL
      AND TRIM(UPPER(REMARKS)) = 'PENDING'
      AND DB_SVR_DT >= p_cutoff_time
    ORDER BY OTP_SL DESC
    LIMIT 1;
END $$

CREATE DEFINER=`root`@`localhost` PROCEDURE CLICKNET_GetAppSettingsByKeys (
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

CREATE DEFINER=`root`@`localhost` PROCEDURE CLICKNET_GetAllAppSettings()
BEGIN
    SELECT `KEY`, `VALUE` FROM APP_SETTINGS;
END$$

CREATE PROCEDURE CLICKNET_GetTableSl (
    IN input_table_nm VARCHAR(500)
)
BEGIN
    DECLARE current_sl INT;

    SELECT TABLE_SL INTO current_sl
    FROM SYSTEM_TABLE_SL
    WHERE TABLE_NM = input_table_nm
    FOR UPDATE;

    IF current_sl IS NULL THEN
        SET current_sl = 1;
        INSERT INTO SYSTEM_TABLE_SL (TABLE_NM, TABLE_SL) VALUES (input_table_nm, current_sl + 1);
    ELSE
        UPDATE SYSTEM_TABLE_SL SET TABLE_SL = current_sl + 1 WHERE TABLE_NM = input_table_nm;
    END IF;

    SELECT current_sl AS output_sl;

    COMMIT;
END $$

DELIMITER ;


