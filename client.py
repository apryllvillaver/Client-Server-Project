import requests

BASE_URL = "http://127.0.0.1:5000"
token = None
current_user = None

# ---------------- API FUNCTIONS ----------------
def register(username, password):
    response = requests.post(f"{BASE_URL}/register", json={
        "username": username,
        "password": password
    })
    try:
        print("REGISTER:", response.json())
    except:
        print("REGISTER ERROR:", response.text)

def login(username, password):
    global token, current_user
    response = requests.post(f"{BASE_URL}/login", json={
        "username": username,
        "password": password
    })
    try:
        data = response.json()
        print("LOGIN:", data)
        token = data.get("token")
        if token:
            current_user = username
        return token
    except:
        print("LOGIN ERROR:", response.text)
        return None

def create_event(name, date):
    global token
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/events", json={
        "name": name,
        "date": date
    }, headers=headers)
    try:
        print("CREATE EVENT:", response.json())
    except:
        print("CREATE EVENT ERROR:", response.text)

def list_events():
    global token
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/events", headers=headers)
    try:
        events = response.json()
        print("\n=== EVENTS ===")
        for ev in events:
            print(f"ID: {ev['_id']} | {ev['name']} on {ev['date']}")
        return events
    except:
        print("LIST EVENTS ERROR:", response.text)
        return []

def register_student(event_id, username):
    global token
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/events/{event_id}/register", json={
        "username": username
    }, headers=headers)
    try:
        print("REGISTER STUDENT:", response.json())
    except:
        print("REGISTER STUDENT ERROR:", response.text)


# ---------------- MENUS ----------------
def main_menu():
    """Main menu shown before login"""
    global token, current_user
    while True:
        print("\n=== MAIN MENU ===")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Choose option: ")

        if choice == "1":
            u = input("Enter username: ")
            p = input("Enter password: ")
            register(u, p)

        elif choice == "2":
            u = input("Enter username: ")
            p = input("Enter password: ")
            if login(u, p):
                user_menu()  # go to logged-in menu

        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.")


def user_menu():
    """Menu shown after login"""
    global token, current_user
    while token:  # stays until logout
        print(f"\n=== USER MENU (Logged in as {current_user}) ===")
        print("1. Create Event")
        print("2. List Events")
        print("3. Register Student to Event")
        print("4. Logout")

        choice = input("Choose option: ")

        if choice == "1":
            name = input("Enter event name: ")
            date = input("Enter event date (YYYY-MM-DD): ")
            create_event(name, date)

        elif choice == "2":
            list_events()

        elif choice == "3":
            events = list_events()
            if events:
                event_id = input("Enter event ID from the list: ")
                uname = input("Enter student username to register: ")
                register_student(event_id, uname)
            else:
                print("No events available!")

        elif choice == "4":
            print("Logging out...")
            token = None
            current_user = None
            break
        else:
            print("Invalid choice, try again.")

# ---------------- RUN ----------------
if __name__ == "__main__":
    main_menu()
