"""
Vertex AI Custom Job 제출 스크립트
"""
import os
from google.cloud import aiplatform
from gcp_utils import set_gcp_credentials, download_from_gcs
from dotenv import load_dotenv

load_dotenv()
GCP_CREDENTIALS_PATH = "gcp_auth.json"
GCP_REGION = os.getenv('GCP_REGION')
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID')
GCS_BUCKET = os.getenv('GCS_BUCKET')
GCS_DATA_PATH = os.getenv('GCS_DATA_PATH')
GCS_MODEL_DIR = os.getenv('GCS_MODEL_DIR')
MODEL_FILENAME = os.getenv('MODEL_FILENAME')
CONTAINER_TAG_FILE = os.getenv('CONTAINER_TAG_FILE')
CONTAINER_REGISTRY_PATH = os.getenv('CONTAINER_REGISTRY_PATH')


def submit_custom_job():
    """
    Vertex AI Custom Job 제출
    """
    # GCP 인증 설정
    set_gcp_credentials(GCP_CREDENTIALS_PATH)
    
    # GCS에서 최신 태그 조회
    print("GCS에서 최신 컨테이너 태그 조회 중...")
    try:
        download_from_gcs(GCS_BUCKET, CONTAINER_TAG_FILE, CONTAINER_TAG_FILE)
        with open(CONTAINER_TAG_FILE, "r") as file:
            CONTAINER_IMAGE = f"{CONTAINER_REGISTRY_PATH}:{file.read().strip()}"
        os.remove(CONTAINER_TAG_FILE) 
        print(f"최신 태그: {CONTAINER_IMAGE}")
    except Exception as e:
        print(f"태그 조회 실패: {e}")
        print("프로세스를 종료합니다.")
        exit(1)
    
    # Vertex AI 초기화
    aiplatform.init(project=GCP_PROJECT_ID, location=GCP_REGION)
    
    # Custom Job 정의
    job = aiplatform.CustomJob(
        display_name="titanic-ml-training-job",
        worker_pool_specs=[
            {
                "machine_spec": {
                    "machine_type": "n1-standard-4",
                },
                "replica_count": 1,
                "container_spec": {
                    "image_uri": CONTAINER_IMAGE,
                    "env": [
                        {"name": "GCP_CREDENTIALS_PATH", "value": GCP_CREDENTIALS_PATH},
                        {"name": "GCS_BUCKET", "value": GCS_BUCKET},
                        {"name": "GCS_DATA_PATH", "value": GCS_DATA_PATH},
                        {"name": "GCS_MODEL_DIR", "value": GCS_MODEL_DIR},
                        {"name": "MODEL_FILENAME", "value": MODEL_FILENAME},
                    ]
                }
            }
        ],
        staging_bucket=f"gs://{GCS_BUCKET}" # 이거 꼭 해주어야함. 데이터가 저장되진 않는듯..?
    )
    
    print("Vertex AI Custom Job 제출 중...")
    print(f"Job 이름: titanic-ml-training-job")
    print(f"컨테이너 이미지: {CONTAINER_IMAGE}")
    print(f"머신 타입: n1-standard-4")
    
    # Job 제출
    job.submit()
    
    print(f"Job이 제출되었습니다!")
    print(f"Job ID: {job.resource_name}")
    print(f"상태 확인: https://console.cloud.google.com/vertex-ai/training/custom-jobs")
    
    return job


if __name__ == "__main__":
    # Job 제출
    job = submit_custom_job()
