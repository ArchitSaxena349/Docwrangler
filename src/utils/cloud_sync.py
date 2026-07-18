import os
import shutil
import logging
from pathlib import Path
from src.core.config import Config

logger = logging.getLogger(__name__)

class CloudSyncService:
    """Utility to backup and restore the local vector database from AWS S3"""
    
    @classmethod
    def _get_s3_client(cls):
        """Get an S3 client if credentials are configured"""
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            bucket_name = os.getenv("AWS_S3_BUCKET_NAME")
            access_key = os.getenv("AWS_ACCESS_KEY_ID")
            secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            
            if not all([bucket_name, access_key, secret_key]):
                logger.debug("Cloud sync skipped: S3 environment variables not configured.")
                return None, None
                
            region = os.getenv("AWS_S3_REGION_NAME", "us-east-1")
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            return s3_client, bucket_name
        except ImportError:
            logger.warning("boto3 library not found. Skipping cloud sync capabilities.")
            return None, None
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}", exc_info=True)
            return None, None

    @classmethod
    def download_vector_store(cls) -> bool:
        """Download and extract vector store backup from S3"""
        s3_client, bucket_name = cls._get_s3_client()
        if not s3_client:
            return False
            
        persist_dir = Path(Config.CHROMA_PERSIST_DIRECTORY)
        zip_path = persist_dir.parent / "vector_store_backup.zip"
        
        try:
            logger.info(f"Checking for vector store backup in S3 bucket '{bucket_name}'...")
            
            # Download zip from S3
            s3_client.download_file(
                Bucket=bucket_name,
                Key="vector_store_backup.zip",
                Filename=str(zip_path)
            )
            
            logger.info("Backup archive downloaded. Extracting to local vector store...")
            
            # Remove existing database to prevent merge conflicts
            if persist_dir.exists():
                shutil.rmtree(persist_dir)
            persist_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract zip contents
            shutil.unpack_archive(str(zip_path), str(persist_dir), 'zip')
            
            # Cleanup downloaded zip file
            if zip_path.exists():
                os.remove(zip_path)
                
            logger.info("Vector database restored from S3 successfully.")
            return True
            
        except Exception as e:
            # Check if it was just a 404 (file not found), which is normal for first startup
            from botocore.exceptions import ClientError
            if isinstance(e, ClientError) and e.response.get('Error', {}).get('Code') == '404':
                logger.info("No vector store backup found in S3 bucket. Starting with a fresh database.")
            else:
                logger.error(f"Failed to download vector store from S3: {e}", exc_info=True)
            
            # Cleanup zip if extraction failed halfway
            if zip_path.exists():
                try:
                    os.remove(zip_path)
                except:
                    pass
            return False

    @classmethod
    def upload_vector_store(cls) -> bool:
        """Compress and upload the local vector store to S3"""
        s3_client, bucket_name = cls._get_s3_client()
        if not s3_client:
            return False
            
        persist_dir = Path(Config.CHROMA_PERSIST_DIRECTORY)
        if not persist_dir.exists():
            logger.warning(f"Local vector store directory '{persist_dir}' does not exist. Skipping backup.")
            return False
            
        zip_base_name = persist_dir.parent / "vector_store_backup"
        zip_file_path = persist_dir.parent / "vector_store_backup.zip"
        
        try:
            logger.info("Compressing local vector store database...")
            
            # Archive directory contents as a zip
            shutil.make_archive(str(zip_base_name), 'zip', str(persist_dir))
            
            logger.info(f"Uploading vector store archive to S3 bucket '{bucket_name}'...")
            
            # Upload to S3
            s3_client.upload_file(
                Filename=str(zip_file_path),
                Bucket=bucket_name,
                Key="vector_store_backup.zip"
            )
            
            # Cleanup archive
            if zip_file_path.exists():
                os.remove(zip_file_path)
                
            logger.info("Vector database successfully backed up to S3.")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload vector store to S3: {e}", exc_info=True)
            if zip_file_path.exists():
                try:
                    os.remove(zip_file_path)
                except:
                    pass
            return False
