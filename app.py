from flask import Flask, request, url_for, render_template, redirect
from flask_mysqldb import MySQL
import simplejson as json
from datetime import datetime,date

app = Flask(__name__)
mysql = MySQL(app)
url = 'http://127.0.0.1:5000/'

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "Xu@n20Quy03$"
app.config["MYSQL_PORT"] = 3306
app.config["MYSQL_DB"] = "grocery_drone_delivery"


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/logout", methods=["GET"])
def logout():
    user={
        "username":None,
        "role":None,
        "login":False
    }
    f=open("user.json",'w')
    f.write(json.dumps(user))
    return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        form = request.form
        username = form['username']
        password = form['password']
        cur = mysql.connection.cursor()
        cur.execute("CALL login(%s, %s)", (username, password))
        cur.execute("Select * from login_result")
        cur.connection.commit()
        table = cur.fetchall() 
        cur.close() 
        # table[0][0] indicate status, table[0][1] indicate role (drone tech, manager, customer, admin, or null)
        if table[0][0] == 0:
            return render_template('userNoExist.html')
        else:
            f = open('user.json', 'r')
            user = json.load(f)
            f.close()
            if table[0][1] == "drone tech":
                user['username'] = username
                user['role'] = "drone tech"
                user['login'] = True
                f = open('user.json', 'w')
                f.write(json.dumps(user))
                f.close()
                return redirect(url_for('dronetech'))
            elif table[0][1] == "customer":
                user['username'] = username
                user['role'] = "customer"
                user['login'] = True
                f = open('user.json', 'w')
                f.write(json.dumps(user))
                f.close()
                return redirect(url_for('customer'))
            elif table[0][1] == "manager":
                user['username'] = username
                user['role'] = "manager"
                user['login'] = True
                f = open('user.json', 'w')
                f.write(json.dumps(user))
                f.close()
                return redirect(url_for('manager'))
            elif table[0][1] == "admin":
                user['username'] = username
                user['role'] = "admin"
                user['login'] = True
                f = open('user.json', 'w')
                f.write(json.dumps(user))
                f.close()
                return redirect(url_for('admin'))
            else:
                return "Something is wrong, and we need to fix it!"
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET"])
def register():
    return render_template("register.html")

@app.route("/customerregister", methods=["GET", "POST"])
def customer_register():
    if request.method == "POST":
        form = request.form
        fname = form['fname']
        lname = form['lname']
        street = form['street']
        city = form['city']
        username = form['username']
        state = form['state']
        password = form['password'].strip()
        zipCode = form['zip']
        confirmedPassword = form['confirm-pass'].strip()
        ccNumber = form['ccNumber']
        cvv = form['cvv']
        expDate = form['expDate']
        
        cur = mysql.connection.cursor()
        message = None
        cur.execute("select count(*) from users where Username=%s",(username,))
        cur.connection.commit()
        numCustomers=cur.fetchall()
        if password != confirmedPassword:
            message = "Registration fails. Password mismatches!"
        elif numCustomers[0][0] == 1:
            message = "Registration fails. Username is not available!"
        else:
            cur.execute("CALL register_customer(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", \
                (username, password, fname, lname, street, city, state, zipCode, ccNumber, cvv, expDate))
            cur.connection.commit()
            cur.close()
            return redirect(url_for('login'))
        
        return render_template("customerregister.html", message=message)
    else:
        return render_template("customerregister.html", message=None)

@app.route("/employeeregister", methods=["GET", "POST"])
def employee_register():
    if request.method=="POST":
        form = request.form
        fname = form['fname']
        lname = form['lname']
        street = form['street']
        city = form['city']
        username = form['username']
        state = form['state']
        password = form['password'].strip()
        zipCode = form['zip']
        confirmedPassword = form['confirm-pass'].strip()
        chain = form['chainName'].strip()
        store = form['storeName'].strip()
        
        cur = mysql.connection.cursor()
        message = None
        cur.execute("select count(*) from users where Username=%s",(username,))
        cur.connection.commit()
        numCustomers=cur.fetchall()
        cur.execute("select count(*) from chain where ChainName=%s",(chain,))
        cur.connection.commit()
        numChains=cur.fetchall()
        numStores=None
        if len(store) != 0:
            cur.execute("select count(*) from store where StoreName=%s and ChainName=%s",(store,chain))
            cur.connection.commit()
            numStores=cur.fetchall()
        cur.execute("select count(*) from manager where ChainName=%s",(chain,))
        cur.connection.commit()
        numManagers=cur.fetchall()
        if password != confirmedPassword:
            message = "Registration fails. Password mismatches!"
        elif numCustomers[0][0] == 1:
            message = "Registration fails. Username is not available!"
        elif numChains[0][0] == 0:
            message = "Registration fails. Chain does not exist!"
        elif numStores and numStores[0][0] == 0:
            message="Registration fails. The combination of store and chain does not exist!"
        elif numManagers[0][0] == 1:
            message="Registration fails. The input chain has already had a manager!"
        else:
            cur = mysql.connection.cursor()
            cur.execute("CALL register_employee(%s, %s, %s, %s, %s, %s, %s, %s)", \
                (username, password, fname, lname, street, city, state, zipCode))
            if (len(store) == 0):
                cur.execute("Insert into manager values (%s, %s)", (username, chain))
            else:
                cur.execute("Insert into drone_tech values (%s, %s, %s)", (username, store, chain))
            cur.connection.commit()
            cur.close()
            return redirect(url_for('login'))
        return render_template("employeeregister.html", message=message)
    else:
        return render_template("employeeregister.html", message=None)

@app.route('/admin', methods=['GET'])
def admin():
    return render_template('admin.html', error=None)

@app.route('/adminItem', methods=['GET', 'POST'])
def admin_create_item():
    message=None
    if request.method=="POST":
        form = request.form
        item = form['name']
        itemType = form['type']
        organic = form['organic']
        origin = form['origin']
        cur = mysql.connection.cursor()
        cur.execute("select count(*) from item where ItemName=%s",(item,))
        cur.connection.commit()
        numItems=cur.fetchall()
        if numItems[0][0] != 0:
            message="Insertion fails. Item has already existed in the database."
        elif itemType=="empty" or organic=="empty":
            message="Insertion fails. Please select Type and Organic."
        else:
            cur.execute("CALL admin_create_item(%s, %s, %s, %s)", \
                (item, itemType, organic, origin))
            cur.connection.commit()
            cur.close()
    return render_template('adminItem.html', message=message)

@app.route('/adminDrone', methods=['GET', 'POST'])
def admin_create_drone():
    cur = mysql.connection.cursor()
    cur.execute("select Zipcode, Username from drone_tech natural join store")
    cur.connection.commit()
    table = cur.fetchall()
    employees = dict()
    for row in table:
        if row[0] not in employees:
            employees[row[0]] = []
        employees[row[0]].append(row[1])
    cur.execute("select max(ID) from drone")
    cur.connection.commit()
    droneID = cur.fetchall()[0][0]+1
    cur.close()

    if request.method=="POST":
        form = request.form
        zipcode = form['zip']
        radius = form['radius']
        associate = form['associate']
        if zipcode!="Please Select" and associate!="Please Select":
            cur = mysql.connection.cursor()
            cur.execute("CALL admin_create_drone(%s, %s, %s, %s)", \
                (droneID, zipcode, radius, associate))
            cur.connection.commit()
            cur.close()
        return redirect(url_for('admin_create_drone'))
    else:
        return render_template('adminDrone.html', error=None, employees=employees, droneID=droneID)

@app.route('/adminCustomer', methods=['GET', "POST"])
def admin_view_customer():
    cur = mysql.connection.cursor()
    cur.execute("CALL admin_view_customers(null, null)")
    cur.execute("select * from admin_view_customers_result")
    cur.connection.commit()
    customers = cur.fetchall()

    cur.execute("select * from admin_view_customers_result order by Username")
    cur.connection.commit()
    ascUsername = cur.fetchall()

    cur.execute("select * from admin_view_customers_result order by Username DESC")
    cur.connection.commit()
    descUsername = cur.fetchall()

    cur.execute("select * from admin_view_customers_result order by FullName")
    cur.connection.commit()
    ascFullname = cur.fetchall()

    cur.execute("select * from admin_view_customers_result order by FullName DESC")
    cur.connection.commit()
    descFullname = cur.fetchall()

    cur.close()

    if request.method=="POST":
        form = request.form
        fname = form['fname'].strip()
        lname = form['lname'].strip()
        if len(fname)==0:
            fname = None
        if len(lname)==0:
            lname = None
        cur = mysql.connection.cursor()
        cur.execute("CALL admin_view_customers(%s, %s)", (fname, lname))
        cur.execute("select * from admin_view_customers_result")
        cur.connection.commit()
        customers = cur.fetchall()
        cur.close()
    
    return render_template('adminCustomer.html', error=None, \
        customers=customers, ascUsername=ascUsername, descUsername=descUsername, \
            ascFullname=ascFullname, descFullname=descFullname)

@app.route('/adminChain', methods=['GET', 'POST'])
def admin_create_chain():
    if request.method=='POST':
        form = request.form
        chain = form['chainName']
        cur = mysql.connection.cursor()
        message=None
        cur.execute("select count(*) from chain where ChainName=%s",(chain,))
        cur.connection.commit()
        numChains=cur.fetchall()
        if numChains[0][0] != 0:
            message="Insertion fails. The input chain has already existed in the database"
        else:
            cur.execute("CALL admin_create_grocery_chain(%s)", (chain,))
            cur.connection.commit()
        cur.close()
        return render_template('adminChain.html', message=message)
    else:
        return render_template('adminChain.html', message=None)

@app.route('/adminStore', methods=['GET', 'POST'])
def admin_create_store():
    message=None
    cur = mysql.connection.cursor()
    cur.execute("select ChainName from chain")
    cur.connection.commit()
    table = cur.fetchall()
    if request.method=='POST':
        form = request.form
        chain = form['chain']
        store = form['store']
        street = form['street']
        city = form['city']
        state = form['state']
        zipcode = form['zip']
        cur = mysql.connection.cursor()
        cur.execute("select count(*) from store where ChainName=%s and Zipcode=%s",(chain,zipcode))
        cur.connection.commit()
        chainZipCombination=cur.fetchall()
        cur.execute("select count(*) from store where ChainName=%s and StoreName=%s",(chain,store))
        cur.connection.commit()
        chainStoreCombination=cur.fetchall()
        if chainZipCombination[0][0] != 0:
            message="This combination of chain name and zipcode has already existed. Insertion fails!"
        elif chainStoreCombination[0][0] !=0:
            message="This combination of chain name and store name has already existed. Insertion fails!"
        else:
            cur.execute("CALL admin_create_new_store(%s, %s, %s, %s, %s, %s)", \
            (store, chain, street, city, state, zipcode))
            cur.connection.commit()  
    cur.close()
    return render_template('adminStore.html', message=message, chains=table)

@app.route('/manager', methods=["GET"])
def manager():
    return render_template('manager.html')

@app.route("/managerDrone", methods=["GET", "POST"])
def manager_view_drone():
    # need mgr, drone_id(optional), drone_radius(options)
    # get mgr
    f = open("user.json", 'r')
    user = json.load(f)
    mgr=user['username']
    #get drone_id
    droneID=None
    #get drone_radius
    radius=None
    if request.method=="POST":
        form=request.form
        droneID=form['droneID'].strip()
        radius=form['radius'].strip()
        if len(droneID)==0:
            droneID=None
        if len(radius)==0:
            radius=None
    # call mysql procedure to get drones
    cur = mysql.connection.cursor()
    cur.execute("CALL manager_view_drones(%s,%s,%s)", (mgr,droneID,radius))
    cur.execute("select * from manager_view_drones_result")
    cur.connection.commit()
    drones=cur.fetchall()
    # create 8 states: ascID, descID, ascRadius, descRadius, ascZip, descZip, ascStatus, descStatus
    #ascID
    cur.execute("select * from manager_view_drones_result order by ID")
    cur.connection.commit()
    ascID=cur.fetchall()
    #descID
    cur.execute("select * from manager_view_drones_result order by ID DESC")
    cur.connection.commit()
    descID=cur.fetchall()
    #ascRadius
    cur.execute("select * from manager_view_drones_result order by Radius")
    cur.connection.commit()
    ascRadius=cur.fetchall()
    #descRadius
    cur.execute("select * from manager_view_drones_result order by Radius DESC")
    cur.connection.commit()
    descRadius=cur.fetchall()
    #ascZip
    cur.execute("select * from manager_view_drones_result order by Zip")
    cur.connection.commit()
    ascZip=cur.fetchall()
    #descZip
    cur.execute("select * from manager_view_drones_result order by Zip DESC")
    cur.connection.commit()
    descZip=cur.fetchall()
    #ascStatus
    cur.execute("select * from manager_view_drones_result order by DroneStatus")
    cur.connection.commit()
    ascStatus=cur.fetchall()
    #descStatus
    cur.execute("select * from manager_view_drones_result order by DroneStatus DESC")
    cur.connection.commit()
    descStatus=cur.fetchall()
    cur.close()
    states=[ascID,descID,ascRadius,descRadius,ascZip,descZip,ascStatus,descStatus]
    return render_template('managerDrone.html', drones=drones, states=states)

@app.route("/managerDroneTech", methods=["GET", "POST"])
def manager_view_dronetech():
    # need manager's username, manager chain, store of chain, and employees
    # manager Username
    f = open('user.json', 'r')
    user = json.load(f)
    f.close()
    username=user['username']
    # ChainName
    cur = mysql.connection.cursor()
    cur.execute('select ChainName from manager where Username=%s', (username,))
    cur.connection.commit()
    chain = cur.fetchall()[0][0]
    # stores of chain
    cur.execute('select StoreName from store where ChainName=%s', (chain,))
    cur.connection.commit()
    locations = cur.fetchall()
    # employees
    cur.execute('CALL manager_view_drone_technicians(%s, null, null)', (chain,))
    cur.execute('select * from manager_view_drone_technicians_result')
    cur.connection.commit()
    droneTechs = cur.fetchall()
    cur.close()
    if request.method=="POST":
        form=request.form
        droneTech=form['username'].strip()
        store=form['location'].strip()
        if len(droneTech)==0:
            droneTech=None
        if store=="empty":
            store=None
        # employees
        cur = mysql.connection.cursor()
        cur.execute("CALL manager_view_drone_technicians(%s,%s,%s)", \
            (chain, droneTech, store))
        cur.execute("select * from manager_view_drone_technicians_result")
        cur.connection.commit()
        droneTechs = cur.fetchall()
        cur.close()
    return render_template('managerDroneTech.html', chain=chain, droneTechs=droneTechs, locations=locations)

@app.route("/managerReassignDroneTech", methods=["POST"])
def manager_reassign_dronetech():
    # need manager's username, manager chain, and employees
    # manager Username
    f = open('user.json', 'r')
    user = json.load(f)
    f.close()
    username=user['username']
     # ChainName
    cur = mysql.connection.cursor()
    cur.execute('select ChainName from manager where Username=%s', (username,))
    cur.connection.commit()
    chain = cur.fetchall()[0][0]
    # employees
    cur.execute('CALL manager_view_drone_technicians(%s, null, null)', (chain,))
    cur.execute('select * from manager_view_drone_technicians_result')
    cur.connection.commit()
    droneTechs = cur.fetchall()
    # need new location
    form=request.form
    for i in range(len(droneTechs)):
        droneTech=droneTechs[i] #0 is username, 2 is location
        new_location=form[droneTech[0]]
        cur.execute("CALL manager_reassign_drone_technicians(%s, %s,% s)", \
            (chain, droneTech[0], new_location))
        cur.connection.commit()
    cur.close()
    return redirect(url_for("manager_view_dronetech"))

@app.route("/managerItem", methods=["GET", "POST"])
def manager_create_chainitem():
    # get manager Username, ChainName, and next PLUNumber, and item
    # manager Username
    f = open('user.json', 'r')
    user = json.load(f)
    f.close()
    username = user['username']
    # ChainName
    cur = mysql.connection.cursor()
    cur.execute('select ChainName from manager where Username=%s', (username,))
    cur.connection.commit()
    chain = cur.fetchall()[0][0]
    # next PLUNumber
    cur.execute('select max(PLUNumber) from chain_item group by ChainName having ChainName=%s', (chain,))
    cur.connection.commit()
    plu = cur.fetchall()[0][0] + 1
    # item
    cur.execute('select ItemName from item')
    cur.connection.commit()
    items = cur.fetchall()
    cur.close()
    # error message
    message=None
    if request.method=="POST":
        form = request.form
        item = form['item']
        quantity = form['quantity']
        limit = form['limit']
        price = form['price']
        cur = mysql.connection.cursor()
        cur.execute("select count(*) from chain_item where ChainName=%s and ChainItemName=%s",(chain,item))
        cur.connection.commit()
        count=cur.fetchall()
        if count[0][0] != 0:
            message="The combination of item and chain has already existed. Insertion fails."
        else:
            cur.execute('CALL manager_create_chain_item(%s, %s, %s, %s, %s, %s)', \
                (chain, item, quantity, limit, plu, price))
            cur.connection.commit()
            cur.close()
            return redirect(url_for('manager_create_chainitem'))
    return render_template('managerItem.html', chain=chain, plu=plu, items=items, message=message)


@app.route("/managerStore", methods=["GET", "POST"])
def manager_manage_store():
    # get mgr, chain
    f = open("user.json", "r")
    user=json.load(f)
    mgr=user['username']
    cur=mysql.connection.cursor()
    cur.execute("select ChainName from manager where Username=%s", (mgr,))
    cur.connection.commit()
    chain=cur.fetchall()[0][0]
    # get store name
    store=None
    # get min, max total
    minTotal=None
    maxTotal=None
    if request.method=="POST":
        form=request.form
        store=form['store'].strip()
        minTotal=form['min'].strip()
        maxTotal=form['max'].strip()
        if len(store)==0:
            store=None
        if len(minTotal)==0:
            minTotal=None
        if len(maxTotal)==0:
            maxTotal=None
    # get stores
    cur.execute("CALL manager_manage_stores(%s,%s,%s,%s)", (mgr,store,minTotal,maxTotal))
    cur.execute("select * from manager_manage_stores_result")
    cur.connection.commit()
    stores=cur.fetchall()
    # get states for ordering
    # ascName
    cur.execute("select * from manager_manage_stores_result order by StoreName")
    cur.connection.commit()
    ascName=cur.fetchall()
    # descName
    cur.execute("select * from manager_manage_stores_result order by StoreName DESC")
    cur.connection.commit()
    descName=cur.fetchall()
    # ascAddress
    cur.execute("select * from manager_manage_stores_result order by Address")
    cur.connection.commit()
    ascAddress=cur.fetchall()
    # descAddress
    cur.execute("select * from manager_manage_stores_result order by Address DESC")
    cur.connection.commit()
    descAddress=cur.fetchall()
    # ascOrder
    cur.execute("select * from manager_manage_stores_result order by Orders")
    cur.connection.commit()
    ascOrder=cur.fetchall()
    # descOrder
    cur.execute("select * from manager_manage_stores_result order by Orders DESC")
    cur.connection.commit()
    descOrder=cur.fetchall()
    # ascEmp
    cur.execute("select * from manager_manage_stores_result order by Employees")
    cur.connection.commit()
    ascEmp=cur.fetchall()
    # descEmp
    cur.execute("select * from manager_manage_stores_result order by Employees DESC")
    cur.connection.commit()
    descEmp=cur.fetchall()
    # ascTotal
    cur.execute("select * from manager_manage_stores_result order by Total")
    cur.connection.commit()
    ascTotal=cur.fetchall()
    # descTotal
    cur.execute("select * from manager_manage_stores_result order by Total DESC")
    cur.connection.commit()
    descTotal=cur.fetchall()
    cur.close()
    # assemble states
    states=[ascName,descName,ascAddress,descAddress,ascOrder,descOrder,ascEmp,descEmp,ascTotal,descTotal]
    return render_template('managerStore.html', chain=chain, stores=stores, states=states)

@app.route("/customer", methods=["GET"])
def customer():
    # get username
    f=open("user.json", 'r')
    user=json.load(f)
    username=user['username']
    # get chain and store current order is at
    cur=mysql.connection.cursor()
    cur.execute('CALL customer_find_created_order(%s)',(username,))
    cur.execute("select * from customer_find_created_order_result")
    cur.connection.commit()
    result=cur.fetchall()
    if result:
        chain=result[0][0]
        store=result[0][1]
        return render_template("customer.html",chain=chain,store=store)
    else:
        return render_template("customer.html",chain=None,store=None)

@app.route("/customerCC", methods=["GET", "POST"])
def customer_change_cc():
    # get username, fname, lname
    f=open("user.json", 'r')
    user=json.load(f)
    customer=user['username']
    cur=mysql.connection.cursor()
    cur.execute('select FirstName, LastName from users where Username=%s', (customer,))
    cur.connection.commit()
    name=cur.fetchall()
    fname=name[0][0]
    lname=name[0][1]
    # get ccNumber, security code, and expiration date
    error=None
    if request.method=="POST":
        form=request.form
        ccNumber=form['ccNumber'].strip()
        cvv=form['cvv'].strip()
        expDate=form['expDate'].strip()
        if datetime.strptime(expDate,'%Y-%m-%d') < datetime.today():
            error="Credit Card Has Expired!"
        else:
            cur.execute("CALL customer_change_credit_card_information(%s,%s,%s,%s)", (customer,ccNumber,cvv,expDate))
            cur.connection.commit()
            cur.close()
    return render_template('customerCC.html',error=error,customer=customer,fname=fname,lname=lname)


@app.route("/customerOrderHistory", methods=["GET", "POST"])
def customer_view_order_history():
    # find all orderID of customer
    f=open("user.json",'r')
    customer=json.load(f)
    username=customer['username']
    cur=mysql.connection.cursor()
    cur.execute("select ID from orders where CustomerUsername=%s and OrderStatus<>'Creating'",(username,))
    cur.connection.commit()
    orderIDs=cur.fetchall()
    # create a dictionary that map orderID to [totalAmount, totalItems, date, droneID, droneTech, status]
    orders=dict()
    i=0
    # create an initial state with [orderID,totalAmount,totalItems,date,droneID,droneTech,state]
    initial=[] 
    for row in orderIDs:
        orderID=row[0]
        cur.execute("CALL customer_view_order_history(%s,%s)", (username,orderID))
        cur.execute("select * from customer_view_order_history_result")
        cur.connection.commit()
        result=cur.fetchall()
        if not result:
            continue
        orders[orderID]=result[0]
        if i==0:
            initial.append(orderID)
            for item in orders[orderID]:
                initial.append(item)
        i+=1
    cur.close()
    return render_template('customerOrderHistory.html',customer=username,orders=orders,initial=initial)

@app.route("/customerItems", methods=["GET", "POST"])
def customer_view_store_items():
    # hasStores hold states: hasStore[0]-store available, hasStore[1]-store selected
    hasStores=[0,0]
    # get the customer's username
    f=open("user.json",'r')
    customer=json.load(f)
    username=customer['username']
    # get the stores where the customer can shop
    # if customer has created an order, can only shop from the store where the order were created
    # otherwise, can shop from any store
    cur=mysql.connection.cursor()
    cur.execute("CALL customer_find_created_order(%s)",(username,))
    cur.execute("select * from customer_find_created_order_result")
    cur.connection.commit()
    result=cur.fetchall()
    if result:
        return render_template("orderExists.html",chain=result[0][0],store=result[0][0])

    stores=dict() #map chain to stores
    cur.execute("select ChainName, StoreName from users join store on users.Zipcode=store.Zipcode and Username=%s",(username,))
    cur.connection.commit()
    table=cur.fetchall()
    for row in table:
        if row[0] not in stores:
            stores[row[0]]=[]
        stores[row[0]].append(row[1])
    if stores:
        hasStores[0]=1
    else:
        hasStores[0]=0
    # get items and store selections
    items=[]
    prevSelections=[None,None]
    if request.method=="POST":
        form=request.form
        chain=form['chain'].strip()
        store=form['store'].strip()
        category=form['category'].strip()
        if chain=="empty":
            chain=None
        else:
            prevSelections[0]=chain
        if store=="empty":
            store=None
        else:
            prevSelections[1]=store
        if category=="empty":
            category=None
        cur.execute("CALL customer_view_store_items(%s,%s,%s,%s)",(username,chain,store,category))
        cur.execute("select * from customer_view_store_items_result")
        cur.connection.commit()
        items=cur.fetchall()
        if items:
            hasStores[1]=1
        else:
            hasStores[1]=0
    cur.close()
    return render_template('customerItems.html',customer=username,\
        stores=stores,hasStores=hasStores,items=items,prevSelections=prevSelections)

@app.route("/customerNewOrder",methods=["POST"])
def customer_create_new_order():
    cur=mysql.connection.cursor()
    form=request.form
    i=0
    userInfo=[None,None,None]
    for item in form:
        if i<3:
            userInfo[i]=form[item]
        else:
            cur.execute("CALL customer_select_items(%s,%s,%s,%s,%s)",\
                (userInfo[0],userInfo[1],userInfo[2],item,form[item]))
            cur.connection.commit()
        i+=1
    cur.close()
    return redirect(url_for("customer_review_order",chain=userInfo[1],store=userInfo[2]))

@app.route("/customerOrder/<chain>/<store>",methods=["GET", "POST"])
def customer_review_order(chain,store):
    if chain=="None" and store=="None":
        return render_template("noOrder.html")
    # get customer
    f=open("user.json", 'r')
    customer=json.load(f)
    username=customer['username']
    # get items, and order limit for each item
    cur=mysql.connection.cursor()
    cur.execute("CALL customer_review_order(%s)", (username,))
    cur.execute("select * from customer_review_order_result")
    cur.connection.commit()
    items=cur.fetchall()
    total=0
    limits=dict()
    for row in items:
        total+=float(row[1])*float(row[2])
        if row[0] not in limits:
            limits[row[0]] = 0
        cur.execute("select Orderlimit from chain_item where ChainItemName=%s and ChainName=%s", (row[0],chain))
        cur.connection.commit()
        limits[row[0]] += cur.fetchall()[0][0]
    if request.method=="POST":
        # check if the credit card is valid, aka not expired
        cur.execute("select EXP_DATE from customer where Username=%s",(username,))
        cur.connection.commit()
        expDate=cur.fetchall()[0][0]
        if expDate < date.today():
            return render_template("expiredCC.html")
        form=request.form
        for item in items:
            itemName=item[0]
            quantity=form[itemName]
            cur.execute("call customer_update_order(%s,%s,%s)",(username,itemName,quantity))
            cur.connection.commit()
        cur.execute("call customer_place_order(%s)",(username,))
        cur.connection.commit()
        cur.close()
        return redirect(url_for("customer_view_store_items"))
    else:
        cur.close()
        return render_template("customerOrder.html",chain=chain,store=store,items=items,total=round(total,2),limits=limits)

@app.route("/customerCancelOrder", methods=["GET"])
def customer_cancel_order():
    # get customer
    f=open("user.json", 'r')
    customer=json.load(f)
    username=customer['username']
    cur=mysql.connection.cursor()
    cur.execute("CALL customer_cancel_order(%s)",(username,))
    cur.connection.commit()
    cur.close()
    return redirect(url_for("customer_view_store_items"))

@app.route("/dronetech", methods=["GET"])
def dronetech():
    return render_template("dronetech.html")

@app.route("/droneTechStoreOrder", methods=["GET", "POST"])
def dronetech_view_store_order():
    # get drone tech, and start and end date
    f=open("user.json",'r')
    dronetech=json.load(f)
    username=dronetech['username']
    startDate=None
    endDate=None
    if request.method=="POST":
        form=request.form
        if len(form['startDate']) != 0:
            startDate=datetime.strptime(form['startDate'], "%Y-%m-%d")
        if len(form['endDate']) != 0:
            endDate=datetime.strptime(form['endDate'], "%Y-%m-%d")
    cur=mysql.connection.cursor()
    cur.execute('CALL drone_technician_view_order_history(%s,%s,%s)',(username,startDate,endDate))
    cur.execute("select * from drone_technician_view_order_history_result")
    cur.connection.commit()
    orders=cur.fetchall()
    # get states=[ascID,descID,ascDate,descDate,ascDrone,descDrone,ascStatus,descStatus,ascTotal,descTotal]
    # ID
    cur.execute("select * from drone_technician_view_order_history_result order by ID")
    cur.connection.commit()
    ascID=cur.fetchall()
    cur.execute("select * from drone_technician_view_order_history_result order by ID DESC")
    cur.connection.commit()
    descID=cur.fetchall()
    # date
    cur.execute("select * from drone_technician_view_order_history_result order by Date")
    cur.connection.commit()
    ascDate=cur.fetchall()
    cur.execute("select * from drone_technician_view_order_history_result order by Date DESC")
    cur.connection.commit()
    descDate=cur.fetchall()
    # drone
    cur.execute("select * from drone_technician_view_order_history_result order by DroneID")
    cur.connection.commit()
    ascDrone=cur.fetchall()
    cur.execute("select * from drone_technician_view_order_history_result order by DroneID DESC")
    cur.connection.commit()
    descDrone=cur.fetchall()
    # status
    cur.execute("select * from drone_technician_view_order_history_result order by Status")
    cur.connection.commit()
    ascStatus=cur.fetchall()
    cur.execute("select * from drone_technician_view_order_history_result order by Status DESC")
    cur.connection.commit()
    descStatus=cur.fetchall()
    # total
    cur.execute("select * from drone_technician_view_order_history_result order by Total")
    cur.connection.commit()
    ascTotal=cur.fetchall()
    cur.execute("select * from drone_technician_view_order_history_result order by Total DESC")
    cur.connection.commit()
    descTotal=cur.fetchall()
    # states
    states=[ascID,descID,ascDate,descDate,ascDrone,descDrone,ascStatus,descStatus,ascTotal,descTotal]
    cur.close()
    return render_template("droneTechOrder.html",orders=orders,states=states)

@app.route("/droneTechViewOrderDetial", methods=["POST"])
def dronetech_view_order_detail():
    # get order ID
    form=request.form
    orderID=form['selectedOrder']
    # get technician username
    f=open("user.json","r")
    droneTech=json.load(f)
    username=droneTech["username"]
    # get name of dronetech
    cur=mysql.connection.cursor()
    cur.execute("select concat(FirstName,' ',LastName) from users where Username=%s",(username,))
    cur.connection.commit()
    name=cur.fetchall()[0][0]
    # get order details
    cur.execute("CALL dronetech_order_details(%s,%s)",(username,orderID))
    cur.execute("select * from dronetech_order_details_result")
    cur.connection.commit()
    orderDetails=cur.fetchall()[0]
    # get order items
    cur.execute("CALL dronetech_order_items(%s,%s)",(username,orderID))
    cur.execute("select * from dronetech_order_items_result")
    cur.connection.commit()
    orderItems=cur.fetchall()
    # get available drones
    cur.execute("CALL dronetech_assigned_drones(%s,%s,%s)",(username,None,"Available"))
    cur.execute("select * from dronetech_assigned_drones_result")
    cur.connection.commit()
    drones=cur.fetchall()
    cur.close()
    return render_template("droneTechOrderDetails.html",orderDetails=orderDetails,orderItems=orderItems,\
        username=username,name=name,drones=drones)

@app.route("/droneTechAssignOrder/<orderID>", methods=["POST"])
def dronetech_assign_order(orderID):
    # get technician username
    f=open("user.json","r")
    droneTech=json.load(f)
    username=droneTech["username"]
    # update order if drone Tech assign his drone or update order status
    form=request.form
    droneID=form['droneID']
    droneTech=form['droneTech']
    status=form['status']
    cur=mysql.connection.cursor()
    if droneID!="empty" and droneTech!="empty":
        cur.execute("CALL dronetech_assign_order(%s,%s,%s,%s)",(username,droneID,status,orderID))
        cur.connection.commit()
    return redirect(url_for('dronetech_view_store_order'))
    
@app.route("/droneTechAssignedDrone", methods=["GET", "POST"])
def dronetech_view_assigned_drones():
    # get username
    f=open("user.json",'r')
    dronetech=json.load(f)
    username=dronetech['username']
    # droneID, status
    droneID=None
    status=None
    if request.method=="POST":
        form=request.form
        droneID=form['droneID']
        status=form['status']
        if len(droneID)==0:
            droneID=None
        if status=='empty':
            status=None
    cur=mysql.connection.cursor()
    cur.execute("CALL dronetech_assigned_drones(%s,%s,%s)",(username,droneID,status))
    cur.execute("select * from dronetech_assigned_drones_result")
    cur.connection.commit()
    drones=cur.fetchall()
    #states=[ascID,descID,ascStatus,descStatus,ascRadius,descRadius]
    # ID
    cur.execute("select * from dronetech_assigned_drones_result order by DroneID")
    cur.connection.commit()
    ascID=cur.fetchall()
    cur.execute("select * from dronetech_assigned_drones_result order by DroneID DESC")
    cur.connection.commit()
    descID=cur.fetchall()
    # status
    cur.execute("select * from dronetech_assigned_drones_result order by DroneStatus")
    cur.connection.commit()
    ascStatus=cur.fetchall()
    cur.execute("select * from dronetech_assigned_drones_result order by DroneStatus DESC")
    cur.connection.commit()
    descStatus=cur.fetchall()
    # Radius
    cur.execute("select * from dronetech_assigned_drones_result order by Radius")
    cur.connection.commit()
    ascRadius=cur.fetchall()
    cur.execute("select * from dronetech_assigned_drones_result order by Radius DESC")
    cur.connection.commit()
    descRadius=cur.fetchall()
    states=[ascID,descID,ascStatus,descStatus,ascRadius,descRadius]
    cur.close()
    return render_template("droneTechDrone.html", drones=drones, states=states)

if __name__ == "__main__":
    app.run(debug=True)