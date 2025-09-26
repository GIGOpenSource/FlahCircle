import os
import boto3
from botocore.exceptions import ClientError
from django.conf import settings


class S3Uploader:
    def __init__(self):
        # 从环境变量获取AWS凭证和配置
        self.aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.environ.get('AWS_REGION', 'us-east-1')
        self.s3_bucket_name = os.environ.get('AWS_S3_BUCKET_NAME')
        
        # 创建S3客户端
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.aws_region
        )

    def upload_file(self, file_obj, file_name, folder_path=''):
        """
        上传文件到S3
        
        Args:
            file_obj: 文件对象
            file_name: 文件名
            folder_path: S3上的文件夹路径（可选）
            
        Returns:
            str: 文件的URL，如果上传失败则返回None
        """
        try:
            # 构建S3键名
            if folder_path:
                s3_key = f"{folder_path.rstrip('/')}/{file_name}"
            else:
                s3_key = file_name
            
            # 上传文件
            self.s3_client.upload_fileobj(
                file_obj,
                self.s3_bucket_name,
                s3_key,
                ExtraArgs={'ACL': 'public-read'}  # 设置文件为公开可读
            )
            
            # 构建并返回文件URL
            file_url = f"https://{self.s3_bucket_name}.s3.{self.aws_region}.amazonaws.com/{s3_key}"
            return file_url
            
        except ClientError as e:
            print(f"上传文件到S3时出错: {e}")
            return None
    
    def upload_file_from_path(self, file_path, file_name=None, folder_path=''):
        """
        从本地路径上传文件到S3
        
        Args:
            file_path: 本地文件路径
            file_name: 存储在S3上的文件名（可选，默认使用原文件名）
            folder_path: S3上的文件夹路径（可选）
            
        Returns:
            str: 文件的URL，如果上传失败则返回None
        """
        if not file_name:
            file_name = os.path.basename(file_path)
            
        try:
            # 构建S3键名
            if folder_path:
                s3_key = f"{folder_path.rstrip('/')}/{file_name}"
            else:
                s3_key = file_name
                
            # 上传文件
            self.s3_client.upload_file(
                file_path,
                self.s3_bucket_name,
                s3_key,
                ExtraArgs={'ACL': 'public-read'}  # 设置文件为公开可读
            )
            
            # 构建并返回文件URL
            file_url = f"https://{self.s3_bucket_name}.s3.{self.aws_region}.amazonaws.com/{s3_key}"
            return file_url
            
        except ClientError as e:
            print(f"上传文件到S3时出错: {e}")
            return None
    
    def delete_file(self, file_name, folder_path=''):
        """
        从S3删除文件
        
        Args:
            file_name: 文件名
            folder_path: S3上的文件夹路径（可选）
            
        Returns:
            bool: 删除成功返回True，否则返回False
        """
        try:
            # 构建S3键名
            if folder_path:
                s3_key = f"{folder_path.rstrip('/')}/{file_name}"
            else:
                s3_key = file_name
                
            # 删除文件
            self.s3_client.delete_object(
                Bucket=self.s3_bucket_name,
                Key=s3_key
            )
            return True
            
        except ClientError as e:
            print(f"从S3删除文件时出错: {e}")
            return False

# 使用示例的函数
def upload_to_s3(file_obj, file_name, folder_path=''):
    """
    便捷函数：上传文件到S3
    
    Args:
        file_obj: 文件对象
        file_name: 文件名
        folder_path: S3上的文件夹路径（可选）
        
    Returns:
        str: 文件的URL，如果上传失败则返回None
    """
    uploader = S3Uploader()
    return uploader.upload_file(file_obj, file_name, folder_path)
