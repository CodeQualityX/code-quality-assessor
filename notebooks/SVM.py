import pandas as pd
import os
import joblib

from sklearn.svm import SVC
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report

""" 
    When you load a single-column DataFrame with `pd.read_csv()`, it returns a DataFrame. with shape (n, 1) instead of a Series with shape (n,).
    However most machine learning models in scikit-learn expect the target variable to be a Series (1D array-like structure) rather than a DataFrame (2D structure with one column).
    hence, we use `.squeeze()` to convert the single-column DataFrame into a Series.

"""

X_train = pd.read_csv('data/processed/X_train.csv').drop(columns = ['code_snippet'])
X_test = pd.read_csv('data/processed/X_test.csv').drop(columns = ['code_snippet'])
y_train = pd.read_csv('data/processed/y_train.csv').squeeze()
y_test = pd.read_csv('data/processed/y_test.csv').squeeze()

numeric_features = X_train.select_dtypes(include=['int64', 'float64']).columns.tolist()
boolean_features = X_train.select_dtypes(include=['bool']).columns.tolist()


pipeline = Pipeline(steps=[
    ('classifier', SVC(probability=True, kernel='rbf', C=1.0, random_state=42))
])

pipeline.fit(X_train, y_train)

y_pred = pipeline.predict(X_test)
y_proba = pipeline.predict_proba(X_test)


print("Classification Report:")
print(classification_report(
    y_test,
    y_pred,
    target_names=["bad", "moderate", "excellent"]
))


os.makedirs('models', exist_ok=True)
os.makedirs('outputs', exist_ok=True)


joblib.dump(pipeline, 'models/svm_model.pkl')


pd.DataFrame({'predicted_label': y_pred}).to_csv('outputs/svm_predictions.csv', index=False)


proba_df = pd.DataFrame(y_proba, columns=pipeline.named_steps['classifier'].classes_)
proba_df.to_csv('outputs/svm_predicted_probs.csv', index=False)

print("Model, predictions, and probabilities saved.")
