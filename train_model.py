import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

data = pd.read_csv("../data/indian_housing_dataset.csv")

# convert balcony
data["Balcony"] = data["Balcony"].apply(lambda x: 1 if x > 0 else 0)

# encode city
data = pd.get_dummies(data, columns=["City"])

X = data.drop("Price", axis=1)
y = data["Price"]

X_train,X_test,y_train,y_test = train_test_split(
X,y,test_size=0.2,random_state=42
)

model = RandomForestRegressor()
model.fit(X_train,y_train)

# save model
joblib.dump(model,"house_price_model.pkl")

# save column names
joblib.dump(X.columns,"model_columns.pkl")

print("Model trained successfully")