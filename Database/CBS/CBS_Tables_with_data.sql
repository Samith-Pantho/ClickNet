
CREATE TABLE cbs_customers (
    customer_id VARCHAR(100) NOT NULL PRIMARY KEY,
    type VARCHAR(50),
    name VARCHAR(500),
    title VARCHAR(50),
    first_name VARCHAR(100),
    middle_name VARCHAR(100),
    last_name VARCHAR(100),
    suffix VARCHAR(50),
    birth_date DATE,
    formation_date DATE,
    tax_id VARCHAR(50),
    tax_id_type VARCHAR(50),
    branch_code VARCHAR(50)
);

CREATE TABLE cbs_customer_addresses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(100) NOT NULL,
    type VARCHAR(50),
    line_1 VARCHAR(500),
    line_2 VARCHAR(500),
    line_3 VARCHAR(500),
    line_4 VARCHAR(500),
    city VARCHAR(100),
    state_code VARCHAR(100),
    zip_code VARCHAR(100),
    country_code VARCHAR(100)
);

CREATE TABLE cbs_customer_emails (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(100) NOT NULL,
    type VARCHAR(100),
    address VARCHAR(500)
);

CREATE TABLE cbs_customer_phones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(100) NOT NULL,
    type VARCHAR(100),
    number VARCHAR(500)
);

ALTER TABLE cbs_customer_addresses ADD CONSTRAINT fk_cbs_customer_addresses FOREIGN KEY (customer_id) REFERENCES cbs_customers(customer_id);
ALTER TABLE cbs_customer_emails ADD CONSTRAINT fk_cbs_customer_emails FOREIGN KEY (customer_id) REFERENCES cbs_customers(customer_id);
ALTER TABLE cbs_customer_phones ADD CONSTRAINT fk_cbs_customer_phones FOREIGN KEY (customer_id) REFERENCES cbs_customers(customer_id);

 CREATE TABLE cbs_products (
    product_code VARCHAR(20) NOT NULL PRIMARY KEY,
    product_category VARCHAR(50) NOT NULL,  -- e.g., DEPOSIT, LOAN, CARD
    product_type VARCHAR(50) NOT NULL,      -- e.g., SAVINGS, CURRENT, FIXED_DEPOSIT
    product_name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    effective_date DATE NOT NULL,
    expiry_date DATE,
    created_by VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated_by VARCHAR(50),
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_product_category (product_category),
    INDEX idx_product_type (product_type),
    INDEX idx_active_products (is_active)
);

CREATE TABLE cbs_product_interest (
    product_code VARCHAR(20) NOT NULL PRIMARY KEY,
    interest_rate DECIMAL(5,2) NOT NULL,
    interest_rate_type VARCHAR(20) NOT NULL,  -- FIXED, VARIABLE, TIERED
    compounding_frequency VARCHAR(20),        -- DAILY, MONTHLY, QUARTERLY, YEARLY
    min_term_days INT,                        -- For term products
    max_term_days INT,                        -- For term products
    
    FOREIGN KEY (product_code) REFERENCES cbs_products(product_code)
);

CREATE TABLE cbs_product_payment_limit (
    product_code VARCHAR(20) NOT NULL PRIMARY KEY,
    payment_frequency VARCHAR(20),          -- DAILY, WEEKLY, MONTHLY, QUARTERLY, YEARLY
    min_amount_of_payments_allowed DECIMAL(18,2),       
    no_of_payments_allowed INT,      
    max_amount_of_payments_allowed DECIMAL(18,2),
    
    FOREIGN KEY (product_code) REFERENCES cbs_products(product_code)
);

CREATE TABLE cbs_product_fees (
    product_code VARCHAR(20) NOT NULL PRIMARY KEY,
    monthly_fee DECIMAL(18,2) DEFAULT 0.00,
    annual_fee DECIMAL(18,2) DEFAULT 0.00,
    withdrawal_fee DECIMAL(18,2) DEFAULT 0.00,
    late_payment_fee DECIMAL(18,2) DEFAULT 0.00,
    maintenance_fee DECIMAL(18,2) DEFAULT 0.00,
    
    FOREIGN KEY (product_code) REFERENCES cbs_products(product_code)
);

CREATE TABLE cbs_product_features (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    product_code VARCHAR(20) NOT NULL,
    feature_code VARCHAR(50) NOT NULL,
    feature_name VARCHAR(100) NOT NULL,
    feature_description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_code) REFERENCES cbs_products(product_code),
    UNIQUE KEY uk_product_feature (product_code, feature_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE cbs_customer_accounts (
    account_number VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(100) NOT NULL,
    account_title VARCHAR(100),
    product_code VARCHAR(20),
    status VARCHAR(20),
    relationship VARCHAR(50),
    branch_code VARCHAR(10),
    opened_date DATE,
    maturity_date DATE,
    original_balance DECIMAL(18,2) NOT NULL,
    current_balance DECIMAL(18,2) NOT NULL,
    available_balance DECIMAL(18,2) NOT NULL,
    payment_frequency VARCHAR(20),
    interest_rate DECIMAL(5,2),
    
    FOREIGN KEY (customer_id) REFERENCES cbs_customers(customer_id),
    FOREIGN KEY (product_code) REFERENCES cbs_products(product_code)
);

CREATE TABLE cbs_Transactions (
    FROM_ACCOUNT VARCHAR(15) NOT NULL,
    SENDER_NAME VARCHAR(150) NOT NULL,
    TO_ACCOUNT VARCHAR(15) NOT NULL,
    RECEIVER_NAME VARCHAR(150) NOT NULL,
    TRANS_DATE DATETIME(3) NOT NULL,
    TRANS_MODE ENUM('TRANSFER', 'CASH') NOT NULL DEFAULT 'TRANSFER',
    DR_CR ENUM('D', 'C') NOT NULL,
    TRANS_ID VARCHAR(20) NOT NULL,
    NARRATION VARCHAR(500) NOT NULL,
    PURPOSE VARCHAR(50) NOT NULL,
    DR_AMOUNT DECIMAL(18,2) NOT NULL DEFAULT 0.0,
    CR_AMOUNT DECIMAL(18,2) NOT NULL DEFAULT 0.0,
    CURRENCY_NM VARCHAR(10) NOT NULL DEFAULT 'USD',
    PRIMARY KEY (DR_CR, TRANS_ID)
);


CREATE TABLE cbs_branches (
    branch_code VARCHAR(10) NOT NULL PRIMARY KEY,
    branch_name VARCHAR(100) NOT NULL,
    lat VARCHAR(100) NOT NULL,
    lng VARCHAR(100) NOT NULL
);

CREATE TABLE account_sequences (
    prefix VARCHAR(3) PRIMARY KEY,
    seq BIGINT NOT NULL DEFAULT 1
);

CREATE TABLE cbs_gl_accounts (
    account_number VARCHAR(20) PRIMARY KEY,
    account_name VARCHAR(100) NOT NULL,
    account_type VARCHAR(50) NOT NULL,  -- ASSET, LIABILITY, EQUITY, INCOME, EXPENSE
    currency_code VARCHAR(10) NOT NULL DEFAULT 'USD',
    current_balance DECIMAL(18,2) NOT NULL DEFAULT 0.00,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE cbs_gl_account_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_name VARCHAR(50) NOT NULL,  -- Stripe, PayPal, etc.
    gl_account_number VARCHAR(20) NOT NULL,
    currency_code VARCHAR(10) NOT NULL DEFAULT 'USD',
    is_default BOOLEAN NOT NULL DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (gl_account_number) REFERENCES cbs_gl_accounts(account_number),
    UNIQUE KEY uk_vendor_currency (vendor_name, currency_code)
);

INSERT INTO `cbs_customers`(`customer_id`, `type`, `name`, `title`, `first_name`, `middle_name`, `last_name`, `suffix`, `birth_date`, `formation_date`, `tax_id`, `tax_id_type`, `branch_code`) VALUES ('100000001','INDIVIDUAL','Samith Binda Pantho','Mr.','Samith Binda','','Pantho','','1997-12-03','2025-07-13','741852963','Passport','0031');
INSERT INTO `cbs_customers`(`customer_id`, `type`, `name`, `title`, `first_name`, `middle_name`, `last_name`, `suffix`, `birth_date`, `formation_date`, `tax_id`, `tax_id_type`, `branch_code`) VALUES ('100000002','INDIVIDUAL','Ashfak Haidar','Mr.','Ashfak','','Haidar','','1998-10-23','2025-07-13','852147963','Passport','0031');

INSERT INTO `cbs_customer_addresses`(`id`, `customer_id`, `type`, `line_1`, `line_2`, `line_3`, `line_4`, `city`, `state_code`, `zip_code`, `country_code`) VALUES ('1','100000001','Home','Vaajakatu 7','','','','Tampere','NA','33720','FI');
INSERT INTO `cbs_customer_addresses`(`id`, `customer_id`, `type`, `line_1`, `line_2`, `line_3`, `line_4`, `city`, `state_code`, `zip_code`, `country_code`) VALUES ('2','100000001','Work','Orivedenkatu 87','','','','Tampere','NA','33720','FI');
INSERT INTO `cbs_customer_addresses`(`id`, `customer_id`, `type`, `line_1`, `line_2`, `line_3`, `line_4`, `city`, `state_code`, `zip_code`, `country_code`) VALUES ('3','100000002','Home','Alaverstaanraitti 5','','','','Tampere','NA','33720','FI');
INSERT INTO `cbs_customer_addresses`(`id`, `customer_id`, `type`, `line_1`, `line_2`, `line_3`, `line_4`, `city`, `state_code`, `zip_code`, `country_code`) VALUES ('4','100000002','Work','Laiturikatu 1,','','','','Tampere','NA','33720','FI');

INSERT INTO `cbs_customer_emails`(`id`, `customer_id`, `type`, `address`) VALUES ('1','100000001','primary','samith.pantho@hotmail.com');
INSERT INTO `cbs_customer_emails`(`id`, `customer_id`, `type`, `address`) VALUES ('2','100000002','primary','samithbindapantho@hotmail.com');

INSERT INTO `cbs_customer_phones`(`id`, `customer_id`, `type`, `number`) VALUES ('1','100000001','primary','+358417434881');
INSERT INTO `cbs_customer_phones`(`id`, `customer_id`, `type`, `number`) VALUES ('2','100000002','primary','+358417434881');

INSERT INTO `cbs_products` (`product_code`, `product_category`, `product_type`, `product_name`, `description`, `is_active`, `effective_date`, `created_by`)
VALUES
('DPS-MONTHLY', 'Deposit', 'DPS', 'Monthly DPS Plan', 
'Our Monthly Deposit Plan (DPS) is a disciplined savings program designed to help you build wealth over a 5-year period. Perfect for individuals looking for a structured savings approach with attractive returns.
- 5-year monthly deposit savings plan
- Competitive interest rates higher than regular savings
- Fixed monthly installment amounts
- Maturity payout with accrued interest
- Partial withdrawal options available with terms
- Auto-renewal option at maturity
- Tax benefits as per government regulations', 
TRUE, '2020-01-01', 'SYSTEM'),

('LN-PERSONAL', 'Loan', 'Personal Loan', 'Home Renovation Loan', 
'Transform your living space with our flexible Home Renovation Loan, offering competitive rates and quick approvals for your improvement projects.
- Loan tenure up to 5 years
- Competitive interest rates
- No collateral required
- Quick approval process (typically within 48 hours)
- Flexible repayment options (monthly, quarterly)
- Loan amounts from $1,000 to $50,000
- Option to prepay with minimal charges
- Insurance coverage option available', 
TRUE, '2020-01-01', 'SYSTEM'),

('LN-AUTO', 'Loan', 'Auto Loan', 'Car Loan', 
'Drive your dream car sooner with our Auto Loan featuring competitive rates and flexible terms for both new and pre-owned vehicles.
- Financing for new and used vehicles
- Loan terms up to 5 years
- Competitive interest rates based on credit score
- Up to 90% financing available
- Fast approval process
- Flexible repayment schedules
- Option to include insurance in monthly payments
- No prepayment penalties after 1 year', 
TRUE, '2020-01-01', 'SYSTEM'),

('SAV-REGULAR', 'Deposit', 'Savings', 'Regular Savings', 
'The foundation of your financial journey, our Regular Savings account offers convenience and accessibility for everyday banking needs.
- No minimum balance requirement
- Free online banking access
- Monthly interest credited to account
- Free debit card included
- Mobile check deposit
- 24/7 customer support
- Overdraft protection option
- Linked to checking account for transfers', 
TRUE, '2020-01-01', 'SYSTEM'),

('SAV-SMART', 'Deposit', 'Savings', 'Smart Saver', 
'Maximize your savings potential with our Smart Saver account that rewards higher balances with premium interest rates.
- Higher interest rates for balances above $5,000
- Tiered interest structure
- No monthly maintenance fees
- Free ATM transactions nationwide
- Mobile banking with check deposit
- Automatic savings plan options
- Linked to checking account for overdraft protection
- Quarterly bonus interest for consistent deposits', 
TRUE, '2020-01-01', 'SYSTEM'),

('SAV-SENIOR', 'Deposit', 'Savings', 'Senior Savings', 
'We value our senior customers with this specialized account offering enhanced benefits tailored for retirement lifestyles.
- Special interest rates for customers 60+
- No monthly service charges
- Free checks
- Higher withdrawal limits
- Free notary services
- Discounts on safe deposit boxes
- Priority customer service
- Medicare/insurance premium payment services', 
TRUE, '2020-01-01', 'SYSTEM'),

('SAV-WOMEN', 'Deposit', 'Savings', 'Women\'s Savings', 
'Empowering women financially with special benefits and services designed to support their unique financial goals.
- Special benefits for female account holders
- Higher interest rates for first 6 months
- Free financial planning consultations
- Discounts on loan processing fees
- Special overdraft facilities
- Women entrepreneur business support services
- Health insurance discounts
- Exclusive networking and financial literacy events', 
TRUE, '2020-01-01', 'SYSTEM'),

('SAV-STUDENT', 'Deposit', 'Savings', 'Student Savings', 
'Building healthy financial habits early, our Student Savings account helps young adults manage money while studying.
- No minimum balance requirements
- No monthly fees for students under 25
- Special interest rates
- Free online and mobile banking
- Budgeting tools and financial education resources
- Parental monitoring options
- Discounts on student loans
- Automatic conversion to regular savings after graduation', 
TRUE, '2020-01-01', 'SYSTEM');

INSERT INTO `cbs_product_interest` (`product_code`, `interest_rate`, `interest_rate_type`, `compounding_frequency`)
VALUES
('DPS-MONTHLY', 5.00, 'FIXED', 'M'),
('LN-PERSONAL', 10.50, 'FIXED', 'M'),
('LN-AUTO', 9.00, 'FIXED', 'M'),
('SAV-REGULAR', 2.50, 'VARIABLE', 'D'),
('SAV-SMART', 2.70, 'VARIABLE', 'D'),
('SAV-SENIOR', 3.00, 'VARIABLE', 'D'),
('SAV-WOMEN', 2.80, 'VARIABLE', 'D'),
('SAV-STUDENT', 2.00, 'FIXED', 'D');

INSERT INTO `cbs_product_payment_limit` (`product_code`, `payment_frequency`, `min_amount_of_payments_allowed`, `no_of_payments_allowed`, `max_amount_of_payments_allowed`)
VALUES
('DPS-MONTHLY', 'M', 100, 10, 1000),
('LN-PERSONAL', 'M', 1000, 10, 10000),
('LN-AUTO', 'M', 750, 10, 7500),
('SAV-REGULAR', 'D', 10, 20, 10000),
('SAV-SMART', 'D', 10, 20, 10000),
('SAV-SENIOR', 'D', 10, 20, 10000),
('SAV-WOMEN', 'D', 10, 20, 10000),
('SAV-STUDENT', 'D', 10, 20, 10000);

INSERT INTO `cbs_product_features` (`product_code`, `feature_code`, `feature_name`, `feature_description`, `is_active`) VALUES
('SAV-REGULAR', 'CLICKKYC', 'Online eKYC', 'Online eKYC and open account', TRUE);
INSERT INTO `cbs_product_features` (`product_code`, `feature_code`, `feature_name`, `feature_description`, `is_active`) VALUES
('SAV-SMART', 'CLICKKYC', 'Online eKYC', 'Online eKYC and open account', TRUE);
INSERT INTO `cbs_product_features` (`product_code`, `feature_code`, `feature_name`, `feature_description`, `is_active`) VALUES
('SAV-STUDENT', 'CLICKKYC', 'Online eKYC', 'Online eKYC and open account', TRUE);


-- Updated insert statements for cbs_customer_accounts
INSERT INTO `cbs_customer_accounts` (`account_number`, `customer_id`, `account_title`, `product_code`, `status`, `relationship`, `branch_code`, `opened_date`, `maturity_date`, `original_balance`, `current_balance`, `available_balance`, `payment_frequency`, `interest_rate`) VALUES
('DP100000001', '100000001', 'Monthly DPS Plan', 'DPS-MONTHLY', 'Active', 'Primary', '001', '2023-07-01', '2028-07-01', 60000, 12000, 12000, 'M', 5.00),
('LN100000001', '100000001', 'Home Renovation Loan', 'LN-PERSONAL', 'Active', 'Primary', '001', '2022-06-01', '2027-06-01', 500000, 350000, 350000, 'M', 10.50),
('LN100000002', '100000001', 'Car Loan', 'LN-AUTO', 'Active', 'Primary', '001', '2021-03-01', '2026-03-01', 300000, 120000, 120000, 'M', 9.00),
('SA100000001', '100000001', 'Regular Savings', 'SAV-REGULAR', 'Active', 'Primary', '001', '2023-01-01', NULL, 15000, 15000, 15000, 'D', 2.50),
('SA100000002', '100000001', 'Smart Saver', 'SAV-SMART', 'Active', 'Primary', '001', '2023-02-01', NULL, 18000, 18000, 18000, 'D', 2.70),
('SA100000003', '100000001', 'Senior Savings', 'SAV-SENIOR', 'Active', 'Primary', '001', '2023-03-01', NULL, 20000, 20000, 20000, 'D', 3.00),
('SA100000004', '100000001', 'Women\'s Savings', 'SAV-WOMEN', 'Active', 'Primary', '001', '2023-04-01', NULL, 16000, 16000, 16000, 'D', 2.80),
('SA100000005', '100000001', 'Student Savings', 'SAV-STUDENT', 'Active', 'Primary', '001', '2023-05-01', NULL, 15500, 15500, 15500, 'D', 2.00),
('SA100000006', '100000002', 'Regular Savings', 'SAV-REGULAR', 'Active', 'Primary', '002', '2023-01-15', NULL, 6000, 6000, 6000, 'D', 2.50),
('SA100000007', '100000002', 'Smart Saver', 'SAV-SMART', 'Active', 'Primary', '002', '2023-02-15', NULL, 7500, 7500, 7500, 'D', 2.80);


INSERT INTO cbs_branches (branch_code, branch_name, lat, lng) VALUES
('001','Helsinki Branch, Helsinki, Uusimaa', 60.1695, 24.9354),
('002','Espoo Branch, Espoo, Uusimaa', 60.2055, 24.6559),
('003','Vantaa Branch, Vantaa, Uusimaa', 60.2934, 25.0378),
('004','Tampere Branch, Tampere, Pirkanmaa', 61.4916, 23.8358),
('005','Turku Branch, Turku, Southwest Finland', 60.4518, 22.2666),
('006','Oulu Branch, Oulu, North Ostrobothnia', 65.0121, 25.4651),
('007','Jyväskylä Branch, Jyväskylä, Central Finland', 62.2426, 25.7473),
('008','Lahti Branch, Lahti, Päijänne Tavastia', 60.9827, 25.6615),
('009','Kuopio Branch, Kuopio, North Savo', 62.8924, 27.6770),
('010','Joensuu Branch, Joensuu, North Karelia', 62.6010, 29.7633),
('011','Lappeenranta Branch, Lappeenranta, South Karelia', 61.0583, 28.1889),
('012','Hämeenlinna Branch, Hämeenlinna, Tavastia Proper', 61.0008, 24.4662),
('013','Vaasa Branch, Vaasa, Ostrobothnia', 63.0951, 21.6161),
('014','Rovaniemi Branch, Rovaniemi, Lapland', 66.5039, 25.7294),
('015','Seinäjoki Branch, Seinäjoki, South Ostrobothnia', 62.7902, 22.8400),
('016','Kajaani Branch, Kajaani, Kainuu', 64.2254, 27.7304),
('017','Porvoo Branch, Porvoo, Uusimaa', 60.3939, 25.6634),
('018','Mikkeli Branch, Mikkeli, South Savo', 61.6876, 27.2733),
('019','Kouvola Branch, Kouvola, Kymenlaakso', 60.8660, 26.7055),
('020','Kotka Branch, Kotka, Kymenlaakso', 60.4667, 26.9450),
('021','Järvenpää Branch, Järvenpää, Uusimaa', 60.4747, 25.0894),
('022','Hyvinkää Branch, Hyvinkää, Uusimaa', 60.6339, 24.8698),
('023','Nurmijärvi Branch, Nurmijärvi, Uusimaa', 60.5079, 24.7726),
('024','Salo Branch, Salo, Southwest Finland', 60.3833, 23.1333),
('025','Rauma Branch, Rauma, Southwest Finland', 61.1286, 21.5111),
('026','Kemi Branch, Kemi, Lapland', 65.7362, 24.5636),
('027','Raahe Branch, Raahe, North Ostrobothnia', 64.6863, 24.4795),
('028','Iisalmi Branch, Iisalmi, North Savo', 63.5610, 27.1903),
('029','Lohja Branch, Lohja, Uusimaa', 60.2481, 24.0613),
('030','Savonlinna Branch, Savonlinna, South Savo', 61.8691, 28.8867),
('031','Kangasala Branch, Kangasala, Pirkanmaa', 61.4833, 24.1167),
('032','Nokia Branch, Nokia, Pirkanmaa', 61.4667, 23.3833),
('033','Kerava Branch, Kerava, Uusimaa', 60.4069, 25.1000),
('034','Kauniainen Branch, Kauniainen, Uusimaa', 60.2234, 24.7356),
('035','Lappeenranta Branch 2, Lappeenranta, South Karelia', 61.0585, 28.1888),
('036','Kaarina Branch, Kaarina, Southwest Finland', 60.4446, 22.3332),
('037','Uusikaupunki Branch, Uusikaupunki, Southwest Finland', 60.8000, 21.4289),
('038','Imatra Branch, Imatra, South Karelia', 61.1667, 28.7667),
('039','Siilinjärvi Branch, Siilinjärvi, North Savo', 63.0569, 27.6644),
('040','Kristiinankaupunki Branch, Kristiinankaupunki, Ostrobothnia', 62.2640, 21.4185),
('041','Korsholm Branch, Korsholm, Ostrobothnia', 63.1655, 21.6169),
('042','Närpes Branch, Närpes, Ostrobothnia', 62.4395, 21.3324),
('043','Pori Branch, Pori, Satakunta', 61.4850, 21.7973),
('044','Kauhajoki Branch, Kauhajoki, South Ostrobothnia', 62.3789, 22.4841),
('045','Mäntsälä Branch, Mäntsälä, Uusimaa', 60.5849, 25.4807),
('046','Jämsä Branch, Jämsä, Central Finland', 61.8694, 25.2052),
('047','Vihti Branch, Vihti, Uusimaa', 60.3505, 24.2603),
('048','Lohja Branch 2, Lohja, Uusimaa', 60.2461, 24.0604),
('049','Kemiönsaari Branch, Kemiönsaari, Southwest Finland', 60.2020, 22.0200),
('050','Tornio Branch, Tornio, Lapland', 65.8460, 24.1476),
('051','Kankaanpää Branch, Kankaanpää, Satakunta', 61.7763, 22.9739),
('052','Raisio Branch, Raisio, Southwest Finland', 60.4649, 22.1605),
('053','Sipoo Branch, Sipoo, Uusimaa', 60.3667, 25.2800),
('054','Lempäälä Branch, Lempäälä, Pirkanmaa', 61.3333, 23.7667),
('055','Kempele Branch, Kempele, North Ostrobothnia', 64.9244, 25.5053),
('056','Pietarsaari Branch, Pietarsaari, Ostrobothnia', 63.6728, 22.7015),
('057','Hamina Branch, Hamina, Kymenlaakso', 60.5681, 27.1921),
('058','Järvenpää Branch 2, Järvenpää, Uusimaa', 60.4730, 25.0900),
('059','Kemi Branch 2, Kemi, Lapland', 65.7361, 24.5637),
('060','Ylöjärvi Branch, Ylöjärvi, Pirkanmaa', 61.5630, 23.6421),
('061','Joutsa Branch, Joutsa, Central Finland', 61.8127, 26.0606),
('062','Savitaipale Branch, Savitaipale, South Karelia', 61.1786, 27.0276),
('063','Pukkila Branch, Pukkila, Uusimaa', 60.6615, 25.7432),
('064','Taivalkoski Branch, Taivalkoski, North Ostrobothnia', 65.8620, 28.2810),
('065','Uurainen Branch, Uurainen, Central Finland', 62.1083, 25.8061),
('066','Vehmaa Branch, Vehmaa, Southwest Finland', 60.7356, 22.7590),
('067','Kuhmo Branch, Kuhmo, Kainuu', 64.1306, 29.8511),
('068','Laitila Branch, Laitila, Southwest Finland', 60.7887, 22.8882),
('069','Rautalampi Branch, Rautalampi, Central Finland', 62.7015, 26.0672),
('070','Kivijärvi Branch, Kivijärvi, Central Finland', 63.1134, 25.4704),
('071','Pyhäjärvi Branch, Pyhäjärvi, North Ostrobothnia', 64.0246, 26.6354),
('072','Ikaalinen Branch, Ikaalinen, Pirkanmaa', 61.8161, 23.5287),
('073','Lohja Branch 3, Lohja, Uusimaa', 60.2430, 24.0618),
('074','Kontiolahti Branch, Kontiolahti, North Karelia', 62.7683, 29.8800),
('075','Tervo Branch, Tervo, North Savo', 62.7622, 27.8368),
('076','Taipalsaari Branch, Taipalsaari, South Karelia', 61.2061, 28.7937),
('077','Mäntyharju Branch, Mäntyharju, South Savo', 61.3673, 26.9047),
('078','Muonio Branch, Muonio, Lapland', 67.9391, 23.9277),
('079','Karijoki Branch, Karijoki, South Ostrobothnia', 62.2821, 21.1691),
('080','Pirkkala Branch, Pirkkala, Pirkanmaa', 61.4430, 23.6500),
('081','Ruovesi Branch, Ruovesi, Pirkanmaa', 61.7294, 24.0467),
('082','Korsnäs Branch, Korsnäs, Ostrobothnia', 62.5266, 21.3687),
('083','Ylivieska Branch, Ylivieska, North Ostrobothnia', 64.0591, 24.5025),
('084','Hanko Branch, Hanko, Uusimaa', 59.8315, 22.9586),
('085','Keitele Branch, Keitele, North Savo', 62.9870, 26.4089),
('086','Kurikka Branch, Kurikka, South Ostrobothnia', 62.5551, 22.3989),
('087','Pirkkala Branch 2, Pirkkala, Pirkanmaa', 61.4379, 23.6469),
('088','Kittilä Branch, Kittilä, Lapland', 67.6617, 24.8461),
('089','Askola Branch, Askola, Uusimaa', 60.5176, 25.6100),
('090','Virolahti Branch, Virolahti, Kymenlaakso', 60.5653, 27.5533),
('091','Säkylä Branch, Säkylä, Satakunta', 61.3958, 22.2592),
('092','Sodankylä Branch, Sodankylä, Lapland', 67.4167, 26.5917),
('093','Kauhava Branch, Kauhava, South Ostrobothnia', 63.0647, 23.1344),
('094','Savukoski Branch, Savukoski, Lapland', 67.4333, 28.3167),
('095','Kaustinen Branch, Kaustinen, Central Ostrobothnia', 63.8344, 23.7499),
('096','Tervo Branch 2, Tervo, North Savo', 62.7633, 27.8325),
('097','Liperi Branch, Liperi, North Karelia', 62.5354, 29.2693),
('098','Pello Branch, Pello, Lapland', 66.8923, 23.7472),
('099','Jämsä Branch 2, Jämsä, Central Finland', 61.8675, 25.2081),
('100','Kannonkoski Branch, Kannonkoski, Central Finland', 62.9431, 25.1831)
('101','Banani Branch, Banani, Dhaka', 23.792223133754813, 90.3985670342989);

INSERT INTO account_sequences (prefix, seq) VALUES 
('DP', 6),
('LN', 7),
('SA', 12)
ON DUPLICATE KEY UPDATE seq = VALUES(seq);

INSERT INTO cbs_gl_accounts (account_number, account_name, account_type, currency_code, current_balance, description)
VALUES 
('GL100000001', 'Stripe Settlement Account', 'ASSET', 'USD', 1000000.00, 'Primary settlement account for Stripe transactions'),
('GL100000002', 'PayPal Settlement Account', 'ASSET', 'USD', 500000.00, 'Primary settlement account for PayPal transactions'),
('GL200000001', 'Cash in Vault', 'ASSET', 'USD', 2000000.00, 'Physical cash held in vault'),
('GL300000001', 'Fees Income', 'INCOME', 'USD', 0.00, 'Income from transaction fees'),
('GL400000001', 'Suspense Account', 'LIABILITY', 'USD', 0.00, 'Temporary holding for unresolved transactions');

INSERT INTO cbs_gl_account_config (vendor_name, gl_account_number, currency_code, description)
VALUES 
('STRIPE', 'GL100000001', 'USD', 'Primary Stripe settlement account for USD transactions'),
('PAYPAL', 'GL100000002', 'USD', 'Primary PayPal settlement account for USD transactions');