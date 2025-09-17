import os
from datetime import datetime
import pandas as pd
import numpy as np
import joblib
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from gcp_utils import set_gcp_credentials, download_from_gcs, upload_to_gcs

load_dotenv()
GCP_CREDENTIALS_PATH = os.getenv('GCP_CREDENTIALS_PATH')
GCS_BUCKET = os.getenv('GCS_BUCKET')
GCS_DATA_PATH = os.getenv('GCS_DATA_PATH')
GCS_MODEL_DIR = os.getenv('GCS_MODEL_DIR')
MODEL_FILENAME = os.getenv('MODEL_FILENAME')


def preprocess_data(df):
    print("데이터 전처리 중...")

    df['Age'].fillna(df['Age'].mean(), inplace=True)
    df['Embarked'].fillna(df['Embarked'].mode()[0], inplace=True)
    df['Sex'] = df['Sex'].map({'male': 0, 'female': 1})
    df['Embarked'] = df['Embarked'].map({'S': 0, 'C': 1, 'Q': 2})

    features = ['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare', 'Embarked']
    X = df[features]
    y = df['Survived']

    return X, y, features

def train_model(X_train, y_train):
    print("\모델 학습 중...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test, features):
    print("\모델 평가 중...")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    report = classification_report(y_test, y_pred)
    importance_df = pd.DataFrame({
        'feature': features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    return accuracy, report, importance_df

def save_model_and_info(model, model_filename, info_filename, accuracy, report, importance_df, X_train, X_test, df, features):
    print("모델 및 정보 저장 중...")
    
    # 모델 저장 (joblib 사용)
    joblib.dump(model, model_filename)
    print(f"모델 저장 완료: {model_filename}")
    
    # 모델 정보 저장
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    content = f"""
Titanic Survival Prediction Model
==================================
생성 시간: {timestamp}
정확도: {accuracy:.4f}

데이터 정보:
- 총 샘플 수: {len(df)}
- 학습 샘플: {len(X_train)}
- 테스트 샘플: {len(X_test)}

사용된 특성:
{', '.join(features)}

모델 파라미터:
- 알고리즘: RandomForestClassifier
- n_estimators: {model.n_estimators}
- random_state: {model.random_state}

특성 중요도:
{importance_df.to_string(index=False)}

분류 보고서:
{report}
"""

    with open(info_filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"모델 정보 저장 완료: {info_filename}")

def log_section(title):
    print(f"\n========== {title} ==========")


# ======================
# 코드 실행
# ======================
log_section("GCP 인증 설정")
set_gcp_credentials(GCP_CREDENTIALS_PATH)

log_section("데이터 다운로드")
download_from_gcs(GCS_BUCKET, GCS_DATA_PATH, GCS_DATA_PATH)

log_section("데이터 로드 및 확인")
df = pd.read_csv(GCS_DATA_PATH)
print(df.info())
print("\n결측값:\n", df.isnull().sum())

X, y, features = preprocess_data(df)

log_section("데이터 분할")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = train_model(X_train, y_train)

accuracy, report, importance_df = evaluate_model(model, X_test, y_test, features)

log_section("모델 평가 결과")
print(f"정확도: {accuracy:.4f}")
print("\n분류 보고서:\n", report)
print("\n특성 중요도:\n", importance_df)

log_section("모델 및 정보 저장 및 업로드")

# 파일명 설정
model_filename = "titanic_model.pkl"
info_filename = "model_info.txt"

# 모델과 정보 저장
save_model_and_info(model, model_filename, info_filename, accuracy, report, importance_df, X_train, X_test, df, features)

# GCS에 모델 업로드
gcs_model_path = os.path.join(GCS_MODEL_DIR, model_filename)
upload_to_gcs(GCS_BUCKET, model_filename, gcs_model_path)
print(f"모델 업로드 완료: gs://{GCS_BUCKET}/{gcs_model_path}")

# GCS에 모델 정보 업로드
gcs_info_path = os.path.join(GCS_MODEL_DIR, info_filename)
upload_to_gcs(GCS_BUCKET, info_filename, gcs_info_path)
print(f"모델 정보 업로드 완료: gs://{GCS_BUCKET}/{gcs_info_path}")

# 로컬 임시 파일 삭제
os.remove(model_filename)
os.remove(info_filename)
print("로컬 임시 파일 삭제 완료.")
