import streamlit as st
import sqlite3
import pandas as pd
import joblib
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu

st.set_page_config(page_title="AI Real Estate", layout="wide")

# DATABASE
conn = sqlite3.connect("database/users.db")
c = conn.cursor()

# LOGIN STATE
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN PAGE ----------------

if not st.session_state.logged_in:

    st.title("🏠 AI Real Estate System")

    option = st.radio("", ["Login", "Register"])

    if option == "Login":

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            c.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, password)
            )

            result = c.fetchone()

            if result:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()

            else:
                st.error("Invalid Login")

    else:

        new_user = st.text_input("Create Username")
        new_pass = st.text_input("Create Password", type="password")

        if st.button("Register"):

            c.execute(
                "INSERT INTO users VALUES (?,?)",
                (new_user, new_pass)
            )

            conn.commit()

            st.success("Account Created")

    st.stop()

# ---------------- TOP MENU ----------------

selected = option_menu(
    menu_title=None,
    options=["Home","Predict","Analytics","History","Logout"],
    icons=["house","search","bar-chart","clock-history","box-arrow-right"],
    orientation="horizontal"
)

# ---------------- HOME ----------------

if selected == "Home":

    st.title("🏠 Home Dashboard")

    st.write("Welcome to AI Real Estate System")

    col1,col2,col3 = st.columns(3)

    with col1:
        st.info("🔎 Predict House Prices")

    with col2:
        st.info("📊 Housing Market Analytics")

    with col3:
        st.info("📜 Prediction History")

# ---------------- PREDICT ----------------

elif selected == "Predict":

    import pandas as pd
    import joblib
    import matplotlib.pyplot as plt

    st.title("🔎 Predict House Price")

    # Load model and columns
    model = joblib.load("model/house_price_model.pkl")
    model_columns = joblib.load("model/model_columns.pkl")

    # Input fields
    city = st.selectbox("City",[
        "Ahmedabad","Bangalore","Bhopal","Chandigarh",
        "Chennai","Delhi","Hyderabad","Kolkata","Mumbai","Pune"
    ])

    area = st.number_input("Area (sqft)",200,10000)
    bedrooms = st.slider("Bedrooms",1,6)
    bathrooms = st.slider("Bathrooms",1,5)
    balcony = st.selectbox("Balcony",["Yes","No"])
    age = st.slider("Building Age",0,30)

    if balcony == "Yes":
        balcony = 1
    else:
        balcony = 0

    # Prediction button
    if st.button("Predict Price"):

        input_dict = {
            "Area_sqft": area,
            "Bedrooms": bedrooms,
            "Bathrooms": bathrooms,
            "Balcony": balcony,
            "Age": age
        }

        input_data = pd.DataFrame([input_dict])

        # City encoding
        city_column = "City_" + city
        input_data[city_column] = 1

        # Match training columns
        input_data = input_data.reindex(columns=model_columns, fill_value=0)

        # Predict
        price = model.predict(input_data)
        predicted_price = int(price[0])

        st.success(f"Estimated Price: ₹ {predicted_price:,}")

        # ---------------- GRAPH 1 ----------------

        st.subheader("Property Feature Comparison")

        feature_data = pd.DataFrame({
            "Feature": ["Area","Bedrooms","Bathrooms","Balcony","Age"],
            "Value": [area, bedrooms, bathrooms, balcony, age]
        })

        st.bar_chart(feature_data.set_index("Feature"))

        # ---------------- GRAPH 2 ----------------

        st.subheader("Area vs Predicted Price")

        graph_df = pd.DataFrame({
            "Area": [area],
            "Predicted Price": [predicted_price]
        })

        fig, ax = plt.subplots()
        ax.scatter(graph_df["Area"], graph_df["Predicted Price"])

        ax.set_xlabel("Area (sqft)")
        ax.set_ylabel("Predicted Price")
        ax.set_title("Area vs Price")

        st.pyplot(fig)

        # ---------------- SAVE HISTORY ----------------

        c.execute(
            "INSERT INTO history VALUES (?,?,?,?)",
            (st.session_state.username,city,area,predicted_price)
        )

        conn.commit()

# ---------------- ANALYTICS ----------------

elif selected == "Analytics":

    st.title("📊 Housing Market Analytics")

    data = pd.read_csv("data/indian_housing_dataset.csv")

    st.subheader("Price Distribution")

    fig,ax = plt.subplots()
    ax.hist(data["Price"],bins=30)

    st.pyplot(fig)

    st.subheader("Average Price by City")

    city_price = data.groupby("City")["Price"].mean()

    st.bar_chart(city_price)

# ---------------- HISTORY ----------------

elif selected == "History":

    st.title("📜 Prediction History")

    history = pd.read_sql("SELECT * FROM history", conn)

    if history.empty:
        st.info("No history available")

    else:
        st.dataframe(history)

        st.line_chart(history["price"])

# ---------------- LOGOUT ----------------

elif selected == "Logout":

    st.session_state.logged_in = False
    st.rerun()