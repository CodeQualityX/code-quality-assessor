import pandas as pd
import os
import joblib

from sklearn.linear_model import LogisticRegression
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report


X_train = pd.read_csv('data/processed/X_train.csv').drop(columns = "code_snippet")
X_test = pd.read_csv('data/processed/X_test.csv').drop(columns = "code_snippet")
y_train = pd.read_csv('data/processed/y_train.csv').squeeze()
y_test = pd.read_csv('data/processed/y_test.csv').squeeze()

numeric_features = X_train.select_dtypes(include=['int64', 'float64']).columns.tolist()
boolean_features = X_train.select_dtypes(include=['bool']).columns.tolist()



pipeline = Pipeline(steps=[
    ('classifier', LogisticRegression(
        multi_class='multinomial',
        solver='lbfgs',
        max_iter=1000,
        random_state=42
    ))
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

# Ensure output directories exist
os.makedirs('models', exist_ok=True)
os.makedirs('outputs', exist_ok=True)

# Save model
joblib.dump(pipeline, 'models/logistic_model.pkl')

# Save predicted labels
pd.DataFrame({'predicted_label': y_pred}).to_csv('outputs/logistic_predictions.csv', index=False)

# Save predicted probabilities
proba_df = pd.DataFrame(y_proba, columns=pipeline.named_steps['classifier'].classes_)
proba_df.to_csv('outputs/logistic_predicted_probs.csv', index=False)

print("Model, predictions, and probabilities saved.")
