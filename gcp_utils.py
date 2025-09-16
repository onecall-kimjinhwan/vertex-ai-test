"""
Google Cloud Platform (GCP) 유틸리티 함수들
"""
import os
from google.cloud import storage


def set_gcp_credentials(credentials_path="gcp_auth.json"):
    """
    GCP 인증 파일 설정
    
    Args:
        credentials_path (str): 인증 JSON 파일 경로
    """
    if os.path.exists(credentials_path):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        print(f"GCP 인증 파일 설정 완료: {credentials_path}")
        return True
    else:
        print(f"인증 파일을 찾을 수 없습니다: {credentials_path}")
        return False


def download_from_gcs(bucket_name, source_blob_name, destination_file_name):
    """
    GCS에서 파일을 로컬로 다운로드
    
    Args:
        bucket_name (str): GCS 버킷 이름
        source_blob_name (str): GCS 내 파일 경로
        destination_file_name (str): 로컬 저장 파일명
    """
    try:
        # 디렉토리가 없으면 생성
        print(f"GCS에서 파일 다운로드 시작: gs://{bucket_name}/{source_blob_name}... {destination_file_name}")
        
        # destination_file_name이 유효한지 확인
        if not destination_file_name:
            raise ValueError("destination_file_name이 비어있습니다.")
        
        # 디렉토리 경로가 있으면 생성
        dir_path = os.path.dirname(destination_file_name)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        
        print(f"GCS에서 파일 다운로드 중: gs://{bucket_name}/{source_blob_name}")
        blob.download_to_filename(destination_file_name)
        print(f"다운로드 완료: {destination_file_name}")
        
    except Exception as e:
        print(f"다운로드 실패: {e}")
        raise


def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    """
    로컬 파일을 GCS에 업로드
    
    Args:
        bucket_name (str): GCS 버킷 이름
        source_file_name (str): 로컬 파일 경로
        destination_blob_name (str): GCS 저장 경로
    """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        
        print(f"GCS에 파일 업로드 중: {source_file_name} -> gs://{bucket_name}/{destination_blob_name}")
        blob.upload_from_filename(source_file_name)
        print(f"업로드 완료: gs://{bucket_name}/{destination_blob_name}")
        
    except Exception as e:
        print(f"업로드 실패: {e}")
        raise


def list_gcs_files(bucket_name, prefix=""):
    """
    GCS 버킷의 파일 목록 조회
    
    Args:
        bucket_name (str): GCS 버킷 이름
        prefix (str): 파일 경로 접두사 (선택사항)
    """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=prefix)
        
        files = []
        for blob in blobs:
            files.append(blob.name)
            
        return files
        
    except Exception as e:
        print(f"파일 목록 조회 실패: {e}")
        return []


def check_gcp_authentication():
    """
    GCP 인증 상태 확인
    """
    try:
        storage_client = storage.Client()
        # 간단한 API 호출로 인증 확인
        list(storage_client.list_buckets())
        print("GCP 인증이 정상적으로 설정되어 있습니다.")
        return True
    except Exception as e:
        print(f"GCP 인증 실패: {e}")
        print("다음 명령어로 인증을 설정하세요: gcloud auth application-default login")
        return False


def get_project_id():
    """
    현재 GCP 프로젝트 ID 조회
    """
    try:
        storage_client = storage.Client()
        return storage_client.project
    except Exception as e:
        print(f"프로젝트 ID 조회 실패: {e}")
        return None
