DELIMITER $$

CREATE DEFINER=`root`@`localhost` PROCEDURE CBS_GetAccountBalancesAndRate(IN p_account_number VARCHAR(20))
BEGIN
    SELECT original_balance, current_balance, available_balance, interest_rate
    FROM cbs_customer_accounts
    WHERE account_number = p_account_number;
END $$

CREATE DEFINER=`root`@`localhost` PROCEDURE CBS_GetAccountInfo(IN p_account_number VARCHAR(20))
BEGIN
    SELECT 
        a.account_number,
        p.product_category,
        p.product_type,
        p.product_name,
        a.status,
        a.relationship,
        a.branch_code,
        a.opened_date,
        a.maturity_date
    FROM cbs_customer_accounts a
    JOIN cbs_products p ON a.product_code = p.product_code
    WHERE a.account_number = p_account_number;
END $$

CREATE DEFINER=`root`@`localhost` PROCEDURE CBS_GetAccountWiseTransLimitInfo(
    IN p_account_number VARCHAR(20))
BEGIN
    SELECT 
        a.payment_frequency,
        pl.min_amount_of_payments_allowed as payment_min_amount,
        pl.max_amount_of_payments_allowed as payment_max_amount,
        pl.no_of_payments_allowed AS daily_no_of_payments,
        
        IFNULL((
            SELECT SUM(t.DR_AMOUNT)
            FROM cbs_Transactions t
            WHERE t.FROM_ACCOUNT = p_account_number
              AND t.DR_CR = 'D'
              AND DATE(t.TRANS_DATE) = CURDATE()
        ), 0) AS today_total_amount,
        
        IFNULL((
            SELECT COUNT(*)
            FROM cbs_Transactions t
            WHERE t.FROM_ACCOUNT = p_account_number
              AND t.DR_CR = 'D'
              AND DATE(t.TRANS_DATE) = CURDATE()
        ), 0) AS today_total_transactions
    FROM cbs_customer_accounts a
    JOIN cbs_product_payment_limit pl ON a.product_code = pl.product_code
    WHERE a.account_number = p_account_number;
END $$

CREATE DEFINER=`root`@`localhost` PROCEDURE CBS_GetAvailableBalance(IN p_account_number VARCHAR(20))
BEGIN
    SELECT available_balance
    FROM cbs_customer_accounts
    WHERE account_number = p_account_number;
END $$

CREATE DEFINER=`root`@`localhost` PROCEDURE CBS_GetCustomerAccounts(IN p_customer_id VARCHAR(20), IN p_product_category VARCHAR(20))
BEGIN
    IF p_product_category IS NULL OR TRIM(p_product_category) = '' THEN
        SELECT 
            a.account_number,
            a.branch_code,
            p.product_category,
            p.product_type,
            p.product_name
        FROM cbs_customer_accounts a
        JOIN cbs_products p ON a.product_code = p.product_code
        WHERE a.customer_id = p_customer_id;
    ELSE
        SELECT 
            a.account_number,
            a.branch_code,
            p.product_category,
            p.product_type,
            p.product_name
        FROM cbs_customer_accounts a
        JOIN cbs_products p ON a.product_code = p.product_code
        WHERE a.customer_id = p_customer_id
          AND UPPER(p.product_category) = UPPER(p_product_category);
    END IF;
END $$

CREATE DEFINER=`root`@`localhost` PROCEDURE CBS_GetCustomerAccountsWithDetails(IN p_customer_id VARCHAR(20), IN p_product_category VARCHAR(20))
BEGIN
    IF p_product_category IS NULL OR TRIM(p_product_category) = '' THEN
        SELECT 
            a.account_number,
            a.customer_id,
            a.account_title,
            a.product_code,
            p.product_category,
            p.product_type,
            p.product_name,
            a.status,
            a.relationship,
            a.branch_code,
            a.opened_date,
            a.maturity_date,
            a.original_balance,
            a.current_balance,
            a.available_balance,
            a.payment_frequency,
            a.interest_rate
        FROM cbs_customer_accounts a
        JOIN cbs_products p ON a.product_code = p.product_code
        WHERE a.customer_id = p_customer_id;
    ELSE
        SELECT 
            a.account_number,
            a.customer_id,
            a.account_title,
            a.product_code,
            p.product_category,
            p.product_type,
            p.product_name,
            a.status,
            a.relationship,
            a.branch_code,
            a.opened_date,
            a.maturity_date,
            a.original_balance,
            a.current_balance,
            a.available_balance,
            a.payment_frequency,
            a.interest_rate
        FROM cbs_customer_accounts a
        JOIN cbs_products p ON a.product_code = p.product_code
        WHERE a.customer_id = p_customer_id
          AND UPPER(p.product_category) = UPPER(p_product_category);
    END IF;
END $$

CREATE DEFINER=`root`@`localhost` PROCEDURE CBS_GetCustomerAddresses(IN p_customer_id VARCHAR(20))
BEGIN
    SELECT * FROM cbs_customer_addresses
    WHERE customer_id = p_customer_id;
END $$

CREATE DEFINER=`root`@`localhost` PROCEDURE CBS_GetCustomerEmails(IN p_customer_id VARCHAR(20))
BEGIN
    SELECT * FROM cbs_customer_emails
    WHERE customer_id = p_customer_id;
END $$

CREATE DEFINER=`root`@`localhost` PROCEDURE CBS_GetCustomerInfo(IN p_customer_id VARCHAR(20))
BEGIN
    SELECT * FROM cbs_customers
    WHERE customer_id = p_customer_id;
END $$

CREATE DEFINER=`root`@`localhost` PROCEDURE CBS_GetCustomerPhones(IN p_customer_id VARCHAR(20))
BEGIN
    SELECT * FROM cbs_customer_phones
    WHERE customer_id = p_customer_id;
END $$

CREATE DEFINER=`root`@`localhost` PROCEDURE CBS_FundTransfer (
    IN  p_FROM_ACCOUNT   VARCHAR(15),
    IN  p_SENDER_NAME    VARCHAR(150),
    IN  p_TO_ACCOUNT     VARCHAR(15),
    IN  p_RECEIVER_NAME  VARCHAR(150),
    IN  p_TRANS_MODE     ENUM('TRANSFER','CASH'),
    IN  p_PURPOSE        VARCHAR(50),
    IN  p_AMOUNT         DECIMAL(18,2),
    IN  p_CURRENCY_NM    VARCHAR(10),
    OUT p_TRANS_ID       VARCHAR(20),
    OUT p_ERROR_MSG      VARCHAR(255)
)
BEGIN
    -- Vars
    DECLARE v_available_balance     DECIMAL(18,2);
    DECLARE v_payment_min_amount    DECIMAL(18,2);
    DECLARE v_payment_max_amount    DECIMAL(18,2);
    DECLARE v_daily_no_of_payments  INT;

    DECLARE v_today_total_amount    DECIMAL(18,2) DEFAULT 0.0;
    DECLARE v_today_txn_count       INT DEFAULT 0;

    DECLARE v_narration             VARCHAR(500);
    DECLARE v_trans_date            DATETIME(3);

    -- Error handler
    DECLARE EXIT HANDLER FOR SQLEXCEPTION 
    BEGIN
        ROLLBACK;
        SET p_TRANS_ID  = NULL;
        SET p_ERROR_MSG = 'Transaction failed due to internal error.';
    END;

    -- Use system current timestamp
    SET v_trans_date = NOW(3);

    START TRANSACTION;

    main_block: BEGIN

        -- Fetch sender limits/balance
        SELECT 
            a.available_balance, 
            pl.min_amount_of_payments_allowed, 
            pl.max_amount_of_payments_allowed, 
            pl.no_of_payments_allowed
        INTO 
            v_available_balance, 
            v_payment_min_amount, 
            v_payment_max_amount, 
            v_daily_no_of_payments
        FROM cbs_customer_accounts a
        JOIN cbs_product_payment_limit pl ON a.product_code = pl.product_code
        WHERE a.account_number = p_FROM_ACCOUNT;

        -- Available balance check
        IF v_available_balance < p_AMOUNT THEN
            SET p_ERROR_MSG = 'Insufficient Available Balance';
            ROLLBACK;
            LEAVE main_block;
        END IF;

        -- Sender daily debit total
        SELECT IFNULL(SUM(DR_AMOUNT), 0)
          INTO v_today_total_amount
          FROM cbs_Transactions
         WHERE FROM_ACCOUNT = p_FROM_ACCOUNT
           AND DR_CR = 'D'
           AND DATE(TRANS_DATE) = CURDATE();

        -- Min amount check
        IF p_AMOUNT < v_payment_min_amount THEN
            SET p_ERROR_MSG = CONCAT(
                'Transfer amount ', p_AMOUNT,
                ' is below the minimum daily transfer amount of ', v_payment_min_amount
            );
            ROLLBACK;
            LEAVE main_block;
        END IF;

        -- Max amount check
        IF (v_today_total_amount + p_AMOUNT) > v_payment_max_amount THEN
            SET p_ERROR_MSG = CONCAT(
                'Maximum daily transfer limit exceeded: current total (including this) = ',
                v_today_total_amount + p_AMOUNT,
                ', allowed maximum = ',
                v_payment_max_amount
            );
            ROLLBACK;
            LEAVE main_block;
        END IF;

        -- Daily transaction count
        SELECT COUNT(*)
          INTO v_today_txn_count
          FROM cbs_Transactions
         WHERE FROM_ACCOUNT = p_FROM_ACCOUNT
           AND DR_CR = 'D'
           AND DATE(TRANS_DATE) = CURDATE();

        IF v_today_txn_count >= v_daily_no_of_payments THEN
            SET p_ERROR_MSG = CONCAT(
                'Maximum number of daily transactions exceeded for sender: current count = ',
                v_today_txn_count,
                ', allowed maximum = ',
                v_daily_no_of_payments
            );
            ROLLBACK;
            LEAVE main_block;
        END IF;

        -- Generate TRANS_ID
        SET p_TRANS_ID = UPPER(SUBSTRING(MD5(UUID()), 1, 20));

        -- Debit sender
        UPDATE cbs_customer_accounts
           SET available_balance = available_balance - p_AMOUNT,
               current_balance   = current_balance   - p_AMOUNT
         WHERE account_number = p_FROM_ACCOUNT;

        SET v_narration = CONCAT(
            'TRANSFER of ', p_AMOUNT, ' ', p_CURRENCY_NM,
            ' from ', p_FROM_ACCOUNT, ' (', p_SENDER_NAME, ')',
            ' to ', p_TO_ACCOUNT, ' (', p_RECEIVER_NAME, ')',
            ' on ', DATE_FORMAT(v_trans_date, '%Y-%m-%d %H:%i:%s.%f'),
            ' via ', p_TRANS_MODE,
            ' for ', p_PURPOSE
        );

        INSERT INTO cbs_Transactions (
            FROM_ACCOUNT, SENDER_NAME, TO_ACCOUNT, RECEIVER_NAME, TRANS_DATE, TRANS_MODE,
            DR_CR, TRANS_ID, NARRATION, PURPOSE, DR_AMOUNT, CURRENCY_NM
        ) VALUES (
            p_FROM_ACCOUNT, p_SENDER_NAME, p_TO_ACCOUNT, p_RECEIVER_NAME, v_trans_date, p_TRANS_MODE,
            'D', p_TRANS_ID, v_narration, p_PURPOSE, p_AMOUNT, p_CURRENCY_NM
        );

        -- Credit receiver
        UPDATE cbs_customer_accounts
           SET available_balance = available_balance + p_AMOUNT,
               current_balance   = current_balance   + p_AMOUNT
         WHERE account_number = p_TO_ACCOUNT;

        SET v_narration = CONCAT(
            'RECEIPT of ', p_AMOUNT, ' ', p_CURRENCY_NM,
            ' to ', p_TO_ACCOUNT, ' (', p_RECEIVER_NAME, ')',
            ' from ', p_FROM_ACCOUNT, ' (', p_SENDER_NAME, ')',
            ' on ', DATE_FORMAT(v_trans_date, '%Y-%m-%d %H:%i:%s.%f'),
            ' via ', p_TRANS_MODE,
            ' for ', p_PURPOSE
        );

        INSERT INTO cbs_Transactions (
            FROM_ACCOUNT, SENDER_NAME, TO_ACCOUNT, RECEIVER_NAME, TRANS_DATE, TRANS_MODE,
            DR_CR, TRANS_ID, NARRATION, PURPOSE, CR_AMOUNT, CURRENCY_NM
        ) VALUES (
            p_FROM_ACCOUNT, p_SENDER_NAME, p_TO_ACCOUNT, p_RECEIVER_NAME, v_trans_date, p_TRANS_MODE,
            'C', p_TRANS_ID, v_narration, p_PURPOSE, p_AMOUNT, p_CURRENCY_NM
        );

        COMMIT;
        SET p_ERROR_MSG = NULL;

    END main_block;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE CBS_GetAccountTransactionHistory(
    IN p_account_number VARCHAR(20),
    IN p_start_date DATE,
    IN p_end_date DATE,
    IN p_sort_direction VARCHAR(4) -- 'ASC' or 'DESC'
)
BEGIN
    -- Validate sort direction (default to DESC if invalid)
    SET @sort_dir = IF(UPPER(p_sort_direction) IN ('ASC','DESC'), 
                     UPPER(p_sort_direction), 
                     'DESC');
    
    SET @sql = CONCAT('
        SELECT 
            CASE WHEN DR_CR = ''D'' THEN RECEIVER_NAME ELSE SENDER_NAME END AS name,
            TRANS_DATE as trans_date,
            TRANS_MODE as trans_mode,
            DR_CR as dr_cr,
            TRANS_ID as trans_id,
            NARRATION as narration,
            PURPOSE as purpose,
            CASE WHEN DR_CR = ''D'' THEN DR_AMOUNT ELSE CR_AMOUNT END AS amount,
            CURRENCY_NM as currency_nm
        FROM cbs_Transactions
        WHERE ((FROM_ACCOUNT = ''', p_account_number, ''' AND DR_CR = ''D'')
               OR (TO_ACCOUNT = ''', p_account_number, ''' AND DR_CR = ''C''))
          AND DATE(TRANS_DATE) BETWEEN ''', p_start_date, ''' AND ''', p_end_date, '''
        ORDER BY TRANS_DATE ', @sort_dir);
    
    PREPARE stmt FROM @sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE CBS_GetProductsForKyc(
    IN p_product_category VARCHAR(50)
)
BEGIN
    SELECT 
        p.product_code,
        p.product_name,
        p.product_type,
        p.description
    FROM 
        cbs_products p
    WHERE 
        p.product_category = p_product_category
        AND p.is_active = TRUE
        AND EXISTS (
            SELECT 1 
            FROM cbs_product_features pf 
            WHERE pf.product_code = p.product_code 
            AND pf.feature_code = 'CLICKKYC' 
            AND pf.is_active = TRUE
        )
    ORDER BY 
        p.product_name;
END$$


CREATE DEFINER=`root`@`localhost` PROCEDURE CBS_GetBranchList()
BEGIN
    SELECT 
        branch_code,
        branch_name
    FROM 
        cbs_branches
    ORDER BY 
        branch_name;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE CBS_GetBranchListWithDetails()
BEGIN
    SELECT 
        branch_code,
        branch_name,
        lat,
        lng
    FROM 
        cbs_branches
    ORDER BY 
        branch_name;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE CBS_GetCustomerById(
    IN p_tax_id VARCHAR(20),
    OUT p_customer_id VARCHAR(20)
)
BEGIN
    SELECT customer_id INTO p_customer_id
    FROM cbs_customers
    WHERE tax_id = p_tax_id
    LIMIT 1;
    
    IF p_customer_id IS NULL THEN
        SET p_customer_id = '';
    END IF;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE CBS_CheckCustomerForProduct(
    IN p_tax_id VARCHAR(20),
    IN p_product_code VARCHAR(20),
    OUT p_customer_id VARCHAR(20)
)
BEGIN
    DECLARE v_temp_customer_id VARCHAR(20);
    
    SELECT customer_id INTO v_temp_customer_id
    FROM cbs_customers
    WHERE tax_id = p_tax_id
    LIMIT 1;
    
    -- If customer exists, check if they have the specified product
    IF v_temp_customer_id IS NOT NULL THEN
        SELECT a.customer_id INTO p_customer_id
        FROM cbs_customer_accounts a
        LEFT JOIN cbs_products p ON a.product_code = p.product_code
        WHERE a.customer_id = v_temp_customer_id
        AND p.product_code = p_product_code
        LIMIT 1;
    END IF;
    
    -- Set empty string if no match found
    IF p_customer_id IS NULL THEN
        SET p_customer_id = '';
    END IF;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE CBS_CreateCustomer(
    IN p_type VARCHAR(20),
    IN p_name VARCHAR(500),
    IN p_title VARCHAR(50),
    IN p_first_name VARCHAR(100),
    IN p_middle_name VARCHAR(100),
    IN p_last_name VARCHAR(100),
    IN p_suffix VARCHAR(50),
    IN p_birth_date DATE,
    IN p_formation_date DATE,
    IN p_tax_id VARCHAR(50),
    IN p_tax_id_type VARCHAR(50),
    IN p_branch_code VARCHAR(50),
    
    -- Address parameters
    IN p_address_type VARCHAR(50),
    IN p_line_1 VARCHAR(500),
    IN p_line_2 VARCHAR(500),
    IN p_line_3 VARCHAR(500),
    IN p_line_4 VARCHAR(500),
    IN p_city VARCHAR(100),
    IN p_state_code VARCHAR(100),
    IN p_zipcode VARCHAR(100),
    IN p_country_code VARCHAR(100),
    
    -- Email parameters
    IN p_email_type VARCHAR(50),
    IN p_email_address VARCHAR(200),
    
    -- Phone parameters
    IN p_phone_type VARCHAR(50),
    IN p_phone_number VARCHAR(200)
)
BEGIN
    DECLARE v_customer_exists VARCHAR(100);
    DECLARE v_new_customer_id VARCHAR(100);
    
    -- Check if customer already exists with this tax ID
    SELECT customer_id INTO v_customer_exists 
    FROM cbs_customers 
    WHERE tax_id = p_tax_id 
    LIMIT 1;
    
    IF v_customer_exists IS NOT NULL THEN
        -- Return existing ID
        SELECT v_customer_exists AS customer_id;
    ELSE
        -- Generate new customer ID
        SELECT CONCAT('1', LPAD(IFNULL(MAX(SUBSTRING(customer_id, 2)), 0) + 1, 8, '0')) 
        INTO v_new_customer_id
        FROM cbs_customers;
        
        -- Insert customer record
        INSERT INTO cbs_customers (
            customer_id, type, name, title, first_name, middle_name, last_name, suffix, 
            birth_date, formation_date, tax_id, tax_id_type, branch_code
        ) VALUES (
            v_new_customer_id, p_type, p_name, p_title, p_first_name, p_middle_name, 
            p_last_name, p_suffix, p_birth_date, p_formation_date, p_tax_id, 
            p_tax_id_type, p_branch_code
        );
        
        -- Insert address
        INSERT INTO cbs_customer_addresses (
            customer_id, type, line_1, line_2, line_3, line_4, 
            city, state_code, zip_code, country_code
        ) VALUES (
            v_new_customer_id, p_address_type, p_line_1, p_line_2, p_line_3, p_line_4, 
            p_city, p_state_code, p_zipcode, p_country_code
        );
        
        -- Insert email
        INSERT INTO cbs_customer_emails (
            customer_id, type, address
        ) VALUES (
            v_new_customer_id, p_email_type, p_email_address
        );
        
        -- Insert phone
        INSERT INTO cbs_customer_phones (
            customer_id, type, number
        ) VALUES (
            v_new_customer_id, p_phone_type, p_phone_number
        );
        
        -- Return new ID
        SELECT v_new_customer_id AS customer_id;
    END IF;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE CBS_OpenAccount(
    IN p_customer_id VARCHAR(100),
    IN p_product_code VARCHAR(50)
)
BEGIN
    DECLARE v_product_category VARCHAR(100);
    DECLARE v_product_type VARCHAR(100);
    DECLARE v_product_name VARCHAR(500);
    DECLARE v_payment_frequency VARCHAR(100);
    DECLARE v_interest_rate DECIMAL(5,2);
    DECLARE v_branch_code VARCHAR(100);
    DECLARE v_account_prefix VARCHAR(3);
    DECLARE v_new_account_number VARCHAR(100);
    
    -- Get product details
    SELECT 
        p.product_category, 
        p.product_type, 
        p.product_name,
        pl.payment_frequency,
        pi.interest_rate
    INTO 
        v_product_category, 
        v_product_type, 
        v_product_name,
        v_payment_frequency,
        v_interest_rate
    FROM cbs_products p
    LEFT JOIN cbs_product_interest pi ON p.product_code = pi.product_code
    LEFT JOIN cbs_product_payment_limit pl ON p.product_code = pl.product_code
    WHERE p.product_code = p_product_code;
    
    -- Get customer's branch code
    SELECT branch_code INTO v_branch_code
    FROM cbs_customers
    WHERE customer_id = p_customer_id;
    
    -- Determine account prefix
    IF v_product_category = 'Deposit' THEN
        IF v_product_type = 'DPS' THEN
            SET v_account_prefix = 'DP';
        ELSE
            SET v_account_prefix = 'SA';
        END IF;
    ELSEIF v_product_category = 'Loan' THEN
        SET v_account_prefix = 'LN';
    END IF;
    
    -- Generate new account number
    INSERT INTO account_sequences (prefix) VALUES (v_account_prefix)
    ON DUPLICATE KEY UPDATE seq = seq + 1;
    
    SELECT seq INTO @seq_num 
    FROM account_sequences 
    WHERE prefix = v_account_prefix;
    
    SET v_new_account_number = CONCAT(v_account_prefix, LPAD(@seq_num, 9, '0'));
    
    -- Insert account record
    INSERT INTO cbs_customer_accounts (
        account_number, 
        customer_id, 
        account_title, 
        product_code, 
        status, 
        relationship, 
        branch_code, 
        opened_date, 
        maturity_date, 
        original_balance, 
        current_balance, 
        available_balance, 
        payment_frequency, 
        interest_rate
    ) VALUES (
        v_new_account_number,
        p_customer_id,
        v_product_name,
        p_product_code,
        'Active',
        'Primary',
        v_branch_code,
        CURDATE(),
        CASE 
            WHEN v_product_type = 'DPS' THEN DATE_ADD(CURDATE(), INTERVAL 5 YEAR)
            WHEN v_product_category = 'Loan' THEN DATE_ADD(CURDATE(), INTERVAL 5 YEAR)
            ELSE NULL
        END,
        0,
        0,
        0,
        v_payment_frequency,
        v_interest_rate
    );
    
    -- Return account number
    SELECT v_new_account_number AS account_number;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE CBS_GLToAccountTransfer(
    IN p_TO_ACCOUNT VARCHAR(15),
    IN p_RECEIVER_NAME VARCHAR(150),
    IN p_AMOUNT_CENTS INT,
    IN p_CURRENCY VARCHAR(10),
    IN p_VENDOR VARCHAR(50),
    OUT p_TRANS_ID VARCHAR(20),
    OUT p_ERROR_MSG VARCHAR(255))
BEGIN
    -- Variables
    DECLARE v_FROM_ACCOUNT VARCHAR(20);
    DECLARE v_SENDER_NAME VARCHAR(150);
    DECLARE v_AMOUNT DECIMAL(18,2);
    DECLARE v_TRANS_DATE DATETIME(3);
    DECLARE v_NARRATION VARCHAR(500);
    DECLARE v_CUSTOMER_EXISTS INT;
    DECLARE v_MASKED_GL_ACCOUNT VARCHAR(20);
    
    -- Error handler
    DECLARE EXIT HANDLER FOR SQLEXCEPTION 
    BEGIN
        ROLLBACK;
        SET p_TRANS_ID = NULL;
        SET p_ERROR_MSG = CONCAT('Transaction failed: ', COALESCE(p_ERROR_MSG, 'Internal error'));
    END;
    
    -- Convert cents to dollars and initialize variables
    SET v_AMOUNT = p_AMOUNT_CENTS / 100.0;
    SET v_TRANS_DATE = NOW(3);
    SET v_SENDER_NAME = UPPER(p_VENDOR);
    
    START TRANSACTION;
    
    main_block: BEGIN
        -- Fetch GL account
        SELECT gl_account_number INTO v_FROM_ACCOUNT
        FROM cbs_gl_account_config
        WHERE vendor_name = UPPER(p_VENDOR)
        AND currency_code = p_CURRENCY;
        
        IF v_FROM_ACCOUNT IS NULL THEN
            SET p_ERROR_MSG = CONCAT('No GL account configured for vendor: ', p_VENDOR, ' and currency: ', p_CURRENCY);
            ROLLBACK;
            LEAVE main_block;
        END IF;
        
        -- Create masked GL account (first 2 and last 3 digits)
        SET v_MASKED_GL_ACCOUNT = CONCAT(
            LEFT(v_FROM_ACCOUNT, 2),
            REPEAT('*', LENGTH(v_FROM_ACCOUNT) - 5),
            RIGHT(v_FROM_ACCOUNT, 3)
        );
        
        -- Check if customer account exists
        SELECT COUNT(*) INTO v_CUSTOMER_EXISTS
        FROM cbs_customer_accounts
        WHERE account_number = p_TO_ACCOUNT;
        
        IF v_CUSTOMER_EXISTS = 0 THEN
            SET p_ERROR_MSG = CONCAT('Customer account not found: ', p_TO_ACCOUNT);
            ROLLBACK;
            LEAVE main_block;
        END IF;
        
        -- Generate transaction ID
        SET p_TRANS_ID = UPPER(SUBSTRING(SHA1(CONCAT(v_TRANS_DATE, RAND())), 1, 20));
        
        -- Debit GL account
        UPDATE cbs_gl_accounts
        SET current_balance = current_balance - v_AMOUNT
        WHERE account_number = v_FROM_ACCOUNT;
        
        -- Insert debit transaction
        SET v_NARRATION = CONCAT(
            'Transfer of ', FORMAT(v_AMOUNT, 2), ' ', p_CURRENCY,
            ' from GL account ', v_MASKED_GL_ACCOUNT, ' (', v_SENDER_NAME, ')',
            ' to account ', p_TO_ACCOUNT, ' (', p_RECEIVER_NAME, ')',
            ' on ', DATE_FORMAT(v_TRANS_DATE, '%Y-%m-%d %H:%i:%s.%f'),
            ' via ', p_VENDOR
        );
        
        INSERT INTO cbs_Transactions (
            FROM_ACCOUNT, SENDER_NAME, TO_ACCOUNT, RECEIVER_NAME, TRANS_DATE, 
            TRANS_MODE, DR_CR, TRANS_ID, NARRATION, PURPOSE, DR_AMOUNT, CURRENCY_NM
        ) VALUES (
            v_FROM_ACCOUNT, v_SENDER_NAME, p_TO_ACCOUNT, p_RECEIVER_NAME, v_TRANS_DATE,
            'TRANSFER', 'D', p_TRANS_ID, v_NARRATION, 'DEPOSIT', v_AMOUNT, p_CURRENCY
        );
        
        -- Credit customer account
        UPDATE cbs_customer_accounts
        SET available_balance = available_balance + v_AMOUNT,
            current_balance = current_balance + v_AMOUNT
        WHERE account_number = p_TO_ACCOUNT;
        
        -- Insert credit transaction
        SET v_NARRATION = CONCAT(
            'Receipt of ', FORMAT(v_AMOUNT, 2), ' ', p_CURRENCY,
            ' to account ', p_TO_ACCOUNT, ' (', p_RECEIVER_NAME, ')',
            ' from GL account ', v_MASKED_GL_ACCOUNT, ' (', v_SENDER_NAME, ')',
            ' on ', DATE_FORMAT(v_TRANS_DATE, '%Y-%m-%d %H:%i:%s.%f'),
            ' via ', p_VENDOR
        );
        
        INSERT INTO cbs_Transactions (
            FROM_ACCOUNT, SENDER_NAME, TO_ACCOUNT, RECEIVER_NAME, TRANS_DATE, 
            TRANS_MODE, DR_CR, TRANS_ID, NARRATION, PURPOSE, CR_AMOUNT, CURRENCY_NM
        ) VALUES (
            v_FROM_ACCOUNT, v_SENDER_NAME, p_TO_ACCOUNT, p_RECEIVER_NAME, v_TRANS_DATE,
            'TRANSFER', 'C', p_TRANS_ID, v_NARRATION, 'DEPOSIT', v_AMOUNT, p_CURRENCY
        );
        
        COMMIT;
        SET p_ERROR_MSG = NULL;
    END main_block;
END$$

DELIMITER ;



