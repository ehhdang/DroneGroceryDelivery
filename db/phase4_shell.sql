SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));

DROP PROCEDURE IF EXISTS hash_passwords;
DELIMITER //
CREATE PROCEDURE hash_passwords ()
BEGIN
	update users set Pass=MD5(Pass);
END //
DELIMITER;

DROP PROCEDURE IF EXISTS login;
DELIMITER //
CREATE PROCEDURE login (
	IN i_username VARCHAR(40),
    IN i_password VARCHAR(40)
)
BEGIN
	DROP TABLE IF EXISTS login_result;
    CREATE TABLE login_result (
		authenticated INT,
        roles VARCHAR(40)
    );
    SELECT count(*) INTO @authenticated FROM users WHERE Username = i_username AND Pass = MD5(i_password);
    IF @authenticated = 0 THEN
		INSERT INTO login_result (authenticated, roles) VALUES (@authenticated, NULL);
	ELSE
		IF (select count(*) from admin where admin.Username = i_username) = 1 then
			INSERT INTO login_result (authenticated, roles) VALUES (@authenticated, "admin");
		ELSEIF (select count(*) from customer where customer.Username = i_username) = 1 then
			INSERT INTO login_result (authenticated, roles) VALUES (@authenticated, "customer");
		ELSEIF (select count(*) from manager where manager.Username = i_username) = 1 then
			INSERT INTO login_result (authenticated, roles) VALUES (@authenticated, "manager");
		ELSEIF (select count(*) from drone_tech where drone_tech.Username = i_username) = 1 then
			INSERT INTO login_result (authenticated, roles) VALUES (@authenticated, "drone tech");
		ELSE
			INSERT INTO login_result (authenticated, roles) VALUES (@authenticated, NULL);
		END IF;
	END IF;
END //
DELIMITER ;

-- ID: 2a
-- Author: hdang40
-- Name: register_customer
DROP PROCEDURE IF EXISTS register_customer;
DELIMITER //
CREATE PROCEDURE register_customer(
	   IN i_username VARCHAR(40),
       IN i_password VARCHAR(40),
	   IN i_fname VARCHAR(40),
       IN i_lname VARCHAR(40),
       IN i_street VARCHAR(40),
       IN i_city VARCHAR(40),
       IN i_state VARCHAR(2),
	   IN i_zipcode CHAR(5),
       IN i_ccnumber VARCHAR(40),
	   IN i_cvv CHAR(3),
       IN i_exp_date DATE
)
main: BEGIN
	-- check if zipcode has length of 5
    if char_length(i_zipcode) <> 5 then leave main; end if;
    -- if already in users (either an admin, manager, or drone tech), then should not be in customer
    if (select count(*) from USERS where Username = i_username) >= 1 then leave main; end if;
	insert into USERS (Username, Pass, FirstName, LastName, Street, City, State, Zipcode)
		values (i_username, MD5(i_password), i_fname, i_lname, i_street, i_city, i_state, i_zipcode);
    insert into CUSTOMER (Username, CcNumber, CVV, EXP_DATE)
		values (i_username, i_ccnumber, i_cvv, i_exp_date);
END //
DELIMITER ;

-- ID: 2b
-- Author: hdang40
-- Name: register_employee
DROP PROCEDURE IF EXISTS register_employee;
DELIMITER //
CREATE PROCEDURE register_employee(
	   IN i_username VARCHAR(40),
       IN i_password VARCHAR(40),
	   IN i_fname VARCHAR(40),
       IN i_lname VARCHAR(40),
       IN i_street VARCHAR(40),
       IN i_city VARCHAR(40),
       IN i_state VARCHAR(2),
       IN i_zipcode CHAR(5)
)
main: BEGIN       
	insert into USERS (Username, Pass, FirstName, LastName, Street, City, State, Zipcode)
		values (i_username, MD5(i_password), i_fname, i_lname, i_street, i_city, i_state, i_zipcode);
	insert into EMPLOYEE (Username) values (i_username);
END //
DELIMITER ;

-- ID: 4a
-- Author: asmith457
-- Name: admin_create_grocery_chain
DROP PROCEDURE IF EXISTS admin_create_grocery_chain;
DELIMITER //
CREATE PROCEDURE admin_create_grocery_chain(
        IN i_grocery_chain_name VARCHAR(40)
)
BEGIN
	insert into chain (ChainName) values (i_grocery_chain_name);
END //
DELIMITER ;

-- ID: 5a
-- Author: ahatcher8
-- Name: admin_create_new_store
DROP PROCEDURE IF EXISTS admin_create_new_store;
DELIMITER //
CREATE PROCEDURE admin_create_new_store(
    	IN i_store_name VARCHAR(40),
        IN i_chain_name VARCHAR(40),
    	IN i_street VARCHAR(40),
    	IN i_city VARCHAR(40),
    	IN i_state VARCHAR(2),
    	IN i_zipcode CHAR(5)
)
main: BEGIN
	if (select count(*) from store where ChainName=i_chain_name and ZipCode=i_zipcode) >= 1 then leave main; end if;
	insert into store (StoreName, ChainName, Street, City, State, ZipCode)
    values (i_store_name, i_chain_name, i_street, i_city, i_state, i_zipcode);
END //
DELIMITER ;

-- ID: 6a
-- Author: ahatcher8
-- Name: admin_create_drone
DROP PROCEDURE IF EXISTS admin_create_drone;
DELIMITER //
CREATE PROCEDURE admin_create_drone(
	   IN i_drone_id INT,
       IN i_zip CHAR(5),
       IN i_radius INT,
       IN i_drone_tech VARCHAR(40)
)
main: BEGIN
	if (select count(*) from drone_tech, store
		where drone_tech.StoreName = store.StoreName
		and drone_tech.ChainName = store.ChainName
        and drone_tech.Username = i_drone_tech
        and store.Zipcode = i_zip) = 0 then leave main; end if;
	insert into drone (ID, DroneStatus, Zip, Radius, DroneTech)
    values (i_drone_id, "Available", i_zip, i_radius, i_drone_tech);
END //
DELIMITER ;

-- ID: 7a
-- Author: ahatcher8
-- Name: admin_create_item
DROP PROCEDURE IF EXISTS admin_create_item;
DELIMITER //
CREATE PROCEDURE admin_create_item(
        IN i_item_name VARCHAR(40),
        IN i_item_type VARCHAR(40),
        IN i_organic VARCHAR(3),
        IN i_origin VARCHAR(40)
)
main: BEGIN
	if (select count(ItemName) from item where ItemName=i_item_name) >= 1 then leave main; end if;
    if find_in_set(i_item_type, 'Dairy,Bakery,Meat,Produce,Personal Care,Paper Goods,Beverages,Other') = 0
		then leave main; end if;
	if find_in_set(i_organic, 'Yes,No') = 0 then leave main; end if;
    insert into item (ItemName, ItemType, Origin, Organic)
		values (i_item_name, i_item_type, i_origin, i_organic);
END //
DELIMITER ;

-- ID: 8a
-- Author: dvaidyanathan6
-- Name: admin_view_customers
DROP PROCEDURE IF EXISTS admin_view_customers;
DELIMITER //
CREATE PROCEDURE admin_view_customers(
	   IN i_first_name VARCHAR(40),
       IN i_last_name VARCHAR(40)
)
BEGIN
	drop table if exists admin_view_customers_result;
    create table admin_view_customers_result (
		Username varchar(40),
        FullName varchar(80),
        Address varchar(200)
    );
	insert into admin_view_customers_result (Username, FullName, Address)
	select users.Username, concat(users.FirstName, ' ', users.LastName), concat(users.Street, ',', users.City, ',', users.State, users.Zipcode)
	from users natural join customer
	where (i_first_name is null or users.FirstName = i_first_name) 
    and (i_last_name is null or users.LastName = i_last_name);
END //
DELIMITER ;

-- ID: 9a
-- Author: dvaidyanathan6
-- Name: manager_create_chain_item
DROP PROCEDURE IF EXISTS manager_create_chain_item;
DELIMITER //
CREATE PROCEDURE manager_create_chain_item(
        IN i_chain_name VARCHAR(40),
    	IN i_item_name VARCHAR(40),
    	IN i_quantity INT, 
    	IN i_order_limit INT,
    	IN i_PLU_number INT,
    	IN i_price DECIMAL(4, 2)
)
main: BEGIN
-- Type solution below
	-- the 1st IF statement is unnecessary because 2 different chain items can have same name and chain, but different PLU Number
	-- if(select count(ChainItemName) from CHAIN_ITEM where ChainItemName=i_item_name and ChainName=i_chain_name)>0 then leave main; end if;
	-- if(select count(ItemName) from ITEM where ItemName=i_item_name)<1 then leave main; end if;
	Insert into CHAIN_ITEM (ChainItemName, ChainName, PLUNumber, Orderlimit, Quantity, Price) 
		values (i_item_name, i_chain_name, i_PLU_number, i_order_limit, i_quantity, i_price);
-- End of solution
END //
DELIMITER ;

-- ID: 10a
-- Author: dvaidyanathan6
-- Name: manager_view_drone_technicians
DROP PROCEDURE IF EXISTS manager_view_drone_technicians;
DELIMITER //
CREATE PROCEDURE manager_view_drone_technicians(
	   IN i_chain_name VARCHAR(40),
       IN i_drone_tech VARCHAR(40),
       IN i_store_name VARCHAR(40)
)
main:BEGIN
-- Type solution below
	-- if(select count(Username) from DRONE_TECH where Username=i_drone_tech and StoreName=i_store_name)<1 then leave main; end if;
	drop table if exists manager_view_drone_technicians_result;
	create table manager_view_drone_technicians_result (
		Username VARCHAR(40),
        FullName VARCHAR(40),
        Location VARCHAR(40)
    );

	insert into manager_view_drone_technicians_result(Username, FullName, Location)
	select USERS.Username, concat(FirstName, " ", LastName) as FullName, StoreName as Location 
    from DRONE_TECH INNER JOIN USERS on USERS.Username=DRONE_TECH.Username 
    where (StoreName=i_store_name or i_store_name is null) 
    and (users.Username = i_drone_tech or i_drone_tech is null) 
    and ChainName = i_chain_name;
-- End of solution
END //
DELIMITER ;

-- ID: 10b
-- Author: dvaidyanathan6
-- Name: manager_update_drone_technicians
DROP PROCEDURE IF EXISTS manager_reassign_drone_technicians;
DELIMITER //
CREATE PROCEDURE manager_reassign_drone_technicians(
	   IN i_chain_name VARCHAR(40),
       IN i_drone_tech VARCHAR(40),
       IN i_store_name VARCHAR(40)
)
main:BEGIN
-- Type solution below
	-- if store_name is not changed, then exit the procedure
	if (select count(*) from drone_tech natural join store where Username=i_drone_tech and ChainName=i_chain_name
    and StoreName=i_store_name) >= 1 then leave main; end if;
	-- update drone_tech table
    update drone_tech set StoreName=i_store_name, ChainName=i_chain_name where Username=i_drone_tech;
	-- update the zipcode of drone
	update drone set Zip = (select ZipCode from drone_tech natural join store where Username=i_drone_tech)
	where DroneTech=i_drone_tech;
-- End of solution
END //
DELIMITER ;

-- ID: 11a
-- Author: vtata6
-- Name: manager_view_drones
DROP PROCEDURE IF EXISTS manager_view_drones;
DELIMITER //
CREATE PROCEDURE manager_view_drones(
	   IN i_mgr_username varchar(40), 
	   IN i_drone_id int, IN drone_radius int
)
main: BEGIN
-- Type solution below	   
	-- if(select count(Username) from MANAGER where Username=i_mgr_username)=0 then leave main; end if;
	-- if(select ID from DRONE INNER JOIN DRONE_TECH on DroneTech=DRONE_TECH.Username where ChainName=(select ChainName from Manager where Username=i_mgr_username))=0 then leave main; end if;  
	drop table if exists manager_view_drones_result;
	create table manager_view_drones_result (
		ID INT ,
        Operator VARCHAR(40) ,
        Radius INT ,
        Zip char(5) ,
        DroneStatus VARCHAR(20) 
    ); 
	insert into  manager_view_drones_result(ID, Operator, Radius, Zip, DroneStatus)
		select ID, DroneTech as Operator, Radius, Zip, DroneStatus
		from DRONE join DRONE_TECH on DRONE.DroneTech = DRONE_TECH.Username
		where (ID=i_drone_id or i_drone_id is null) and (Radius >= drone_radius or drone_radius is null)
		and DRONE_TECH.ChainName=(select ChainName from Manager where Username=i_mgr_username);
-- End of solution
END //
DELIMITER ;

-- ID: 12a
-- Author: vtata6
-- Name: manager_manage_stores
DROP PROCEDURE IF EXISTS manager_manage_stores;
DELIMITER //
CREATE PROCEDURE manager_manage_stores(
	   IN i_mgr_username varchar(50), 
	   IN i_storeName varchar(50), 
	   IN i_minTotal int, 
	   IN i_maxTotal int
)
BEGIN
-- Type solution below
    drop table if exists manager_manage_stores_result;
    create table manager_manage_stores_result (
		StoreName varchar(40),
        Address varchar(200),
        Orders int,
        Employees int,
        Total varchar(11)
    );
	drop view if exists orders_map_to_total;
	create view orders_map_to_total as
		select OrderID, round(sum(subtotal), 2) as total
		from (
			select OrderID, ItemName, contains.ChainName, contains.PLUNumber, contains.Quantity, Price,
			round(contains.Quantity * Price, 2) as subtotal  
			from contains, chain_item
			where contains.ItemName = chain_item.ChainItemName
			and contains.chainName = chain_item.ChainName
			and contains.PLUNumber = chain_item.PLUNumber
		) as temp group by OrderID;

	drop view if exists drone_tech_to_store;
	create view drone_tech_to_store as
		select manager.Username as mgr, drone_tech.Username as DroneTech, drone_tech.ChainName, 
		drone_tech.StoreName, concat(store.Street,' ', store.City, ', ', store.State,' ', store.Zipcode) as address
		from manager, drone_tech, store
		where drone_tech.ChainName = manager.ChainName
		and drone_tech.StoreName = store.StoreName
		and drone_tech.ChainName = store.ChainName;

	drop view if exists orders_map_to_store;
	create view orders_map_to_store as
		select orders.ID as OrderID, orders.DroneID, drone.DroneTech, mgr, temp.ChainName, temp.StoreName, temp.address
		from orders, drone, drone_tech_to_store as temp
		where orders.DroneID = drone.ID
		and drone.DroneTech = temp.DroneTech;
	
    insert into manager_manage_stores_result (Storename, Address, Orders, Employees, Total)
	select A.StoreName, A.address, A.Orders, B.Employees, A.Total
	from (
		select ChainName, StoreName, address, count(orders_map_to_total.OrderID) as Orders, round(sum(total), 2) as Total
		from orders_map_to_total join orders_map_to_store
		where orders_map_to_total.OrderID = orders_map_to_store.OrderID
		group by ChainName, StoreName 
	) as A, (
		select ChainName, StoreName, mgr, count(DroneTech) + 1 as Employees
		from drone_tech_to_store group by ChainName, StoreName
	) as B
	where A.ChainName = B.ChainName and A.StoreName = B.StoreName
	and (mgr = i_mgr_username) and (A.StoreName = i_storeName or i_storeName is null)
	and (A.Total >= i_minTotal or i_minTotal is null)
	and (A.Total <= i_maxTotal or i_maxTotal is null);

-- End of solution
END //
DELIMITER ;

-- ID: 13a
-- Author: vtata6
-- Name: customer_change_credit_card_information
DROP PROCEDURE IF EXISTS customer_change_credit_card_information;
DELIMITER //
CREATE PROCEDURE customer_change_credit_card_information(
	   IN i_custUsername varchar(40), 
	   IN i_new_cc_number varchar(19), 
	   IN i_new_CVV int, 
	   IN i_new_exp_date date
)
main: BEGIN
-- Type solution below
	if i_new_exp_date< curdate() then leave main; end if;
	update CUSTOMER set CcNumber=i_new_cc_number, CVV=i_new_CVV, EXP_DATE=i_new_exp_date  
    where USERNAME=i_custUsername;
-- End of solution
END //
DELIMITER ;

-- ID: 14a
-- Author: hdang40
-- Name: customer_view_order_history
DROP PROCEDURE IF EXISTS customer_view_order_history;
DELIMITER //
CREATE PROCEDURE customer_view_order_history(
	   IN i_username VARCHAR(40),
       IN i_orderid INT
)
main: BEGIN
	drop table if exists customer_view_order_history_result;
	create table customer_view_order_history_result (
		total_amount varchar(20),
        total_items int,
        orderdate varchar(12),
        droneID int,
        dronetech varchar(30),
        orderstatus varchar(20)
    );
    drop view if exists order_sale_view;
	create view order_sale_view as
		select contains.OrderID, sum(contains.Quantity) as total_items,
		round(sum(contains.Quantity * chain_item.Price),2) as total_amount
		from contains, chain_item
		where contains.ItemName = chain_item.ChainItemName
		and contains.ChainName = chain_item.ChainName
		and contains.PLUNumber = chain_item.PLUNumber
		group by contains.OrderID;
	
    drop view if exists order_drone_view;
	create view order_drone_view as
		select orders.CustomerUsername, orders.ID, OrderDate, DroneID, DroneTech, OrderStatus 
		from orders left outer join drone
		on orders.DroneID = drone.ID;
	
    insert into customer_view_order_history_result (total_amount, total_items, orderdate, droneID, dronetech, orderstatus)
		select total_amount, total_items, OrderDate, DroneID, DroneTech, OrderStatus 
		from order_drone_view, order_sale_view
		where order_drone_view.ID = order_sale_view.OrderID
		and CustomerUsername=i_username and OrderID = i_orderid;
END //
DELIMITER ;

-- ID: 15a
-- Author: hdang40
-- Name: customer_view_store_items
DROP PROCEDURE IF EXISTS customer_view_store_items;
DELIMITER //
CREATE PROCEDURE customer_view_store_items(
	   IN i_username VARCHAR(40),
       IN i_chain_name VARCHAR(40),
       IN i_store_name VARCHAR(40),
       IN i_item_type VARCHAR(40)
)
BEGIN
	drop table if exists customer_view_store_items_result;
    create table customer_view_store_items_result (
		chainItemName varchar(30),
        orderLimit int
    );
    
    drop view if exists store_items_view;
    create view store_items_view as
		select ChainItemName, Orderlimit, ItemType, store.StoreName, store.ChainName, Zipcode 
		from item, chain_item, store 
		where item.ItemName = chain_item.ChainItemName
		and chain_item.ChainName = store.ChainName;
    
	insert into customer_view_store_items_result (chainItemName, orderLimit)
	select ChainItemName, Orderlimit
	from store_items_view
	where StoreName = i_store_name and ChainName = i_chain_name
	and exists (
		select * from users where users.Zipcode = store_items_view.Zipcode
		and Username = i_username
	) and (i_item_type is null or ItemType = i_item_type);

END //
DELIMITER ;

-- ID: 15b
-- Author: hdang40
-- Name: customer_select_items
DROP PROCEDURE IF EXISTS customer_select_items;
DELIMITER //
CREATE PROCEDURE customer_select_items(
	    IN i_username VARCHAR(40),
    	IN i_chain_name VARCHAR(40),
    	IN i_store_name VARCHAR(40),
    	IN i_item_name VARCHAR(40),
    	IN i_quantity INT
)
main: BEGIN
	if i_quantity = 0 then leave main; end if;
    
    if (select count(*) from store, users
	where Username = i_username and StoreName = i_store_name 
    and ChainName = i_chain_name and users.Zipcode = store.Zipcode) <= 0 then leave main; end if;
    
	if (select count(*) from chain_item 
	where ChainItemName = i_item_name and ChainName = i_chain_name
	and i_quantity <= Orderlimit and i_quantity <= Quantity) <= 0 then leave main; end if;
    
    if (select count(ID) from orders where OrderStatus = "Creating" and CustomerUsername = i_username) < 1 then
		insert into orders (OrderStatus, OrderDate, CustomerUsername, DroneID)
			values ("Creating", curdate(), i_username, null);
	end if;
    insert into contains (OrderID, ItemName, ChainName, PLUNumber, Quantity) values 
		(
		(select ID from orders where OrderStatus = "Creating" and CustomerUsername = i_username and DroneID is null),
        i_item_name, i_chain_name,
		(select PLUNumber from chain_item where ChainItemName=i_item_name and ChainName=i_chain_name),
		i_quantity
		);
    
END //
DELIMITER ;

-- ID: 16a
-- Author: hdang40
-- Name: customer_review_order
DROP PROCEDURE IF EXISTS customer_review_order;
DELIMITER //
CREATE PROCEDURE customer_review_order(
	   IN i_username VARCHAR(40)
)
BEGIN
	drop table if exists customer_review_order_result;
    create table customer_review_order_result (
		ItemName varchar(50),
        Quantity int,
        Price decimal(9,2)
    );
    insert into customer_review_order_result (ItemName, Quantity, Price)
		select contains.ItemName, contains.Quantity, chain_item.Price from orders, contains, chain_item
		where orders.ID = contains.OrderID and contains.ItemName = chain_item.ChainItemName 
		and contains.ChainName = chain_item.ChainName and contains.PLUNumber = chain_item.PLUNumber
		and CustomerUsername=i_username and OrderStatus="Creating";
END //
DELIMITER ;

-- ID: 16b
-- Author: hdang40
-- Name: customer_update_order
DROP PROCEDURE IF EXISTS customer_update_order;
DELIMITER //
CREATE PROCEDURE customer_update_order(
	   IN i_username VARCHAR(40),
       IN i_item_name VARCHAR(40),
       IN i_quantity INT
)
main: BEGIN
	select ID into @orderID from orders where CustomerUsername=i_username
		and OrderStatus="Creating" and DroneID is null;
	if i_quantity <= 0 then delete from contains where OrderID = @orderID and ItemName = i_item_name;
	else update contains set Quantity = i_quantity where OrderID = @orderID and ItemName = i_item_name;
    end if;
END //
DELIMITER ;

-- ID: 16c
-- Author: hdang40
-- Name: customer_update_order
DROP PROCEDURE IF EXISTS customer_place_order;
DELIMITER //
CREATE PROCEDURE customer_place_order(
	   IN i_username VARCHAR(40)
)
main: BEGIN
	select ID into @orderID from orders where CustomerUsername=i_username
		and OrderStatus="Creating" and DroneID is null;
	if (select count(OrderID) from contains where OrderID=@orderID) <= 0 then leave main; end if;
    # update order status to pending
    update orders set OrderStatus="Pending", OrderDate=curdate() where ID=@orderID;
    # subtract the quantity from the chain_item quantity
    update chain_item join contains on chain_item.ChainItemName=contains.ItemName
	and chain_item.PLUNumber=contains.PLUNumber and chain_item.ChainName=contains.ChainName
	set chain_item.Quantity=chain_item.Quantity-contains.Quantity
	where contains.OrderID=@orderID;
END //
DELIMITER ;

-- ID: 16d
-- Author: hdang40
-- Name: customer_cancel_order
DROP PROCEDURE IF EXISTS customer_cancel_order;
DELIMITER //
CREATE PROCEDURE customer_cancel_order(
	   IN i_username VARCHAR(40)
)
main: BEGIN
	select ID into @orderID from orders where CustomerUsername=i_username
		and OrderStatus="Creating" and DroneID is null;
	delete from contains where OrderID=@orderID;
    delete from orders where ID=@orderID;
END //
DELIMITER ;

-- ID: 16e
-- Author: hdang40
-- Name: customer_has_order
DROP PROCEDURE IF EXISTS customer_find_created_order;
DELIMITER //
CREATE PROCEDURE customer_find_created_order(
	   IN i_username VARCHAR(40)
)
main: BEGIN
	drop table if exists customer_find_created_order_result;
    create table customer_find_created_order_result (
		ChainName varchar(40),
        StoreName varchar(40)
    );
    insert into customer_find_created_order_result
    select ChainName,StoreName from store
		where ChainName=(select ChainName from contains join orders on contains.OrderID=orders.ID
		where OrderStatus="Creating" and CustomerUsername=i_username group by ChainName)
		and ZipCode=(select ZipCode from users where Username=i_username);
END //
DELIMITER ;

-- ID: 17a
-- Author: jkomskis3
-- Name: drone_technician_view_order_history
DROP PROCEDURE IF EXISTS drone_technician_view_order_history;
DELIMITER //
CREATE PROCEDURE drone_technician_view_order_history(
        IN i_username VARCHAR(40),
    	IN i_start_date DATE,
    	IN i_end_date DATE
)
BEGIN
	drop table if exists drone_technician_view_order_history_result;
    create table drone_technician_view_order_history_result (
		ID varchar(40),
        Operator varchar(40),
        Date varchar(20),
        DroneID varchar(40),
        Status varchar(40),
        Total varchar(20)
    );
    
	drop view if exists orders_map_to_total;
	create view orders_map_to_total as
	select OrderID, OrderStatus, OrderDate, DroneID, CustomerUsername,ChainName, round(sum(subtotal), 2) as total, users.ZipCode as OrderZipcode
	from (
		select OrderID, ItemName, contains.ChainName, contains.PLUNumber, contains.Quantity, Price,
		round(contains.Quantity * Price, 2) as subtotal  
		from contains, chain_item
		where contains.ItemName = chain_item.ChainItemName
		and contains.chainName = chain_item.ChainName
		and contains.PLUNumber = chain_item.PLUNumber
	) as temp join orders on temp.OrderID = orders.ID
    join users on orders.CustomerUsername=users.Username
    group by OrderID, ChainName;
	
    drop view if exists drone_full_view;
	create view drone_full_view as
	select ID as DroneID, DroneTech, concat(FirstName, ' ', LastName)  as Operator,store.ChainName,store.ZipCode
	from drone join users on DroneTech = users.Username
	join drone_tech on DroneTech=drone_tech.Username
	join store on drone_tech.ChainName=store.ChainName and drone_tech.StoreName=store.StoreName;
	
    insert into drone_technician_view_order_history_result (ID, Operator, Date, DroneID, Status, Total)
	select OrderID, Operator, OrderDate, drone_full_view.DroneID, OrderStatus, total 
	from orders_map_to_total left outer join drone_full_view
	on orders_map_to_total.DroneID = drone_full_view.DroneID
	where OrderStatus <> "Creating"
	and OrderZipcode in (
		select ZipCode from drone_full_view
		where DroneTech=i_username
	) and orders_map_to_total.ChainName in (
		select ChainName from drone_full_view
		where DroneTech=i_username
	) and (i_end_date is null or OrderDate <= i_end_date )
		and (i_start_date is null or OrderDate >= i_start_date);
END //
DELIMITER ;

-- ID: 17b
-- Author: agoyal89
-- Name: dronetech_assign_order
DROP PROCEDURE IF EXISTS dronetech_assign_order;
DELIMITER //
CREATE PROCEDURE dronetech_assign_order(
	   IN i_username VARCHAR(40),
       IN i_droneid INT,
       IN i_status VARCHAR(20),
       IN i_orderid INT
)
BEGIN
	IF (SELECT OrderStatus FROM orders WHERE i_orderid = ID)  = 'Pending' AND (SELECT DroneID FROM orders WHERE i_orderid = ID) IS NULL AND i_status != 'Pending' 
    AND (SELECT DroneStatus FROM drone WHERE i_droneid = ID) = 'Available'
    THEN UPDATE orders, drone SET DroneID = i_droneid, OrderStatus = i_status, DroneStatus = 'Busy' WHERE i_orderid = ORDERS.ID AND i_droneid = DRONE.ID; END IF;
    
	IF (SELECT OrderStatus FROM orders WHERE i_orderid = ID)  != 'Pending' AND (SELECT DroneID FROM orders WHERE i_orderid = ID) = i_droneid
    THEN UPDATE orders SET OrderStatus = i_status  WHERE i_orderid = ID; END IF; 
END //
DELIMITER ;

-- ID: 18a
-- Author: agoyal89
-- Name: dronetech_order_details
DROP PROCEDURE IF EXISTS dronetech_order_details;
DELIMITER //
CREATE PROCEDURE dronetech_order_details(
	   IN i_username VARCHAR(40),
       IN i_orderid VARCHAR(40)
)
BEGIN
	drop table if exists dronetech_order_details_result;
	create table dronetech_order_details_result (
		Customer_Name VARCHAR(40),
        Order_ID INT,
        Total_Amount DECIMAL(9, 2),
        Total_Items INT, 
        Date_of_Purchase Date, 
        Drone_ID INT, 
		Store_Associate VARCHAR(40),
        Order_Status VARCHAR(20), 
		Address VARCHAR(200)
    );
    
	drop view if exists order_total;
	create view order_total as
	select OrderID, round(sum(contains.Quantity),2) as Total_Items, round(sum(contains.Quantity*chain_item.Price),2) as Total_Amount 
	from contains join chain_item on contains.ItemName=chain_item.ChainItemName
	and contains.ChainName=chain_item.ChainName and contains.PLUNumber=chain_item.PLUNumber
	group by OrderID;
    
    drop view if exists customer_summary;
	create view customer_summary as
	select Username as CustomerUsername, concat(FirstName, ' ', LastName) as CustomerName, 
	concat(Street,' ',City,' ',State,' ',Zipcode) as Address from users natural join customer;
	
    drop view if exists dronetech_summary;
	create view dronetech_summary as
	select Username as DronetechUsername, concat(Firstname,' ',Lastname) as StoreAssociate, drone.ID as DroneID
	from users natural join drone_tech join drone on drone_tech.Username=drone.DroneTech;
    
    insert into dronetech_order_details_result
    select CustomerName, OrderID,Total_Amount,Total_Items,OrderDate,orders.DroneID,StoreAssociate,OrderStatus,Address
	from orders left outer join order_total on orders.ID=order_total.OrderID 
	left join customer_summary on orders.CustomerUsername=customer_summary.CustomerUsername
	left join dronetech_summary on orders.DroneID=dronetech_summary.DroneID
    where OrderID=i_orderid;
    
END //
DELIMITER ;

-- ID: 18b
-- Author: agoyal89
-- Name: dronetech_order_items
DROP PROCEDURE IF EXISTS dronetech_order_items;
DELIMITER //
CREATE PROCEDURE dronetech_order_items(
        IN i_username VARCHAR(40),
    	IN i_orderid INT
)
BEGIN
	drop table if exists dronetech_order_items_result;
	create table dronetech_order_items_result (
        Item VARCHAR(20),
        Count INT
    );
    
	INSERT INTO dronetech_order_items_result(Item, Count)
    SELECT ItemName AS Item, Quantity AS Count
	FROM contains
	WHERE (OrderID = i_orderid OR i_orderid IS NULL);
END //
DELIMITER ;

-- ID: 19a
-- Author: agoyal89
-- Name: dronetech_assigned_drones
DROP PROCEDURE IF EXISTS dronetech_assigned_drones;
DELIMITER //
CREATE PROCEDURE dronetech_assigned_drones(
        IN i_username VARCHAR(40),
    	IN i_droneid INT,
    	IN i_status VARCHAR(20)
)
BEGIN
	DROP TABLE IF EXISTS dronetech_assigned_drones_result;
	CREATE TABLE dronetech_assigned_drones_result (
		DroneID int,
        DroneStatus varchar(40),
        Radius int
    );
    INSERT INTO dronetech_assigned_drones_result
		SELECT ID, DroneStatus, Radius
        FROM drone
        WHERE DroneTech = i_username AND (ID = i_droneID OR i_droneID is null) 
        AND (DroneStatus = i_status OR i_status is null OR i_status = 'All');
END //
DELIMITER ;

