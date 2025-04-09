CREATE DATABASE pyqt_mdk_11;
USE pyqt_mdk_11;

CREATE TABLE staff (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    salary DECIMAL(10, 2),
    is_veteran BOOLEAN DEFAULT FALSE
);

CREATE TABLE children (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    birth_date DATE,
    staff_id INT,
    FOREIGN KEY (staff_id) REFERENCES staff(id)
);

CREATE TABLE type_operation (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255)
);

CREATE TABLE type_payment (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    percent DECIMAL(10, 2)
);


CREATE TABLE payment (
    id INT PRIMARY KEY AUTO_INCREMENT,
    payment_date DATE DEFAULT CURRENT_DATE,
    amount DECIMAL(10, 2),
    staff_id INT,
    type_operation_id INT,
    FOREIGN KEY (type_operation_id) REFERENCES type_operation(id),
    FOREIGN KEY (staff_id) REFERENCES staff(id)
);


CREATE TABLE payment_type_payment (
    id INT PRIMARY KEY AUTO_INCREMENT,
    payment_id INT,
    type_payment_id INT,
    FOREIGN KEY (payment_id) REFERENCES payment(id),
    FOREIGN KEY (type_payment_id) REFERENCES type_payment(id)
);

CREATE TABLE Proc_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    payment_id INT,
    log_message VARCHAR(255),
    log_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


DELIMITER $$
CREATE TRIGGER log_payment_after_insert
AFTER INSERT ON payment
FOR EACH ROW
BEGIN
    DECLARE staff_name VARCHAR(255);
    DECLARE type_operation_name VARCHAR(255);
    SELECT name INTO staff_name FROM staff WHERE id = NEW.staff_id;
    SELECT name INTO type_operation_name FROM type_operation WHERE id = NEW.type_operation_id;
    INSERT INTO Proc_log (payment_id, log_message)
    VALUES (
        NEW.id,
        CONCAT('Начисление для сотрудника ', staff_name,
               ' по операции "', type_operation_name,
               '" создано. Сумма: ', NEW.amount,
               '. Дата начисления: ', NEW.payment_date)
    );
END$$
DELIMITER ;



INSERT INTO staff (name, salary, is_veteran) VALUES
('Иванов Иван Иванович', 50000.00, FALSE),
('Петров Петр Петрович', 60000.00, TRUE),
('Сидоров Сергей Сергеевич', 45000.00, FALSE);

INSERT INTO children (name, birth_date, staff_id) VALUES
('Алексей Иванов', '2010-05-15', 1),
('Мария Петрова', '2012-03-20', 3),
('Дмитрий Сидоров', '2014-07-10', 3);

INSERT INTO type_operation (name) VALUES
('Расчёт налоговой базы'),
('Расчёт НДФЛ');

INSERT INTO type_payment (name, percent) VALUES
('Наличие ребёнка', 13.00),
('Наличие ветеранства', 10.00);


DELIMITER $$

CREATE FUNCTION calculate_tax(
    p_staff_id INT,
    p_tax_base BOOLEAN,
    p_ndfl BOOLEAN,
    p_veteran BOOLEAN,
    p_children BOOLEAN
) RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE base_salary DECIMAL(10, 2);
    DECLARE tax_base DECIMAL(10, 2);
    DECLARE ndfl_value DECIMAL(10, 2);
    DECLARE children_count INT DEFAULT 0;
    DECLARE veteran_discount DECIMAL(5, 2) DEFAULT 0.00;
    DECLARE children_discount DECIMAL(5, 2) DEFAULT 0.00;

    -- Получение базовой зарплаты
    SELECT salary INTO base_salary FROM staff WHERE id = p_staff_id;

    -- Учет льготы ветерана
    IF p_veteran THEN
        SELECT percent INTO veteran_discount FROM type_payment WHERE name = 'Наличие ветеранства';
    END IF;

    -- Учет льготы за детей
    IF p_children THEN
        SELECT COUNT(*) INTO children_count FROM children WHERE staff_id = p_staff_id;
        IF children_count > 0 THEN
            SELECT percent INTO children_discount FROM type_payment WHERE name = 'Наличие ребёнка';
            SET children_discount = children_discount * children_count;
        END IF;
    END IF;

    -- Расчет налоговой базы
    SET tax_base = base_salary * (1 - (veteran_discount + children_discount) / 100);

    -- Расчет НДФЛ
    SET ndfl_value = tax_base * 0.13;

    -- Возврат нужного значения
    IF p_tax_base THEN
        RETURN ROUND(tax_base, 2);
    ELSEIF p_ndfl THEN
        RETURN ROUND(ndfl_value, 2);
    ELSE
        RETURN NULL;
    END IF;
END$$
DELIMITER ;


DELIMITER $$
CREATE FUNCTION record_tax(
    p_staff_id INT,
    p_tax_base BOOLEAN,
    p_ndfl BOOLEAN,
    p_veteran BOOLEAN,
    p_children BOOLEAN
) RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE calculated_value DECIMAL(10,2);
    DECLARE type_operation_id INT;
    DECLARE new_payment_id INT;
        SET calculated_value = calculate_tax(p_staff_id, p_tax_base, p_ndfl, p_veteran, p_children);

    IF p_tax_base THEN
        SET type_operation_id = 1;
    ELSEIF p_ndfl THEN
        SET type_operation_id = 2;
    ELSE
        RETURN NULL;
    END IF;

    INSERT INTO payment (amount, staff_id, type_operation_id)
    VALUES (calculated_value, p_staff_id, type_operation_id);

    SET new_payment_id = LAST_INSERT_ID();
    IF p_veteran THEN
        INSERT INTO payment_type_payment (payment_id, type_payment_id)
        VALUES (new_payment_id, 2);
    END IF;
    IF p_children THEN
        INSERT INTO payment_type_payment (payment_id, type_payment_id)
        VALUES (new_payment_id, 1);
    END IF;
    RETURN calculated_value;
END$$
DELIMITER ;

