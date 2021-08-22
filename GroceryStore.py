import PySimpleGUI as sg
import mysql.connector
from datetime import datetime
from getpass import getpass
from mysql.connector import connect, Error

def mainMenu():
    sg.theme('dark')
    layout = [[sg.Text('Main Menu')],
              [sg.Button('Shoppers', size = (20,5))],
              [sg.Button('Staff',size = (20,5))],
              [sg.Button('Exit',size = (20,5))]]
    return sg.Window('Main Menu', layout, finalize=True)
              

def shopperMenu():
    sg.theme('dark')
    layout = [[sg.Text('Shopper Menu')],
              [sg.Text("Your cart:")],
              [sg.Text(size = (40,20), key = ('Cart'))],
              [sg.Text('Enter the SKU of your product to add to the cart:'), sg.Input(key =('SKU'),size=(25,1),do_not_clear=False)],
              [sg.Button('Enter',bind_return_key = True)],[sg.Text('Total:')],[sg.Text('0.00', size = (9,2), key = ('Total'))],
              [sg.Button('Finish')]]
    return sg.Window('Shopper Menu', layout, finalize=True)


def staffLogin():
    sg.theme('dark')
    layout = [[sg.Text('Staff Login')],
              [sg.Text('Name:'),sg.Input(key = ('USERNAME'),enable_events=True)],
              [sg.Text('Password:'),sg.Input(key = ('PASSWORD'),password_char='*',enable_events=True)],
              [sg.Text('Error Output:')],
              [sg.Output(key = ('ERROR CODE'), size = (50,0))],
              [sg.Button('Log In', bind_return_key = True)],[sg.Button('Back')]]
    return sg.Window('Staff Login', layout, finalize=True)
               
def staffMenu():
    #contains buttons have tooltips to show to user what variables to enter, and their order
    add_block = [[sg.Button('Add Product', tooltip = 'Format: SKU (int), UPC(int), name(string),dept/loc(string),unitSize(string), price(float), quantity(int),0')],[sg.Button('Add Order', tooltip = 'Format: orderID (int), supplierID(int), employeeID(int), orderDate(date, YY/MM/DD), SKU (int), quantity(int)')] ,[sg.Button('Add Employee', tooltip = 'Format: employeeID (int), firstname (string), lastname(string), jobTitle(string)')],[sg.Button('Add Supplier',tooltip = 'Format: supplierID (int), name(sting), address(string),city(string),country(string),phone(string)')]]
    remove_block = [[sg.Button('Remove Product', tooltip ='Format: SKU(int)')], [sg.Button('Remove Order', tooltip = 'Format: orderID(int)')],[sg.Button('Remove Employee', tooltip = 'Format: employeeID(int)')],[sg.Button('Remove Supplier',tooltip = 'Format: supplierID(int)')]]
    mod_block = [[sg.Button('Mod Product', tooltip = 'Format: name(string),unitSize(string), price(float), quantity(int), numSold(int), SKU-to-modify(int)')],[sg.Button('Mod Order', tooltip = 'Format: orderDate(date, YY/MM/DD), quantity(int),orderid-to-modify(int)')] ,[sg.Button('Mod Employee', tooltip = 'Format: firstname (string), lastname(string), jobTitle(string), employeeid-to-modify(int)')],[sg.Button('Mod Supplier',tooltip = 'Format:name(sting), address(string),city(string),country(string),phone(string),supplierID-to-modify(int)')]]
    sg.theme('dark')
    layout = [[sg.Text('Staff Menu')],
              [sg.Text('Output for database query:')],
              [sg.Output(key = ('OUTPUT'), size = (50,20))],
              [sg.Text('Input:'),sg.Input(key = ('QUERY_VALUES'),size=(50,1),do_not_clear=False)],
              [sg.Column(add_block) ,sg.Column(remove_block),sg.Column(mod_block)],
              [sg.Button('Number Sold',tooltip = 'No input needed.',pad=(10,10)),sg.Button('Advanced Query')],
              [sg.Button('Logout',pad=(5,30))]]
    return sg.Window('Staff Menu', layout, finalize=True)
    

main, shop, login, menu = mainMenu(), None, None, None
#initalize values
shopping_cart = []
query_history = []
total = 0.0

while True:
    window, event, values = sg.read_all_windows()
        
    if window == main and event in (sg.WIN_CLOSED, 'Exit'):
        break

    if window == main:
        if event =='Shoppers':
            main.hide()
            shop = shopperMenu()
        if event =='Staff':
            main.hide()
            login = staffLogin()
        if event == sg.WIN_CLOSED:
            break;

    if window == shop:
        if event =='Enter':
            shop['Cart'].update(values['SKU'])
            user = values['SKU']
            with connect(
                host ="10.0.0.54",
                user = "root",
                password = "project"
            )as connection:
                get_name = "SELECT name FROM grocerydb.product WHERE SKU = %s"
                get_price = "SELECT price FROM grocerydb.product WHERE SKU = %s"
                update_num_sold = "UPDATE grocerydb.product SET numsold = numsold + 1 WHERE SKU = %s"
                with connection.cursor() as cursor:
                    cursor.execute(get_name, (user,))
                    name_record =cursor.fetchall()
                    cursor.execute(get_price, (user,))
                    price_record =cursor.fetchall()
                    cursor.execute(update_num_sold, (user,))
                    connection.commit()
                shopping_cart.append(name_record)
                shopping_cart.append(price_record)
                string_price = str(price_record[0])
                string_price = string_price.strip("(),")
                price = float(string_price)
                total = total + price
                shop['Total'].update(total)
                shop['Cart'].update(shopping_cart)
                cursor.close()
                connection.close()    
        if event =='Finish':
            sg.popup("Thank you for shopping with us!"+"\n\nYour total is " +str(total)+".");
            shop.hide()
            main.un_hide()
        if event == sg.WIN_CLOSED:
            break;

    if window == login:
        entered_username = values['USERNAME']
        entered_password = values['PASSWORD']
        generic_error = ["Invalid username/password."]
        if event == 'Log In':
            try:
                with connect(
                    host ="10.0.0.54",
                    user = entered_username,
                    password = entered_password
                )as connection:
                    login['ERROR CODE'].update(connection)
                    connection_string = str(connection)
                    if "1045" in connection_string:
                        login['ERROR CODE'].update(generic_error)
                    else:
                        login.hide()
                        menu = staffMenu()
            except Error as e:
                login['ERROR CODE'].update(e)
        if event == 'Back':
            login.hide()
            main.un_hide()
        if event == sg.WIN_CLOSED:
            break;
    if window == menu:
        if event =='Add Product':
            add_to_table = "INSERT INTO grocerydb.product values(%s, %s, %s, %s, %s, %s, %s, %s)"
            tell_user = "Product information added successfully! \n"
            query = values['QUERY_VALUES']
            insert_values = query.split(',')
            with connect(
                host = "10.0.0.54",
                user = entered_username,
                password = entered_password
            )as connection:
                with connection.cursor() as cursor:
                    cursor.execute(add_to_table, (int(insert_values[0]),int(insert_values[1]),str(insert_values[2]),str(insert_values[3]),str(insert_values[4]),float(insert_values[5]),int(insert_values[6]),int(insert_values[7])))
                    query_result = cursor.fetchall()
                    connection.commit()
                    cursor.close()
                    connection.close()
                    query_histroy.append(tell_user)
                    query_history.append(insert_values)
            menu['OUTPUT'].update(query_history)
        if event == 'Add Order':
            #works correctly
            add_order = "INSERT INTO grocerydb.orders values (%s, %s, %s, %s, %s, %s)"
            tell_user = "Order information added sucessfully! \n"
            query = values['QUERY_VALUES']
            split_values = query.split(',')
            split_values[3] = datetime.strptime(split_values[3],'%m/%d/%y')
            with connect(
                host = "10.0.0.54",
                user = entered_username,
                password = entered_password
            )as connection:
                with connection.cursor() as cursor:
                    cursor.execute(add_order, (int(split_values[0]),int(split_values[1]),int(split_values[2]),split_values[3],int(split_values[4]),int(split_values[5])))
                    query_result = cursor.fetchall()
                    connection.commit()
                    cursor.close()
                    connection.close()
                    query_history.append(tell_user)
                    query_history.append(split_values)
                menu['OUTPUT'].update(query_history)
            pass
        if event == 'Add Employee':
            add_employee = ("INSERT INTO grocerydb.employee values (%s, %s, %s, %s)")
            tell_user = "Employee information added successfully! \n"
            query = values['QUERY_VALUES']
            split_values = query.split(',')
            with connect(
                host = "10.0.0.54",
                user = entered_username,
                password = entered_password
            )as connection:
                with connection.cursor() as cursor:
                    cursor.execute(add_employee, (int(split_values[0]),str(split_values[1]),str(split_values[2]),str(split_values[3])))
                    query_result = cursor.fetchall()
                    connection.commit()
                    cursor.close()
                    connection.close()
                    query_history.append(tell_user)
                    query_history.append(split_values)
                menu['OUTPUT'].update(query_history)
        if event == 'Add Supplier':
            add_supplier = "INSERT INTO grocerydb.supplier values (%s, %s, %s, %s, %s, %s)"
            tell_user = "Supplier information added successfully! \n"
            query = values['QUERY_VALUES']
            split_values = query.split(',')
            with connect(
                host = "10.0.0.54",
                user = entered_username,
                password = entered_password
            )as connection:
                with connection.cursor() as cursor:
                    cursor.execute(add_supplier, (int(split_values[0]),str(split_values[1]),str(split_values[2]),str(split_values[3]),str(split_values[4]),str(split_values[5])))
                    query_result = cursor.fetchall()
                    connection.commit()
                    cursor.close()
                    connection.close()
                    query_history.append(tell_user)
                    query_history.append(split_values)
                menu['OUTPUT'].update(query_history)
        if event == 'Advanced Query':
            query = values['QUERY_VALUES']
            with connect(
                host = "10.0.0.54",
                user = entered_username,
                password = entered_password
            )as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    query_result = cursor.fetchall()
                    connection.commit()
                    cursor.close()
                    connection.close()
                    query_history.append(query_result)
            menu['OUTPUT'].update(query_history)
        if event == 'Remove Product':
            query = "DELETE from grocerydb.product where SKU = %s"
            tell_user = "Product deleted sucessfully. \n"
            del_SKU = values['QUERY_VALUES']
            split_values = del_SKU.split(',')
            with connect(
                host = "10.0.0.54",
                user = entered_username,
                password = entered_password
            )as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query,(del_SKU,))
                    query_result = cursor.fetchall()
                    connection.commit()
                    cursor.close()
                    connection.close()
                    query_history.append(tell_user)
                    query_history.append(query_result)
            menu['OUTPUT'].update(query_history)
        if event == 'Remove Order':
            query = "DELETE from grocerydb.orders where orderid = %s"
            tell_user = "Order deleted sucessfully. \n"
            del_order = values['QUERY_VALUES']
            with connect(
                host = "10.0.0.54",
                user = entered_username,
                password = entered_password
            )as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query,(del_order,))
                    query_result = cursor.fetchall()
                    connection.commit()
                    cursor.close()
                    connection.close()
                    query_history.append(tell_user)
                    query_history.append(query_result)
            menu['OUTPUT'].update(query_history)
        if event == 'Remove Employee':
            query = "DELETE from grocerydb.employee where employeeid = %s"
            tell_user = "Employee deleted sucessfully. \n"
            del_emp = values['QUERY_VALUES']
            with connect(
                host = "10.0.0.54",
                user = entered_username,
                password = entered_password
            )as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query,(del_emp,))
                    query_result = cursor.fetchall()
                    connection.commit()
                    cursor.close()
                    connection.close()
                    query_history.append(tell_user)
                    query_history.append(query_result)
            menu['OUTPUT'].update(query_history)
        if event == 'Remove Supplier':
            query = "DELETE from grocerydb.supplier where supplierid = %s"
            tell_user = "Supplier deleted sucessfully. \n"
            del_id = values['QUERY_VALUES']
            with connect(
                host = "10.0.0.54",
                user = entered_username,
                password = entered_password
            )as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query,(del_id,))
                    query_result = cursor.fetchall()
                    connection.commit()
                    cursor.close()
                    connection.close()
                    query_history.append(tell_user)
                    query_history.append(query_result)
            menu['OUTPUT'].update(query_history)
        if event == 'Mod Product':
            query = "UPDATE grocerydb.product SET name = %s, unitsize = %s, price = %s, quantity = %s, numsold = %s WHERE SKU = %s"
            tell_user = "Product modified successfully. \n"
            mod_prod = values ['QUERY_VALUES']
            split_values = mod_prod.split(',')
            with connect(
                host = "10.0.0.54",
                user = entered_username,
                password = entered_password
            )as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query,(str(split_values[0]),str(split_values[1]),float(split_values[2]),int(split_values[3]),int(split_values[4]),int(split_values[5])))
                    query_result = cursor.fetchall()
                    connection.commit()
                    cursor.close()
                    connection.close()
                    query_history.append(tell_user)
                    query_history.append(query_result)
            menu['OUTPUT'].update(query_history)
        if event == 'Mod Order':
            query = "UPDATE grocerydb.orders SET orderdate = %s, quantity = %s WHERE orderid = %s"
            tell_user = "Order modified successfully. \n"
            mod_order = values ['QUERY_VALUES']
            split_values = mod_order.split(',')
            split_values[0] = datetime.strptime(split_values[0],'%m/%d/%y')
            with connect(
                host = "10.0.0.54",
                user = entered_username,
                password = entered_password
            )as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query,(split_values[0],int(split_values[1]),int(split_values[2])))
                    query_result = cursor.fetchall()
                    connection.commit()
                    cursor.close()
                    connection.close()
                    query_history.append(tell_user)
                    query_history.append(query_result)
            menu['OUTPUT'].update(query_history)
        if event == 'Mod Employee':
            query = "UPDATE grocerydb.employee SET firstname = %s, lastname = %s, jobTitle = %s WHERE employeeid = %s"
            tell_user = "Employee modified successfully. \n"
            mod_emp = values ['QUERY_VALUES']
            modify_param = mod_emp.split(',')
            with connect(
                host = "10.0.0.54",
                user = entered_username,
                password = entered_password
            )as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query,modify_param)
                    query_result = cursor.fetchall()
                    connection.commit()
                    cursor.close()
                    connection.close()
                    query_history.append(tell_user)
                    query_history.append(query_result)
            menu['OUTPUT'].update(query_history)
        if event == 'Mod Supplier':
            query = "UPDATE grocerydb.supplier SET name = %s, address = %s, city = %s, country = %s, phone = %s WHERE supplierid = %s"
            tell_user = "Supplier modified successfully. \n"
            mod_sup = values ['QUERY_VALUES']
            split_values = mod_sup.split(',')
            with connect(
                host = "10.0.0.54",
                user = entered_username,
                password = entered_password
            )as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query,(str(split_values[0]),str(split_values[1]),str(split_values[2]),str(split_values[3]),str(split_values[4]),int(split_values[5])))
                    query_result = cursor.fetchall()
                    connection.commit()
                    cursor.close()
                    connection.close()
                    query_history.append(tell_user)
                    query_history.append(query_result)
            menu['OUTPUT'].update(query_history)
        if event == 'Number Sold':
            query = "SELECT name,numsold from grocerydb.product order by numsold"
            with connect(
                host = "10.0.0.54",
                user = entered_username,
                password = entered_password
            )as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    query_result = cursor.fetchall()
                    connection.commit()
                    cursor.close()
                    connection.close()
                    query_history.append(query_result)
            menu['OUTPUT'].update(query_history)
        if event =='Logout':
            menu.hide()
            main.un_hide()
        if event == sg.WIN_CLOSED:
            break;
        
    

window.close()
